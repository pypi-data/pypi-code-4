#!/usr/bin/env python
"""
Module QTMAINWIN -- Python Qt Main Window Objects
Sub-Package GUI.TOOLKITS.QT of Package PLIB -- Python GUI Toolkits
Copyright (C) 2008-2013 by Peter A. Donis

Released under the GNU General Public License, Version 2
See the LICENSE and README files for more information

This module contains the Qt GUI main window objects.
"""

import qt

from plib.gui.defs import *
from plib.gui._base import mainwin

from ._qtapp import _PQtMainMixin
from ._qtaction import PQtMenu, PQtToolBar, PQtAction
from ._qtstatusbar import PQtStatusBar


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
        self.setUsesBigPixmaps(self.large_icons)
        self.setUsesTextLabel(self.show_labels)  # text still displays in tooltips
        self.abouttoolkitfunc = self.app.aboutQt
        self.setCentralWidget(self.clientwidget)
        if self.toolbar is not None:
            vmajor = qt.qVersion()[0]
            if vmajor == "2":
                self.setToolBarsMovable(False)
            elif vmajor == "3":
                self.setDockWindowsMovable(False)
            self.setDockMenuEnabled(False)
    
    def show_init(self):
        mainwin.PMainWindowBase.show_init(self)
        _PQtMainMixin.show_init(self)
