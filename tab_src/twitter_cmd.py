import sys

from twitter_connection import TwitterConnection


def cmd_loop ( tc ):

    while True:

        text = input ( "Twitter: " )
        
        if text [ : 2 ] == "t ":

            id_list = tc.send_message_chain ( [ text [ 2 : ] ] )

            print ( id_list )

        elif text == "q":
             
            break

        elif text == "m":

            print ( "Mentions:" )

            print ( tc.get_latest_mentions () )

        else:

            print ( "Command not recognized.  Valid commands :\n" +
                    "t [message]   - send a tweet\n"              +
                    "m             - get mentions\n"
                    "q             - quit" )
                     

def main ():

    with TwitterConnection () as tc:

        cmd_loop ( tc )


if __name__ == "__main__" :

    sys.exit ( main () )
