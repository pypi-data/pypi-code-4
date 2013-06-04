#!/usr/bin/env python
"""
Module KDETABWIDGET -- Python KDE Tab Widget
Sub-Package GUI.TOOLKITS.KDE of Package PLIB -- Python GUI Toolkits
Copyright (C) 2008-2013 by Peter A. Donis

Released under the GNU General Public License, Version 2
See the LICENSE and README files for more information

This module contains the KDE GUI objects for the tab widget.
"""

import kdeui

from plib.gui.defs import *
from plib.gui._widgets import tabwidget

from _kdecommon import _PKDEMeta, _PKDEClientWidget


class PKDETabWidget(_PKDEClientWidget, kdeui.KTabWidget,
                    tabwidget.PTabWidgetBase):
    
    __metaclass__ = _PKDEMeta
    
    widget_class = kdeui.KTabWidget
    
    def __init__(self, parent, tabs=None, target=None):
        self._target = None
        self._setting_index = False
        kdeui.KTabWidget.__init__(self, parent)
        tabwidget.PTabWidgetBase.__init__(self, parent, tabs, target)
        
        # Re-interpret tab changed event to send index instead of widget
        self.setup_notify(SIGNAL_TABCURRENTCHANGED, self._tab_currentchanged)
    
    def _tab_currentchanged(self, item):
        self.do_notify(SIGNAL_TABCHANGED, self.index((self.tabLabel(item), item)))
    
    def count(self, value):
        # Method name collision, we want it to be the Python sequence
        # count method here
        return tabwidget.PTabWidgetBase.count(self, value)
    
    def __len__(self):
        # Let this method access the KDE tab widget count method
        return kdeui.KTabWidget.count(self)
    
    def _get_tabtitle(self, index):
        return str(self.tabLabel(self._items[index]))
    
    def _set_tabtitle(self, index, title):
        self.setTabLabel(self._items[index], str(title))
    
    def _add_tab(self, index, title, widget):
        self.insertTab(widget, str(title), index)
    
    def _del_tab(self, index):
        self.removePage(self._items[index])
    
    def current_index(self):
        return self.currentPageIndex()
    
    def _current_changed(self, index):
        # Wrapper for tab changed signal.
        if (not self._setting_index) and self._target:
            self._target(index)
    
    def connect_to(self, target):
        # Hack to capture double firing of tab changed signal when
        # tab is changed programmatically instead of by user.
        self._target = target
        tabwidget.PTabWidgetBase.connect_to(self, self._current_changed)
    
    def set_current_index(self, index):
        # Wrap the call to avoid double calling of signal handler, then
        # make the call by hand.
        self._setting_index = True
        self.setCurrentPage(index)
        self._setting_index = False
        self._current_changed(index)
