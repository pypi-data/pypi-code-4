#!/usr/bin/env python3

import unittest

from ptTools.patterns import AnyPattern as Any
from ptTools.patterns import ConcatenationPattern as Con
from ptTools.patterns import LiteralPattern as Lit
from ptTools.patterns import TuplePattern as Tup
from ptTools.patterns import UnionPattern as Union

from . abstractpatterntest import AbstractPatternTest


class ClosurePatternTest(AbstractPatternTest):

    def test_instantiation(self):
        """Tests instantiation of closure over LiteralPattern."""
        X = Lit('x')
        self.assertRaises(AttributeError, (+X).matches, 'x')
        self.assertRaises(AttributeError, (-X).matches, 'x')
        self.assertRaises(AttributeError, (~X).matches, 'x')
        
    def test_match_01(self):
        """Tests closure over LiteralPattern."""
        X = Any()
        self.assertMatch((), Tup([X]))
        self.assertMatch((), Tup(~X))
        self.assertMatch((), Tup(-X))
        self.denyMatch((), Tup(+X))
        
        self.assertMatch(('x',), Tup([X]))
        self.assertMatch(('x',), Tup(~X))
        self.assertMatch(('x',), Tup(-X))
        self.assertMatch(('x',), Tup(+X))
        
        self.assertMatch(('x','x'), Tup(+X))
        self.assertMatch(('x','x'), Tup(~X))
        self.denyMatch(('x','x'), Tup([X]))        
        self.denyMatch(('x','x'), Tup(-X))

    def test_match_02(self):
        _ = Any()
        self.assertMatch(('a','b'), Tup(-Lit('a'), _))
        self.assertMatch((1,'a'), Tup(1, [Lit('a')]))
        self.denyMatch(('a','a'), Tup([Lit('a')]))
        self.denyMatch((1,'a','a','a'), Tup(1, [Lit('a')]))

    def test_match_03(self):
        A = Lit('a')
        B = Lit('b')
        self.assertMatch((), Tup([A], [B]))

        self.assertMatch(('b',), Tup([A], B))
        self.assertMatch(('b',), Tup(-A, B))
        self.assertMatch(('b',), Tup(~A, B))
        self.denyMatch(('b',), Tup(+A, B))
        
        self.assertMatch(('a','b'), Tup([A], B))
        self.assertMatch(('a','b',), Tup(-A, B))
        self.assertMatch(('a','b',), Tup(~A, B))
        self.assertMatch(('a','b',), Tup(+A, B))
        
        self.denyMatch(('a','a','b'), Tup([A], B))
        self.denyMatch(('a','a','b'), Tup(-A, B))
        self.assertMatch(('a','a','b'), Tup(~A, B))
        self.assertMatch(('a','a','b'), Tup(+A, B))
        
        self.assertMatch(('a','b'), Tup(A, [B]))
        self.assertMatch(('a','b'), Tup(A, -B))
        self.assertMatch(('a','b'), Tup(A, ~B))
        self.assertMatch(('a','b'), Tup(A, +B))
        
        self.assertMatch(('a','b','b'), Tup(A, +B))        
        self.assertMatch(('a','b','b'), Tup(A, ~B))
        
        self.assertMatch(('a','a','b','b'), Tup(+A, +B))
        self.assertMatch(('a','a','b','b'), Tup(~A, ~B))

    def test_match_04(self):
        pattern = Tup(+(Lit('a') >> 'b'))
        self.assertMatch(('a','b'), pattern)        
        self.assertMatch(('a','b','a','b'), pattern)        
        self.assertMatch(('a',(0, 'b')), pattern)        
        self.assertMatch(('a',(0, 'b'),'a',(0, (1, 'b'))), pattern)
        
    def test_nested_00(self):
        pattern = Tup(['(',[ 'x' ],')',])
        self.assertMatch((), pattern)
        self.assertMatch(('(',')'), pattern)        
        self.assertMatch(('(','x',')'), pattern)
        self.denyMatch(('x',), pattern)                        
        self.denyMatch(('(','x','x',')'), pattern)                

    def test_nested_01(self):
        pattern = Tup('(',+Tup('a','b'),')')
        self.assertMatch(('(',('a','b'),')'), pattern)        
        self.assertMatch(('(',('a','b'), ('a','b'),')'), pattern)        
        self.denyMatch(('a','b',), pattern)                        

    def test_copy_01(self):
        """Tests equivalence of copy."""
        p = Tup(1, [Lit('x')]).copy()
        self.assertMatch((1,), p)        
        self.assertMatch((1,'x',), p)
        self.denyMatch((1,'x','x'), p)

    def test_copy_02(self):
        """Tests equivalence of copy."""
        p = Tup(1, +Lit('x'))
        cp = p.copy()
        self.denyMatch((1,), p)
        self.denyMatch((1,), cp)                
        self.assertMatch((1,'x',), p)
        self.assertMatch((1,'x',), cp)        
        self.assertMatch((1,'x','x','x'), p)
        self.assertMatch((1,'x','x','x'), cp)        

    def test_copy_03(self):
        """Tests equivalence of copy."""
        p = Tup(1, +Lit('x')).copy()
        self.denyMatch((1,), p)        
        self.assertMatch((1,'x',), p)
        self.assertMatch((1,'x','x'), p)
        self.assertMatch((1,'x','x','x','x'), p)

    def test_callback_00(self):
        """Tests ClosurePattern with callback."""
        l = []
        A = Lit('a') % l.append
        self.assertMatch(('a',), Tup(-A))
        self.assertListEqual(l, ['a'])
        l.pop()
        self.assertListEqual(l, [])        
        self.assertMatch(('a','a','a'), Tup(+A))
        self.assertListEqual(l, ['a','a','a'])

    def test_callback_01(self):
        """Tests ClosurePattern with callback."""
        t = (1, (2, 'a'), (3, (4, 'b')))
        l = []
        _ = Any()
        self.assertMatch(t, Tup(+_%l.append))
        self.assertListEqual(l, [1, (2, 'a'), (3, (4, 'b'))])
        l.pop();l.pop();l.pop()
        self.assertMatch(t, Tup(+(_%l.append)))
        self.assertListEqual(l, [1, (2, 'a'), (3, (4, 'b'))])

    def test_callback_02(self):
        l = []
        a = Lit('a')
        pattern = Tup(~a%l.append)
        self.assertMatch((), pattern)
        self.assertListEqual(l, [])
        self.assertMatch(('a',), pattern)
        self.assertListEqual(l, ['a'])        
        l.pop()
        self.assertMatch(('a','a','a'), pattern)
        self.assertListEqual(l, ['a','a','a'])        

    def test_callback_03(self): ## TODO - move
        """Tests ClosurePattern with callback."""
        l = []
        _ = Any()
        p = Tup(1, (Tup(2, _)%l.append)*2)        
        self.assertMatch((1, (2, 'a'), (2, 'b')), p)
        self.assertListEqual(l, [(2, 'a'), (2, 'b')])

    def test_callback_04(self):
        l = []
        _ = Any()
        b = Lit('b')%l.append
        p = Tup('a', +Con(b,'c'), 'd')
        t = ('a','b','c','b','c','d')
        self.assertMatch(t, p)
        self.assertListEqual(l, ['b', 'b'])

    def test_callback_05(self):
        l = []
        _ = Any()
        bc = Tup('b', ['c'])%l.append
        p = Tup('a', +Con(bc, ['d']))
        t = ('a',('b','c'),'d',('b',),'d')
        self.assertMatch(t, p)
        self.assertListEqual(l, [('b','c'), ('b',)])

    def test_concatenation_00(self):
        t = ('a','b','c','b','c','d')
        self.assertMatch(t, Tup('a', +Con('b','c'), 'd'))

    def test_concatenation_01(self):
        t = ('a','b','c','b','d')
        self.assertMatch(t, Tup('a', +Con('b',['c']), 'd'))

    def test_concatenation_02(self):
        t = ('a','b','c','b','d')
        more = ~Any()
        self.assertMatch(t, Tup('a', +Con('b',['c']), more))

    def test_concatenation_03(self):
        t = ('a',('b','c'),'d')
        self.assertMatch(t, Tup('a', Con(Tup('b',['c'])), 'd'))

    def test_concatenation_04(self):
        self.assertMatch(('a',('b',),'c'), Tup('a', Con(~Tup('b',),'c')))
        self.assertMatch(('a',('b',),('b',),'c'), Tup('a', Con(~Tup('b',),'c')))

    def test_concatenation_05(self):
        self.assertMatch((), Tup(~Tup('a',['b'])))
        self.assertMatch((('a',),), Tup(~Tup('a',['b'])))
        self.assertMatch((('a','b'),), Tup(~Tup('a',['b'])))
        self.assertMatch((('a','b'),('a','b',)), Tup(~Tup('a',['b'])))
        self.assertMatch((('a','b'),('a','b',),'c'), Tup(~Tup('a',['b']),'c'))

    def test_concatenation_06(self):
        t = ('a',('b','c'),('b',),'d')
        self.assertMatch(t, Tup('a', Con(~Tup('b',['c'])), 'd'))

    def test_concatenation_07(self):
        t = ('a',('b',),'c',('b',),'d')
        self.assertMatch(t, Tup('a', +Con(Tup('b'), ['c']), 'd'))

    def test_union_00(self):
        _ = Any()
        self.assertMatch((), Tup(+Union(~_)))

    def test_union_01(self):
        _ = Any()
        self.assertMatch((), Tup(+(Tup('foo') | ~_)))
