FROM python:3-alpine
LABEL maintainer="steve@tyzen9.com"

ARG url=http://localhost
ARG port=8080
ARG username
ARG password
ARG portFilePath=/pia-shared/port.dat
ARG watchIntervalSecs=30

ENV QBITTORRENT_URL=$url
ENV QBITTORRENT_PORT_NUMBER=$port
ENV QBITTORRENT_USERNAME=$username
ENV QBITTORRENT_PASSWORD=$password
ENV FILE=$portFilePath
ENV WATCH_INTERVAL=$watchIntervalSecs

# Install the Alpine libraries that we need using APK
RUN apk add --no-cache \
        bash \
        curl \
        nmap-ncat

WORKDIR /usr/src/app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

RUN mkdir -p qph
COPY app/. ./qph/.

#ENTRYPOINT ["tail", "-f", "/dev/null"]
ENTRYPOINT ["python3", "qph/main.py"]

