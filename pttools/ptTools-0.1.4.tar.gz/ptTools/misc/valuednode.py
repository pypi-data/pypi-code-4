#!/usr/bin/env python3

"""Module providing a simple tree node class: ValuedNode."""

__all__ = [
    'ValuedNode',
    ]

class ValuedNode(object):

    """A simple node class."""

    def __init__(self, value, *args, **kwargs):
        """Initialized with value."""
        super().__init__(*args, **kwargs)
        self.value = value
        self.children = []
        self.parent = None

    @property
    def ancestors(self):
        """Returns list of ancestors from root up to self,
        inclusively."""
        if self.isroot():
            return [self]
        else:
            return self.parent.ancestors + [self]
        
    @property
    def leaves(self):
        """Returns list of Node instances that are leaves in the tree."""
        lst = []
        fn = lambda n : lst.append(n) if n.isleaf() else None
        self.preorder_do(fn)
        return lst

    @property
    def root(self):
        """Returns root of tree."""
        return self if self.isroot() else self.parent.root

    def append(self, child):
        """Appends Node instance as last child of self."""
        self.children.append(child)
        child.parent = self
               
    def isleaf(self):
        """True, if self has no children."""
        return False if self.children else True        

    def isroot(self):
        """True, if self has no parent."""
        return False if self.parent else True

    def postorder(self):
        """Generator function.  Returns postorder iterator over self."""
        for child in self.children:
            for descendent in child.postorder():
                yield descendent
        yield self

    def postorder_do(self, fn):
        """Traverses nodes postorder, applying callback to every node,
        starting with self."""    
        for child in self.children:
            child.postorder_do(fn)
        fn(self)

    def preorder(self):
        """Generator function.  Returns preorder iterator over self."""
        yield self
        for child in self.children:
            for descendent in child.preorder():
                yield descendent

    def preorder_do(self, fn):
        """Traverses nodes preorder, applying callback to every node,
        starting with self."""    
        fn(self)
        for child in self.children:
            child.preorder_do(fn)
        
        
            
