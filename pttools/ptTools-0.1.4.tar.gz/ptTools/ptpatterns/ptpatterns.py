#!/usr/bin/env python3

"""Module providing pattern classes for matching against
ptTools.ParseTreeNodes."""

import sys

from .. import patterns
from .. import tokenizer


def TerminalPattern(val):
    """Creates and returns pattern matching a TerminalNode with val.

    For example TerminalPattern('class') creates
    TuplePattern(token.NAME, 'class').

    """
    ## TODO - create class.
    identifier = tokenizer.identify(val)
    return TuplePattern(identifier, LiteralPattern(val))

def prettyinput(node):
    """Prints node in a more readable form"""
    node.prettyinput()

def prettyprint(node, writer=sys.stdout):
    """Prints node in a more readable form"""
    node.prettyprint(writer)


class AbstractPattern(patterns.AbstractPattern):
    """Like superclass, but with customized pattern creation function."""

    def create_pattern(self, arg):
        if isinstance(arg, str):
            return TerminalPattern(arg)
        else:
            return super().create_pattern(arg)
        
    @property
    def union_class(self):
        return UnionPattern

    @property
    def literal_pattern_class(self):
        return LiteralPattern

    @property
    def tuple_pattern_class(self):
        return TuplePattern


## Must override all patterns that call the create_pattern method, in
## order to create TerminalPatterns.

class ConcatenationPattern(patterns.ConcatenationPattern, AbstractPattern):
    """Like superclass, but with customized pattern creation function."""    
    pass

class LiteralPattern(patterns.LiteralPattern, AbstractPattern):
    """Like superclass, but with customized pattern creation function."""    
    pass

class TuplePattern(patterns.TuplePattern, AbstractPattern):
    """Like superclass, but with customized pattern creation function."""
    pass

class UnionPattern(patterns.UnionPattern, AbstractPattern):
    """Like superclass, but with customized pattern creation function."""
    pass
