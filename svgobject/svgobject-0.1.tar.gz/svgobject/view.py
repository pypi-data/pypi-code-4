# ----------------------------------------
# Copyright (C) 2010-2011  Frank Paehlke
#
# This file is part of svgobject.
#
# svgobject is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.###
#
# svgobject is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with svgobject.  If not, see <http://www.gnu.org/licenses/>.
# ----------------------------------------

import math
import sys

# Python 3 compatibility
if sys.version_info[0] >= 3:
    from tkinter import *
else:
    from Tkinter import *

# PDF export requires ReportLab to be installed
try:
    from svgobject import pdf
    _with_pdf = True
except ImportError:
    _with_pdf = False

# ----------------------------------------

class SVGView(Toplevel):

    """
Simple Tkinter application for viewing a svgobject drawing
"""

    def __init__ (self, svg, title=None):
        Toplevel.__init__ (self)

        self.zoom = 1.0
        self.svg = svg

        self.width = svg.width
        self.height = svg.height

        if title != None:
            self.title (title)

        self.grid_rowconfigure (1, weight=1)
        self.grid_columnconfigure (0, weight=1)

        self.buttons = Frame (self);
        self.buttons.grid (row=0, column=0, columnspan=2, pady=1)

        self.QUIT = Button (self.buttons, text="Quit", command=self.quit)
        self.QUIT.pack (side=LEFT)

        self.ZOOMIN = Button (self.buttons, text="Zoom in", command=self.zoomIn)
        self.ZOOMIN.pack (side=LEFT)

        self.ZOOMOUT = Button (self.buttons, text="Zoom out", command=self.zoomOut)
        self.ZOOMOUT.pack (side=LEFT)

        self.zoomlabel = Label (self.buttons) # text will be set in self.repaint()
        self.zoomlabel.pack (side=LEFT)

        if _with_pdf:
            self.buttonPDF = Button (self.buttons, text="Export PDF", command=self.exportPDF)
            self.buttonPDF.pack (side=LEFT)

        self.canvas = Canvas (self, width=self.width, height=self.height,
                              borderwidth=2, relief=SUNKEN)
        self.canvas.grid (sticky=NSEW)

        self.scrollY = Scrollbar (self, command=self.canvas.yview)
        self.canvas.config (yscrollcommand=self.scrollY.set)
        self.scrollY.grid (row=1, column=1, sticky=NS)

        self.scrollX = Scrollbar(self, command=self.canvas.xview, orient=HORIZONTAL)
        self.canvas.config (xscrollcommand=self.scrollX.set)
        self.scrollX.grid (row=2, column=0, sticky=EW)

        self.repaint()

    def repaint(self):
        self.zoomlabel.config (text="Zoom: "+str(round(100*self.zoom))+"%")
        self.canvas.delete (ALL)
        self.canvas.config (scrollregion=(0, 0, self.zoom*self.width, self.zoom*self.height))
        self.svg.paint (self.canvas, self.zoom)

    def zoomIn(self):
        self.zoom = self.zoom * math.sqrt(2)
        self.repaint()

    def zoomOut(self):
        self.zoom = self.zoom / math.sqrt(2)
        self.repaint()

    if _with_pdf:
        def exportPDF(self):
            writer = pdf.PDFWriter ('graph.pdf')
            writer.writeSVG (self.svg)
            writer.close()

# ----------------------------------------
