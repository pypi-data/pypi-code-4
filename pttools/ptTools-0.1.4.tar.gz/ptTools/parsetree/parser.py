#!/usr/bin/env python3

"""Module providing functions for parsetree creation."""

__all__ = [
    'fromfile',
    'fromliteral',
    'fromstring',
    'fromtuple',
    ]

import parser

from .. tokenizer import generate_tokens
from . import NonTerminalNode
from . import TerminalNode

## TODO - I used to need this additional information.  Not so anymore.
## Why?  It may go to tostr(), totuple() or other places where we may
## want to ignore this info.  grep for a file which includes an
## encoding decl and make sure it gets printed and does not confuse
## the parsetree.  Should be covered by tests already.  Verify!  Make
## a note to the testmethod!
##
## if n.identifier == symbol.encoding_decl and \
##     isinstance(c, str):
## ## This is a special case.
## ## symbol.encoding_decl is not included in gramamr,
## ## although it may appear in the parse tree.  The
## ## omitted child node has a string value, such as
## ## 'iso-8...'.  See
## ## http://docs.python.org/2/reference/grammar.html


def _instantiate_nonterminal(tup, tokenizer, attr_type):
    """Creates and returns NonTerminalNode with children."""
    if not isinstance(tup, tuple):
        msg = 'must instantiate from tuple'
    elif not tup:
        msg = 'tuple must not be empty'
    elif not isinstance(tup[0], int):
        msg = 'tuple must start with int, got {}'.format(tup[0])
    else:
        parent = NonTerminalNode(tup[0], attr_type)
        children = tup[1:]
        if children:
            for obj in children:
                parent.append(_instantiate(obj, tokenizer, attr_type))
            return parent
        else:
            msg = 'Missing terminal in {}'.format(tup)
    raise TypeError(msg)

def _instantiate_terminal(val, tokenizer, attr_type):
    """Creates and returns TerminalNode, and adds tokens if tokenizer
    not None."""
    return TerminalNode(val, tokenizer, attr_type)    

def _instantiate(obj, tokenizer, attr_type):
    """Creates and returns terminal or nonterminal ParseTreeNode."""    
    if isinstance(obj, tuple):
        return fromtuple(obj, tokenizer, attr_type)
    else:
        return _instantiate_terminal(obj, tokenizer, attr_type)

def fromfile(filename, tokenize_fn=generate_tokens, attr_type=None):
    """Returns parsetree root from source file as ptnode.NonTerminal.

    Optional attribute types may be given, setting the type of
    ParseTreeNode and LinkedToken instances .attributes attribute.
    See the AttributesCollection class.
    
    """
    ## TODO - Get two parallel ro pointers, if possible.
    with open(filename, 'r') as f:
        string = f.read()
    with open(filename, 'r') as f:
        tokenizer = tokenize_fn(f.readline)
        return fromstring(string, tokenizer, attr_type)

def fromliteral(obj, tokenizer=None, attr_type=None):
    """Factory for TerminalNodes."""
    return _instantiate_terminal(obj, tokenizer, attr_type)
    
def fromstring(string, tokenizer=None, attr_type=None):
    """Returns parsetree root from source string as
    ptnode.NonTerminal."""
    ## TODO - Allow tokenization of strings.
    parsetree = parser.suite(string).totuple()
    return fromtuple(parsetree, tokenizer, attr_type)

def fromtuple(tup, tokenizer=None, attr_type=None):
    """Factory for NonTerminalNodes.  Builds tree from tuple
    representation and token stream.

    Takes tuple of form (int, child+ | str), where children are of the
    same tuple form.  If tup[1] is a string, a TerminalNode is
    created, otherwise a NonTerminalNode.  Takes a tokenizer as an
    optional second argument.  If given, corresponding tokens are
    appended to terminal_node.tokens.

    """
    return _instantiate_nonterminal(tup, tokenizer, attr_type)

