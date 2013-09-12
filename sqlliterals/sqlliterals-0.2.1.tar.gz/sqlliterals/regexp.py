#!/usr/bin/env python

"""
A regular expression implementation of SQL statement tokenisation.

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
import re

region_expr = re.compile("(?P<non_literal>[^']+)|(?P<literal>'(?:[^']|(?:''))*')")

def parseString(s):

    """
    Parse the string 's' and return a list of regions, with the first element
    being a non-literal region, the next element being a literal region, and
    with subsequent elements repeating this pattern. Note that the first region
    may be an empty string.
    """

    regions = []
    first = 1
    for match in region_expr.finditer(s):
        non_literal, literal = match.groups()
        if first and literal:
            regions.append("")
        if non_literal:
            regions.append(non_literal)
        elif literal:
            regions.append(literal)
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
