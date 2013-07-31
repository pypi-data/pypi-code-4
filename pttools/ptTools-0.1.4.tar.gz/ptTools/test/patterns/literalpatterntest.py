#!/usr/bin/env python3

import unittest

from ptTools.patterns import AnyPattern as Any
from ptTools.patterns import LiteralPattern as Lit

from . abstractpatterntest import AbstractPatternTest


class LiteralPatternTest(AbstractPatternTest):

    """Tests patterns matching literals (LiteralPattern class)."""

    def test_instantiation(self):
        """Tests instantiation of LiteralPatterns."""
        Lit(None)
        Lit(23)
        Lit('foo')
        Lit(('x',))        
        Lit((1,2,3))
        Lit([1, 2, 3])
        Lit((1, 2))
        self.assertRaises(TypeError, Lit)
        self.assertRaises(TypeError, Lit, 'x', 'y')
        self.assertRaises(TypeError, Lit , 1, 2)
        
    def test_match(self):
        """Tests matching LiteralPatterns against literals."""
        self.assertMatch(23, Lit(23))
        self.assertMatch('foo', Lit('foo'))
        self.assertMatch('a', Lit('a'))        
        self.denyMatch(('a',), Lit('a'))        
        self.denyMatch([23], Lit(23))

    def test_callback(self):
        """Tests matching input and calling back a function with the
        matched object."""
        l = []
        X = Lit('x') % l.append
        X.matches('x')
        self.assertListEqual(l, ['x'])
        l = []
        X.matches(42)
        self.assertListEqual(l, [])

    def test_copy(self):
        """Tests equivalence of copy."""
        l = []
        A = (Lit('a') % l.append).copy()
        self.assertMatch('a', A)
        self.assertListEqual(l, ['a'])
        l.pop()

    def test_extend_00(self):
        """Tests extending LiteralPatterns (negative)."""
        A = Lit('a')
        B = Lit('b')        
        self.assertRaises(AttributeError, A.__getattribute__, 'extend')


if __name__ == '__main__':

    unittest.main()
