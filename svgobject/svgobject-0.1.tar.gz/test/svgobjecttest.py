#! /usr/bin/env python
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

from xml.dom.minidom import parse, getDOMImplementation
import sys
if sys.version_info[0] >= 3:
    from tkinter import Tk
else:
    from Tkinter import Tk
from svgobject import svg, view

doc = svg.SVG(640, 300, view_box=(-100, -100, 840, 500))
r = svg.Rect(doc, 0, 0, 639, 299, svg.Style(fill="#cccccc", stroke="#0000ff", stroke_width=1))
g = svg.Group(doc, translate=(80,50), style=svg.Style(font_family="Arial,Helvetica,sans-serif"))
l = svg.Line(g, 0, 0, 500, 200, svg.Style(stroke_width=2,stroke="#ff0000"))
t = svg.Text(g, 100, 100, "bla blubb", svg.Style(text_anchor="end"))
svg.PolyLine(g, [(100,100),(100,200),(300,50),(300,100)], svg.Style(stroke="#999999", fill="none"))
svg.Bezier(g, [(100,100),(100,200),(300,50),(300,100)], svg.Style(stroke_width=2, stroke="#009900", fill="#00cc00"))

domImpl = getDOMImplementation()
sys.stdout.write(doc.toDOM(domImpl).toprettyxml(indent=" "))

root = Tk()
root.withdraw()
app = view.SVGView (doc, title='SVGObject Test')
app.mainloop()
root.destroy()
