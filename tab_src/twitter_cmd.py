import sys

from twitter_connection import *

def main ():

    tc = TwitterConnection ()

    while True:

        text = input ( "Tweet: " )

        status = tc.api.update_status ( text )

        print ( status )

if __name__ == "__main__" :

    sys.exit ( main () )
