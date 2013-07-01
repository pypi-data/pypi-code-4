#!/usr/bin/env python3
"""
Module PYSIDEBUTTON -- Python PySide Button Widgets
Sub-Package GUI.TOOLKITS.PYSIDE of Package PLIB3 -- Python GUI Toolkits
Copyright (C) 2008-2013 by Peter A. Donis

Released under the GNU General Public License, Version 2
See the LICENSE and README files for more information

This module contains the PySide GUI objects for button widgets.
"""

from PySide import QtGui as qt

from plib.gui._widgets import button

from ._pysidecommon import _PQtWidgetMeta, _PQtWidget


class _PQtButtonMixin(object):
    
    def set_caption(self, caption):
        self.setText(caption)


class PQtButton(_PQtButtonMixin, _PQtWidget, qt.QPushButton,
                button.PButtonBase, metaclass=_PQtWidgetMeta):
    
    def __init__(self, parent, caption=None, pxname=None,
                 target=None, geometry=None):
        
        qt.QPushButton.__init__(self, parent)
        self.setSizePolicy(qt.QSizePolicy.Fixed, qt.QSizePolicy.Fixed)
        button.PButtonBase.__init__(self, caption, pxname, target, geometry)
    
    def set_icon(self, pxname):
        self.setIcon(qt.QIcon(qt.QPixmap(pxname)))
    
    def set_width(self, width):
        self.resize(width, self.height())
        # Qt buttons don't appear to fully respect QSizePolicy.Fixed
        self.setMinimumWidth(width)


class PQtCheckBox(_PQtButtonMixin, _PQtWidget, qt.QCheckBox,
                  button.PCheckBoxBase, metaclass=_PQtWidgetMeta):
    
    fn_get_checked = 'isChecked'
    fn_set_checked = 'setChecked'
    
    def __init__(self, parent, caption=None, pxname=None, tristate=False,
                 target=None, geometry=None):
        
        qt.QCheckBox.__init__(self, parent)
        self.setSizePolicy(qt.QSizePolicy.Fixed, qt.QSizePolicy.Fixed)
        button.PCheckBoxBase.__init__(self, caption, pxname, tristate,
                                      target, geometry)
    
    def set_icon(self, pxname):
        # FIXME: pixmaps on checkboxes?
        pass
    
    def make_tristate(self):
        self.setTriState(True)
