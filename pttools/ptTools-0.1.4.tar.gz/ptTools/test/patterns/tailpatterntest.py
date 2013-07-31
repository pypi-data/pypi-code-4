#!/usr/bin/env python3

import unittest

from ptTools.patterns import AnyPattern as Any
from ptTools.patterns import LiteralPattern as Lit
from ptTools.patterns import TuplePattern as Tup

from . abstractpatterntest import AbstractPatternTest


class TailPatternTest(AbstractPatternTest):

    def test_instantiation(self):
        """Tests instantiation of Head-TailPattern."""
        Lit(1) >> Lit(2)
        Lit(1) >> Tup(2, 'b')
        Lit(1) >> Tup(Tup(2, 'b'))
        Tup(Tup(1)) >> Tup(Tup(2, 'b'))
        X = Lit('x')
        cons = Lit(1) >> Tup(3, 'a')
        X | cons
        cons | X
        +cons
        ~cons
        -cons

    def test_match_00(self):
        """Tests Head-TailPattern match (negative)."""        
        t = (1, (2, 'a'))
        p = Lit(1) >> Tup(2, 'a')
        self.assertRaises(AttributeError, p.matches, t)
        p = Tup(Lit(1) >> Tup(2, 'a'))
        self.assertMatch(t, p)
        
    def test_match_01(self):
        """Tests Head-TailPattern match."""                
        t = (1, (2, (3, 'a')))
        self.assertMatch(t, Tup(Lit(1) >> Tup(3, 'a')))
        self.assertMatch(t, Tup(Lit(1) >> (3, 'a'))) ## Shorthand notation.
        self.assertMatch(t, Tup(Lit(1) >> Tup(2, (3, 'a'))))
        self.assertMatch(t, Tup(Lit(1) >> (2, (3, 'a'))))
        self.assertMatch(t, Tup(Lit(1) >> Lit('a')))
        self.assertMatch(t, Tup(Lit(1) >> ('a')))
        self.denyMatch(t, Tup(Lit(2) >> Tup(3, 'a')))
        self.denyMatch(t, Tup(Lit(1) >> Tup(2, 'a')))
        
    def test_match_02(self):
        """Tests Head-TailPattern match."""                        
        t = (0, 'a', (2, (3, 'b')), 'c')
        p = Tup(0, Lit('a') >> (3, 'b'), 'c')
        self.assertMatch(t, p)
        p = Tup(0, (Lit('a') >> (3, 'b')), 'c')        
        self.assertMatch(t, p)
        p = Tup(0, Tup(Lit('a') >> (3, 'b')), 'c')                
        self.denyMatch(t, p)        

    def test_match_03(self):
        """Tests Head-TailPattern match."""
        _ = Any()
        t = (0, 'a', (2, (3, 'b')), 'c')
        p = Tup(0, 'a', Tup(_ >> (3, 'b')), 'c')
        self.assertMatch(t, p)
        p = Tup(0, 'a', (_ >> (3, 'b')), 'c')
        self.denyMatch(t, p)

    def test_match_04(self):
        """Tests union."""
        _ = Any()
        t = (0, (2, (3, 'b')))
        p = Tup(0, Tup(_ >> (3, 'b')) | _)
        self.assertMatch(t, p)
        p = Tup(0, _ | (_ >> (3, 'b')))
        self.assertMatch(t, p)
        p = Tup(0, Tup(2, _) | (_ >> (3, 'b')))
        self.assertMatch(t, p)
        p = Tup(0, Tup(_ >> (3, 'b')) | (2, _))
        self.assertMatch(t, p)

    def test_match_05(self):
        """Tests closure."""
        _ = Any()
        p = Tup(+(Lit(0) >> (2, 'a')))
        t = (0, (2, 'a'))
        self.assertMatch(t, p)
        t = (0, (2, 'a'), 0, (2, 'a'))
        self.assertMatch(t, p)
        t = (0, (2, 'a'), 1, (2, 'a'))
        self.denyMatch(t, p)
        t = (0, (2, 'a'), 0, (2, 'b'))
        self.denyMatch(t, p)

    def test_callback(self):
        p = (Lit(0) >> (2, 'a'))
        self.assertRaises(AttributeError, p.__getattribute__, '__mod__')
