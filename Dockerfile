FROM ubuntu:latest

# Install apt packages
RUN apt-get update
RUN DEBIAN_FRONTEND=noninteractive apt-get install -y \
    python3 \
    python3-pip \
    tini

# Set work path
RUN mkdir /app
WORKDIR /app

# Install python requirements
COPY requirements.txt .
RUN pip3 install -r requirements.txt

# Setup config
RUN mkdir /config
RUN mv /app/config_example.yml /config/config.yml
RUN mv /app/languages /config/languages

# Copy program
COPY . /app

# Delete useless files
RUN rm requirements.txt

# Set ENV to tell the program to run in Docker
ENV RUN_IN_DOCKER 1

# Set ENV to display the output properly
ENV PYTHONUNBUFFERED 1

VOLUME ["/config"]

ENTRYPOINT ["/bin/tini", "--", "python3", "/app/main.py"]
