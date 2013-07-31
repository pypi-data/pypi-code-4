#!/usr/bin/env python3

import unittest

from ptTools.patterns import AnyPattern as Any
from ptTools.patterns import ConcatenationPattern as Con
from ptTools.patterns import LiteralPattern as Lit
from ptTools.patterns import TuplePattern as Tup
from ptTools.patterns import UnionPattern as Union

from . import AbstractPatternTest


class UnionPatternTest(AbstractPatternTest):

    def test_instantiation_00(self):
        """Tests instantiation of UnionPatterns."""
        Union(None)
        Union('foo')
        Union(23)
        Union([1, 2, 3])
        Union(1, 2, 3, 4)
        Union()
        self.assertRaises(AttributeError, Union, [])        
        self.assertRaises(AttributeError, Union, 'a', [], 'b')        

    def test_match_00(self):
        """Tests simple UnionPattern."""                                
        t = 'a'
        self.assertMatch(t, Union('a'))        
        self.assertMatch(t, Union('a', 'b'))
        self.assertMatch(t, Union('a', 'b', 'c'))        

    def test_match_01(self):
        """Tests simple UnionPattern."""                                
        t = (1,)
        self.assertMatch(t, Union(Tup(1), Tup(2)))
        self.assertMatch(t, Union(Tup(1), Tup(2), 'a'))
        self.assertMatch(t, Union(Tup(1), Tup(2), Tup(3)))

    def test_match_02(self):
        """Tests simple UnionPattern."""                        
        t = (1, 'a')
        self.assertMatch(t, Tup(1, Union('a')))
        self.assertMatch(t, Tup(1, Union('a', 'b')))
        self.assertMatch(t, Tup(1, Union('a', 'b', 'c')))
        
    def test_match_03(self):
        """Tests UnionPattern."""                        
        t = (1, (2, 'a'))
        self.assertMatch(t, Tup(1, (2, Union('a'))))
        self.assertMatch(t, Tup(1, (2, Union('a', 'b'))))
        self.assertMatch(t, Tup(1, (2, Union('a', 'b', 'c'))))
        
    def test_match_04(self):
        """Tests UnionPattern."""                
        t = (1, 'a')
        _ = Any()
        self.assertMatch(t, Union(_))
        self.assertMatch(t, Union(_, _))
        self.assertMatch(t, Union(_, 'foo'))
        self.assertMatch(t, Union((1, 'a'), 'foo'))
        self.assertMatch(t, Union('foo', (1, 'a')))
        self.denyMatch(t, Union(0,))        
        self.denyMatch(t, Union(1, 'a'))
        self.denyMatch(t, Union('foo', 'bar'))
        self.denyMatch(t, Union((((1, 'a'),),),))

    def test_match_05(self):
        """Test options of variable length."""
        p = Union((1, 'a', 'b'), (1, 'a'), (1, 'x', 'y'))
        self.assertMatch((1, 'a'), p)
        self.assertMatch((1, 'a', 'b'), p)        

    def test_nested_00(self):
        """Tests nested UnionPatterns."""                
        t = (1, 'a')
        _ = Any()
        self.assertMatch(t, Tup(1, Union(_, Union('x', 'y'))))
        self.assertMatch(t, Tup(1, Union('x', Union(_, 'y'))))
        self.assertMatch(t, Tup(1, Union('x', Union('y', _))))                
        self.assertMatch(t, Tup(1, Union('a', Union('x', 'y'))))
        self.assertMatch(t, Tup(1, Union('x', Union('a', 'y'))))
        self.assertMatch(t, Tup(1, Union('x', Union('y', 'a'))))
        self.denyMatch(t, Tup(1, Union('x', Union('y', 'z'))))                        

    def test_nested_01(self):
        """Tests nested UnionPatterns."""        
        t = (1, 'a')
        _ = Any()
        self.assertMatch(t, Union(1, Union('x', 'y', (1, 'a'))))
        self.assertMatch(t, Union('x', Union((1, 'a'), 'y')))

    def test_abbreviated_00(self):
        """Tests UnionPattern created with __or__."""        
        t = (1, 'a')
        self.assertMatch('a', Tup() | 'a')
        self.assertMatch('a', Lit('x') | 'a')
        self.assertMatch('a', Lit('a') | 'x')        
        self.assertMatch(t, Tup(1, Lit('x') | Lit('a') | Lit('y')))
        self.assertMatch(t, Tup(1, 'x') | Tup(1, 'a'))

    def test_abbreviated_01(self):
        """Tests UnionPattern created with __or__."""
        A = Lit('a')
        B = Lit('b')
        C = Lit('c')
        self.assertMatch('a', A)
        self.assertMatch('a', A | B)
        self.assertMatch('a', A | C)                        
        self.assertMatch('a', A | B | C)
        self.denyMatch('a', B | C)
        
    def test_callback_00(self):
        """Tests UnionPattern with callback-fn."""
        t = (1, (2, 'a'))
        _ = Any()
        l = []
        p = Union((1, _), 'foobar') % l.append
        self.assertMatch(t, p)
        self.assertListEqual(l, [(1, (2, 'a'))])

    def test_callback_01(self):
        """Tests UnionPattern with callback-fn."""
        t = (1, 'a', 'b')
        _ = Any()
        l = []
        A = Tup(Con(1, _, _))
        B = 'foo'
        p = Union(A,B) % l.append
        self.assertMatch(t, p)
        self.assertListEqual(l, [(1,'a','b')])


if __name__ == '__main__':

    unittest.main()
