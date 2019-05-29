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

#----------------------------------------------------------------------------

#Location of the twitter keys file.
TWITTER_KEYS_PATH = os.path.join ( "config","twitter_keys.json" )

#How long to sleep after a tweep error message - usually a rate limit error
TWEEP_RATE_ERROR_SLEEP = 16*60

#how long to sleep after an API call encounters a connection error
NETWORK_ERROR_SLEEP = 20*60

#Sleep period after an unexpected error from the twitter API
UNEXPECTED_ERROR_SLEEP = 60*60

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

class CursorIterWrapper:

    def __init__ ( self, twitterConnection, cursor ):

        self.tc = twitterConnection
        self.cursor = cursor

    def __iter__ ( self ):

        return self

    def __next__ ( self ):

        api_call = lambda api=None: next ( self.cursor )

        mention = None

        try:

            mention = self.tc.call_twitter_api ( api_call )
        
        except StopIteration:

            raise StopIteration

        return mention

    def first ( self ):

        try:

            return self.__next__ ()
        
        except StopIteration:

            return None


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

        #the get_latest_mentions method will return status id's greater
        #than this value
        self.latestMention = self._init_latest_mention ()

        return self

    #------------------------------------------------------------------------

    def __exit__ ( self, *args ):

        pass

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

        except tweepy.RateLimitError as e:

            logging.warning ( "Rate-limit Error:  %s", e )

            time.sleep ( TWEEP_RATE_ERROR_SLEEP )

        #Most likely thrown during network error
        except tweepy.TweepError as e:

            logging.warning ( "Tweepy Error: %s  ", e )

            time.sleep ( NETWORK_ERROR_SLEEP )

        except ( SSLError, Timeout, ConnectionError, NewConnectionError ):

            logging.warning ( "Network Error:  ", exc_info=True )

            time.sleep ( NETWORK_ERROR_SLEEP )

        #special case for tweepy cursor calls when no more items
        except StopIteration:

            raise StopIteration

        except Exception:
            
            logging.critical ( "Unexpected Error during twitter API call:  ",
                               exc_info=True )

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

    def _init_latest_mention ( self ):
        """
        Returns the id of the most recent mention.

        Used when the system starts to get the most recent mention that
        occurred before the system started.
        """

        #get an iterator for all mentions using tweepy.Cursor

        api_call = lambda api: tweepy.Cursor ( 
                api.mentions_timeline,
                since_id  = None 
            ).items ()

        cursor = self.call_twitter_api ( api_call )

        wrappedIterator = CursorIterWrapper ( self, cursor )

        #try and get the id of the first item in the mentions iterator

        latestMention = wrappedIterator.first ()

        if latestMention is None:

            return 0

        else:
            
            return latestMention.id
            

    #------------------------------------------------------------------------

    def get_latest_mentions ( self ):
        """
        This function is run by a thread in order to periodically check
        twitter for mentions.

        The mentions will be put on a queue so that they can be checked
        using get_latest_mentions
        """

        logging.info ( "Checking mentions." )

        returnList = []

        api_call = lambda api: tweepy.Cursor ( 
                api.mentions_timeline,
                since_id  = self.latestMention 
            ).items ()

        cursor = self.call_twitter_api ( api_call )

        wrappedIterator = CursorIterWrapper ( self, cursor )

        for mention in wrappedIterator:

            #API return can be None if there is a connection error
            if mention is None:

                break

            #update the latestMention field

            if mention.id > self.latestMention:

                self.latestMention = mention.id

            #Create a dict containing only the desired data
            mentionData = \
                {
                    "text"     : mention.text,
                    "id"       : mention.id,
                    "username" : mention.user.screen_name
                }

            returnList.append ( mentionData )

        return returnList

