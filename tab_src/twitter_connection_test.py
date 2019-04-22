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
        },

        {
            "txt" : "aabbccdd",
            "n"   : 18,
            "out" : [ "aabbccdd" ]
        },

        {
            "txt" : "aabbccdd",
            "n"   : 8,
            "out" : [ "aabbccdd" ]
        },

        {
            "txt" : "",
            "n"   : 2,
            "out" : []
        }

    ]

    for tc in testCases:

        out = chop_text ( tc [ "txt" ], tc [ "n" ] )

        #check that the output ( list of strings ) is equal to the output
        #expected in the test case

        assert ( len ( out ) == len ( tc [ "out" ] ) ), tc

        for i in range ( len ( out ) ):

            assert ( out [ i ] == tc [ "out" ] [ i ] ), tc

#----------------------------------------------------------------------------

def test_pack_messages ():
    
    testCases = \
    [
        {
            "txt" : [ "abc" ],
            "out" : [ "abc" ],
            "n"   : 45
        }

    ]

    for tc in testCases:

        out = pack_messages ( tc [ "txt" ], tc [ "n" ] )

        assert ( len ( out ) == len ( tc [ "out" ] ) ), tc

        for i in range ( len ( out ) ):

            assert ( out [ i ] == tc [ "out" ] [ i ] ), tc

