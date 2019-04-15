# frotz_cmd.py
#
# Simple command line program for testing the frotz runner.

from frotz_runner import *
from queue import Empty

import sys

def main ():

    print ( "Starting dfrotz...." )

    with FrotzRunner ( "z8/advent.z8" ) as gameRunner: 

        while True:

            for line in gameRunner.read_output_block ():

                print ( line )

            if gameRunner.poll() != None:

                print ( "Frotz process has ended." )

                break

            usr_input = input ( "Input >> " )

            gameRunner.write_command ( usr_input + "\n" )

        return gameRunner.return_code ()

if __name__ == "__main__":
    sys.exit ( main () )
