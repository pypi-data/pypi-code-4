#!/usr/bin/env python
"""
PXMLVIEW.PY
Copyright (C) 2008-2013 by Peter A. Donis

Released under the GNU General Public License, Version 2
See the LICENSE and README files for more information

A simple read-only XML file viewer using the PLIB package.
"""

import sys
import os
import xml.etree.ElementTree as etree

from plib.stdlib.coll import basecontainer

from plib.gui import __version__
from plib.gui import main as gui
from plib.gui.defs import *


block_elements = ["p"]  # NOT a complete list, just enough to work with test XML files


def tagtype(node):
    if node.tag in block_elements:
        return "markup block"
    return "element"


def is_leaf(node):
    return len(node) < 1


def cdata(node):
    return node.text


class ETreeNodeWrapper(basecontainer):
    # Ensures that the node objects seen by the list view items will work
    # like standard sequences (etree nodes have some peculiarities since
    # they are a sort of hybrid of sequence and mapping); note that this
    # is a read-only view since we are not doing any XML editing here
    
    def __init__(self, node):
        self._node = node
        basecontainer.__init__(self)
    
    def _indexlen(self):
        return len(self._node)
    
    def _get_data(self, index):
        # Wrap child nodes the same way
        return ETreeNodeWrapper(self._node[index])


class XMLListViewItem(gui.PListViewItem):
    
    def __init__(self, parent, index, node):
        if isinstance(node, ETreeNodeWrapper):
            # Parse node info into listview columns
            cols = [
                " ".join([node._node.tag] + [
                    "{}='{}'".format(key, node._node.get(key))
                    for key in node._node.keys()
                ]),
                tagtype(node._node)
            ]
            if is_leaf(node._node):
                s = cdata(node._node)
                childlist = [s] if s else None
            else:
                childlist = node
            data = (cols, childlist)
        else:
            # Make character data look like a child node
            data = ([node, "cdata"], None)
        gui.PListViewItem.__init__(self, parent, index, data)
        self.expand()


class XMLListView(gui.PListView):
    
    itemclass = XMLListViewItem
    
    def __init__(self, parent, data):
        self._filename = data
        self._xml = etree.parse(data)
        gui.PListView.__init__(
            self, parent,
            [
                gui.PHeaderLabel("XML"),
                gui.PHeaderLabel("Node Type", 150, ALIGN_CENTER)
            ],
            [ETreeNodeWrapper(self._xml.getroot())],
            self.current_changed
        )
        if sys.platform == 'darwin':
            fontsize = 16
        else:
            fontsize = 12
        self.set_font("Arial", fontsize)
        self.set_header_font("Arial", fontsize, bold=True)
    
    def current_changed(self, item):
        self._parent.print_status(item.cols[0])


class XMLTabWidget(gui.PTabWidget):
    
    aboutdata = {
        'name': "PXMLViewer",
        'version': __version__,
        'copyright': "Copyright (C) 2008-2013 by Peter A. Donis",
        'license': "GNU General Public License (GPL) Version 2",
        'description': "XML File Viewer",
        'developers': ["Peter Donis"],
        'website': "http://www.peterdonis.net",
        'icon': os.path.join(os.path.split(os.path.realpath(__file__))[0],
                             "pxmlview.png")
    }
    
    actionflags = [
        ACTION_FILEOPEN, ACTION_ABOUT, ACTION_ABOUTTOOLKIT,
        ACTION_EXIT
    ]
    
    defaultcaption = "XML File Viewer"
    large_icons = True
    placement = (SIZE_MAXIMIZED, MOVE_NONE)
    queryonexit = False
    
    def __init__(self, parent):
        # Some gymnastics to help the file open dialog find our test XML files
        realfile = __file__
        if os.path.islink(realfile):
            realfile = os.path.realpath(realfile)
        self._path = os.path.dirname(realfile)
        
        self.mainwin = parent
        if len(sys.argv) > 1:
            filenames = sys.argv[1:]
        else:
            filenames = []
        if not filenames:
            filename = self.get_filename()
            if not filename:
                sys.exit("You must select an XML file to view.")
            filenames.append(filename)
        gui.PTabWidget.__init__(self, parent, None, self.tab_changed)
        for filename in filenames:
            self.add_file(filename)
        parent.connectaction(ACTION_FILEOPEN, self.open_file)
    
    def get_filename(self):
        fname = self.mainwin.getfiledialog(path=self._path)
        if len(fname) > 0:
            fname = str(fname)
            self._path = os.path.dirname(fname)
            return fname
        return ""
    
    def add_file(self, fname):
        widget = XMLListView(self, fname)
        self.append((os.path.basename(fname), widget))
        if len(self) > 1:
            self.set_current_index(len(self) - 1)
    
    def open_file(self):
        fname = self.get_filename()
        if len(fname) > 0:
            self.add_file(fname)
    
    def tab_changed(self, index):
        self.print_status(self.current_widget()._filename)
    
    def print_status(self, text):
        self._parent.statusbar.set_text(text)


if __name__ == "__main__":
    gui.runapp(XMLTabWidget, use_mainwindow=True)
