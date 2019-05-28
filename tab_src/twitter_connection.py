#############################################################################
# twitter_connection.py
#----------------------------------------------------------------------------
# Provides a context manager that can be used to access Twitter
#############################################################################

import json, threading, queue, time, logging, os

import tweepy

#Errors thrown during Internet connection interruption:

from ssl import SSLError
from requests.exceptions import Timeout, ConnectionError

from urllib3.exceptions import NewConnectionError

CONNECTION_ERRORS = ( SSLError, Timeout, ConnectionError,
                      NewConnectionError )

#----------------------------------------------------------------------------

#Location of the twitter keys file.
TWITTER_KEYS_PATH = os.path.join ( "config","twitter_keys.json" )

#How long to sleep between checking mentions
CHECK_MENTION_SLEEP = 5#4*60

#How long to sleep after a tweep error message - usually a rate limit error
TWEEP_RATE_ERROR_SLEEP = 16*60

#how long to sleep after an API call encounters a connection error
NETWORK_ERROR_SLEEP = 20*60

#Sleep period after an unexpected error from the twitter API
UNEXPECTED_ERROR_SLEEP = 60*60

#Sleep period between sending messages in a chain
MESSAGE_CHAIN_SLEEP = 5


#----------------------------------------------------------------------------

def load_keys ():

    logging.info ( "Loading keys..." )

    with open ( TWITTER_KEYS_PATH ) as json_data_file :

        data = json.load ( json_data_file ) 

        return data

#----------------------------------------------------------------------------

def pack_messages ( msgList, size = 265 ):
    """
    Packs a list of strings into as few tweet messages as possible.

    Splits the msgList up into words so that words will not be split
    across tweets.

    Returns a list of strings that can be sent as tweets.
    """

    assert size > 0

    words = []

    #Loop through all of the messages in order to combine them into a
    #single list of words - Note:  Spaces are inserted into the words list
    #as words to simplify the process of re-combining them

    msg = " ".join ( msgList )


    msgSplit = msg.split ( ' ' )

    while len ( msgSplit ) > 0:

        word = msgSplit.pop ()

        #call chop_text just for the rare case that the word is too
        #long for a single tweet
        chopped = chop_text ( word, size )


        # Need to reverse the chopped list in case the word was split
        # since the next phase expects the list in reverse order
        words = [ *words, *reversed ( chopped ) ]

        if len ( msgSplit ) > 0:

            words.append ( " " )

    tweets = []

    currentTweet = ""

    while len ( words ) > 0:

        #Since the list is in reverse order pop is used to process the items
        word = words.pop ()

        #if the word fits add it - special case for first word
        if len ( currentTweet ) + len ( word ) < size or \
           currentTweet == "":

            currentTweet += word

        #not enough room for the word in current tweet
        else:

            tweets.append ( currentTweet )

            currentTweet = word

        #last word in the list append the word so far
        if len ( words ) == 0:

            tweets.append ( currentTweet )

    #remove any tweets that are just spaces

    tweets = [ x for x in tweets if x.strip () != '' ]

    return tweets



#----------------------------------------------------------------------------

def chop_text ( txt, n = 265 ):

    """
    Chops a string into a list of strings of n length.
    """

    assert ( n > 0 )

    #thanks stack overflow...

    return [ txt [ i : i + n ] for i in range ( 0, len ( txt ), n ) ]


#----------------------------------------------------------------------------

class TwitterConnection:

    def __enter__ ( self ):

        keys = load_keys ()

        auth = tweepy.OAuthHandler ( 
                keys [ "consumer_key" ],
                keys [ "consumer_secret" ] )

        auth.set_access_token (
                keys [ "access_token" ],
                keys [ "access_token_secret" ] )

        self._api = tweepy.API ( auth )

        # Used to ensure only one thread accesses the api object at a time
        self._apiLock = threading.Lock ()

        # Used to signal that the twitter connection is no longer needed
        self._stopEvent = threading.Event ()
        
        # Queue for posting and reading mentions from twitter
        self._mentionQ = queue.Queue ()

        # This thread will loop continuously checking for twitter mentions
        self.mentionThread = threading.Thread ( 
                target = self._check_mentions_loop ) 

        self.mentionThread.daemon = True
        self.mentionThread.start ()

        return self

    #------------------------------------------------------------------------

    def __exit__ ( self, *args ):

        self._stopEvent.set ()

    #------------------------------------------------------------------------

    def call_twitter_api ( self, api_call ):
        """
        This function is used to encapsulate calls to the twitter function
        so that logging and error handling can be contained in one place.

        api_call - lambda function that can be called with the _api object
                   as a parameter to execute the desired twitter call

        sleep_time - how long the function should sleep after calling the
                     twitter API

        The funcion will log a message and sleep if an error occurs. 
        """

        api_return = None

        try:

            with self._apiLock:

                api_return = api_call ( self._api )

        except CONNECTION_ERRORS as e:

            logging.warning ( "Network Error:  ", str ( e ) )

            time.sleep ( NETWORK_ERROR_SLEEP )

        except tweepy.RateLimitError as e:

            logging.warning ( "Network Error:  ", str ( e ) )

            time.sleep ( TWEEP_RATE_ERROR_SLEEP )

        except e:
            
            logging.critical ( "Unexpected Error during twitter API call:  ",
                               str ( e ) )

            time.sleep ( UNEXPECTED_ERROR_SLEEP )

        return api_return 

    #------------------------------------------------------------------------

    def send_message_chain ( self, msgList, replyID = None ):

        msgIDs = []

        packedMsgList = pack_messages ( msgList )

        for msg in packedMsgList:

            status = None

            logging.info ( "Sending Message: "+msg )

            #Use a loop to send message in order to retry on rate limit
            while status == None:

                api_call = lambda api:  api.update_status ( msg, replyID )

                status = self.call_twitter_api ( api_call )

            replyID = status.id

            msgIDs.append ( replyID )

        return msgIDs

    #------------------------------------------------------------------------

    def _check_mentions_loop ( self ):
        """
        This function is run by a thread in order to periodically check
        twitter for mentions.

        The mentions will be put on a queue so that they can be checked
        using get_latest_mentions
        """

        #This is the id of the most recent mention.  The first time the 
        #loop runs the value will be stored here so that mentions made 
        #before the system started will be discarded
        latestMention = None
        
        while not self._stopEvent.is_set ():

            logging.info ( "Checking mentions." )

            api_call = lambda api: tweepy.Cursor ( 
                    api.mentions_timeline,
                    since_id  = latestMention 
                ).items ()

            mentions = self.call_twitter_api ( api_call )

            #on first call record latest mention in order to
            #avoid mentions made before the system started

            if latestMention == None:

                try:

                    latestMention = next ( mentions ).id

                except StopIteration:
                    
                    latestMention = 0

            
            #Iterate through mentions as normal on future calls

            else:

                for mention in mentions:

                    if mention.id > latestMention:

                        latestMention = mention.id

                    #Create a dict containing only the desired data
                    mentionData = \
                        {
                            "text"     : mention.text,
                            "id"       : mention.id,
                            "username" : mention.user.screen_name
                        }

                    self._mentionQ.put ( mentionData )

            time.sleep ( CHECK_MENTION_SLEEP )


    #------------------------------------------------------------------------

    def get_latest_mentions ( self, maxM = 100 ):

        mentions = []

        while len ( mentions ) < 100:

            try:
                m = self._mentionQ.get_nowait ()
            except queue.Empty:
                break
            else:
                mentions.append ( m )

        return mentions
    
