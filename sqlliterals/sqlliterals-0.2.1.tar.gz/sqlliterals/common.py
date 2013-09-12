#!/usr/bin/env python

"""
Convert one paramstyle to another in SQL statements.

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

def replace(fromstyle, tostyle, regions):

    """
    Return a new sequence of regions, where the paramstyle 'fromstyle' is
    replaced with 'tostyle' in the appropriate elements of 'regions'.
    """ 

    new_regions = []
    non_literal = 1
    for region in regions:
        if non_literal:
            new_regions.append(region.replace(fromstyle, tostyle))
        else:
            new_regions.append(region)
        non_literal = not non_literal
    return new_regions

# vim: tabstop=4 expandtab shiftwidth=4
