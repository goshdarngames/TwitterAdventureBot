import sys
from subprocess import PIPE, Popen
from threading import Thread
from queue import Queue, Empty

def subprocess_communication ( subP, outQueue ):

    #keep reading output lines and adding to queue until program finishes
    for line in iter ( subP.stdout.readline, b'' ):
        outQueue.put ( line )

    #process has halted - write an EOF to the output
    outQueue.put ( b'' )
    subP.stdout.close ()

class FrotzRunner:

    def __init__ ( self, gamePath ):

        self.subP = Popen ( ['dfrotz', gamePath ], 
                            stdout = PIPE, stdin = PIPE, 
                            universal_newlines = True )

        self.outputQueue = Queue ()

        self.outputThread = \
                Thread ( target = subprocess_communication, \
                         args = ( self.subP, self.outputQueue ) )
        
        self.outputThread.daemon = True
        self.outputThread.start ()

    def readline ( self ):

        return self.outputQueue.get_nowait ()


