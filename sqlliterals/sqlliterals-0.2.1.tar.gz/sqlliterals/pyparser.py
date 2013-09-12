#!/usr/bin/env python

"""
A pyparsing implementation of SQL statement tokenisation.

Copyright (C) 2007 Paul Boddie <paul@boddie.org.uk>

This library is free software; you can redistribute it and/or
modify it under the terms of the GNU Lesser General Public
License as published by the Free Software Foundation; either
version 2.1 of the License, or (at your option) any later version.

This library is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
Lesser General Public License for more details.

You should have received a copy of the GNU Lesser General Public
License along with this library; if not, write to the Free Software
Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA
"""

import sqlliterals.common
from pyparsing import *

try:
    ParserElement.enablePackrat()
except AttributeError:
    pass

# Classes and functions.

class Grammar:

    "A convenience class whose objects enforce the naming of grammar rules."

    def __setattr__(self, name, value):
        self.__dict__[name] = value.setResultsName(name)

# NOTE: Sufficient grouping seems to be provided by pyparsing.
# NOTE: Otherwise, we might introduce Group objects in the above class.

g = grammar = Grammar()

g.non_literal = Combine(OneOrMore(CharsNotIn("'")))
g.value = ZeroOrMore(Or([Literal("''"), CharsNotIn("'")]))
g.literal = Combine(Literal("'") + g.value + Literal("'"))
g.query = ZeroOrMore(Or([g.non_literal, g.literal]))
g.query.leaveWhitespace()

def parseString(s):

    "Return a pyparsing result object from the parsing of the string 's'."

    regions = []
    first = 1
    for region in g.query.parseString(s).asList():
        if isinstance(region, list):
            if first:
                regions.append("")
            regions.append(region[0])
        else:
            regions.append(region)
        first = 0
    return regions

# NOTE: Duplicated across implementations.

def replace(fromstyle, tostyle, s):

    """
    Return a new string, where the paramstyle 'fromstyle' is
    replaced with 'tostyle' in the appropriate regions of 's'.
    """

    regions = parseString(s)
    return "".join(sqlliterals.common.replace(fromstyle, tostyle, regions))

# vim: tabstop=4 expandtab shiftwidth=4
