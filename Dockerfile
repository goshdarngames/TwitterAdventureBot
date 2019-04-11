# TwitterAdventureBot Dockerfile

FROM alpine

#create user 'tab' to run the system
RUN adduser -Ds /bin/sh tab
USER tab
WORKDIR /home/tab

#copy across story file
COPY z8 /home/tab/z8
