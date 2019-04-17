import tweepy
import json

from queue  import Queue, Empty
from threading import Thread, Lock

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

def check_mentions ( api, apiLock, mentionQ ):
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

        self.api = tweepy.API ( auth )

        self.apiLock = Lock ()
        
        self.mentionQ = Queue ()

        self.mentionThread = \
                Thread ( target = check_mentions, 
                         args   = ( self.api, self.apiLock, self.mentionQ )) 

        self.mentionThread.daemon = True
        self.mentionThread.start ()

    #------------------------------------------------------------------------

    def __exit__ ( self ):

        self.mentionThread.terminate ()

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


    
