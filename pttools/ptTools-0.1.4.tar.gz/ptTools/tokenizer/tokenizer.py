#!/usr/bin/env python3

"""Wrapper module for tokenize.  Provides iterator yielding
LinkedToken instances from an input readline object."""

__all__= [
    'generate_tokens',
    'identify'
    'SYMBOLS'
    'Tokenizer',
    ]


import token
import tokenize

from . linkedtoken import LinkedToken


TOKENS = {
    ## I did not find this mapping in any of the modules tokenize,
    ## parser, or token.  It is certainly not worth starting to
    ## tokenize a single character, just because we need the
    ## identifier, so I did it the hard way.
    '(' : token.LPAR,
    ')' : token.RPAR,
    '[' : token.LSQB,
    ']' : token.RSQB,
    ':' : token.COLON,
    ',' : token.COMMA,
    ';' : token.SEMI,
    '+' : token.PLUS,
    '-' : token.MINUS,
    '*' : token.STAR,
    '/' : token.SLASH,
    '|' : token.VBAR,
    '&' : token.AMPER,
    '<' : token.LESS,
    '>' : token.GREATER,
    '=' : token.EQUAL,
    '.' : token.DOT,
    '%' : token.PERCENT,
    '{' : token.LBRACE,
    '}' : token.RBRACE,
    '==' : token.EQEQUAL,
    '!=' : token.NOTEQUAL,
    '<=' : token.LESSEQUAL,
    '>=' : token.GREATEREQUAL,
    '~'  : token.TILDE,
    '^'  : token.CIRCUMFLEX,
    '<<' : token.LEFTSHIFT,
    '>>' : token.RIGHTSHIFT,
    '**' : token.DOUBLESTAR,
    '+=' : token.PLUSEQUAL,
    '-=' : token.MINEQUAL,
    '*=' : token.STAREQUAL,
    '/=' : token.SLASHEQUAL,
    '%=' : token.PERCENTEQUAL,
    '&=' : token.AMPEREQUAL,
    '|=' : token.VBAREQUAL,
    '^=' : token.CIRCUMFLEXEQUAL,
    '<<=' : token.LEFTSHIFTEQUAL,
    '>>=' : token.RIGHTSHIFTEQUAL,
    '**=' : token.DOUBLESTAREQUAL,
    '//'  : token.DOUBLESLASH,
    '//=' : token.DOUBLESLASHEQUAL,
    '@'   : token.AT,
    '->'  : token.RARROW,
    '...' : token.ELLIPSIS,    
    }

SYMBOLS = {}
"""Reverse mapping of token identifiers to their name as string."""
for key, value in token.__dict__.items():
    if isinstance(value, int):
        SYMBOLS[value] = key

def identify(val):
    """Takes a token value (str) and returns the identifier (int) for
    that value.  Defaults to token.NAME."""
    if isinstance(val, int):
        return token.NUMBER
    elif val.startswith("'"):
        return token.STRING   
    elif val.startswith('"'):
        return token.STRING
    else:
        return TOKENS.get(val, token.NAME)

def generate_tokens(readline):
    """Iterator, yielding LinkedToken instances.  Takes readline
    object.
    
    Wraps tokenize.generate_tokens.
    
    """
    return _IterableTokenizer([], None, readline)


class _IterableTokenizer(object):

    """Iterator class, yielding LinkedToken instances.

    Wraps tokenize.generate_tokens to return LinkedToken instances
    instead of TokenInfo objects.

    """

    def __init__(self, patterns, attr_type, readline):
        self.iterator = tokenize.generate_tokens(readline)
        """The original iterator (tokenize.generate_tokens)."""
        self.last = None
        """The previous token, already yielded by __next__.  None if
        self has not yielded any elements."""
        self.attr_type = attr_type
        """dict, list, or set."""
        self.patterns = patterns

    def __next__(self):
        """Yields LinkedToken instance."""
        ## TODO - Currently, a multicomment (multiline strings)
        ## consists of only one token with a multiline string.  Note
        ## that the 'less' command destroys ansi markups accross
        ## linebreaks.  Hence, we will have to split mulitline strings
        ## into separate lines to preserve markups accross
        ## lines. Further splitting may be necessary to suppress
        ## markups during indentation, as the leading space is not an
        ## indent, but of course part of the comment string itself.
        litoken = LinkedToken.fromtinfo(next(self.iterator), self.attr_type)
        litoken.predecessor = self.last
        if self.last: 
            self.last.successor = litoken
        self.last = litoken
        ## Applying patterns:
        if self.patterns:
            for pattern in self.patterns:                
                pattern.match(litoken)
        return litoken


class Tokenizer(object):
    
    """Factory for iterable tokenizers, yielding LinkedToken
    instances.

    Emulates behaviour of tokenize.generate_tokens which is an
    iterator function, called with a readline instance.

    """

    def __init__(self, patterns, attr_type=None):
        """Initialized with a collection of token patterns and an
        optional type for token attributes.""" 
        self.patterns = patterns
        """list fo token attributes"""
        self.attr_type = attr_type
        """dict, list, or set."""

    def __call__(self, readline):
        """Takes readline object and returns iterator."""
        return _IterableTokenizer(self.patterns, self.attr_type, readline)


