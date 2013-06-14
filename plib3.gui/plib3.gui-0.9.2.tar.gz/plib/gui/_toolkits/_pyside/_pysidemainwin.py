#!/usr/bin/env python3
"""
Module PYSIDEMAINWIN -- Python PySide Main Window Objects
Sub-Package GUI.TOOLKITS.PYSIDE of Package PLIB3 -- Python GUI Toolkits
Copyright (C) 2008-2013 by Peter A. Donis

Released under the GNU General Public License, Version 2
See the LICENSE and README files for more information

This module contains the PySide GUI main window objects.
"""

from plib.gui.defs import *
from plib.gui._base import mainwin

from ._pysidecommon import _PQtWidgetMeta
from ._pysideapp import _PQtMainMixin
from ._pysideaction import PQtMenu, PQtToolBar, PQtAction
from ._pysidestatusbar import PQtStatusBar


class PQtMainWindow(_PQtMainMixin, mainwin.PMainWindowBase, metaclass=_PQtWidgetMeta):
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
