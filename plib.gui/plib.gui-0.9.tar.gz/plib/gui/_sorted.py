#!/usr/bin/env python
"""
Module SORTED -- Sorted Sequence-Type Widgets for GUI
Sub-Package GUI of Package PLIB -- Python GUI Framework
Copyright (C) 2008-2013 by Peter A. Donis

Released under the GNU General Public License, Version 2
See the LICENSE and README files for more information

Implements customized ``SortMixin`` classes for GUI widgets
that provide correct widget constructor signatures and extract
SortMixin arguments so that everything can be passed through
and set up correctly.
"""

from plib.gui import main as gui

from plib.stdlib.coll import SortMixin


class ComboBoxSortMixin(SortMixin):
    """Customized mixin class for sorted combo box.
    """
    
    def __init__(self, parent, sequence=None, target=None, geometry=None, key=None):
        super(ComboBoxSortMixin, self).__init__(parent, target=target, geometry=geometry)
        self._init_seq(sequence, key)


class _ListSortMixin(SortMixin):
    # List view/list box keys are handled in a special way; we interpret
    # the key parameter as the function to apply to each column separately,
    # so we have to adjust it before using it
    
    def _init_key(self, key):
        # Construct key function that applies given key to each list column;
        # assume that our constructed function will be called on each item
        # in a sequence of (cols, children) tuples
        return (
            (lambda x: tuple(x[0])) if key is None else
            (lambda x: tuple(key(c) for c in x[0]))
        )


class ListViewItemSortMixin(_ListSortMixin):
    """Customized mixin class for sorted list view item.
    """
    
    def __init__(self, parent, index, data=None):
        # The data is a tuple (cols, children), we have to separate it
        # out so the inherited constructor initializes the cols but we
        # initialize the children
        if data is not None:
            cols, children = data
            data = (cols, [])
        else:
            children = None
        super(ListViewItemSortMixin, self).__init__(parent, index, data)
        self._init_seq(children, self.listview._given_key)


class ListViewSortMixin(_ListSortMixin):
    """Customized mixin class for sorted list view.
    """
    
    itemclass = gui.PSortedListViewItem
    
    def __init__(self, parent, labels=None, data=None, target=None, key=None):
        super(ListViewSortMixin, self).__init__(parent, labels=labels, target=target)
        self._init_seq(data, key)


class ListBoxSortMixin(_ListSortMixin):
    """Customized mixin class for sorted list box.
    """
    
    itemclass = gui.PSortedListViewItem
    
    def __init__(self, parent, labels=None, data=None, target=None, geometry=None, key=None):
        super(ListBoxSortMixin, self).__init__(parent, labels=labels, target=target, geometry=geometry)
        self._init_seq(data, key)
