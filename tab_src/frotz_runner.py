import sys, time
from subprocess import PIPE, Popen
from threading import Thread
from queue import Queue, Empty

#----------------------------------------------------------------------------

#These function are used by the FrotzRunner threads to continuously read
#output and send commands to the game sub-process

def read_subp_output ( subPstdout, outQueue ):

    #keep reading output lines and adding to queue until program finishes
    for line in iter ( subPstdout.readline, b'' ):
        outQueue.put ( line )

def write_subp_input ( subPstdin, inQueue ):

    while True:

        subPstdin.write ( inQueue.get () )

#----------------------------------------------------------------------------

class FrotzRunner:
    """
    Provides a 'context manager' that can be used to control a dfrotz game.

    The game is run in a sub-process and two threads are used to input
    commands and read output from the game.

    A demonstration of its usage can be found in the 'frotz_cmd.py' file.
    """

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

        """
        Reads the latest line of output and returns it as a string.
        
        Throws Empty if there is no output available but the game 
        sub-process is still running.

        Throws EOFError when the final line of output is read from 
        game sub-process.

        Calling this again after the EOFError is undefined.  Use poll()
        to check the game sub-process is running.
        """

        line = self.outputQueue.get_nowait ()

        if line == '':
            
            raise EOFError ()

        else:

            return line

    #------------------------------------------------------------------------

    def read_output_block ( self, num_retry = 5, wait_time = 0.1 ):
        """
        Tries to read a block of lines from the game sub-process.  

        After reading each line the system will wait and try read again
        in case there are more lines of output that have been delayed by
        the game sub-process.

        This function will return a list containing all the lines of
        output.

        No error will be thrown when the process is closed so it is 
        important to call poll() to ensure the game is still alive.

        It was designed not to throw an error so that the 'quit' message
        from the game would not be lost.
        """

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
        """
        Sends a command to the game.
        """

        self.inputQueue.put ( cmd )

    #------------------------------------------------------------------------

    def poll ( self ):
        """
        Returns None if the game sub-process is running.

        If the game sub-process has finished it returns the returncode
        of the sub-process.
        """

        return self.subP.poll ()

    #------------------------------------------------------------------------

    def return_code ( self ):
        """
        Returns the returncode of the game sub-process if it has finished.
        """

        return self.subP.returncode
