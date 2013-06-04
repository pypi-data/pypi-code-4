#!/usr/bin/env python
"""
Module PYSIDECOMMON -- Python PySide Common Objects
Sub-Package GUI.TOOLKITS.PYSIDE of Package PLIB -- Python GUI Toolkits
Copyright (C) 2008-2013 by Peter A. Donis

Released under the GNU General Public License, Version 2
See the LICENSE and README files for more information

This module contains common PySide GUI objects for use by the other
PySide modules.
"""

from abc import ABCMeta
from itertools import chain

from PySide import QtGui as qt, QtCore as qtc

from plib.gui.defs import *

_qtalignmap = {
    ALIGN_LEFT: qtc.Qt.AlignLeft | qtc.Qt.AlignVCenter,
    ALIGN_CENTER: qtc.Qt.AlignCenter,
    ALIGN_RIGHT: qtc.Qt.AlignRight | qtc.Qt.AlignVCenter
}

_qtcolormap = dict(
    (color, qt.QColor(color.lower()))
    for color in COLORNAMES
)

_qtmessagefuncs = {
    MBOX_INFO: qt.QMessageBox.information,
    MBOX_WARN: qt.QMessageBox.warning,
    MBOX_ERROR: qt.QMessageBox.critical,
    MBOX_QUERY: qt.QMessageBox.question
}

_qtsignalmap = {
    SIGNAL_ACTIVATED: "triggered",
    SIGNAL_CLICKED: "clicked",
    SIGNAL_TOGGLED: "toggled",
    SIGNAL_SELECTED: "activated",
    SIGNAL_LISTSELECTED: "currentItemChanged",
    SIGNAL_CELLSELECTED: "currentCellChanged",
    SIGNAL_TABLECHANGED: "cellChanged",
    SIGNAL_TEXTCHANGED: "textChanged",  # textEdited()?
    SIGNAL_EDITCHANGED: "textChanged",  # textEdited(const QString&)?
    SIGNAL_ENTER: "returnPressed",
    SIGNAL_TABCHANGED: "currentChanged",
    SIGNAL_NOTIFIER: "activated",
    SIGNAL_BEFOREQUIT: "aboutToQuit"
}

_qteventmap = {
    SIGNAL_CELLCHANGED: ("sig_cellChanged", (int, int)),
    SIGNAL_TEXTSTATECHANGED: ("sig_textStateChanged", ()),
    SIGNAL_FOCUS_IN: ("sig_focusInEvent", ()),
    SIGNAL_FOCUS_OUT: ("sig_focusOutEvent", ()),
    SIGNAL_CLOSING: ("sig_closeEvent", ()),
    SIGNAL_SHOWN: ("sig_showEvent", ()),
    SIGNAL_HIDDEN: ("sig_hideEvent", ())
}


def _qtmap(signal):
    if signal in _qtsignalmap:
        return _qtsignalmap[signal]
    elif signal in _qteventmap:
        return _qteventmap[signal][0]
    else:
        return None


# Ugly hacks to fix metaclass conflict for classes that use the collection
# ABCs, and to allow auto-construction of event signals without a lot of
# boilerplate code in each widget class

_QtMeta = type(qtc.QObject)


def _setup_signals(bases, attrs):
    for signal in chain(
        attrs.get('event_signals', ()),
        *(getattr(base, 'event_signals', ()) for base in bases)
    ):
        signame, args = _qteventmap.get(signal)
        if signame:
            attrs[signame] = qtc.Signal(*args, name=signame)


class _PQtWidgetMeta(_QtMeta):
    # Metaclass for non-sequence widgets
    
    def __new__(meta, name, bases, attrs):
        _setup_signals(bases, attrs)
        return super(_PQtWidgetMeta, meta).__new__(meta, name, bases, attrs)


class _PQtSequenceMeta(ABCMeta, _QtMeta):
    # Metaclass for sequence widgets
    
    def __new__(meta, name, bases, attrs):
        _setup_signals(bases, attrs)
        return super(_PQtSequenceMeta, meta).__new__(meta, name, bases, attrs)
    
    def __init__(cls, name, bases, attrs):
        _QtMeta.__init__(cls, name, bases, attrs)
        ABCMeta.__init__(cls, name, bases, attrs)


class _PQtCommunicator(object):
    """Mixin class to abstract signal/slot functionality in Qt.
    """
    
    def setup_notify(self, signal, target):
        sig = _qtmap(signal)
        if sig is not None:
            try:
                getattr(self, sig).connect(target)
            except AttributeError:
                pass
    
    def do_notify(self, signal, *args):
        sig = _qtmap(signal)
        if sig is not None:
            try:
                getattr(self, sig).emit(*args)
            except AttributeError:
                pass
    
    _emit_event = do_notify


class _PQtWidgetBase(object):
    """Mixin class to provide common Qt widget methods.
    """
    
    fn_enable_get = 'isEnabled'
    fn_enable_set = 'setEnabled'
    
    _palette = None
    
    def update_widget(self):
        self.update()
    
    def preferred_width(self):
        return max(self.minimumSize().width(), self.sizeHint().width())
    
    def preferred_height(self):
        return max(self.minimumSize().height(), self.sizeHint().height())
    
    def set_width(self, width):
        self.resize(width, self.height())
    
    def set_height(self, height):
        self.resize(self.width(), height)
    
    def set_position(self, left, top):
        if not (None in (left, top)):
            self.move(left, top)
    
    def _mapped_color(self, color):
        if isinstance(color, qt.QColor):
            return color
        return _qtcolormap[color]
    
    def set_colors(self, fg=None, bg=None):
        palette = qt.QPalette(self.palette())
        if fg is not None:
            palette.setColor(self.foregroundRole(), self._mapped_color(fg))
        if bg is not None:
            self.setAutoFillBackground(True)
            palette.setColor(self.backgroundRole(), self._mapped_color(bg))
        self.setPalette(palette)
    
    def set_foreground_color(self, color):
        self.set_colors(fg=color)
    
    def set_background_color(self, color):
        self.set_colors(bg=color)
    
    def get_font_name(self):
        return self.font().family()
    
    def get_font_size(self):
        return self.font().pointSize()
    
    def get_font_bold(self):
        return self.font().bold()
    
    def get_font_italic(self):
        return self.font().italic()
    
    def _qt_font_object(self, font_name, font_size, bold, italic):
        font = qt.QFont(font_name, font_size)
        font.setBold(bold)
        font.setItalic(italic)
        return font
    
    def _set_font_object(self, font_name, font_size, bold, italic):
        self.setFont(self._qt_font_object(
            font_name, font_size, bold, italic))
    
    def set_focus(self):
        self.setFocus()


class _PQtWidget(_PQtCommunicator, _PQtWidgetBase):
    """Mixin class for Qt widgets that can send/receive signals.
    """
    
    event_signals = (SIGNAL_FOCUS_IN, SIGNAL_FOCUS_OUT)
    
    def focusInEvent(self, event):
        super(_PQtWidget, self).focusInEvent(event)
        self._emit_event(SIGNAL_FOCUS_IN)
    
    def focusOutEvent(self, event):
        super(_PQtWidget, self).focusOutEvent(event)
        self._emit_event(SIGNAL_FOCUS_OUT)


class _PQtClientWidget(_PQtWidget):
    """Mixin class for Qt main window client widgets.
    """
    pass
