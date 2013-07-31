#!/usr/bin/env python3

"""Module providing a LinkedToken class, wrapping tokenize.tinfo
objects."""

__all__ = [
    'LinkedToken',
    ]

import token
import tokenize

from ptTools.misc import AttributesMixIn


class  LinkedToken(tokenize.TokenInfo, AttributesMixIn):

    """Wrapper class for tokenize.TokenInfo objects.

    LinkedTokens have .predecessor and .successor attributes, pointing
    to the previous and next LinkedTokens yielded by the
    generate_tokens function.  If self was created during parsing,
    together with a ptTools.TerminalNode, self.terminal is a
    backreference to that node.  See the ptTools.parsetree package.
    
    LinkedToken may optionally be instantiated with an attributes
    collection type of dict, list, set.  Regardless of its type, the
    same methods are provided.
        
    """

    @classmethod
    def fromtinfo(cls, tinfo, attr_type=None):
        """Factory method.  Extends TokenInfo object with LinkedToken
        attributes, and returns the updated instance."""
        tinfo.__class__ = cls
        AttributesMixIn.__init__(tinfo, attr_type)
        tinfo.predecessor = None
        tinfo.successor = None
        tinfo.terminal = None
        return tinfo

    def __init__(self, *args):
        """Calls super().__init__(*args)."""
        super().__init__(*args)
        self.predecessor = None ## Set by tokenizer.
        """Returns preceeding LinkedToken, or None if self was the
        first token generated during tokenization."""
        self.successor = None   ## Set by tokenizer.
        """Returns following LinkedToken, or None if self is the last
        token generated during tokenization, or a successor has not
        yet been yielded by tokenizer."""
        self.terminal = None    ## Set by parser.
        """Reference to ParseTreeNode if self has a representation in
        a parsetree."""

    def __str__(self):
        return self.string
        
    @property
    def endx(self):
        """Returns the x coordinate of self.end."""                
        return self.end[1]

    @property
    def endy(self):
        """Returns the y coordinate of self.end."""                
        return self.end[0]

    @property
    def identifier(self):
        """Alias for the self.type attribute."""        
        return self.type

    @property
    def leading_space(self):
        """Returns the absolute distance from previous token's end (or
        the start of line) to self start.x."""
        if not self.predecessor:
            return self.startx
        elif self.predecessor.endy == self.starty:
            return self.startx - self.predecessor.endx
        else:
            return self.startx

    @property
    def length(self):
        """Returns the length of self.string."""        
        return len(self.string)

    @property
    def predecessors(self):
        """Returns list of all preceeding tokens from the start of
        tokenization up to self, inclusively."""
        if self.predecessor:
            return self.predecessor.predecessors + [self.predecessor]
        else:
            return []

    @property
    def rest(self):
        """Returns string following self.string up to the end of line."""
        return self.line[self.endx:]

    @property
    def startx(self):
        """Returns the x coordinate of self.start."""                
        return self.start[1] 

    @property
    def starty(self):
        """Returns the y coordinate of self.start."""        
        return self.start[0]
        
    def iscomment(self):
        """True, if self is a comment.

        TODO - Does not recognize multiline comments!

        """
        return self.identifier == tokenize.COMMENT

    def iscontinuation(self):
        """True, if self follows a non-syntactic linebreak."""
        return self.predecessor and \
            self.predecessor.endy != self.starty

    def isdecorativenewline(self):
        """True, if self is a non-syntactic newline."""
        return self.identifier == tokenize.NL

    def isdedent(self):
        """True, if self is a dedent."""                
        return self.identifier == token.DEDENT

    def isindent(self):
        """True, if self is a indent."""                        
        return self.identifier == token.INDENT

    def ismulticomment(self):
        """True, if self is a multiline comment.        

        TODO - Also returns True for multiline strings.

        """
        return self.identifier == token.STRING and \
               (self.string.startswith('"""') or \
                self.string.startswith("'''"))

