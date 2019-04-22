#############################################################################
# twitter_connection_test.py
#----------------------------------------------------------------------------
# Unit tests for the twitter connection.
#############################################################################

from twitter_connection import *

def test_chop_text ():

    testCases = \
    [
        {
            "txt" : "aabbccdd",
            "n"   : 2,
            "out" : [ "aa", "bb", "cc", "dd" ]
        }
    ]

    for tc in testCases:

        out = chop_text ( tc [ "txt" ], tc [ "n" ] )

        #check that the output ( list of strings ) is equal to the output
        #expected in the test case

        assert ( len ( out ) == len ( tc [ "out" ] ) )

        for i in range ( len ( out ) ):

            assert ( out [ i ] == tc [ "out" ] [ i ] )


