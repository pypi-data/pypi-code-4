#!/usr/bin/env python
"""
Module PYSIDECOMBO -- Python PySide Combo Box Widgets
Sub-Package GUI.TOOLKITS.PYSIDE of Package PLIB -- Python GUI Toolkits
Copyright (C) 2008-2013 by Peter A. Donis

Released under the GNU General Public License, Version 2
See the LICENSE and README files for more information

This module contains the PySide GUI objects for combo boxes.
"""

from PySide import QtGui as qt

from plib.gui._widgets import combo

from _pysidecommon import _PQtSequenceMeta, _PQtWidget


class PQtComboBox(_PQtWidget, qt.QComboBox, combo.PComboBoxBase):
    
    __metaclass__ = _PQtSequenceMeta
    
    def __init__(self, parent, sequence=None, target=None, geometry=None):
        qt.QComboBox.__init__(self, parent)
        self.setSizePolicy(qt.QSizePolicy.Fixed, qt.QSizePolicy.Fixed)
        combo.PComboBoxBase.__init__(self, sequence, target, geometry)
    
    def set_width(self, width):
        self.resize(width, self.height())
        # Qt buttons don't appear to fully respect QSizePolicy.Fixed
        self.setMinimumWidth(width)
    
    def current_text(self):
        return str(self.currentText())
    
    # Note that there's no quick override for set_current_text in Qt; the
    # corresponding method to the above doesn't do what we want (it changes
    # the stored text in the combo instead of selecting the text we give it)
    
    def current_index(self):
        return self.currentIndex()
    
    def set_current_index(self, index):
        self.setCurrentIndex(index)
    
    def count(self, value):
        # Method name collision, we want it to be the Python sequence
        # count method here.
        return combo.PComboBoxBase.count(self, value)
    
    def _indexlen(self):
        # Let this method access the Qt combo box count method.
        return qt.QComboBox.count(self)
    
    def _get_data(self, index):
        return str(self.itemText(index))
    
    def _set_data(self, index, value):
        self.setItemText(index, str(value))
    
    def _add_data(self, index, value):
        self.insertItem(index, str(value))
    
    def _del_data(self, index):
        self.removeItem(index)
