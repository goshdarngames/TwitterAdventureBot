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

            print ( msg, flush=True )

            headerID = post_header_status ( tc, tcLock, msg )

            frotz.write_command ( command + "\n" )


        #out ID is the message that the next output chain should reply to
        outID = headerID

        output = frotz.read_output_block ()

        if len ( output ) > 0:
            
            consoleMsg = "Sending output:\n" + join( output )
            print ( consoleMsg, flush = True )
            
            with tcLock:
                outID = tc.send_message_chain ( output, outID ) [ -1 ]


        time.sleep ( 0.3 )

#----------------------------------------------------------------------------

def main ():
    
    print ( "Twitter Adventure Bot", flush = True )

    print ( "Creating Twitter Connection", flush = True )

    tc = TwitterConnection ()

    #only allow one thread to use twitter object 
    tcLock = Lock ()

    #this queue will hold commands from twitter that should be sent
    #to the game
    twitterCommandQueue = Queue ()

    print ( "Creating FrotzRunner", flush = True )

    with FrotzRunner ( "z8/advent.z8" ) as frotz:

        game_loop ( frotz, tc, tcLock, twitterCommandQueue )




if __name__ == "__main__":
    sys.exit ( main () )
