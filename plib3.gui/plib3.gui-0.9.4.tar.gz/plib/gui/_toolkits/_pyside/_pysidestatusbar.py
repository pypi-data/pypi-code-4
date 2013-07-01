#!/usr/bin/env python3
"""
Module PYSIDESTATUSBAR -- Python PySide Status Bar Objects
Sub-Package GUI.TOOLKITS.PYSIDE of Package PLIB3 -- Python GUI Toolkits
Copyright (C) 2008-2013 by Peter A. Donis

Released under the GNU General Public License, Version 2
See the LICENSE and README files for more information

This module contains the PySide GUI objects for the status bar.
"""

from PySide import QtGui as qt

from plib.gui._base import statusbar

from ._pysidecommon import _PQtWidgetBase
from ._pysidelabel import PQtTextLabel


class PQtStatusBar(_PQtWidgetBase, qt.QStatusBar, statusbar.PStatusBarBase):
    
    textareaclass = PQtTextLabel
    
    def __init__(self, parent, widgets=None):
        qt.QStatusBar.__init__(self, parent)
        statusbar.PStatusBarBase.__init__(self, parent, widgets)
        parent.setStatusBar(self)
    
    def _add_widget(self, widget, expand=False, custom=True):
        if custom:
            self.addPermanentWidget(widget, int(expand))
        else:
            self.addWidget(widget, int(expand))
