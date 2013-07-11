#!/usr/bin/env python3
"""
Module CLASSES -- Common GUI Classes
Sub-Package GUI of Package PLIB3 -- Python GUI Framework
Copyright (C) 2008-2013 by Peter A. Donis

Released under the GNU General Public License, Version 2
See the LICENSE and README files for more information

Defines common classes that can be used with GUI objects.
The following classes are included:

- PTextFile: a convenience wrapper that makes a text
  control look like a file object.
"""


class PTextFile(object):
    """ File-like object to redirect output to text control.
    
    Note that 'file-like' is used very loosely; this object only
    implements the minimum necessary to make a PTextDisplay
    look like a bare bones file-like object. In particular,
    iterator functionality is *not* implemented.
    """
    
    def __init__(self, control):
        self.control = control  # should normally be a PTextDisplay
    
    def close(self):
        pass  # nothing to do here
    
    def truncate(self, size=None):
        if size is None:
            raise IOError("Must specify a size to truncate to (usually 0).")
        if size == 0:
            s = ""
        else:
            s = self.control.get_text()[:size]
        self.control.set_text(s)
        self.flush()
    
    def read(self):
        return self.control.get_text()
    
    def write(self, data):
        data = "".join([self.control.get_text(), data])
        self.control.set_text(data)
    
    def flush(self):
        self.control.update_widget()
