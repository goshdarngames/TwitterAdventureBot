#############################################################################
# tab.py
#----------------------------------------------------------------------------
# Twitter Adventure Bot
#
# Allows an Interactive Fiction game to be controlled by multiple users
# through twitter comments.
#############################################################################

import sys, time, uuid, random, logging

import urlmarker, re

from queue import Queue, Empty
from threading import Thread, Lock

from frotz_runner import FrotzRunner
from twitter_connection import TwitterConnection

#----------------------------------------------------------------------------

#How long to sleep at the end of each 'game loop'
GAME_LOOP_SLEEP = 10

#----------------------------------------------------------------------------

def char_allowed_in_cmd ( c ):
    """
    Returns true if a character is allowed to be sent from a tweet to
    the game.
    """

    return c.isalnum () or c == " "

#----------------------------------------------------------------------------

def string_has_url ( s ):
    """
    Returns true if a string seems like it contains a URL.

    It is undesirable for the bot to send commands to the game that
    contains a url.  The bot posts a message with the command text and
    that could be abused to make the bot spam out URLs.
    """

    return len ( re.findall ( urlmarker.ANY_URL_REGEX, s ) ) > 0

#----------------------------------------------------------------------------

def cmd_from_text ( text, bannedCmds ):

    logging.info ( "cmd_from_text:\n"+text )
    
    if len ( text ) < 5:
        return None

    cmd = None

    #check each line for a command

    for line in text.split ( "\n" ):

        #strip before checking for 'cmd' in case the user put spaces
        line = line.strip ()

        #if the first word is a username then process the rest of the line
        #after the first word

        if len( line ) > 0 and line [ 0 ] == "@":

            line = line.split ( " ", 1 ) [ 1 ].strip ()

        #convert to lower case

        line = line.lower ()

        #check for cmd and return the rest of the command

        if len ( line ) > 4 and line [ : 4 ] == "cmd ":

            #The rest of the line after 'cmd '
            cmd = line [ 4 : ]

            #block commands with urls - note that urls are allowed in 
            #cmd tweets just not as part of the command

            if string_has_url ( cmd ):

                logging.warning ( "Ignored command with URL:\n"+cmd )

                return None
            
            #remove whitespace at beginning and end of command
            cmd = cmd.strip ()

            #only allow alpha-numeric and space characters

            allowed_chars = [ x for x in cmd if char_allowed_in_cmd ( x ) ]

            cmd = "".join ( allowed_chars )

            #check the command's first word against the banned commands

            firstWord = cmd.split ( " " ) [ 0 ]

            for banned in bannedCmds:

                if firstWord == banned:

                    return None

            #only parse the first command
            break

    return cmd 

#----------------------------------------------------------------------------

def check_mentions_for_cmd ( tc, bannedCmds ):

    cmd = None

    for mention in tc.get_latest_mentions ():

        parsedCmd = cmd_from_text ( mention [ "text" ], bannedCmds )

        if parsedCmd != None:
            cmd = { "cmd" : parsedCmd, "username" : mention [ "username" ] }
    
    return cmd

#----------------------------------------------------------------------------

def post_status ( tc, msgList, replyID ):
    """
    Posts a message to twitter and returns a list of the status IDs that
    hold the message.  (The message will be split up into multiple 
    messages when sent to Twitter)
    """

    messageChain = tc.send_message_chain ( msgList, replyID )

    if len ( messageChain ) == 0:

        msgStr = "\n".join ( msgList )

        logging.critical ( "Failed to send tweets:\n"+msgStr )

    return messageChain

#----------------------------------------------------------------------------

def post_tail_status ( tc, msgList, replyID ):
    """
    Posts a list of messages in reply to another status and returns the ID 
    of the final twitter status in the resulting chain.

    Used to add messages onto an existing chain of messages.
    """

    messageChain = post_status ( tc, msgList, replyID )

    if len ( messageChain ) > 0:

        return messageChain [ -1 ]

    else:

        return None

#----------------------------------------------------------------------------

def post_header_status ( tc, text ):

    """
    Posts a message as the first message in a new thread and returns the ID 
    of the first message in the chain.( Message may be split up by twitter )

    Used to start new threads e.g. when a new command is sent.
    """

    #This was used to make sure that every command was unique to stop them
    #getting blocked by the twitter api but it may not be needed any more
    unique = str ( uuid.uuid4 () )[:8]
    text += "\n\n"+unique

    messageChain = post_status ( tc, [ text ], None )

    if len ( messageChain ) > 0:

        return messageChain [ 0 ]

    else:

        return None

#----------------------------------------------------------------------------
    
def game_loop ( frotz, tc, bannedCmds ):

    #The headerID holds the ID of the message that the next piece of 
    #output should reply to
   
    startText  = "Starting Adventure..."
    #startText += "\n\n#InteractiveFiction #TwitterBot #TwitterGame"
    
    headerID = post_header_status ( tc, startText )

    while True:

        #break loop if frotz process has halted

        exitCode = frotz.poll ()

        if exitCode != None:

            logging.warning ( "Frotz process exited.  "+
                              "Exit code: "+str ( exitCode ) )

            break

        #if a commmand is due to be sent then send it and change the 
        #header so later output is posted as a reply
        
        command = check_mentions_for_cmd ( tc, bannedCmds )

        if command != None:

            logging.info ( "Command:" )

            #Expect commands from the command queue to be dictionary
            #objects with the form { user : user.id, cmd : "..." }

            msg =  "Sending Command: " + command [ "cmd" ] + "\n\n"
            msg += "From: @" + command [ "username" ]

            logging.info ( msg )

            headerID = post_header_status ( tc, msg )

            frotz.write_command ( command [ "cmd" ] + "\n" )


        #out ID is the message that the next output chain should reply to
        outID = headerID

        output = frotz.read_output_block ()

        if len ( output ) > 0:
            
            consoleMsg = "Sending output:\n" + "\n".join( output )
            logging.info ( consoleMsg )
            
            #record the last message sent so that the next output will be
            #sent as a reply
            outID = post_tail_status ( tc, output, outID )


        time.sleep ( GAME_LOOP_SLEEP )

#----------------------------------------------------------------------------

def handle_exceptions ( exc_type, exc_value, exc_traceback ):
    """
    Used to log uncaught exceptions."
    """

    if issubclass ( exc_type, KeyboardInterrupt ):

        sys.__excepthook__ ( exc_type, exc_value, exc_traceback )
        return

    logging.critical ( "Unhandled Exception", 
                      exc_info = ( exc_type, exc_value, exc_traceback ) )
#----------------------------------------------------------------------------

def main ():

    logging.basicConfig ( format='%(asctime)s - %(levelname)s - %(message)s', 
                          level=logging.INFO )

    sys.excepthook = handle_exceptions
    
    logging.info ( "Twitter Adventure Bot" )

    logging.info ( "Creating Twitter Connection" )

    #List of commands that will be ignored rather than sent to the game
    #If more words are to be added to this list it would be a good idea
    #to put them in a text file and load them

    bannedCmds = [ "quit" ]

    with TwitterConnection () as tc:

        while True:
        
            logging.info ( "Starting frotz" )

            with FrotzRunner ( "z8/advent.z8" ) as frotz:

                logging.info ( "Entering game loop." )

                game_loop ( frotz, tc, bannedCmds )




if __name__ == "__main__":
    sys.exit ( main () )
