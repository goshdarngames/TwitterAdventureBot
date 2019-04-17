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

#How long to sleep between read commands
CMD_READ_SLEEP = 10

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

def get_cmds_from_twitter ( tc, tcLock, cmdQ ):

    # status id of the last mention tweet processed.  This is used to try
    # and avoid processing the same command twice

    latestMentionID = None

    while True:

        #sleep at the start of the loop so the thread will sleep after a 
        # 'continue'

        time.sleep ( CMD_READ_SLEEP )

        log_msg ( "Checking for mentions." )

        mentions = []

        commands = []

        firstRun = ( latestMentionID == None )

        with tcLock:

            #on the first run only retrieve 1 metion since it would have
            #been sent before the game started
            numTweets = 1 if firstRun else None

            mentions =  tc.api.mentions_timeline ( 
                                    count     = numTweets,
                                    since_id  = latestMentionID, 
                                    trim_user = 1                )

        if len ( mentions ) == 0:

            #no tweets were retrieved so set the latest ID to 0 so that
            #firstRun will not be true on the next run

            latestMentionID = 0

            continue


        latestMentionID = mentions [ 0 ].id

        #ignore mentions that happened before the system started
        if firstRun:
            continue

        for mention in mentions:

            parsed_cmd = cmd_from_text ( mention.text )

            if parsed_cmd == None:
                continue
            
            command = { "cmd" : parsed_cmd }

            log_msg ( "Command Received:" )
            log_msg ( command )

            commands.append ( command )

            latestMentionID = mention.id

        if len ( commands > 0 ):
            cmdQ.put ( random.choice ( commands ) )
                
#----------------------------------------------------------------------------

def post_header_status ( tc, tcLock, text ):

    """
    Special method for posting headers with a unique number attached since
    sometimes tweepy will block repeated messages.
    """

    unique = str ( uuid.uuid4 () )[:8]

    text += "\n\n"+unique

    with tcLock:
        headerID = tc.send_message_chain ( [ text ] ) [ 0 ]

    return headerID

#----------------------------------------------------------------------------
    
def game_loop ( frotz, tc, tcLock, cmdQueue ):

    #The headerID holds the ID of the message that the next piece of 
    #output should reply to
    headerID = post_header_status ( tc, tcLock, "Starting Adventure" )

    while True:

        #if a commmand is due to be sent then send it and change the 
        #header so later output is posted as a reply
        
        try:
            command = cmdQueue.get_nowait ()

        except Empty:
            pass

        else:

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
            
            with tcLock:
                outID = tc.send_message_chain ( output, outID ) [ -1 ]


        time.sleep ( GAME_LOOP_SLEEP )

#----------------------------------------------------------------------------

def main ():
    
    log_msg ( "Twitter Adventure Bot" )

    log_msg ( "Creating Twitter Connection" )

    tc = TwitterConnection ()

    #only allow one thread to use twitter object 
    tcLock = Lock ()

    #this queue will hold commands from twitter that should be sent
    #to the game
    twitterCommandQueue = Queue ()

    twitterCommandThread = \
            Thread ( target = get_cmds_from_twitter,
                     args   = ( tc, tcLock, twitterCommandQueue ) )

    twitterCommandThread.daemon = True
    twitterCommandThread.start ()

    log_msg ( "Creating FrotzRunner" )

    with FrotzRunner ( "z8/advent.z8" ) as frotz:

        game_loop ( frotz, tc, tcLock, twitterCommandQueue )




if __name__ == "__main__":
    sys.exit ( main () )
