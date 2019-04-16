#############################################################################
# tab.py
#----------------------------------------------------------------------------
# Twitter Adventure Bot
#
# Allows an Interactive Fiction game to be controlled by multiple users
# through twitter comments.
#############################################################################

import sys, time, uuid

from Queue import Queue, Empty
from threading import Thread, Lock

from frotz_runner import FrotzRunner
from twitter_connection import TwitterConnection

#----------------------------------------------------------------------------

#How long to sleep between read commands
CMD_READ_SLEEP = 60

#How long to sleep at the end of each 'game loop'
GAME_LOOP_SLEEP = 60

#----------------------------------------------------------------------------

def log_msg ( text ):

    print ( msg, flush = True )

#----------------------------------------------------------------------------

def get_cmds_from_twitter ( tc, tcLock, cmdQ ):

    while True:

        time.sleep ( CMD_READ_SLEEP )

#----------------------------------------------------------------------------

def post_header_status ( tc, tcLock, text ):

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
            command = cmdQueue.get ()

        except Empty:
            pass

        else:

            msg = "Sending Command: "+command

            log_msg ( msg )

            headerID = post_header_status ( tc, tcLock, msg )

            frotz.write_command ( command + "\n" )


        #out ID is the message that the next output chain should reply to
        outID = headerID

        output = frotz.read_output_block ()

        if len ( output ) > 0:
            
            consoleMsg = "Sending output:\n" + join( output )
            log_msg ( consoleMsg )
            
            with tcLock:
                outID = tc.send_message_chain ( output, outID ) [ -1 ]


        time.sleep ( GAME_LOOP_SLEEP )

#----------------------------------------------------------------------------

def main ():
    
    log_msg ( "Twitter Adventure Bot" )

    log_msg ( "Creating Twitter Connection"\)

    tc = TwitterConnection ()

    #only allow one thread to use twitter object 
    tcLock = Lock ()

    #this queue will hold commands from twitter that should be sent
    #to the game
    twitterCommandQueue = Queue ()

    twitterCommandThread = \
            Thread ( target = get_cmds_from_twitter,
                     args   = ( tc, tcLock, twitterCommandQ ) )

    twitterCommandThread.daemon = True
    twitterCommandThread.start ()

    log_msg ( "Creating FrotzRunner" )

    with FrotzRunner ( "z8/advent.z8" ) as frotz:

        game_loop ( frotz, tc, tcLock, twitterCommandQueue )




if __name__ == "__main__":
    sys.exit ( main () )
