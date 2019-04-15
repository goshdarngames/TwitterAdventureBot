# frotz_cmd.py
#
# Simple command line program for testing the frotz runner.

from frotz_runner import *
from queue import Empty

import sys

def main ():

    print ( "Starting dfrotz...." )

    #launch the runner using python's context manager pattern

    with FrotzRunner ( "z8/advent.z8" ) as gameRunner: 

        #keep looping until game quits
        while True:

            #print a block of output from the game
            for line in gameRunner.read_output_block ():

                print ( line )

            #check if the game quit after the last output
            if gameRunner.poll() != None:

                print ( "Frotz process has ended." )

                break

            #read output from the user and send it to the game

            usr_input = input ( "Input >> " )

            gameRunner.write_command ( usr_input + "\n" )

        #exit with the return code of the frotz sub process
        return gameRunner.return_code ()

if __name__ == "__main__":
    sys.exit ( main () )
