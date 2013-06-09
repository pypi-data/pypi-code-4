# ----------------------------------------------------------------------------
# pyojo                                           Copyright (c) 2011 nabla.net
# ----------------------------------------------------------------------------
import pyojo
import unittest

class BasicTestCase(unittest.TestCase):
    def setUp(self):
        pass
    
    def tearDown(self):
        pass



def main():
    print "-"*79+"\nBasic tests for pyojo version %s\n" % pyojo.__version__
    try:
        unittest.main(verbosity=2)
    except SystemExit as inst:
        if inst.args[0] is True: raise 