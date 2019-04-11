# TwitterAdventureBot Dockerfile

FROM alpine

RUN adduser -Ds /bin/sh tab

USER tab

WORKDIR /home/tab

COPY z8 /home/tab/z8
