import sys
from subprocess import PIPE, Popen
from threading import Thread
from queue import Queue, Empty

def subprocess_communication ( subP, outQueue ):

    for line in iter ( subP.stdout.readline, b'' ):
        outQueue.put ( line )

    outQueue.put ( b'' )
    out.close ()

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


