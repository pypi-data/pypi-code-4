#!/usr/bin/env python3

import unittest

from ptTools.patterns import AnyPattern as Any
from ptTools.patterns import TestPattern as Test

from . import AbstractPatternTest


class AnyPatternTest(AbstractPatternTest):

    """Tests patterns matching anything."""

    def test_instantiation(self):
        """Tests instantiation of LiteralPatterns."""
        Any()
        self.assertRaises(TypeError, Any, 'x')
        self.assertRaises(TypeError, Any, ())        

    def test_match(self):
        """Tests matching of LiteralPatterns."""
        _ = Any()
        self.assertMatch(23, _)
        self.assertMatch('foo', _)
        self.assertMatch((1,2), _)
        self.assertMatch([(1,2)], _)
        self.assertMatch(None, _)

    def test_callback(self):
        """Tests matching and calling back a function doing so."""
        l = [] ## Any mutable datastructure will do.
        X = Any()%l.append
        X.matches('foo')
        self.assertListEqual(l, ['foo'])
        l.pop()
        self.assertListEqual(l, [])        
        X.matches(1)        
        self.assertListEqual(l, [1])
        l.pop()
        self.assertListEqual(l, [])        
        X.matches((1, 2))        
        self.assertListEqual(l, [(1, 2)])


if __name__ == '__main__':

    unittest.main()
