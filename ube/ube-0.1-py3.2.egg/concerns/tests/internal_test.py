'''
Created on Nov 18, 2012

@author: Nicklas Boerjesson
'''
import unittest
from ube.concerns.internal import not_implemented


class concern_internal_tests(unittest.TestCase):

    @not_implemented
    def _not_implemented(self):
        pass 

    def test_not_implemented(self):
        try:
            self._not_implemented()
        except Exception as Ex:
            if (str(Ex) != 'Internal error in "_not_implemented": Not implemented.'):
                raise Exception('The @not_implemented decorator does not produce the expected output.')
            else:
                return
                
        raise Exception('The @not_implemented decorator does not raise an exception.')      
           

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()