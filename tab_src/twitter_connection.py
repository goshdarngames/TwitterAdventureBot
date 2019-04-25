#############################################################################
# twitter_connection.py
#----------------------------------------------------------------------------
# Provides a context manager that can be used to access Twitter
#############################################################################

import json, threading, queue, time

import tweepy

#----------------------------------------------------------------------------

#How long to sleep between checking mentions
CHECK_MENTION_SLEEP = 3*60

#How long to sleep after a tweep error message - usually a rate limit error
TWEEP_ERROR_SLEEP = 15*60

#----------------------------------------------------------------------------

def load_keys ():

    print ( "Loading keys..." )

    with open ( "twitter_keys.json" ) as json_data_file :

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

def check_mentions ( api, apiLock, mentionQ, stopEvent ):
    """
    This function is run by a thread in order to periodically check
    twitter for mentions.
    """

    latestMention = None
    
    while not stopEvent.is_set ():

        try:
            with apiLock:

                mentions = tweepy.Cursor ( 
                        api.mentions_timeline,
                        since_id  = latestMention 
                    ).items ()

        except TweepError as e:
            
            print ( e, file = sys.stderr )

            time.sleep ( TWEEP_ERROR_SLEEP )

        else:

            #on firts call record latest mention in order to
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
                            "username" : mention.user.name
                        }

                    mentionQ.put ( mentionData )

        finally:

            time.sleep ( CHECK_MENTION_SLEEP )


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
        self.mentionThread = threading.Thread (  \
                         target = check_mentions, 
                         args   = ( self._api,
                                    self._apiLock,
                                    self._mentionQ,
                                    self._stopEvent )) 

        self.mentionThread.daemon = True
        self.mentionThread.start ()

        return self

    #------------------------------------------------------------------------

    def __exit__ ( self, *args ):

        self._stopEvent.set ()

    #------------------------------------------------------------------------

    def send_message_chain ( self, msgList, replyID = None ):

        msgIDs = []

        packedMsgList = pack_messages ( msgList )

        for msg in packedMsgList:

            with self._apiLock:
                status = self._api.update_status ( msg, replyID )

            replyID = status.id

            msgIDs.append ( replyID )

        return msgIDs

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
    
