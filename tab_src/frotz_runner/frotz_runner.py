import sys, time
from subprocess import PIPE, Popen
from threading import Thread
from queue import Queue, Empty

def read_subp_output ( subPstdout, outQueue ):

    #keep reading output lines and adding to queue until program finishes
    for line in iter ( subPstdout.readline, b'' ):
        outQueue.put ( line )

def write_subp_input ( subPstdin, inQueue ):

    while True:

        subPstdin.write ( inQueue.get () )

class FrotzRunner:

    def __init__ ( self, gamePath ):

        self.subP = Popen ( ['dfrotz', gamePath ], 
                            stdout = PIPE, stdin = PIPE, 
                            universal_newlines = True,
                            bufsize = 1                   )

        self.outputQueue = Queue ()
        self.inputQueue = Queue ()

        self.outputThread = \
                Thread ( target = read_subp_output, \
                         args = ( self.subP.stdout, self.outputQueue ) )
        
        self.outputThread.daemon = True
        self.outputThread.start ()

        self.inputThread = \
                Thread ( target = write_subp_input, \
                         args = ( self.subP.stdin, self.inputQueue ) )
        
        self.inputThread.daemon = True
        self.inputThread.start ()

   #------------------------------------------------------------------------- 

    def read_output_line  ( self ):

        return self.outputQueue.get_nowait ()

    #------------------------------------------------------------------------

    def write_command ( self, cmd ):

        self.inputQueue.put ( cmd )

    #------------------------------------------------------------------------

    def poll ( self ):

        return self.subP.poll ()

    #------------------------------------------------------------------------

    def return_code ( self ):

        return self.subP.returncode
