FROM python:3.6.5-slim
RUN apt-get update && apt-get install -y g++ gcc libxslt-dev make libcurl4-openssl-dev build-essential

RUN apt-get install -y libssl-dev

RUN mkdir -p /var/www/scylla
WORKDIR /var/www/scylla