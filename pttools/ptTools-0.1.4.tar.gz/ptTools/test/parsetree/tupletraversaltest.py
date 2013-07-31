#!/usr/bin/env python3

import unittest

from ptTools.parsetree.tupletraversal import preorder
from ptTools.parsetree.tupletraversal import preorder_do
from ptTools.parsetree.tupletraversal import postorder
from ptTools.parsetree.tupletraversal import postorder_do
from ptTools.parsetree.tupletraversal import leaves_do


def preorder_values(tup):
   for node in preorder(tup):
        yield node[0] if isinstance(node, tuple) else node
        
    
class TupleTraversalTest(unittest.TestCase):    

    def test_preorder_00(self):
        """Tests preorder traversal through tree representation in tuple."""
        l = []
        tup = (1, 'a')
        exp = [(1, 'a'),
               'a']
        val = [1, 'a']
        preorder_do(tup, l.append)
        self.assertListEqual(l, exp)
        self.assertListEqual(exp, [n for n in preorder(tup)])
        self.assertListEqual(val, [n for n in preorder_values(tup)])

    def test_preorder_01(self):
        """Tests preorder traversal through tree representation in tuple."""
        l = []
        tup = (1, (2,))
        exp = [(1, (2,)),
               (2,)]
        val = [1, 2]
        preorder_do(tup, l.append)
        self.assertListEqual(l, exp)
        self.assertListEqual(exp, [n for n in preorder(tup)])
        self.assertListEqual(val, [n for n in preorder_values(tup)])
        
    def test_preorder_02(self):
        """Tests preorder traversal through tree representation in tuple."""
        l = []
        tup = (1, (2, 'a'))
        exp = [(1, (2, 'a')),
               (2, 'a'),
               'a']
        val = [1, 2, 'a']
        preorder_do(tup, l.append)
        self.assertListEqual(l, exp)
        self.assertListEqual(exp, [n for n in preorder(tup)])
        self.assertListEqual(val, [n for n in preorder_values(tup)])
        
    def test_preorder_03(self):
        """Tests preorder traversal through tree representation in tuple."""        
        l = []
        tup = (1, 'a', 'b')
        exp = [(1, 'a', 'b'),
               'a',
               'b']
        val = [1, 'a', 'b']
        preorder_do(tup, l.append)
        self.assertListEqual(l, exp)
        self.assertListEqual(exp, [n for n in preorder(tup)])
        self.assertListEqual(val, [n for n in preorder_values(tup)])

    def test_preorder_04(self):
        """Tests preorder traversal through tree representation in tuple."""
        l = []
        tup = (1, (2, (3, 'a')))
        preorder_do(tup, l.append)
        exp = [(1, (2, (3, 'a'))),
               (2, (3, 'a')),
               (3, 'a'),
               'a']
        val = [1, 2, 3, 'a']
        self.assertListEqual(l, exp)
        self.assertListEqual(exp, [n for n in preorder(tup)])
        self.assertListEqual(val, [n for n in preorder_values(tup)])

    def test_preorder_05(self):
        """Tests preorder traversal through tree representation in tuple."""
        l = []
        tup = (1, (2,), (3, 'a'))
        exp = [(1, (2,), (3, 'a')),
               (2,),
               (3, 'a'),
               'a']
        val = [1, 2, 3, 'a']
        preorder_do(tup, l.append)
        self.assertListEqual(l, exp)
        self.assertListEqual(exp, [n for n in preorder(tup)])
        self.assertListEqual(val, [n for n in preorder_values(tup)])

    def test_postorder_00(self):
        """Tests postorder traversal through tree representation in tuple."""
        l = []
        tup = (1, 'a')
        exp = ['a',
               (1, 'a')]
        postorder_do(tup, l.append)
        self.assertListEqual(l, exp)
        self.assertListEqual(exp, [n for n in postorder(tup)])

    def test_postorder_01(self):
        """Tests postorder traversal through tree representation in tuple."""
        l = []
        tup = (1, (2,))
        exp = [(2,),
               (1, (2,))]
        postorder_do(tup, l.append)
        self.assertListEqual(l, exp)
        self.assertListEqual(exp, [n for n in postorder(tup)])

    def test_postorder_02(self):
        """Tests postorder traversal through tree representation in tuple."""
        l = []
        tup = (1, (2, 'a'))
        exp = ['a',
               (2, 'a'),
               (1, (2, 'a'))]
        postorder_do(tup, l.append)
        self.assertListEqual(l, exp)
        self.assertListEqual(exp, [n for n in postorder(tup)])

    def test_postorder_03(self):
        """Tests postorder traversal through tree representation in tuple."""        
        l = []
        tup = (1, 'a', 'b')
        exp = ['a',
               'b',
               (1, 'a', 'b')]
        postorder_do(tup, l.append)
        self.assertListEqual(l, exp)
        self.assertListEqual(exp, [n for n in postorder(tup)])
                                 
    def test_postorder_04(self):
        """Tests postorder traversal through tree representation in tuple."""        
        l = []
        tup = (1, (2, (3, 'a')))
        exp = ['a',
               (3, 'a'),
               (2, (3, 'a')),
               (1, (2, (3, 'a')))]
        postorder_do(tup, l.append)
        self.assertListEqual(l, exp)
        self.assertListEqual(exp, [n for n in postorder(tup)])

    def test_postorder_05(self):
        """Tests postorder traversal through tree representation in tuple."""
        l = []
        tup = (1, (2,), (3, 'a'))
        exp = [(2,),
               'a',
               (3, 'a'),
               (1, (2,), (3, 'a'))]
        postorder_do(tup, l.append)
        self.assertListEqual(l, exp)
        self.assertListEqual(exp, [n for n in postorder(tup)])

    def test_leaves(self):
        """Tests leaf collection."""
        l = []
        tup = (1, 'a', (2, 'b'), (3, 'c', (4, 'd'), 'e'), 'f')
        leaves_do(tup, l.append)
        self.assertEqual(''.join(l), 'abcdef')


if __name__ == '__main__':

    unittest.main()
