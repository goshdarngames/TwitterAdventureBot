#############################################################################
# tab.py
#----------------------------------------------------------------------------
# Twitter Adventure Bot
#
# Allows an Interactive Fiction game to be controlled by multiple users
# through twitter comments.
#############################################################################

import sys, time, uuid

from frotz_runner import FrotzRunner
from twitter_connection import TwitterConnection

def post_header_status ( tc, text ):

    unique = str ( uuid.uuid4 () )[:8]

    text += "\n\n"+unique

    headerID = tc.send_message_chain ( [ text ] ) [ 0 ]

    return headerID
    
def game_loop ( frotz, tc ):


    headerID = post_header_status ( tc, "Starting Adventure" )

    command = None

    while True:

        if command != None:

            msg = "Sending Command: "+command

            headerID = post_header_status ( tc, msg )


        #out ID is the message that the next output chain should reply to
        outID = headerID

        output = frotz.read_output_block ()

        if len ( output ) > 0:
            
            outID = tc.send_message_chain ( output, outID ) [ -1 ]


        time.sleep ( 0.3 )

def main ():
    
    print ( "Twitter Adventure Bot", flush = True )

    print ( "Creating Twitter Connection", flush = True )

    tc = TwitterConnection ()

    print ( "Creating FrotzRunner", flush = True )

    with FrotzRunner ( "z8/advent.z8" ) as frotz:

        game_loop ( frotz, tc )




if __name__ == "__main__":
    sys.exit ( main () )
