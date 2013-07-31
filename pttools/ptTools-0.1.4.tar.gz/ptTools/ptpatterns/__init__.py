#!/usr/bin/env python3

"""\
ptpatterns
----------

This package is the core of the domain specific language, provided by
ptTools.  It provides pattern classes for matching parsetree nodes.

Parsetrees have to be of the following form

Pattern classes defined in this package, share a pattern creation
method, which transforms strings in pattern descriptions to
TuplePatterns matching those strings as if they were terminal nodes.

For example TuplePattern(1, 'a') is instantiated as
TuplePattern(1, TuplePattern(token.NAME, 'a')).

This fascilitates easier pattern descriptions, because it resembles
the originating grammar more closely.

"""

__author__ = "Markus Rother - python@markusrother.de"
__date__ = "06/2013"
__version__ = "0.1"


from .. patterns import _
from .. patterns import more
from .. patterns import AnyPattern
from .. patterns import TestPattern
from . ptpatterns import prettyinput
from . ptpatterns import prettyprint
from . ptpatterns import ConcatenationPattern
from . ptpatterns import LiteralPattern 
from . ptpatterns import TerminalPattern 
from . ptpatterns import TuplePattern
from . ptpatterns import UnionPattern 


__all__ = [
    '_',
    'more',
    'prettyinput',
    'prettyprint',
    'AnyPattern',
    'ConcatenationPattern',
    'LiteralPattern',
    'TestPattern',
    'TuplePattern',
    'TerminalPattern',        
    'UnionPattern',
    ]


def _mkreadme(out):
    out.write(__doc__)

