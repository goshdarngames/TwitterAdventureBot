#############################################################################
# tab.py
#----------------------------------------------------------------------------
# Twitter Adventure Bot
#
# Allows an Interactive Fiction game to be controlled by multiple users
# through twitter comments.
#############################################################################

import sys, time, uuid, random

from queue import Queue, Empty
from threading import Thread, Lock

from frotz_runner import FrotzRunner
from twitter_connection import TwitterConnection

#----------------------------------------------------------------------------

#How long to sleep at the end of each 'game loop'
GAME_LOOP_SLEEP = 1

#----------------------------------------------------------------------------

def log_msg ( msg ):

    print ( msg, flush = True )

#----------------------------------------------------------------------------

def cmd_from_text ( text ):

    log_msg ( "cmd_from_text:\n"+text )
    
    if len ( text ) < 5:
        return None

    cmd = None

    #check each line for a command

    for line in text.split ( "\n" ):

        #strip before checking for 'cmd' in case the user put spaces
        line = line.strip ()

        #check for cmd and return the rest of the command

        if line [ : 4 ] == "cmd ":

            cmd = line [ 4 : ]

            cmd = cmd.strip ()

            #NOTE: command/profanity filter goes here

    return cmd 

#----------------------------------------------------------------------------

def check_mentions_for_cmd ( tc ):
    
    return None

#----------------------------------------------------------------------------

def post_header_status ( tc, text ):

    """
    Special method for posting headers with a unique number attached since
    sometimes tweepy will block repeated messages.
    """

    unique = str ( uuid.uuid4 () )[:8]

    text += "\n\n"+unique

    headerID = tc.send_message_chain ( [ text ] ) [ 0 ]

    return headerID

#----------------------------------------------------------------------------
    
def game_loop ( frotz, tc ):

    #The headerID holds the ID of the message that the next piece of 
    #output should reply to
    headerID = post_header_status ( tc, "Starting Adventure" )

    while True:

        #if a commmand is due to be sent then send it and change the 
        #header so later output is posted as a reply
        
        command = check_mentions_for_cmd ( tc )

        if command != None:

            log_msg ( "Command:" )

            #Expect commands from the command queue to be dictionary
            #objects with the form { user : user.id, cmd : "..." }

            msg = "Sending Command: "+command [ "cmd" ]

            log_msg ( msg )

            headerID = post_header_status ( tc, tcLock, msg )

            frotz.write_command ( command [ "cmd" ] + "\n" )


        #out ID is the message that the next output chain should reply to
        outID = headerID

        output = frotz.read_output_block ()

        if len ( output ) > 0:
            
            consoleMsg = "Sending output:\n" + "\n".join( output )
            log_msg ( consoleMsg )
            
            #record the last message sent so that the next output will be
            #sent as a reply
            outID = tc.send_message_chain ( output, outID ) [ -1 ]


        time.sleep ( GAME_LOOP_SLEEP )

#----------------------------------------------------------------------------

def main ():
    
    log_msg ( "Twitter Adventure Bot" )


    log_msg ( "Creating Twitter Connection" )

    with TwitterConnection () as tc:
    
        log_msg ( "Starting frotz" )

        with FrotzRunner ( "z8/advent.z8" ) as frotz:

            log_msg ( "Entering game loop." )

            game_loop ( frotz, tc )




if __name__ == "__main__":
    sys.exit ( main () )
