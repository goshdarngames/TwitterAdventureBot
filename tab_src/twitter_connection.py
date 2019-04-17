#############################################################################
# twitter_connection.py
#----------------------------------------------------------------------------
# Provides a context manager that can be used to access Twitter
#############################################################################

import json, threading, queue

import tweepy

def load_keys ():

    print ( "Loading keys..." )

    with open ( "twitter_keys.json" ) as json_data_file :

        data = json.load ( json_data_file ) 

        return data

#----------------------------------------------------------------------------

def chop_text ( txt, n = 265 ):

    """
    Chops a string into a list of strings of n length.
    """

    #thanks stack overflow...

    return [ txt [ i : i + n ] for i in range ( 0, len ( txt ), n ) ]

#----------------------------------------------------------------------------

def check_mentions ( api, apiLock, mentionQ, stopEvent ):
    pass

#----------------------------------------------------------------------------

class TwitterConnection:

    def __enter__ ( self ):

        keys = load_keys ()

        auth = tweepy.OAuthHandler ( 
                keys [ "consumer_key" ],
                keys [ "consumer_secret" ] )

        auth.set_access_token (
                keys [ "access_token" ],
                keys [ "access_token_secret"] )

        self._api = tweepy.API ( auth )

        # Used to ensure only one thread accesses the api object at a time
        self._apiLock = threading.Lock ()

        # Used to signal that the twitter connection is no longer needed
        self._stopEvent = threading.Event ()
        
        # Queue for posting and reading mentions from twitter
        self._mentionQ = queue.Queue ()

        # This thread will loop continuously checking for twitter mentions
        self.mentionThread = threading.Thread (  \
                         target = check_mentions, 
                         args   = ( self._api,
                                    self._apiLock,
                                    self._mentionQ,
                                    self._stopEvent )) 

        self.mentionThread.daemon = True
        self.mentionThread.start ()

    #------------------------------------------------------------------------

    def __exit__ ( self, *args ):

        self._stopEvent.set ()

    #------------------------------------------------------------------------

    def send_message_chain ( self, msgList, replyID = None ):

        msgIDs = []

        for msg in msgList:

            for chopped in chop_text ( msg ):

                with self.apiLock:
                    status = self.api.update_status ( chopped, replyID )

                replyID = status.id

                msgIDs.append ( replyID )

        return msgIDs


    
