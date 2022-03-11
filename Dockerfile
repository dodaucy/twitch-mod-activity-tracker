FROM ubuntu:latest

RUN apt-get update
RUN DEBIAN_FRONTEND=noninteractive apt-get install -y \
    python3 python3-pip \
    tini

RUN mkdir /app
WORKDIR /app

COPY requirements.txt .
RUN pip3 install -r requirements.txt

COPY . /app

RUN mkdir /config /data

COPY config_example.yml /config/config.yml
COPY languages /config/languages

ENV RUN_IN_DOCKER 1
ENV PYTHONUNBUFFERED 1

VOLUME ["/config"]
VOLUME ["/data"]

ENTRYPOINT [ "/bin/tini", "--", "python3", "/app/main.py" ]
