#!/usr/bin/env python3

"""Module providing parsing and traversal functions, as well as
classes to model parsetree nodes.

Parsetree nodes extend the behaviour of tuples of the following form:

    tree ::= (int, (tree | str)*)

This involves two node classes: NonTerminalNode and TerminalNode, both
subclasses of ParseTreeNode.  NonTerminalNodes are the inner nodes of
a parsetree, wheras TerminalNodes are its leaves.  NonTerminals
represent the tuples (inner and outer) in the above form, whereas
TerminalNodes represent the string values.

Both concrete classes combine behaviour of a primitive type (tuple, or
str) with tree-like attributes and operations, such as traversal
methods.  NonTerminalNode is a tuple subtype, whereas TerminalNode is
a str subtype.  NonTerminalNodes have an int type value, but compare
equivalent to their tuple representation.  TerminalNodes have a str
type value to which they compare equivalent to.

For NonTerminalNodes the name 'identifier' is used synonymously for
'value'.  TerminalNodes use the alias 'string' for addressing their
'value'.

For example, assume a ParseTreeNode for the tree (1, 'a').  It would
consist of a NonTerminalNode n and a single child, the TerminalNode t.

>>> from ptTools import parsetree
...
>>> node = parsetree.fromtuple((1, 'a'))
>>> isinstance(node, tuple)
True
>>> node.value
1
>>> node.value == node.identifier
True
>>> node == (1, 'a')
True
>>> child = node.children[0]
>>> child is node[1]
True
>>> isinstance(child, str)
True
>>> child.value
'a'
>>> child.value == child.string
True

ParseTrees are created with the factory methods:

    * fromtuple(tuple) - Where tuples must be of the following form:
        tree ::= (int, (tree | str)*)
        (as created by the parser module).
        
    * fromstring(str) - Returns parsetree from source code string.
    
    * fromfile(str) - Returns parsetree from a file given its name.
    
    * fromliteral(obj) - Instantiates and returns TerminalNode.

If the parsetree is created from a string or a file, TerminalNodes
will have a list of LinkedTokens as their .tokens attribute.  See
the ptTools.tokenizer package.

This module also provides traversal functions for tuples or tuple-like
objects:

    * postorder(tuple) - Generator, yielding nodes in postorder.
    
    * postorder_do(tuple, function) - Application of function to all
        nodes, postorder.
    
    * preorder(tuple) - Generator, yielding nodes in preorder.
    
    * preorder_do(tuple, function) - Application of function to all
        nodes, postorder.
        
    * leaves(tuple, function) - Generator, yielding a tree's leaves.


Examples for parsetrees:

    * (1, (2, 'a') (3, 'b')) is a valid parsetree of three
      NonTerminalNodes with identifiers 1, 2, 3 and two TerminalNodes
      (leafs) with values 'a' and 'b'.  This tree is NOT a binary
      tree, because nodes 2 and 3 have only one child each.

    * (1, 2, 3) is a binary tree with two leaves, but not a valid
      parsetree, because terminals are not of the form (int, str).

    * (1, (2,)) is not a valid parsetree, because its only leaf
      has no value.

    * ((1, 'a'), 'b') is not a valid parsetree, because its first
      element is not an integer.


Also, see the parser module as well as the python grammar
specification for a description of possible derivations.  See the
symbol, and token modules for valid identifiers.  See the
/lib/include/python3.x/graminit.h header file for the mapping of
symbol names to integers.

"""

__author__ = "Markus Rother - python@markusrother.de"
__date__ = "06/2013"
__version__ = "0.1"

__all__ = [
    'fromfile',
    'fromliteral',
    'fromstring',
    'fromtuple',
    'SYMBOLS',
    'tupletraversal',
    'NonTerminalNode',
    'ParseTreeNode',
    'TerminalNode',
    ]

import symbol

import ptTools
from ptTools import tokenizer

SYMBOLS = {}
"""Mapping nonterminal identifiers to str."""
for k, v in symbol.__dict__.items():
    if isinstance(v, int):
        SYMBOLS[v] = k
SYMBOLS.update(tokenizer.SYMBOLS)        

from . parsetreenode import ParseTreeNode
from . nonterminalnode import NonTerminalNode
from . terminalnode import TerminalNode
from . parser import fromfile
from . parser import fromliteral
from . parser import fromstring
from . parser import fromtuple

