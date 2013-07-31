#!/usr/bin/env python3

"""Module providing the TerminalNode class."""

__all__ = [
    'TerminalNode',
    ]

import sys

from . import ParseTreeNode


class TerminalNode(ParseTreeNode, str):    

    """Class modelling parsetree leaves.

    Inherits from str for type equivalence.
    
    If created with a tokenizer, each instance has a tokens attribute
    with a list of LinkedTokens.  Those are the tokens yielded by
    ptTools.tokenizer.generate_tokens().

    The last token in self.tokens is a token with the same string
    value as the node's.  Its predecessors are tokens that were
    skipped since the last relevant token (included in parsetree).
    LinkedTokens themselves are linked by their predecessor and
    successor attributes.  See ptTools.tokenizer.LinkedToken.

    Consider the following:
    
        1. Tokens are quintuples, whereas the parsetree's terminals
        are strings with an identifier.  See ptTools.tokenizer and the
        parser modules.

        2. A token's identifier is not necessarily the same as a
        terminal node's identifier.  Usually, the terminal identifier
        is more descriptive.  Also, see the token.h header file on
        your include/python path, as well as the token module.

        3. A TerminalNode instance's token list may contain tokens not
        included in the parsetree at all, e.g. comment nodes, or
        non-syntactic linebreaks.

    """
    ## Implementation notes: 1. Tokens are kept to allow full
    ## reconstruction of their source.  2. Subtyping from str pulls in
    ## a bunch of useful methods, such as __eq__, __getitem__,
    ## __iter__, __len__, and so forth.

    def __new__(cls, val, *args):
        """Creates str subtype."""
        if not isinstance(val, str):
            raise TypeError('Terminal value must be str.')
        return str.__new__(cls, val)
        
    def __init__(self, value, tokenizer=None, attr_type=None):
        """Instantiated with the terminals str value."""
        super().__init__(value, attr_type)
        self.tokens = []
        if tokenizer:
            for tok in self._generate_tokens(tokenizer):
                self.tokens.append(tok)
                tok.terminal = self

    def _generate_tokens(self, tokenizer):
        """Generator function, yielding tuples created by tokenizer.
        
        Also, yields tokens (tuples) that are NOT included in the
        parse tree, up to the first token, that IS represented in the
        parse tree, inclusively.  The tokenizer is received as an
        argument.

        Raises StopIteration.

        """
        while True:
            tinfo = next(tokenizer) # Raises StopIteration on EOF.
            tinfo.parent = self
            yield tinfo
            if (not tinfo.iscomment()) and (not tinfo.isdecorativenewline()):
                raise StopIteration

    ## @property
    ## def all_attributes(self):
    ##     """Returns inherited attributes joined with token attributes."""
    ##     attrs = super().all_attributes
    ##     for token in self.tokens:
    ##         if token.attributes:
    ##             assert(type(self.attributes) == type(token.attributes))
    ##             self._collector(attrs, token.attributes)
    ##     return attrs

    @property
    def string(self):
        """The terminal's value."""
        return self.value

    @property
    def token(self):
        """The token equivalent to self.

        EOF has no tokens? """
        return self.tokens[-1] if self.tokens else None
        
    def _prettyprint(self, writer, ignore=None):
        writer.write('\'{}\''.format(self))

    def append(self, ignore):
        """Raises AttributeError."""
        raise AttributeError('Cannot add children to TerminalNode')

    def prettyprint(self, writer=sys.stdout):
        self._prettyprint(writer)

    def tostring(self):
        """Returns joined string of all of self's tokens."""
        return ''.join([tok.string for tok in self.tokens])
        
    def tuplevalue(self):
        """Returns value to be inserted for self into its equivalent
        tuple."""
        return self.value
