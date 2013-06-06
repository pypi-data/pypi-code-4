#!/usr/bin/env python
"""
GUI-SIGNALS.PY
Copyright (C) 2008-2013 by Peter A. Donis

Released under the GNU General Public License, Version 2
See the LICENSE and README files for more information

A demo app that tests all of the available GUI signals.
"""

import sys
import os
from functools import partial

from plib.gui import __version__
from plib.gui import main as gui
from plib.gui.defs import *
from plib.gui.specs import *


number_strings = ("One", "Two", "Three")


class GUISignalTester(gui.PMainPanel):
    
    aboutdata = {
        'name': "GUISignalTester",
        'version': "%s on Python %s" % (
            __version__,
            sys.version.split()[0]
        ),
        'copyright': "Copyright (C) 2008-2013 by Peter A. Donis",
        'license': "GNU General Public License (GPL) Version 2",
        'description': "GUI Signal Test Demo",
        'developers': ["Peter Donis"],
        'website': "http://www.peterdonis.net"
    }
    
    maintitle = "GUI Signal Tester"
    
    layout = LAYOUT_HORIZONTAL
    placement = (SIZE_CLIENTWRAP, MOVE_CENTER)
    
    actionflags = [
        ACTION_EXIT, ACTION_OK, ACTION_ABOUT, ACTION_ABOUTTOOLKIT
    ]
    
    menuclass = None
    
    childlist = [
        toplevel_panel(ALIGN_JUST, LAYOUT_VERTICAL, 'controls', [
            tabwidget('panels', [
                ('Dialog', tab_panel(ALIGN_JUST, LAYOUT_VERTICAL, 'dialog', [
                    button("Test Clicked", 'action'),
                    checkbox("Test Toggled", 'option'),
                    combobox('selection', (numstr.lower() for numstr in number_strings)),
                    editbox('text')
                ])),
                ('Memo', tab_panel(ALIGN_JUST, LAYOUT_VERTICAL, 'memo', [
                    memo('notes')
                ])),
                ('List', tab_panel(ALIGN_JUST, LAYOUT_VERTICAL, 'list', [
                    listbox('items', [("Items", -1)])
                ])),
                ('Table', tab_panel(ALIGN_JUST, LAYOUT_VERTICAL, 'table', [
                    table('cells', [("Title", 200), ("Description", -1)])
                ])),
            ]),
        ]),
        toplevel_panel(ALIGN_JUST, LAYOUT_VERTICAL, 'output', [
            textcontrol('output')
        ])
    ]
    
    def _createpanels(self):
        super(GUISignalTester, self)._createpanels()
        self.outputfile = gui.PTextFile(self.text_output)
        self._setup_signals()
        self._init_widgets()
    
    def _setup_signals(self):
        # No automatic setup for this signal
        self.edit_text.setup_notify(SIGNAL_ENTER, self.enter)
        # None for this one either
        self.table_cells.setup_notify(SIGNAL_CELLSELECTED, self.cells_selected)
        # These are seldom used but we test them here
        self._parent.setup_notify(SIGNAL_CLOSING, self.closing)
        self._parent.setup_notify(SIGNAL_SHOWN, self.shown)
        self._parent.setup_notify(SIGNAL_HIDDEN, self.hidden)
        # These can be used on a variety of controls
        for widget_name in (
            'edit_text',
            'memo_notes'
        ):
            widget = getattr(self, widget_name)
            widget.setup_notify(SIGNAL_FOCUS_IN, partial(self.focus_in, widget=widget_name))
            widget.setup_notify(SIGNAL_FOCUS_OUT, partial(self.focus_out, widget=widget_name))
        # This is normally used by a text editor to enable/disable actions
        self.memo_notes.setup_notify(SIGNAL_TEXTSTATECHANGED, self.notes_statechanged)
        # Tab widget doesn't auto-target by default
        self.tabs_panels.setup_notify(SIGNAL_TABCHANGED, self.panels_changed)
        # This action doesn't auto-connect (the others do with a main window)
        self._parent.connectaction(ACTION_OK, self.ok)
    
    def _init_widgets(self):
        # List boxes don't take an item list in their spec
        self.listbox_items.extend_list(
            "Item %s" % numstr for numstr in number_strings
        )
        # Tables don't either
        self.table_cells.extend(
            ("Row %s" % numstr, "Table row number %s" % numstr.lower())
            for numstr in number_strings
        )
    
    def _output_message(self, message):
        print message
        self.outputfile.write("%s%s" % (message, os.linesep))
        self.outputfile.flush()
    
    def ok(self):
        self._output_message("SIGNAL_ACTIVATED ACTION_OK")
    
    def panels_changed(self, index):
        # FIXME: this assertion fails in Qt/KDE 3
        #assert self.tabs_panels.current_index() == index
        self._output_message("SIGNAL_TABCHANGED %s %s" % (
            index, self.tabs_panels[index][0]))
    
    def action(self):
        self._output_message("SIGNAL_CLICKED")
    
    def option_toggled(self, checked):
        assert checked == self.checkbox_option.checked
        self._output_message("SIGNAL_TOGGLED %s" % ('off', 'on')[checked])
    
    def selection_selected(self, index):
        assert self.combo_selection.current_index() == index
        assert self.combo_selection[index] == self.combo_selection.current_text()
        self._output_message("SIGNAL_SELECTED %s %s" % (index, self.combo_selection.current_text()))
    
    def text_changed(self):
        self._output_message("SIGNAL_EDITCHANGED %s" % self.edit_text.edit_text)
    
    def enter(self):
        self._output_message("SIGNAL_ENTER")
    
    def focus_in(self, widget):
        self._output_message("SIGNAL_FOCUS_IN %s" % widget)
    
    def focus_out(self, widget):
        self._output_message("SIGNAL_FOCUS_OUT %s" % widget)
    
    def notes_changed(self):
        self._output_message("SIGNAL_TEXTCHANGED %s" % self.memo_notes.edit_text)
    
    def notes_statechanged(self):
        # FIXME: This signal doesn't work in Gtk and Wx
        self._output_message("SIGNAL_TEXTSTATECHANGED memo_notes")
    
    def items_selected(self, item):
        assert item is self.listbox_items.current_item()
        assert item == self.listbox_items.current_item()
        self._output_message("SIGNAL_LISTSELECTED %s %s" % (
            self.listbox_items.current_index(), item.cols[0]))
    
    def cells_selected(self, row, col):
        # FIXME: these assertions currently fail in Wx
        #assert self.table_cells.current_row() == row
        #assert self.table_cells.current_col() == col
        try:
            cellvalue = self.table_cells[row][col]
        except IndexError:
            # FIXME: this happens in Qt/KDE 3 when this signal fires on widget initialization
            cellvalue = None
        self._output_message("SIGNAL_CELLSELECTED %s %s %s" % (row, col, cellvalue))
    
    def cells_changed(self, row, col):
        assert self.table_cells.current_row() == row
        assert self.table_cells.current_col() == col
        self._output_message("SIGNAL_CELLCHANGED %s %s %s" % (row, col, self.table_cells[row][col]))
    
    def acceptclose(self):
        # Called by application via main widget
        self._output_message("SIGNAL_QUERYCLOSE")
        # No super call needed since this method only has to be implemented if used
        return True
    
    def closing(self):
        self._output_message("SIGNAL_CLOSING")
    
    def shown(self):
        self._output_message("SIGNAL_SHOWN")
    
    def hidden(self):
        # FIXME: Wx throws a spate of RuntimeErrors before this signal fires on app close
        # (appears to be a Wx internal bug)
        self._output_message("SIGNAL_HIDDEN")


def run():
    gui.runapp(GUISignalTester, use_mainwindow=True)


if __name__ == '__main__':
    run()
