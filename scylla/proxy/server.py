import random
import socket
import threading
from multiprocessing import Process

from scylla.database import ProxyIP
from scylla.loggings import logger


def get_proxy(https=False) -> ProxyIP:
    proxies: [ProxyIP] = ProxyIP.select().where(ProxyIP.is_valid == True).where(ProxyIP.stability >= 0.9)

    if https:
        proxies = proxies.where(ProxyIP.is_https == True)

    proxies = proxies.order_by(ProxyIP.updated_at.desc()).limit(63)
    proxy: ProxyIP = random.choice(proxies)

    return proxy


def start_forward_proxy_server_non_blocking():
    p = Process(target=start_forward_proxy_server, daemon=True)
    p.start()


def send(sender, recver, msg):
    while 1:
        data = sender.recv(2048)
        if not data: break
        recver.sendall(data)
    logger.info('close conn {}'.format(msg))
    sender.close()
    recver.close()


def proxy(client):
    retry_time = 1
    while retry_time < 10:
        logger.info('start request time: {}'.format(retry_time))
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        remote_proxy = get_proxy()
        logger.info('use proxy {}:{}'.format(remote_proxy.ip, remote_proxy.port))
        if not server.connect_ex((remote_proxy.ip, remote_proxy.port)):
            logger.info('connect success')
            threading.Thread(target=send, args=(client, server, "send to remote")).start()
            threading.Thread(target=send, args=(server, client, "recv from remote")).start()
            break
        else:
            retry_time += 1


def start_forward_proxy_server():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    if not server.bind(("0.0.0.0", 8081)):
        server.listen(50)
        logger.info('start listener at {}:{}'.format('0.0.0.0', 8081))
        while True:
            conn, addr = server.accept()
            logger.info('get connect from {}'.format(addr))
            threading.Thread(target=proxy, args=(conn,)).start()
    else:
        logger.error("can listener {}:{}".format('0.0.0.0', 8081))
