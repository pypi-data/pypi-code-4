#!/usr/bin/env python3
"""
Module QT4STATUSBAR -- Python Qt 4 Status Bar Objects
Sub-Package GUI.TOOLKITS.QT4 of Package PLIB3 -- Python GUI Toolkits
Copyright (C) 2008-2013 by Peter A. Donis

Released under the GNU General Public License, Version 2
See the LICENSE and README files for more information

This module contains the Qt 4 GUI objects for the status bar.
"""

from PyQt4 import Qt as qt

from plib.gui._base import statusbar

from ._qt4common import _PQtWidgetBase
from ._qt4label import PQtTextLabel


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
