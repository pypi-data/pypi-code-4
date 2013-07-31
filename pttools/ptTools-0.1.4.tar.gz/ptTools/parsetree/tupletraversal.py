#!/usr/bin/env python3

"""Module, providing basic traversal functions over tuple
representations of trees.

tuples must be of the following form:
    tree ::= (val, (tree | val)*)
    val ::= LITERAL

"""

__all__ = [
    'leaves_do',
    'postorder',
    'postorder_do',    
    'preorder',
    'preorder_do',        
    ]


def postorder(tup):
    """Generator function, yielding nodes in postorder traversal."""
    if isinstance(tup, tuple): ## tup is inner node.
        children = tup[1:]
        if children:
            for child in children:
                for node in postorder(child):
                    yield node
        else: ## tup is parent to empty leaf.
            pass
    else: ## tup is value (leaf), and will be yielded, now.
        pass
    yield tup
    raise StopIteration

def postorder_do(tup, fn):
    """Traverses tuple representation of tree postorder, applying
    callback in every node."""
    for node in postorder(tup):
        fn(node)

def preorder(tup):
    """Returns iterator over tuple elements in preorder."""
    yield tup
    if isinstance(tup, tuple): ## tup is inner node.
        children = tup[1:]
        if children:
            for child in children:
                for node in preorder(child):
                    yield node
        else: ## tup is parent to empty leaf.
            pass
    else: ## tup is value (leaf), and will be yielded, now.
        pass
    raise StopIteration

def preorder_do(tup, fn):
    """Traverses tuple representation of tree preorder, applying
    callback in every node."""
    for node in preorder(tup):
        fn(node)

def leaves_do(tup, fn):
    """Traverses tuple representation of tree, applying callback in
    every leaf."""
    func = lambda n: fn(n) if not isinstance(n, tuple) or not n else None
    preorder_do(tup, func)

def leaves(tup):
    """Iterator.  Yields leaves from tuple representation of tree."""
    for node in preorder(tup):
        if not isinstance(node, tuple):
            yield node
    raise StopIteration

def terminals(tup):
    """Iterator.  Yields tuples of the form (token.x, str)."""
    for node in preorder(tup):
        if isinstance(node, tuple) and \
           len(node) == 2 and \
           isinstance(node[1], str):
            yield node
    raise StopIteration
    
