FROM python:3.6.5-slim

RUN apt-get update && apt-get install -y curl gnupg

RUN curl -sL https://deb.nodesource.com/setup_6.x | bash -

RUN apt-get install -y g++ gcc libxslt-dev make libcurl4-openssl-dev build-essential

RUN apt-get install -y libssl-dev

RUN apt-get install -y nodejs npm

RUN npm install -g parcel-bundler

RUN mkdir -p /var/www/scylla

WORKDIR /var/www/scylla

COPY . /var/www/scylla

RUN pip install -r requirements.txt

RUN npm install

RUN make assets-build

EXPOSE 8899
EXPOSE 8081

CMD python -m scylla | grep INFO > log.txt