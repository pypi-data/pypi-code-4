#!/usr/bin/env python3

import unittest

from ptTools.patterns import AnyPattern as Any
from ptTools.patterns import ConcatenationPattern as Con
from ptTools.patterns import TuplePattern as Tup
from ptTools.patterns import LiteralPattern as Lit
from ptTools.parsetree.tupletraversal import preorder_do

from . abstractpatterntest import AbstractPatternTest


class ConcatenationPatternTest(AbstractPatternTest):

    """Tests tuple-like patterns (ConcatenationPattern class)."""

    def test_instantiation_00(self):
        """Tests instantiation of ConcatenationPatterns."""
        Con(None)
        Con('foo')
        Con(23)
        Con([1, 2, 3])
        Con(1, 2, 3, 4)
        Con()
        self.assertRaises(AttributeError, Con, [])        
        self.assertRaises(AttributeError, Con, 'a', [], 'b')        
        
    def test_instantiation_01(self):
        """Tests instantiation of nested ConcatenationPatterns."""        
        Con((1, 2),)
        Con(Con(1, 2))
        Con(Con(Lit('a')))                

    def test_match_00(self):
        """Tests matching TuplePatterns against tuples."""        
        t = ('a', 'b')
        self.assertMatch(t, Tup(Con('a'), Con('b')))
        self.assertMatch(t, Tup(Con('a', 'b')))

    def test_match_01(self):
        """Tests matching ConcatenationPatterns against tuples."""        
        t = ('a', 'b', 'c')
        self.assertMatch(t, Tup(Con('a'), Con('b'), Con('c')))
        self.assertMatch(t, Tup(Con('a'), Con('b', 'c')))
        self.assertMatch(t, Tup(Con('a'), Con('b'), 'c'))
        self.assertMatch(t, Tup(Con('a'), 'b', 'c'))
        self.assertMatch(t, Tup(Con('a'), 'b', Con('c')))
        self.assertMatch(t, Tup('a', 'b', Con('c')))        
        self.assertMatch(t, Tup('a', Con('b'), 'c'))
        self.assertMatch(t, Tup('a', Con('b', 'c')))
        self.assertMatch(t, Tup('a', Con('b'), Con('c')))
        self.assertMatch(t, Tup(Con('a', 'b'), 'c'))
        self.assertMatch(t, Tup(Con('a', 'b'), Con('c')))
        self.assertMatch(t, Tup(Con('a', 'b', 'c')))
        self.assertMatch(t, Tup(Con('a', Con('b', Con('c')))))
        self.denyMatch(t, Tup(Con('a', 'b')))
        self.denyMatch(t, Tup(Con('a', 'b'), Con('b', 'c')))
        self.denyMatch(t, Tup(Con('a'), Con('c')))
        self.denyMatch(t, Tup(Con('a'), Con('b')))                

    def test_match_02(self):
        """Tests matching ConcatenationPatterns against tuples."""        
        t = ('a', 'b', 'b', 'c')
        self.assertMatch(t, Tup(Con('a'), Con('b', 'b'), Con('c')))
        self.assertMatch(t, Tup(Con('a'), +Lit('b'), Con('c')))
        self.assertMatch(t, Tup(Con('a'), +Lit('b'), 'c'))
        self.assertMatch(t, Tup(Con('a', +Lit('b')), 'c'))

    def test_match_03(self):
        """Tests matching ConcatenationPatterns against tuples."""        
        t = ('a','b','c','d')
        self.assertMatch(t, Tup('a', Con('b', 'c'), 'd'))

    def test_nested(self):
        t = ('a','b','c')
        self.assertMatch(t, Tup('a', Con(Con('b','c'))))
        self.assertMatch(t, Tup('a', Con('b',Con('c'))))

    def test_callback(self):
        self.assertRaises(AttributeError, Con('b', 'c').__mod__, print)

    def test_callback_01(self):
        """Tests matching ConcatenationPatterns against tuples."""        
        t = ('a','b','b')
        l = []
        b = Lit('b')%l.append
        _ = Any()
        self.assertMatch(t, Tup('a', Con(+b), ~_))
        self.assertListEqual(l, ['b','b'])
        l.pop();l.pop()
        self.assertMatch(t, Tup('a', +Con(b), ~_))
        self.assertListEqual(l, ['b','b'])
        

if __name__ == '__main__':

    unittest.main()
