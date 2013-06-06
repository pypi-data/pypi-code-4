#!/usr/bin/env python
"""
Module WXMAINWIN -- Python wxWidgets Main Window Objects
Sub-Package GUI.TOOLKITS.WX of Package PLIB -- Python GUI Toolkits
Copyright (C) 2008-2013 by Peter A. Donis

Released under the GNU General Public License, Version 2
See the LICENSE and README files for more information

This module contains the wxWidgets GUI main window objects.
"""

from plib.gui.defs import *
from plib.gui._base import mainwin

from _wxapp import _PWxMainMixin
from _wxaction import PWxMenu, PWxToolBar, PWxAction
from _wxstatusbar import PWxStatusBar


class PWxMainWindow(_PWxMainMixin, mainwin.PMainWindowBase):
    """Customized wxWidgets main window class.
    """
    
    menuclass = PWxMenu
    toolbarclass = PWxToolBar
    statusbarclass = PWxStatusBar
    actionclass = PWxAction
    
    def __init__(self, parent, cls=None):
        _PWxMainMixin.__init__(self, None)
        mainwin.PMainWindowBase.__init__(self, parent, cls)
        if self.menu is not None:
            self.SetMenuBar(self.menu)
        if self.toolbar is not None:
            self.SetToolBar(self.toolbar)
        if self.statusbar is not None:
            self.SetStatusBar(self.statusbar)
        self._setup_events()
    
    def show_init(self):
        mainwin.PMainWindowBase.show_init(self)
        _PWxMainMixin.show_init(self)
