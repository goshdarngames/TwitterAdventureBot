import sys
from subprocess import PIPE, Popen
from threading import Thread
from queue import Queue, Empty

def read_subp_output ( subPstdout, outQueue ):

    #keep reading output lines and adding to queue until program finishes
    for line in iter ( subPstdout.readline, b'' ):
        outQueue.put ( line )

    #process has halted - write an EOF to the output
    outQueue.put ( b'' )
    subPstdout.close ()

class FrotzRunner:

    def __init__ ( self, gamePath ):

        self.subP = Popen ( ['dfrotz', gamePath ], 
                            stdout = PIPE, stdin = PIPE, 
                            universal_newlines = True,
                            bufsize = 1                   )

        self.outputQueue = Queue ()

        self.outputThread = \
                Thread ( target = read_subp_output, \
                         args = ( self.subP.stdout, self.outputQueue ) )
        
        self.outputThread.daemon = True
        self.outputThread.start ()

    def readline ( self ):

        return self.outputQueue.get_nowait ()


