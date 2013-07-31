#!/usr/bin/env python3

"""Module providing the AbstractParseTreeNode class."""

__all__ = [
    'ParseTreeNode',
    ]

from io import StringIO

from .. writers import VerboseParseTreeWriter
from ptTools.misc import AttributesMixIn
from ptTools.misc import ValuedNode


class ParseTreeNode(ValuedNode, AttributesMixIn):
    
    """Abstract class, providing attributes and methods, shared
    amongst both types of parsetree nodes: NonTerminalNode and
    TerminalNode.

    Nodes may be attributed.  Attributes collection may be of list,
    set, or dict type.  See AttributeCollection.

    Note: Does not yet support synthetic attributes.

    """

    def __bool__(self): 
        """Returns True, because initialization is always with a value."""
        return True
        
    @property
    def all_attributes(self):
        """Returns collection of inherited attributes.  Attribute type
        may be list, set or dict.

        If self was initialized with a list, this method will return a
        list containing all attributes of all ancestors, starting with
        root.  If self was initialized with a dict (default), a dict
        is returned with self's attributes presiding over its
        ancestors, recursively.

        """
        if self.attributes is None:
            return None
        else:
            if self.isroot():
                coll = self._collector.__objclass__()
            else:
                coll = self.parent.all_attributes
            ## Adding self's attributes to coll:
            self._collector(coll, self.attributes)
            return coll

    def isnonterminal(self):
        """True if self is an inner parsetree node."""
        return not self.isterminal()
    
    def isterminal(self):
        """True if self is a parsetree leaf."""
        return self.isleaf()

    def prettyinput(self):
        with StringIO() as out:        
            self.prettyprint(out)
            input(out.getvalue())
    
    def prettyprint(self, *ignore):
        """Raises AttributeError.  Subclass responsibility."""
        raise AttributeError
    
    def tuplevalue(self):
        """Returns value to be inserted for self into its equivalent
        tuple."""
        raise AttributeError('Must be implemented by subclass')

    def tostring(self):
        """Returns self's reconstructed source string."""
        with StringIO() as out:        
            writer = VerboseParseTreeWriter(out)
            writer.write_node(self)
            return out.getvalue()
        
