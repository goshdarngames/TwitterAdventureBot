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
            "text" : "banana cmd lets go",
            "cmd"  : None
        },

        { 
            "text" : "cmd ",
            "cmd"  : None
        },

        { 
            "text" : "nothing here",
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
        },

        { 
            "text" : "@tweetintfict cmd abc xyz",
            "cmd"  : "abc xyz"
        },

        { 
            "text" : "cmd quit",
            "cmd"  : None
        },

        { 
            "text" : "stuff\ncmd quit\nmorestuff",
            "cmd"  : None
        },

        { 
            "text" : "cmd quit and other stuff",
            "cmd"  : None
        },

        { 
            "text" : "cmd quite",
            "cmd"  : "quite"
        },

        { 
            "text" : "cmd stuff quit",
            "cmd"  : "stuff quit"
        },

        { 
            "text" : "CMD comm",
            "cmd"  : "comm"
        },

        { 
            "text" : "CmD comm aaBBccDDee",
            "cmd"  : "comm aabbccddee"
        },

        { 
            "text" : "cmd one cmd two",
            "cmd"  : "one cmd two"
        },

        { 
            "text" : "cmd one \ncmd two",
            "cmd"  : "one"
        },

        { 
            "text" : "cmd on!e tw\\o thr33 f@ur",
            "cmd"  : "one two thr33 fur"
        },

        { 
            "text" : "cmd on!e tw\\o thr33 f@ur\ncmd two",
            "cmd"  : "one two thr33 fur"
        },

        { 
            "text" : "cmd http://www.goshdarngames.com",
            "cmd"  : None
        },

        { 
            "text" : "cmd sneaky http://www.goshdarngames.com",
            "cmd"  : None
        },

        { 
            "text" : "cmd sneakierhttp://www.goshdarngames.com",
            "cmd"  : None
        },

        { 
            "text" : "cmd allowed \nhttp://www.goshdarngames.com",
            "cmd"  : "allowed"
        },

        { 
            "text" : "http://www.goshdarngames.com \ncmd allowed",
            "cmd"  : "allowed"
        },

    ]

    for test in testCases:

        bannedCmds = [ "quit" ]

        output = tab.cmd_from_text ( test [ "text" ], bannedCmds ) 

        assert ( output == test [ "cmd" ] ),  test  #output testcase on fail

