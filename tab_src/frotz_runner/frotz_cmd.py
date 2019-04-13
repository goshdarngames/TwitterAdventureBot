from frotz_runner import *
import time

print ( "Starting dfrotz...." )

runner = FrotzRunner ( "z8/advent.z8" )


while True:

    #Try and print all output from dfrotz to the console
    # - retry a few times with a delay between each line
    
    num_retry = 5

    while num_retry > 0:
    
        output = runner.readline () 

        if output is not None:
            num_retry = 5
            print ( output )
        else:
            num_retry -= 1
            time.sleep ( .100 )

    usr_input = input ( "Input >> " )

