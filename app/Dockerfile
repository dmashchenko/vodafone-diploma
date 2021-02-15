FROM ubuntu:latest

MAINTAINER Dima Mashchenko "mashchenkod@gmail.com"

RUN apt-get update -y && \
    apt-get install -y python3-pip

COPY . /app

WORKDIR /app

RUN pip3 install -r requirements.txt


ENTRYPOINT [ "python3" ]

CMD [ "app.py" ]
