#!/usr/bin/env python
"""
Module QT4MAINWIN -- Python Qt 4 Main Window Objects
Sub-Package GUI.TOOLKITS.QT4 of Package PLIB -- Python GUI Toolkits
Copyright (C) 2008-2013 by Peter A. Donis

Released under the GNU General Public License, Version 2
See the LICENSE and README files for more information

This module contains the Qt 4 GUI main window objects.
"""

from plib.gui.defs import *
from plib.gui._base import mainwin

from _qt4app import _PQtMainMixin
from _qt4action import PQtMenu, PQtToolBar, PQtAction
from _qt4statusbar import PQtStatusBar


class PQtMainWindow(_PQtMainMixin, mainwin.PMainWindowBase):
    """Customized Qt main window class.
    """
    
    menuclass = PQtMenu
    toolbarclass = PQtToolBar
    statusbarclass = PQtStatusBar
    actionclass = PQtAction
    
    def __init__(self, parent, cls=None):
        _PQtMainMixin.__init__(self)
        mainwin.PMainWindowBase.__init__(self, parent, cls)
        self.abouttoolkitfunc = self.app.aboutQt
        self.setCentralWidget(self.clientwidget)
    
    def show_init(self):
        mainwin.PMainWindowBase.show_init(self)
        _PQtMainMixin.show_init(self)
