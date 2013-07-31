#!/usr/bin/env python3

"""Additional patterns and styles for the captureex.py example.

Note: To examine what a pattern matches, simply add a ' % print' or '
% prettyprint' to get output on stdout.

"""

import symbol
import token

from ptTools.ptpatterns import AnyPattern as Any
from ptTools.ptpatterns import TuplePattern as Tup
from ptTools.ptpatterns import UnionPattern as Opt
from ptTools.ptpatterns import LiteralPattern as Lit
from ptTools.ptpatterns import TestPattern as Test
from ptTools.ptpatterns import _
from ptTools.ptpatterns import more
from ptTools.ptpatterns import prettyprint
from ptTools.writers.ansiwriter import COLOR as color
from ptTools.writers.ansiwriter import BOLD as bold


def style(key):
    """Returns function that adds an attribute to node."""    
    return lambda n : n.add_attributes(styles[key])


## Styles for AnsiParseTreeWriter:
styles = {
    'string'  : { color: 6 },
    'op'      : { color: 6, bold: True },
    'paren'   : { color: 5, bold: True },
    'any'     : { color: 3, bold: True },
    'pattern' : { color: 2 },
    'dotted'  : { color: 3 },
    }


## Patterns for output markup:
STRING  = Tup(token.STRING, _)
OP      = Tup(Test(lambda n : token.LPAR<= n <=token.OP), _)
PAREN   = Tup(Opt(token.LPAR, token.RPAR), _)
ANY     = Tup(token.NAME, Lit('_'))
TUP     = Tup(token.NAME, Lit('Tup'))
LIT     = Tup(token.NAME, Lit('Lit'))
PATTERN = TUP | LIT
DOTTED  = Tup(symbol.power,
              (symbol.atom, (token.NAME, Lit('symbol') | Lit('token'))),
              (symbol.trailer, more)) ## % prettyprint

patterns = [
    STRING  % style('string'),
    OP      % style('op'),
    PAREN   % style('paren'),
    ANY     % style('any'),    
    PATTERN % style('pattern'),    
    DOTTED  % style('dotted'),
    ]
