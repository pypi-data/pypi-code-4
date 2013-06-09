# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------------
# pyojo                                           Copyright (c) 2011 nabla.net
# ----------------------------------------------------------------------------
""" Tests for the pyojo package.

assertEqual(a, b)     a == b      
assertNotEqual(a, b)     a != b      
assertTrue(x)     bool(x) is True      
assertFalse(x)     bool(x) is False      
assertIs(a, b)     a is b     2.7
assertIsNot(a, b)     a is not b     2.7
assertIsNone(x)     x is None     2.7
assertIsNotNone(x)     x is not None     2.7
assertIn(a, b)     a in b     2.7
assertNotIn(a, b)     a not in b     2.7
assertIsInstance(a, b)     isinstance(a, b)     2.7
assertNotIsInstance(a, b)     not isinstance(a, b)     2.7

"""

from base import *
from test_js import *
from pyojo.server import HTTPD   
        

# ----------------------------------------------------------------------------


def main():
    print "-"*79+"\nTesting pyojo version %s at browser" % pyojo.__version__
    httpd = HTTPD()
    httpd.start()
    try:
        unittest.main()
    except SystemExit as inst:
        httpd.stop()
        if inst.args[0] is True: raise
    httpd.stop()
    
if __name__=='__main__':
    main()
