#tab_test.py

import tab

def test_cmd_from_text ():

    testCases = \
    [
        { 
            "text" : "Blah.",
            "cmd"  : None
        }
    ]

    for test in testCases:

        assert ( tab.cmd_from_text ( test [ "text" ] ) == test [ "cmd" ] )

