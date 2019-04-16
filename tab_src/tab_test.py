#tab_test.py

import tab

def test_cmd_from_text ():

    test_txt = "Bleh"

    ret = tab.cmd_from_text ( test_txt )

    assert ( ret == None )
