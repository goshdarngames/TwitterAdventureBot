# TwitterAdventureBot Dockerfile

FROM alpine

RUN apk update

#install C compiler and make to build frotz and clean up after
RUN apk add --virtual build-dependencies \
    build-base gcc wget git              

#copy across story file
COPY z8 /home/tab/z8

#copy frotz source code
COPY frotz /home/tab/frotz

#create user 'tab' to run the system
RUN adduser -Ds /bin/sh tab

#make and install frotz
WORKDIR /home/tab/frotz

RUN make dumb

RUN make install_dumb

#install python3
RUN apk add python3

#return to home dir before clean
WORKDIR /home/tab

#clean up after install
RUN rm -rf /home/tab/frotz       \
  && rm -rf /tmp/*               \
  && rm -rf /var/cache/apk/*

#change to tab workdir

WORKDIR /home/tab/

#install required python modules

COPY requirements.txt /home/tab/requirements.txt
RUN pip3 install --upgrade pip
RUN pip3 install -r requirements.txt

#copy over python files

COPY tab_src /home/tab/

#--Install Complete

#change user to tab for execution of the Twitter Bot

USER tab

#run the python file

#These entry points are for testing modules with command line
#ENTRYPOINT [ "python3", "frotz_cmd.py" ]
ENTRYPOINT [ "python3", "twitter_cmd.py" ]

#ENTRYPOINT [ "python3", "tab.py" ]
