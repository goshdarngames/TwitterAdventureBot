# TwitterAdventureBot Dockerfile

FROM alpine

RUN apk update

#install C compiler and make to build frotz and clean up after
RUN apk add --virtual build-dependencies \
    build-base gcc wget git 

#  && rm -rf /tmp/* \
#  && rm -rf /var/cache/apk/*

#copy across story file
COPY z8 /home/tab/z8

#copy frotz source code
COPY frotz /home/tab/frotz

#create user 'tab' to run the system
RUN adduser -Ds /bin/sh tab

#make and install frotz
WORKDIR /home/tab/frotz

#RUN make dumb



#change user to tab for execution of the Twitter Bot
#USER tab

#WORKDIR /home/tab
