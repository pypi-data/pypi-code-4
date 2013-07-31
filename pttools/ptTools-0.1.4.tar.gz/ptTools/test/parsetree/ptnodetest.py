#!/usr/bin/env python3

"""Tests parsetree creation from tuples."""

import sys
import unittest

import ptTools
from ptTools import parsetree
from ptTools.parsetree import NonTerminalNode
from ptTools.parsetree import TerminalNode

from testlib import python_library
from testlib import parse


class ParseTreeNodeTest(unittest.TestCase):

    def assertAllTrue(self, coll):
        for each in coll:
            self.assertTrue(each)

    def test_nonterminal_type(self):
        """Assert type of nonterminal node."""
        root = parsetree.fromtuple((0, 'a'))
        self.assertTrue(isinstance(root, tuple))
        self.assertTrue(isinstance(root, NonTerminalNode))
        self.assertTrue(root[0] == 0)
        self.assertTrue(isinstance(root[0], int))
        self.assertTrue(root[1] == 'a')        
        self.assertFalse(isinstance(root[1], tuple))
        self.assertTrue(isinstance(root[1], TerminalNode))
        self.assertTrue(isinstance(root[1], str))        
        
    def test_from_literal(self):
        """Test creation of terminal nodes."""
        node = parsetree.fromliteral('a')
        self.assertTrue(isinstance(node, TerminalNode))
        self.assertTrue(node.isleaf())         
        node = parsetree.fromliteral('')
        self.assertTrue(isinstance(node, TerminalNode))
        self.assertTrue(node.isleaf())         
        self.assertRaises(TypeError, parsetree.fromliteral, (1, 'a'))
        self.assertRaises(TypeError, parsetree.fromliteral, None)
        self.assertRaises(TypeError, parsetree.fromliteral, False)
        self.assertRaises(TypeError, parsetree.fromliteral, True)        
        self.assertRaises(TypeError, parsetree.fromliteral, 0)        
        self.assertRaises(TypeError, parsetree.fromliteral, 1)
        self.assertRaises(TypeError, parsetree.fromliteral, [])        
        
    def test_from_tuple_00(self):
        """Test creation of nonterminal nodes."""
        node = parsetree.fromtuple((1, 'a', (2, 'b')))
        self.assertTrue(isinstance(node, NonTerminalNode))
        self.assertTrue(isinstance(node, tuple))
        self.assertFalse(node.isleaf())        
        self.assertRaises(TypeError, parsetree.fromtuple)        
        self.assertRaises(TypeError, parsetree.fromtuple, (1,))
        self.assertRaises(TypeError, parsetree.fromtuple, ((),))
        self.assertRaises(TypeError, parsetree.fromtuple, ('a',))
        self.assertRaises(TypeError, parsetree.fromtuple, ('a', 'b'))        
        self.assertRaises(TypeError, parsetree.fromtuple, 'a')
        self.assertRaises(TypeError, parsetree.fromtuple, None)
        self.assertRaises(TypeError, parsetree.fromtuple, True)
        self.assertRaises(TypeError, parsetree.fromtuple, False)        
        self.assertRaises(TypeError, parsetree.fromtuple, 0)
        self.assertRaises(TypeError, parsetree.fromtuple, 1)
        self.assertRaises(TypeError, parsetree.fromtuple, '')
        self.assertRaises(TypeError, parsetree.fromtuple, [])
        self.assertRaises(TypeError, parsetree.fromtuple, ((),'a'))
        self.assertRaises(TypeError, parsetree.fromtuple, (1, 23))        

    def test_from_and_to_tuple_00(self):        
        """Asserts equality of conversion from parsed pnode back to
        tuple."""
        tup = (1, 'a')
        root = parsetree.fromtuple(tup)
        self.assertTupleEqual(tup, root.totuple())
        self.assertTrue(root.children)
        self.assertEqual(len(root.children), 1)
        child = root.children[0]
        self.assertFalse(child.children)

    def test_from_and_to_tuple_01(self):
        """Asserts equality of conversion from parsed pnode back to
        tuple."""
        tup = (1, (2, 'three'),)
        root = parsetree.fromtuple(tup)
        self.assertTupleEqual(tup, root.totuple())        

    def test_from_and_to_tuple_02(self):
        """Asserts equality of conversion from parsed ptnode back to
        tuple."""
        tup = (1, (2, 'three'), (0, ''))
        root = parsetree.fromtuple(tup)
        self.assertTupleEqual(tup, root.totuple())        

    def test_terminal_values_00(self):
        """Tests type of Leafs."""
        tup = (1, (2, 'a', (3, 'b')), (4, 'c'), 'd')
        root = parsetree.fromtuple(tup)
        self.assertEqual(''.join([n.value for n in root.leaves]), 'abcd')
        self.assertAllTrue([isinstance(n, TerminalNode) for n in root.leaves])
        self.assertAllTrue([isinstance(n, str) for n in root.leaves])        

    def test_postorder_do(self):
        tup = (6, 'a', (4, (2, 'b'), 'd'), 'f')
        root = parsetree.fromtuple(tup)
        l = []
        fn = lambda node : l.append(node.value)
        root.postorder_do(fn)
        self.assertListEqual(l, ['a', 'b', 2, 'd', 4, 'f', 6])

    def test_preorder_do_00(self):
        """Tests preorder traversal of ParseTreeNode."""
        tup = (1, (2, 'a'),)
        root = parsetree.fromtuple(tup)
        l = []
        root.preorder_do(l.append)
        self.assertListEqual(l, [(1, (2, 'a'),),
                                 (2, 'a'),
                                 'a'])

    def test_preorder_do_01(self):
        tup = (0, 'b', (2, (3, 'e'), 'f'), 'g')
        root = parsetree.fromtuple(tup)
        l = []
        fn = lambda node : l.append(node.value)
        root.preorder_do(fn)
        self.assertListEqual(l, [0, 'b', 2, 3, 'e', 'f', 'g'])

    def test_iter_00(self):
        tup = (1, 'a')
        root = parsetree.fromtuple(tup)
        self.assertListEqual([n for n in root], [1, 'a'])

    def test_iter_01(self):
        root = parsetree.fromtuple((1, (2, 'a'), (3, (4, 'b')), 'c'))
        self.assertListEqual([c for c in root], [1,
                                                 (2, 'a'),
                                                 (3, (4, 'b')),
                                                 'c'])
        self.assertTrue(isinstance(root[0], int))
        self.assertTrue(isinstance(root[1], tuple))
        self.assertTrue(isinstance(root[2], tuple))
        self.assertTrue(isinstance(root[3], str))

    def test_getitem(self):
        tup = (0, (1, (2, 'a'), 'b',), 'c')
        root = parsetree.fromtuple(tup)
        self.assertEqual(len(root), 3)
        self.assertTupleEqual(root.totuple(), (0, (1, (2, 'a'), 'b',), 'c'))
        self.assertTupleEqual(root[1].totuple(), (1, (2, 'a'), 'b',))
        self.assertEqual(root[2], 'c')        
        self.assertRaises(IndexError, root.__getitem__, 3)

    def test_tree(self):
        """Tests consistency of entire tree."""
        tup = (1, (2, 'a', 'b'),)
        root = parsetree.fromtuple(tup)
        self.assertTrue(isinstance(root, NonTerminalNode))
        self.assertFalse(isinstance(root, TerminalNode))        
        self.assertTrue(isinstance(root, tuple))
        self.assertTrue(root.isroot())                        
        self.assertFalse(root.isleaf())
        self.assertTupleEqual(tup, root)
        self.assertEqual(1, root[0])
        self.assertTupleEqual(tup, root.totuple())
        
        child = root[1]
        self.assertTrue(isinstance(child, NonTerminalNode))
        self.assertFalse(isinstance(child, TerminalNode))        
        self.assertTrue(isinstance(child, tuple))
        self.assertFalse(child.isroot())                        
        self.assertFalse(child.isleaf())
        self.assertTupleEqual(tup[1], child)        
        self.assertTupleEqual(tup[1], child.totuple())
        
        leaf = child[1]
        self.assertFalse(isinstance(leaf, NonTerminalNode))
        self.assertTrue(isinstance(leaf, TerminalNode))
        self.assertFalse(isinstance(leaf, tuple))
        self.assertFalse(leaf.isroot())                        
        self.assertTrue(leaf.isleaf())
        self.assertEqual(tup[1][1], leaf)
        self.assertEqual('a', leaf[0])  
        self.assertRaises(AttributeError, leaf.__getattribute__, 'totuple')

        self.assertEqual(root.leaves[0], leaf)
        self.assertEqual(child.root, root)        
        self.assertEqual(leaf.root, root)

        self.assertEqual(root.children, [child])
        self.assertEqual(child.children[0], leaf)
        self.assertEqual(child.children[1], 'b')
        self.assertEqual(leaf.children, [])                


class ParseTreeNodeLibraryTest(ParseTreeNodeTest):

    def test_from_and_to_tuple_03(self):
        """Asserts equality of conversion from parsed parsetree back to
        tuple for whole library."""
        for py in python_library():
            sys.stdout.write('{}...'.format(py))
            pt = parse(py)
            root = parsetree.fromtuple(pt)
            leaves = root.leaves
            self.assertTupleEqual(pt, root.totuple())
            self.assertAllTrue([isinstance(n, TerminalNode) for n in leaves])
            self.assertAllTrue([isinstance(n, str) for n in leaves])            
            print('PASS')

    
if __name__ == """__main__""":

    unittest.main()
