from frotz_runner import *
import time

print ( "Starting frotz...." )

runner = FrotzRunner ( "z8/advent.z8" )


while True:
    output = runner.readline () 
    
    if output is not None:
        print ( output )
    else:
        break

