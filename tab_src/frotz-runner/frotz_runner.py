import sys
from subprocess import PIPE, Popen
from threading import Thread

def enqueue_output ( out, queue ):
    for line in iter ( out.readline, b'' ):
        queue.put ( line )
    out.close ()

class FrotzRunner:

    def __init__ ( self, gameName )

        self.subP = Popen ( ['dfrotz'], stdout=PIPE )

        self.outputQueue = Queue ()

        self.outputThread = \
                Thread ( target=enqueue_output, \
                         args = ( self.subP.stdout, self.outputQueue ) )
        
        self.outputThread.daemon = True
        self.outputThread.start ()

    def readline ():

        return outputQueue.get_nowait ()
