from mvpoly.dict import *
from mvpoly.util.dict import *

import unittest

class TestMVPolyDictUtilNegate(unittest.TestCase) :

    def test_negation_simple(self) :
        obtained = negate({'a':2, 'b':-7})
        expected = {'a':-2, 'b':7}
        self.assertTrue(obtained == expected,
                        "bad negation:\n%s" % repr(obtained))

    def test_negation_empty(self) :
        obtained = negate({})
        expected = {}
        self.assertTrue(obtained == expected,
                        "bad negation:\n%s" % repr(obtained))


class TestMVPolyDictUtilMergeNonzero(unittest.TestCase) :

    def test_merge_dicts_nonzero(self) :
        A = { 'a':3, 'b':2, 'c':1         }
        B = {        'b':1, 'c':2, 'd': 3 }
        obtained = merge_dicts_nonzero(A, B, lambda x, y : x+y)
        self.assertTrue(obtained == { 'a': 3, 'b': 3, 'c': 3, 'd':3 },
                        "bad merge:\n%s" % repr(obtained))
        obtained = merge_dicts_nonzero(A, B, lambda x, y : x - 2*y)
        self.assertTrue(obtained == { 'a': 3, 'c': -3, 'd': -6 },
                        "bad merge:\n%s" % repr(obtained))
