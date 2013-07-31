#!/usr/bin/env python3

"""Module providing the NonTerminalNode class."""

__all__ = [
    'NonTerminalNode',
    ]
    
import sys
from itertools import zip_longest

from . import ParseTreeNode
from . import SYMBOLS


class NonTerminalNode(ParseTreeNode, tuple):

    """Class modelling inner parsetree nodes.

    Inherits from tuple for type equivalence, although NonTerminalNode
    IS MUTABLE!

    """

    def __new__(cls, val, *args, **kwargs):
        """Creates tuple subtype."""
        if not isinstance(val, int):
            raise TypeError('NonTerminal value must be int.')
        ## TODO - Currently, it is not of importance what the tuple is
        ## instantiated with, as __getitem__, and other methods are
        ## overridden.  For now, we only need the type information
        ## from tuple.  If we manage to properly store the children in
        ## self's tuple (maybe list), we could get rid of __eq__,
        ## __getitem__, __len__.
        return tuple.__new__(cls, ())

    def __eq__(self, obj):
        """Returns True if self's tuple equivalent equals obj."""
        if not isinstance(obj, tuple):
            return False
        for a, b in zip_longest(self, obj, fillvalue=StopIteration):
            if (a is StopIteration) != (b is StopIteration): ## xor
                return False
            elif a != b:
                return False
        return True            

    def __getitem__(self, val):
        """Returns items from self's tuple equivalent.

        The first (index 0) item is self's value, all succeeding
        elements are either returned as NonTerminalNode or as
        TerminalNode.  self is NOT included in that collection, as
        self is equivalent to the very tuple to which __getitem__ is
        applied.

        """
        ## The mixture of three different return types may seem
        ## somewhat awkward at first sight.  However, we always return
        ## the equivalent tuple's equivalent contents.  We return
        ## ParseTreeNodes except for the first item.  The first item
        ## is identical to the tuple equivalent's value at a given
        ## index, but so are the ParseTreeNodes, themselves.
        if isinstance(val, slice):
            return ([self.value] + self.children).__getitem__(val)        
        else:
            if val == 0:
                return self.value            
            else:
                return self.children[val-1]

    def __iter__(self): 
        """Iterates over sequence of [self.value] + self.children.
        Does not descend!

        All nodes are yielded as ParseTreeNodes.
        
        """
        yield self.value
        for child in self.children:
            yield child

    def __len__(self):
        """Returns the length of self's tuple equivalent."""
        return 1 + len(self.children)
        
    def __ne__(self, obj):
        """Returns False unless self's tuple equivalent equals obj."""
        return not self.__eq__(obj)

    def __repr__(self):
        """Returns the string of self's tuple equivalent."""
        return repr(self.totuple())

    def __str__(self):
        """Returns the print string of self's tuple equivalent."""
        return str(self.totuple())

    @property
    def identifier(self):
        """Returns self's integer value."""
        return self.value

    @property
    def tokens(self):
        """Returns list of all tokens on the branch that self is."""
        coll = []
        for leaf in self.leaves:
            coll.extend(leaf.tokens)
        return coll
        
    def prettyprint(self, writer=sys.stdout):
        """Substitutes identifiers with names from symbol module."""
        val = SYMBOLS.get(self.value, self.value)
        writer.write('({}, '.format(val))
        for child in self.children:
            child._prettyprint(writer)
        writer.write(')\n')

    def _prettyprint(self, writer, depth=1):
        """Private supplement to .prettyprint."""
        val = SYMBOLS.get(self.value, self.value)
        writer.write('\n{}({}, '.format('  '*depth, val))
        for child in self.children:
            child._prettyprint(writer, depth+1)
        writer.write(')')

    def recompile(self, glbs=None, locs=None):
        """Evaluates code contained in self's leaves and returns
        evaluation result."""
        return eval(self.tostring(), glbs, locs)

    def totuple(self):
        """Returns tuple equivalent of self.

        Returned tuple has form: tree ::= (int, (tree | str)*).
        
        """
        return self.tuplevalue()

    def tuplevalue(self):
        """Returns value to be inserted for self into its equivalent
        tuple."""
        child_gen = (c.tuplevalue() for c in self.children)
        return (self.value,) + tuple(child_gen)
