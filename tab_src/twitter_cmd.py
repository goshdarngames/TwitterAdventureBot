import sys

from twitter_connection import *

def main ():

    tc = TwitterConnection ()

    while True:

        text = input ( "Twitter: " )
        
        if text [ : 2 ] == "t ":

            id_list = tc.send_message_chain ( [ text [ 2 : ] ] )

            print ( id_list )

        else:

            print ( "Command not recognized.  Valid commands :\n" +
                    "t [message]   - send a tweet\n"              +
                    "m             - get mentionszn" )
                     
                     

if __name__ == "__main__" :

    sys.exit ( main () )
