#!/usr/bin/env python3

"""Tests matching ParseTreeNodes with patterns."""

import sys
import unittest

import ptTools

from ptTools.patterns import AnyPattern as Any
from ptTools.ptpatterns import TuplePattern as Tup
from ptTools.ptpatterns import LiteralPattern as Lit
from ptTools.ptpatterns import TerminalPattern as Terminal

from ptTools.misc import ValuedNode

from ptTools import parsetree
from ptTools.parsetree import tupletraversal

from patterns import AbstractPatternTest

from testlib import python_library
from testlib import parse


class PatternMatchTest(AbstractPatternTest):

    def test_match_01(self):
        """Tests simple literal match."""
        self.denyMatch(parsetree.fromtuple((0, (1, 'a'))), Lit('a'))

    def test_match_02(self):
        """Tests tuple match variations."""
        _ = Any()    
        root = parsetree.fromtuple((0, (1, 'a')))
        self.assertMatch(root, Tup(0, _,))
        self.assertMatch(root, Tup(0, 'a'))
        self.assertMatch(root, Tup(_, 'a'))
        self.assertMatch(root, Tup(Lit(0), Terminal('a')))
        self.denyMatch(root, Tup(_, Lit('a')))
        self.denyMatch(root, Tup(0, Lit('a')))
        self.denyMatch(root, Tup(_, Tup('a')))
        self.denyMatch(root, Tup(_, (('a',),)))

    def test_match_03(self):
        """Tests tuple match variations."""
        more = ~Any()    
        root = parsetree.fromtuple((0, (1, 'a'), (1, 'a'), (1, 'a')),)
        self.assertMatch(root, Tup(0, more))

    def test_match_04(self):
        """Tests shorthand for closure [:1]."""
        _ = Any()    
        root = parsetree.fromtuple((0, (1, 'a'), (1, 'b')))
        self.assertMatch(root, Tup(0, ['a'], 'b',))
        self.assertMatch(root, Tup(0, ['a'], 'b', ['c']))
        self.assertMatch(root, Tup(0, 'a', ['a'], 'b', ['c']))                

    def test_match_05(self):
        """Tests shorthand for closure [:1]."""
        _ = Any()    
        root = parsetree.fromtuple((0, (1, 'a'), (1, 'b')),)
        t = Lit('a')
        self.assertMatch(root, Tup(0, ['a'], 'b',))
        self.assertMatch(root, Tup(0, ['a'], 'b', ['c']))
        self.assertMatch(root, Tup(0, 'a', ['a'], 'b', ['c']))                

    def test_callback(self):
        """Tests callback execution after closure."""
        tup = (0, (1, 'a'), (1, 'a'), (1, 'a'))
        more = ~Any()
        l = []
        root = parsetree.fromtuple(tup)
        self.assertMatch(root, Tup(0, more) % l.append)
        self.assertListEqual(l, [tup])

    def test_iter_match_00(self):
        """Tests application of callback during iteration."""
        l = []
        A = Lit('a')
        root = parsetree.fromtuple((1, (1, 'a')),)
        pattern = Tup(1, A % (lambda n : l.append(n.string)))
        root.preorder_do(pattern.matches)
        self.assertListEqual(l, ['a'])

    def test_iter_match_01(self):
        """Tests application of callback during iteration with
        multiple matches."""
        l = []
        A = Lit('a')
        _ = Any()
        root = parsetree.fromtuple((1, (2, 'a'), (3, 'a')))
        pattern = Tup(_, A % (lambda n : l.append(n.string)))
        root.preorder_do(pattern.matches)
        self.assertListEqual(l, ['a', 'a'])

    def test_tuplevalue_00(self):
        """Tests application of callback during iteration with
        multiple matches."""
        l = []
        root = parsetree.fromtuple((1, (2, (1, 'a')), (3, (1, 'b'))))
        pattern = Any() % (lambda n : l.append(n.tuplevalue()))
        root.preorder_do(pattern.matches)
        self.assertListEqual(l, [(1, (2, (1, 'a')), (3, (1, 'b'))),
                                 (2, (1, 'a')),
                                 (1, 'a'),
                                 'a',
                                 (3, (1, 'b')),
                                 (1, 'b'),
                                 'b'])

    def test_iter_match_02(self):
        """Tests application of callback during iteration with
        multiple matches."""
        l = []
        root = parsetree.fromtuple((1, (2, (1, 'a')), (3, (1, 'b'))))
        pattern = Any() % l.append
        root.preorder_do(pattern.matches)
        self.assertListEqual(l, [(1, (2, (1, 'a')), (3, (1, 'b'))),
                                 (2, (1, 'a')),
                                 (1, 'a'),
                                 'a',
                                 (3, (1, 'b')),
                                 (1, 'b'),
                                 'b'])

    def test_iter_match_03(self):
        """Tests application of callback during iteration with
        multiple matches."""
        l = []
        _ = Any()
        root = parsetree.fromtuple((1, (2, (3, (1, 'a')))))
        pattern = Tup(_, _) % (lambda n : l.append(n.totuple()))
        root.preorder_do(pattern.matches)
        self.assertListEqual(l, [(1, (2, (3, (1, 'a')))),
                                 (2, (3, (1, 'a'))),
                                 (3, (1, 'a')),
                                 (1, 'a')])

    def test_iter_match_04(self):
        """Tests application of callback on ConcatenationPattern."""
        l = []
        root = parsetree.fromtuple((0, (1, 'a'), (2, (1, 'b'))))
        pattern = Tup(2, 'b') % l.append
        root.preorder_do(pattern.matches)
        self.assertListEqual([n.totuple() for n in l], [(2, (1, 'b'))])

    def test_iter_match_05(self):
        """Tests multiple matches in one tree."""
        l = []
        _ = Any()
        root = parsetree.fromtuple((1, (2, (1, 'a')), (2, 'b'), (3, (2, (4, 'x', 'y')))))
        pattern = Tup(2, _) % l.append
        root.preorder_do(pattern.matches)
        self.assertListEqual([n.totuple() for n in l], [(2, (1, 'a')),
                                                        (2, 'b'), 
                                                        (2, (4, 'x', 'y'))])

    def test_iter_match_06(self):
        """Tests application of callback during iteration with
        union pattern."""
        l = []
        _ = Any()
        root = parsetree.fromtuple((1, (2, (3, (1, 'a')), (3, 'b'))))
        pattern = (Tup(3, 'a') | Tup(3, 'x')) % (lambda n : l.append(n.totuple()))
        root.preorder_do(pattern.matches)
        self.assertListEqual(l, [(3, (1, 'a'))])

    def test_iter_match_07(self):
        """Tests application of callback during iteration with
        union pattern."""
        l = []
        _ = Any()
        root = parsetree.fromtuple((1, (2, (3, (1, 'a')), (4, 'b'))))
        pattern = (Tup(3, 'a') | Tup(4, _)) % (lambda n : l.append(n.totuple()))
        root.preorder_do(pattern.matches)
        self.assertListEqual(l, [(3, (1, 'a')),
                                 (4, 'b')])

    def test_traversal(self):
        """Tests equivalent traversal behaviour."""
        t = (1, (2, (1, 'a')), (2, 'b'), (3, (2, (4, 'x', 'y'))))
        tuple_iter = tupletraversal.preorder(t)
        root = parsetree.fromtuple(t)
        node_iter = root.preorder()
        for t, n in zip(tuple_iter, node_iter):
            self.assertEqual(t, n)


class ParseTreeNodeLibraryTest(PatternMatchTest):

    ## TODO - move to test.parsetree (?)

    def test_traversal_library(self):
        """Tests equivalent traversal behaviour for all files in
        library."""
        for py in python_library():
            sys.stdout.write('{}...'.format(py))
            pt = parse(py)
            root = parsetree.fromtuple(pt)
            tuple_iter = tupletraversal.preorder(pt)
            node_iter = root.preorder()            
            for t, n in zip(tuple_iter, node_iter):
                self.assertEqual(t, n)
            print('PASS')


if __name__ == '__main__':

    unittest.main()
