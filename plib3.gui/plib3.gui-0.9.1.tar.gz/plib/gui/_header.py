#!/usr/bin/env python3
"""
Module HEADER -- Table/List Header Classes
Sub-Package GUI of Package PLIB3 -- Python GUI Framework
Copyright (C) 2008-2013 by Peter A. Donis

Released under the GNU General Public License, Version 2
See the LICENSE and README files for more information

Defines header classes for tables and list views. The
following classes are defined:

- PHeaderLabel: a label for the header of a table or
  list/treeview widget.
"""

from plib.gui.defs import *


class PHeaderLabel(object):
    """Encapsulates a header label for a table or list/tree view.
    """
    
    def __init__(self, text, width=-1, align=ALIGN_LEFT, readonly=False):
        self.text = text
        self.width = width
        self.align = align
        self.readonly = readonly
    
    def __str__(self):
        return self.text
