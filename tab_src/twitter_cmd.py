import sys

from twitter_connection import *

def main ():

    tc = TwitterConnection ()

    while True:

        text = input ( "Tweet: " )

        id_list = tc.send_message_chain ( [ text ] )

        print ( id_list )

if __name__ == "__main__" :

    sys.exit ( main () )
