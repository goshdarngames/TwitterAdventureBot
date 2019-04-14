from frotz_runner import *
from queue import Empty

import time
import sys


def print_output ( runner ):


    #Try and print all output from dfrotz to the console
    # - retry a few times with a delay between each line
    
    num_retry = 5

    while num_retry > 0:
    
        try:
            output = runner.read_output_line () 
        
        #if the output queue is empty wait and try again until num_retry = 0
        except Empty:

            num_retry -= 1
            time.sleep ( .100 )

        #output was not empty
        else:

            # '' is used to signify EOF 
            if output == '':

                print ( "The dfrotz process ended." )
                return

            #print output and reset num_retry in case there is more output
            else:
                num_retry = 5
                print ( output )

#----------------------------------------------------------------------------

def main ():

    print ( "Starting dfrotz...." )

    runner = FrotzRunner ( "z8/advent.z8" )

    while True:

        print_output ( runner )

        if runner.poll() != None:
            break

        usr_input = input ( "Input >> " )

        runner.write_command ( usr_input + "\n" )

    return runner.return_code ()

if __name__ == "__main__":
    sys.exit ( main () )
