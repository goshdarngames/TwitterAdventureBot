import tweepy
import json

def load_keys ():

    print ( "Loading keys..." )

    with open ( "twitter_keys.json" ) as json_data_file :

        data = json.load ( json_data_file ) 

        return data

#----------------------------------------------------------------------------

def chop_text ( txt, n = 265 ):

    #thanks stack overflow...

     return [ txt [ i : i + n ] for i in range ( 0, len ( txt ), n ) ]

#----------------------------------------------------------------------------

class TwitterConnection:

    def __init__ ( self ):

        #create authentication

        keys = load_keys ()

        auth = tweepy.OAuthHandler ( 
                keys [ "consumer_key" ],
                keys [ "consumer_secret" ] )

        auth.set_access_token (
                keys [ "access_token" ],
                keys [ "access_token_secret"] )

        self.api = tweepy.API ( auth )

    #------------------------------------------------------------------------

    def send_message_chain ( self, msgList, replyID = None ):

        msgIDs = []

        for msg in msgList:

            for chopped in chop_text ( msg ):

                status = self.api.update_status ( chopped, replyID )

                replyID = status.id

                msgIDs.append ( replyID )

        return msgIDs


    
