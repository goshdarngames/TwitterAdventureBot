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

        self.gamePath = gamePath

        self.outputQueue = Queue ()
        self.inputQueue = Queue ()

    #------------------------------------------------------------------------

    def __enter__ ( self ):

        self.subP = Popen ( ['dfrotz', self.gamePath ], 
                            stdout = PIPE, stdin = PIPE, 
                            universal_newlines = True,
                            bufsize = 1                   )

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

        return self

    #------------------------------------------------------------------------ 

    def __exit__ ( self, *args ):
        
        self.subP.kill ()

    #------------------------------------------------------------------------ 

    def read_output_line  ( self ):

        line = self.outputQueue.get_nowait ()

        if line == '':
            
            raise EOFError ()

        else:

            return line

    #------------------------------------------------------------------------

    def read_output_block ( self, num_retry = 5, wait_time = 0.1 ):

        retries = num_retry

        output_lines = []

        while retries > 0:

            try:

                line = self.read_output_line () 

            except Empty:

                retries -= 1
                time.sleep ( wait_time )

            except EOFError:

                retries = 0

            else:

                output_lines.append ( line )

        return output_lines

    #------------------------------------------------------------------------

    def write_command ( self, cmd ):

        self.inputQueue.put ( cmd )

    #------------------------------------------------------------------------

    def poll ( self ):

        return self.subP.poll ()

    #------------------------------------------------------------------------

    def return_code ( self ):

        return self.subP.returncode
