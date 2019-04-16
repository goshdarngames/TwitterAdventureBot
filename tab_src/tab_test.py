#tab_test.py

import tab

def test_cmd_from_text ():

    testCases = \
    [
        { 
            "text" : "",
            "cmd"  : None
        },

        { 
            "text" : "cmd1",
            "cmd"  : None
        },

        { 
            "text" : "cmd      test text ",
            "cmd"  : "test text"
        },

        { 
            "text" : "cmd      test text \n",
            "cmd"  : "test text"
        },

        { 
            "text" : "hey @you\n\n  cmd      test text \nlol #hashtag",
            "cmd"  : "test text"
        },

        { 
            "text" : "cmd abc xyz",
            "cmd"  : "abc xyz"
        }

    ]

    for test in testCases:

        assert ( tab.cmd_from_text ( test [ "text" ] ) == test [ "cmd" ] )

