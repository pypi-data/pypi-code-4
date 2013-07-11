#!/usr/bin/env python3
"""
Module PYSIDELABEL -- Python PySide Text Label Widgets
Sub-Package GUI.TOOLKITS.PYSIDE of Package PLIB3 -- Python GUI Toolkits
Copyright (C) 2008-2013 by Peter A. Donis

Released under the GNU General Public License, Version 2
See the LICENSE and README files for more information

This module contains the PySide GUI objects for text label widgets.
"""

from PySide import QtGui as qt

from plib.gui._widgets import label

from ._pysidecommon import _PQtWidgetMeta, _PQtWidget


class PQtTextLabel(_PQtWidget, qt.QLabel, label.PTextLabelBase, metaclass=_PQtWidgetMeta):
    
    def __init__(self, parent, text=None, geometry=None):
        qt.QLabel.__init__(self, parent)
        label.PTextLabelBase.__init__(self, text, geometry)
    
    def get_text(self):
        return str(self.text())
    
    def set_text(self, value):
        self.setText(value)
    
    def set_width(self, width):
        self.resize(width, self.height())
        # Qt text labels don't seem to fully respect
        # qt.QSizePolicy.MinimumExpanding
        self.setMinimumWidth(width)
