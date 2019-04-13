import sys
from subprocess import PIPE, Popen
from threading import Thread
from queue import Queue, Empty

def enqueue_output ( out, queue ):
    for line in iter ( out.readline, b'' ):
        queue.put ( line )
    queue.put ( b'' )
    out.close ()

class FrotzRunner:

    def __init__ ( self, gameName ):

        self.subP = Popen ( ['dfrotz'], stdout=PIPE, universal_newlines=True )

        self.outputQueue = Queue ()

        self.outputThread = \
                Thread ( target=enqueue_output, \
                         args = ( self.subP.stdout, self.outputQueue ) )
        
        self.outputThread.daemon = True
        self.outputThread.start ()

    def readline ( self ):

        try:
            line =  self.outputQueue.get_nowait ()
            return line
        except Empty:
            return None


