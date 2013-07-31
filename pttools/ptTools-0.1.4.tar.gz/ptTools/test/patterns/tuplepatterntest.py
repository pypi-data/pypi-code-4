#!/usr/bin/env python3

import unittest

from ptTools.patterns import AnyPattern as Any
from ptTools.patterns import TuplePattern as Tup
from ptTools.patterns import LiteralPattern as Lit
from ptTools.parsetree.tupletraversal import preorder_do

from . abstractpatterntest import AbstractPatternTest


class TuplePatternTest(AbstractPatternTest):

    """Tests tuple-like patterns (TuplePattern class)."""

    def test_instantiation_00(self):
        """Tests instantiation of TuplePatterns."""
        Tup()
        Tup(None)
        Tup('foo')
        Tup(23)
        Tup([1, 2, 3])
        Tup(1, 2, 3, 4)
        self.assertRaises(AttributeError, Tup, [])        
        self.assertRaises(AttributeError, Tup, 'a', [], 'b')        

        
    def test_instantiation_01(self):
        """Tests instantiation of nested TuplePatterns."""
        Tup(())
        Tup((1, 2),)
        Tup(Tup(1, 2))
        Tup(Tup(Tup()))
        Tup(Tup(Lit('a')))                

    def test_match_00(self):
        """Tests matching TuplePatterns against tuples."""        
        t = (1, '2')
        _ = Any()
        self.assertMatch(t, Tup(_, _))
        self.assertMatch(t, Tup(1, _))
        self.assertMatch(t, Tup(_, '2'))
        self.assertMatch(t, Tup(1, '2'))
        self.denyMatch(t, Tup())        
        self.denyMatch(t, Tup(_))
        self.denyMatch(t, Tup(1))
        self.denyMatch(t, Tup(1, None))        
        self.denyMatch(t, Tup(None))
        self.denyMatch(t, Tup(None, None))
        self.denyMatch(t, Tup(None, '2'))
        self.denyMatch(t, Tup(1, 2))
        self.denyMatch(t, Tup(_, 2))        
        self.denyMatch(t, Tup(1, 3))
        self.denyMatch(t, Tup(1, 1))
        self.denyMatch(t, Tup(2, 2))
        self.denyMatch(t, Tup(1, '2', _))
        self.denyMatch(t, Tup(1, '2', None))
        self.denyMatch(t, Tup(1, ('2',)))
        self.denyMatch(t, Tup(1, ('2', None)))        

    def test_match_01(self):
        """Tests matching TuplePatterns against tuples(!)."""        
        t = (1,)
        _ = Any()
        self.assertMatch(t, _)        
        self.assertMatch(t, Tup(1))
        ## ## TODO - MOVE >>
        ## self.assertMatch(t, Tup(1, []))
        ## self.assertMatch(t, Tup(1, [], []))
        ## self.assertMatch(t, Tup([1]))
        ## ## <<
        self.assertMatch(t, Tup(Lit(1)))        
        self.denyMatch(t, Tup(_, _))
        self.denyMatch(t, Tup(1, None))
        self.denyMatch(t, Tup(1, _))
        self.denyMatch(t, Tup(1, Tup()))        
        self.denyMatch(t, Tup(Lit(1), _))
        self.denyMatch(t, Tup(Tup(1), _))
        self.denyMatch(t, Tup(Tup(1)))
        self.denyMatch(t, Tup(1, 'x'))

    def test_match_02(self):
        """Tests matching TuplePatterns against tuples(!)."""        
        t = (1, None) 
        _ = Any()
        self.assertMatch(t, Tup(1, _))
        self.assertMatch(t, Tup(1, None))
        self.assertMatch(t, Tup(Lit(1), None))
        self.denyMatch(t, Tup())        
        self.denyMatch(t, Tup(_))
        self.denyMatch(t, Tup(1, 0))
        self.denyMatch(t, Tup(1))
        self.denyMatch(t, Tup(1, 'x'))

    def test_match_03(self):
        """Tests matching TuplePatterns against tuples."""        
        t = ()
        _ = Any()
        self.assertMatch(t, Tup())
        self.denyMatch(t, Tup(None))
        self.denyMatch(t, Tup(_))

    def test_match_04(self):
        """Tests matching TuplePatterns against tuples."""        
        t = (None,)
        _ = Any()
        self.assertMatch(t, Tup(_))
        self.assertMatch(t, Tup(None))
        self.denyMatch(t, Tup())
        self.denyMatch(t, Tup(None, None))                

    def test_match_05(self):
        """Tests matching TuplePatterns against literals."""                
        _ = Any()
        self.denyMatch('a', Tup('a'))
        self.denyMatch('a', Tup(_))
        self.denyMatch('a', Tup())        

    def test_match_06(self):
        """Tests matching TuplePatterns against tuples."""        
        t = (('a',), 'b')
        self.assertMatch(t, Tup(('a',), 'b'))
        self.denyMatch(t, Tup(('a', 'b')))
        self.denyMatch(t, Tup((('a', 'b'),),))
        self.denyMatch(t, Tup('ab'))

    def test_copy_00(self):
        """Tests equivalence of copy."""
        l = []
        A = (Tup('a')%l.append).copy()
        self.assertMatch(('a',), A)
        self.assertListEqual(l, [('a',)])

    def test_copy_01(self):
        """Tests equivalence of copy by print string comparison."""
        self.assertEquivalentCopy(Tup())
        self.assertEquivalentCopy(Tup(None))
        self.assertEquivalentCopy(Tup('foo'))
        self.assertEquivalentCopy(Tup(23))
        self.assertEquivalentCopy(Tup([1, 2, 3]))
        self.assertEquivalentCopy(Tup(1, 2, 3, 4))
        self.assertEquivalentCopy(Tup((1, 2),))
        self.assertEquivalentCopy(Tup(Tup(1, 2)))
        self.assertEquivalentCopy(Tup(Tup(Tup('a', 'b'), 23)))
        self.assertEquivalentCopy(Tup(Tup(Lit('a'))))

    def test_callback_00(self):
        """Tests TuplePatterns with callback-fn."""                        
        l = [] ## Any mutable datastructure will do.
        X = Any()%l.append
        Tup(1, 2, X).matches((1, 2, 3))        
        self.assertListEqual(l, [3])
        l.pop()
        self.assertListEqual(l, [])        
        Tup(1, 0, X).matches((1, 2, 3))        
        self.assertListEqual(l, [])
        Tup(1, X, 3).matches((1, 2, 3))        
        self.assertListEqual(l, [2])
        l.pop()
        self.assertListEqual(l, [])                
        Tup(1, 2, 3).matches((1, 2, 3))        
        self.assertListEqual(l, [])
        Tup(1, X, 'foo').matches((1, 2, 3))
        self.assertListEqual(l, [])
        Tup(1, X).matches((1, 2))
        self.assertListEqual(l, [2])
        l.pop()
        self.assertListEqual(l, [])                
        Tup(1, X).matches((1, (2,)))
        self.assertListEqual(l, [(2,)])        

    def test_callback_01(self):
        """Tests TuplePatterns with callback-fn."""                        
        l = []
        p = Tup(1, 'a')%l.append
        p.matches((1, 'a'))
        self.assertListEqual(l, [(1, 'a')])

    def test_leaf_00(self):
        """Tests TuplePatterns with callback-fn."""                                
        t = (1, (2,))
        l = []
        X = Any()%l.append
        self.assertMatch(t, Tup(1, (2,)))
        self.assertMatch(t, Tup(1, X))
        self.assertListEqual(l, [(2,)])
        self.denyMatch(t, Tup(1, 2))

    def test_leaf_01(self):
        """Tests TuplePatterns with callback-fn."""                                
        t = (1, 2)
        l = []
        X = Any()%l.append
        self.assertMatch(t, Tup(1, 2))
        self.assertMatch(t, Tup(1, X))
        self.assertListEqual(l, [2])
        self.denyMatch(t, Tup(1, (2,)))

    def test_leaf_02(self):
        """Tests TuplePatterns with callback-fn."""                                
        t = (1, 2)
        l = []
        self.assertMatch(t, Tup(1, 2)%l.append)
        self.assertListEqual(l, [(1, 2)])
        self.denyMatch(t, Tup(1, (2,)))

    def test_match_nested(self):
        """Tests matching nested TuplePatterns."""
        t = (1, (2, 'a'))
        _ = Any()
        self.assertMatch(t, Tup(_, _))
        self.assertMatch(t, Tup(1, _))
        self.assertMatch(t, Tup(_, (_, _)))
        self.assertMatch(t, Tup(_, (2, _)))
        self.assertMatch(t, Tup(_, (_, 'a')))
        self.assertMatch(t, Tup(_, (2, 'a')))
        self.assertMatch(t, Tup(1, (2, _)))        
        self.assertMatch(t, Tup(1, (_, 'a')))
        self.assertMatch(t, Tup(1, (2, 'a')))
        self.denyMatch(t, Tup(1, (2, ('a',))))
        self.denyMatch(t, Tup(1, (2, ())))

    def test_multi_match(self):
        """Tests multiple matches in one tree."""
        l = []
        _ = Any()
        tree = (1, (2, 'a'), (2, ('b',)), (3, (2, ('x', 'y'))))
        pattern = Tup(2, _) % l.append
        preorder_do(tree, pattern.matches)
        self.assertListEqual(l, [(2, 'a'),
                                 (2, ('b',)), 
                                 (2, ('x', 'y'))])


if __name__ == '__main__':

    unittest.main()
