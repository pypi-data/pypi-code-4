# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------------
# pyojo                                           Copyright (c) 2011 nabla.net
# ----------------------------------------------------------------------------
""" Tests for the pyojo package.

"""
import unittest
import pyojo

from base import *
from test_basic import *
 
        
# ----------------------------------------------------------------------------

def main():
    print "-"*79+"\nTesting pyojo version %s requests" % pyojo.__version__
    
    try:
        unittest.main()
    except SystemExit as inst:
        if inst.args[0] is True: raise
    
if __name__=='__main__':
    main()