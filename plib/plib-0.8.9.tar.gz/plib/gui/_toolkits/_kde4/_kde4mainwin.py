#!/usr/bin/env python
"""
Module KDE4MAINWIN -- Python KDE Main Window Objects
Sub-Package GUI.TOOLKITS.KDE of Package PLIB -- Python GUI Toolkits
Copyright (C) 2008-2013 by Peter A. Donis

Released under the GNU General Public License, Version 2
See the LICENSE and README files for more information

This module contains the KDE 4 GUI main window objects.
"""

from PyQt4 import Qt as qt
from PyKDE4 import kdeui

from plib.gui.defs import *
from plib.gui._base import mainwin

from _kde4common import _kdestandardactions
from _kde4app import _PKDEMainMixin
from _kde4action import PKDEMenu, PKDEToolBar, PKDEAction
from _kde4statusbar import PKDEStatusBar


class PKDEMainWindow(_PKDEMainMixin, mainwin.PMainWindowBase):
    """Customized KDE main window class.
    """
    
    menuclass = PKDEMenu
    toolbarclass = PKDEToolBar
    statusbarclass = PKDEStatusBar
    actionclass = PKDEAction
    
    def __init__(self, parent, cls=None):
        _PKDEMainMixin.__init__(self)
        mainwin.PMainWindowBase.__init__(self, parent, cls)
        self.setCentralWidget(self.clientwidget)
    
    def actionCollection(self):
        if not hasattr(self, '_actionCollection'):
            self._actionCollection = kdeui.KActionCollection(self)
        return self._actionCollection
    
    def _create_action(self, key):
        if key in _kdestandardactions:
            result = _kdestandardactions[key](self, qt.SLOT("show()"),
                                              self.actionCollection())
            result.__class__ = self.actionclass
            result.init_setup(key, self)
        else:
            result = mainwin.PMainWindowBase._create_action(self, key)
        # We have to do these by hand here because the KStandardAction
        # mechanism doesn't seem to do them right
        if key == ACTION_PREFS:
            txt = "&Configure %s..." % self.aboutdata['name']
            result.setText(qt.QString(txt))
            result.setToolTip(qt.QString(txt.replace('&', '').strip('.')))
        elif (key == ACTION_ABOUT) and ('icon' in self.aboutdata):
            result.setIcon(kdeui.KIcon(qt.QIcon(qt.QPixmap(
                self.aboutdata['icon']))))
        return result
    
    def show_init(self):
        mainwin.PMainWindowBase.show_init(self)
        _PKDEMainMixin.show_init(self)
