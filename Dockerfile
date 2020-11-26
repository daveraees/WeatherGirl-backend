FROM ubuntu:18.04

MAINTAINER David Rais 

RUN apt-get update -y && \
    apt-get install -y python3-pip python3-dev

COPY ./requirements.txt /requirements.txt


WORKDIR /

RUN pip3 install --upgrade pip
RUN pip3 install -r requirements.txt

COPY . /

RUN adduser --disabled-password --gecos '' nginx\
  && chown -R nginx:nginx /app \
  && chmod 777 /run/ -R \
  && chmod 777 /root/ -R

ENTRYPOINT [ "/bin/bash", "/launch.sh"]

