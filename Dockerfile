# TwitterAdventureBot Dockerfile

FROM alpine

RUN adduser -Ds /bin/sh tab

USER tab

WORKDIR /home/tab
