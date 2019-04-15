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

    header = tc.api.update_status ( text )

    reply = tc.api.update_status ( "Reply here to send command:", header.id )

    return ( header, reply )
    
def game_loop ( frotz, tc ):

    unique = str ( uuid.uuid4 () )[:8]

    headerMsg += "Starting Adventure! \n\n"+unique

    header, reply = post_header_status ( tc, "Starting Adventure" )

    commandSent = False

    while True:

        if commandSent:

            #post new header

        outID = header.id

        for line in frotz.read_output_block ():
            
            print ( "Sending output line.", flush = True )
            
            outStatus = tc.api.update_status ( line, outID )

            outID = outStatus.id
            
            time.sleep ( 0.1 )

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
