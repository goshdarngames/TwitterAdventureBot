from frotz_runner import *

print ( "Starting frotz...." )

runner = FrotzRunner ( "z8/advent.z8" )


while True:
    try:
        print ( runner.readline () )
    except:
        break

