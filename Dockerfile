# TwitterAdventureBot Dockerfile

FROM alpine

#create user 'tab' to run the system
RUN adduser -Ds /bin/sh tab

#install C compiler and make to build frotz and clean up after
RUN apk add --update --no-cache build-base sudo \
  && rm -rf /tmp/* \
  && rm -rf /var/cache/apk/*


USER tab
WORKDIR /home/tab

#copy across story file
COPY z8 /home/tab/z8

#copy frotz source code
COPY frotz /home/tab/frotz
