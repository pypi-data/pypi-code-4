#!/usr/bin/env python
"""
Module PYSIDEACTION -- Python PySide Action Objects
Sub-Package GUI.TOOLKITS.PYSIDE of Package PLIB -- Python GUI Toolkits
Copyright (C) 2008-2013 by Peter A. Donis

Released under the GNU General Public License, Version 2
See the LICENSE and README files for more information

This module contains the PySide GUI objects for handling user actions.
"""

from PySide import QtGui as qt, QtCore as qtc

from plib.gui._base import action
from plib.gui.defs import *

from _pysidecommon import _PQtCommunicator, _PQtWidgetBase


class PQtMenu(_PQtWidgetBase, qt.QMenuBar, action.PMenuBase):
    """Customized Qt menu class.
    """
    
    popupclass = qt.QMenu
    
    def __init__(self, mainwidget):
        qt.QMenuBar.__init__(self, mainwidget)
        action.PMenuBase.__init__(self, mainwidget)
        mainwidget.setMenuBar(self)
    
    def _add_popup(self, title, popup):
        popup.setTitle(title)
        self.addMenu(popup)
    
    def _add_popup_action(self, act, popup):
        popup.addAction(act)


class PQtToolBar(_PQtWidgetBase, qt.QToolBar, action.PToolBarBase):
    """Customized Qt toolbar class.
    """
    
    def __init__(self, mainwidget):
        qt.QToolBar.__init__(self, mainwidget)
        if mainwidget.large_icons:
            sz = self.iconSize()
            w, h = map(lambda i: i * 3 / 2, (sz.width(), sz.height()))
            self.setIconSize(qtc.QSize(w, h))
        if mainwidget.show_labels:
            style = qtc.Qt.ToolButtonTextUnderIcon
        else:
            style = qtc.Qt.ToolButtonIconOnly
        self.setToolButtonStyle(style)
        action.PToolBarBase.__init__(self, mainwidget)
        mainwidget.addToolBar(self)
    
    def add_action(self, act):
        self.addAction(act)
    
    def add_separator(self):
        self.addSeparator()


class PQtAction(_PQtCommunicator, qt.QAction, action.PActionBase):
    """Customized Qt action class.
    """
    
    def __init__(self, key, mainwidget):
        qt.QAction.__init__(self, mainwidget)
        self.setIcon(qt.QIcon(qt.QPixmap(self.get_icon_filename(key))))
        self.setText(self.get_menu_str(key))
        self.setToolTip(self.get_toolbar_str(key))
        s = self.get_accel_str(key)
        if s is not None:
            self.setShortcut(qt.QKeySequence(s))
        action.PActionBase.__init__(self, key, mainwidget)
    
    def enable(self, enabled):
        self.setEnabled(enabled)
