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

import codecs
import copy
import gzip
import math
from xml.dom.minidom import getDOMImplementation

# ----------------------------------------

class Style:

    """
Representation of an SVG object's style
"""

    def __init__ (self, font_family=None, font_style=None, font_weight=None, font_size=None, text_anchor=None,
                  fill=None, stroke=None, stroke_width=None):
        self.font_family = font_family
        self.font_style = font_style
        self.font_weight = font_weight
        if font_size == None:
            self.font_size = None
        else:
            self.font_size = float(font_size)
        self.text_anchor = text_anchor
        self.fill = fill
        self.stroke = stroke
        if stroke_width == None:
            self.stroke_width = None
        else:
            self.stroke_width = float(stroke_width)

    def merge (self, style):
        if style == None:
            return
        if self.font_family == None:
            self.font_family = style.font_family
        if self.font_style == None:
            self.font_style = style.font_style
        if self.font_weight == None:
            self.font_weight = style.font_weight
        if self.font_size == None:
            self.font_size = style.font_size
        if self.text_anchor == None:
            self.text_anchor = style.text_anchor
        if self.fill == None:
            self.fill = style.fill
        if self.stroke == None:
            self.stroke = style.stroke
        if self.stroke_width == None:
            self.stroke_width = style.stroke_width

    def toString (self):
        tags = []
        if self.font_family != None:
            tags.append ("font-family:%s" % self.font_family)
        if self.font_style != None:
            tags.append ("font-style:%s" % self.font_style)
        if self.font_weight != None:
            tags.append ("font-weight:%s" % self.font_weight)
        if self.font_size != None:
            tags.append ("font-size:%g" % self.font_size)
        if self.text_anchor != None:
            tags.append ("text-anchor:%s" % self.text_anchor)
        if self.fill != None:
            tags.append ("fill:%s" % self.fill)
        if self.stroke != None:
            tags.append ("stroke:%s" % self.stroke)
        if self.stroke_width != None:
            tags.append ("stroke-width:%g" % self.stroke_width)
        return ";".join(tags)

    def setAttributes (self, dom):
        tags = []
        if self.font_family != None:
            dom.setAttribute ("font-family", self.font_family)
        if self.font_style != None:
            dom.setAttribute ("font-style", self.font_style)
        if self.font_weight != None:
            dom.setAttribute ("font-weight", self.font_weight)
        if self.font_size != None:
            dom.setAttribute ("font-size", "%g" % self.font_size)
        if self.text_anchor != None:
            dom.setAttribute ("text-anchor", self.text_anchor)
        if self.fill != None:
            dom.setAttribute ("fill", self.fill)
        if self.stroke != None:
            dom.setAttribute ("stroke", self.stroke)
        if self.stroke_width != None:
            dom.setAttribute ("stroke-width", "%g" % self.stroke_width)
        return " ".join(tags)

# ----------------------------------------

class Object:

    """Base class for all SVG objects"""

    def __init__ (self, parent, style=None):
        self.parent = parent
        self.style = style
        if parent != None:
            parent.append (self)

    # get full style information, including styles inherited from parent objecjts
    def full_style (self):
        if self.parent == None:
            return self.style
        elif self.style == None:
            return self.parent.full_style()
        else:
            style = copy.copy (self.style)
            style.merge (self.parent.full_style())
            return style

    # transform object coordinates into physical coordinates
    def transform (self, x, y):
        if self.parent == None:
            return (x, y)
        else:
            return self.parent.transform (x, y)

# ----------------------------------------

class Group(Object):

    """
representation of a group of objects

constructor:
    Group (parent[, style][, translate][, rotate])
    where translate is a coordinate pair (x,y)
    and rotate is an angle (in degrees, counter-clockwise)
"""
    def __init__ (self, parent, style=None, translate=None, rotate=None):
        Object.__init__ (self, parent, style)
        self.children = []
        self.translate = translate
        self.rotate = rotate

    def append (self, child):
        self.children.append (child)

    def transform (self, x, y):
        if self.rotate != None:
            s = math.sin(math.radians(self.rotate))
            c = math.cos(math.radians(self.rotate))
            (x, y) = (c*x - s*y, s*x + c*y)
        if self.translate != None:
            x += self.translate[0]
            y += self.translate[1]
        return Object.transform (self, x, y)

    def toDOM (self, doc):
        res = doc.createElement ("g")
        if self.style != None:
            res.setAttribute ("style", self.style.toString())
        if self.translate != None or self.rotate != None:
            transform = []
            if self.translate != None:
                transform.append ("translate(%g,%g)" % self.translate)
            if self.rotate != None:
                transform.append ("rotate(%g)" % self.rotate)
            res.setAttribute ("transform", " ".join(transform))
        for c in self.children:
            res.appendChild (c.toDOM(doc))
        return res

    def paint (self, canvas, zoom=1.0):
        for c in self.children:
            c.paint (canvas, zoom)

# ----------------------------------------

class Rect(Object):

    """
representation of a rectangle

constructor:
    Rect (parent, x, y, width, height[, style])
"""

    def __init__ (self, parent, x, y, width, height, style=None):
        Object.__init__ (self, parent, style)
        self.x = float(x)
        self.y = float(y)
        self.width = float(width)
        self.height = float(height)

    def toDOM (self, doc):
        res = doc.createElement ("rect")
        res.setAttribute ("x", "%g" % self.x)
        res.setAttribute ("y", "%g" % self.y)
        res.setAttribute ("width", "%g" % self.width)
        res.setAttribute ("height", "%g" % self.height)
        if self.style != None:
            self.style.setAttributes (res)
        return res

    def paint (self, canvas, zoom=1.0):
        x1, y1 = self.transform (self.x, self.y)
        x2, y2 = self.transform (self.x+self.width, self.y)
        x3, y3 = self.transform (self.x+self.width, self.y+self.height)
        x4, y4 = self.transform (self.x, self.y+self.height)
        opts = {}
        style = self.full_style()
        if style.stroke_width != None:
            opts["width"] = zoom * style.stroke_width
        if style.stroke != None:
            opts["outline"] = style.stroke
        if style.fill != None:
            opts["fill"] = style.fill
        canvas.create_polygon (zoom*x1, zoom*y1, zoom*x2, zoom*y2,
                               zoom*x3, zoom*y3, zoom*x4, zoom*y4,
                               **opts)

# ----------------------------------------

class Line(Object):

    """
representation of a single line

constructor:
    Line (parent, x1, y2, x2, y2[, style])
"""

    def __init__ (self, parent, x1, y1, x2, y2, style=None):
        Object.__init__ (self, parent, style)
        self.x1 = float(x1)
        self.y1 = float(y1)
        self.x2 = float(x2)
        self.y2 = float(y2)

    def toDOM (self, doc):
        res = doc.createElement ("line")
        res.setAttribute ("x1", str(self.x1))
        res.setAttribute ("y1", str(self.y1))
        res.setAttribute ("x2", str(self.x2))
        res.setAttribute ("y2", str(self.y2))
        if self.style != None:
            self.style.setAttributes (res)
        return res

    def paint (self, canvas, zoom=1.0):
        (x1, y1) = self.transform (self.x1, self.y1)
        (x2, y2) = self.transform (self.x2, self.y2)
        opts = {}
        style = self.full_style()
        if style.stroke_width != None:
            opts["width"] = zoom * style.stroke_width
        if style.stroke != None:
            opts["fill"] = style.stroke
        canvas.create_line (zoom*x1, zoom*y1, zoom*x2, zoom*y2, **opts)

# ----------------------------------------

class PolyLine(Object):

    """
representation of a polyline

constructor:
    PolyLine (parent, coords[, style])
    where coords is a list of (x,y) coordinate pairs
"""

    def __init__ (self, parent, coords, style=None):
        Object.__init__ (self, parent, style)
        self.coords = coords

    def toDOM (self, doc):
        res = doc.createElement ("path")
        d = "M%g,%g" % self.coords[0]
        for c in self.coords[1:]:
            d += "L%g,%g" % c
        res.setAttribute ("d", d)
        if self.style != None:
            self.style.setAttributes (res)
        return res

    def paint (self, canvas, zoom=1.0):
        coords = [ self.transform (c[0], c[1]) for c in self.coords ]
        coords = [ (zoom*x, zoom*y) for x,y in coords ]
        opts = {}
        style = self.full_style()
        if style.stroke_width != None:
            opts["width"] = zoom * style.stroke_width
        if style.fill == None or style.fill.lower() == "none":
            if style.stroke != None:
                opts["fill"] = style.stroke
            canvas.create_line (coords, **opts)
        else:
            opts["fill"] = style.fill
            if style.stroke != None:
                opts["outline"] = style.stroke
            canvas.create_polygon (coords, **opts)

# ----------------------------------------

class Bezier(Object):

    """
representation of a Bezier curve

constructor:
    Bezier (parent, coords[, style])
    where coords is a list of (x,y) coordinate pairs
    and len(coords) = 3n+1
"""

    def __init__ (self, parent, coords, style=None):
        Object.__init__ (self, parent, style)
        self.coords = coords

    def toDOM (self, doc):
        res = doc.createElement ("path")
        d = "M%g,%g" % self.coords[0]
        for i in range(3, len(self.coords), 3):
            d += "C%g,%g,%g,%g,%g,%g" % (self.coords[i-2] + self.coords[i-1] + self.coords[i])
        res.setAttribute ("d", d)
        if self.style != None:
            self.style.setAttributes (res)
        return res

    def paint (self, canvas, zoom=1.0):
        coords = [self.transform (c[0], c[1]) for c in self.coords]
        coords = [ (zoom*x, zoom*y) for x,y in coords ]
        bcoords = [coords[0]]
        for i in range(3, len(coords), 3):
            bcoords = ( bcoords
                        + Bezier.bezier_coords (coords[i-3], coords[i-2], coords[i-1], coords[i])
                        + [coords[i]] )
        opts = {}
        style = self.full_style()
        if style.stroke_width != None:
            opts["width"] = zoom * style.stroke_width
        if style.fill == None or style.fill.lower() == "none":
            if style.stroke != None:
                opts["fill"] = style.stroke
            canvas.create_line (bcoords, **opts)
        else:
            opts["fill"] = style.fill
            if style.stroke != None:
                opts["outline"] = style.stroke
            canvas.create_polygon (bcoords, **opts)

    # approximate Bezier curve by polyline
    @staticmethod
    def bezier_coords (p0, p1, p2, p3):
        # stop recursion if p0 and p3 are less than 5 pixels away from each other
        d0 = p3[0] - p0[0]
        d1 = p3[1] - p0[1]
        if d0*d0 + d1*d1 < 25:
            return []
        x10 = (p0[0] + p1[0]) / 2
        x11 = (p1[0] + p2[0]) / 2
        x12 = (p2[0] + p3[0]) / 2
        x20 = (x10 + x11) / 2
        x21 = (x11 + x12) / 2
        x30 = (x20 + x21) / 2
        y10 = (p0[1] + p1[1]) / 2
        y11 = (p1[1] + p2[1]) / 2
        y12 = (p2[1] + p3[1]) / 2
        y20 = (y10 + y11) / 2
        y21 = (y11 + y12) / 2
        y30 = (y20 + y21) / 2
        return ( Bezier.bezier_coords (p0, (x10,y10), (x20,y20), (x30,y30))
                 + [(x30, y30)]
                 + Bezier.bezier_coords ((x30,y30), (x21,y21), (x12,y12), p3) )

# ----------------------------------------

class Text(Object):

    """
representation of a text label

constructor:
    Text (parent, x, y, text[, style])
"""

    def __init__ (self, parent, x, y, text, style=None):
        Object.__init__ (self, parent, style)
        self.x = float(x)
        self.y = float(y)
        self.text = text

    def toDOM (self, doc):
        res = doc.createElement ("text")
        res.setAttribute ("x", str(self.x))
        res.setAttribute ("y", str(self.y))
        if self.style != None:
            self.style.setAttributes (res)
        res.appendChild (doc.createTextNode (self.text))
        return res

    def paint (self, canvas, zoom=1.0):
        (x, y) = self.transform (self.x, self.y)
        opts = {}
        style = self.full_style()
        if style.stroke != None:
            opts["fill"] = style.stroke
        if style.text_anchor == "start":
            opts["anchor"] = "sw"
        elif style.text_anchor == "end":
            opts["anchor"] = "se"
        else:
            opts["anchor"] = "s"
        if style.font_family != None or style.font_weight != None or style.font_size != None:
            # font family
            if style.font_family == None:
                font = ["Courier"]
            elif style.font_family.lower() == "serif":
                font = ["Times"]
            elif style.font_family.lower() == "sans-serif":
                font = ["Helvetica"]
            elif style.font_family.lower() == "monospace":
                font = ["Courier"]
            else:
                font = [style.font_family]
            if style.font_weight != None or style.font_size != None:
                # font size
                if style.font_size == None:
                    font.append (0)
                else:
                    font.append (int(round(zoom * -style.font_size)))
                # font style
                fontstyle = []
                if style.font_weight != None and style.font_weight.lower() == "bold":
                    fontstyle.append ("bold")
                if style.font_style != None and style.font_style.lower() == "italic":
                    fontstyle.append ("italic")
                if len(fontstyle) > 0:
                    font.append (" ".join(fontstyle))
            opts["font"] = tuple(font)
        canvas.create_text (zoom*x, zoom*y, text=self.text, **opts)

# ----------------------------------------

class SVG(Object):

    """
main class: representation of an SVG drawing

constructor:
    SVG (width, height[, unit[, view_box]])
"""

    def __init__ (self, width, height, unit="px", view_box=None):
        Object.__init__ (self, None, None)
        self.width = float(width)
        self.height = float(height)
        self.unit = unit
        if view_box == None:
            self.view_box = (0, 0, width, height)
        else:
            self.view_box = view_box
        self.children = []

    def append (self, child):
        self.children.append (child)

    def transform (self, x, y):
        return (
            (x-self.view_box[0]) * self.width / self.view_box[2] + 1,
            (y-self.view_box[1]) * self.height / self.view_box[3] + 1
            )

    def toDOM (self, domImpl):
        doctype = domImpl.createDocumentType("svg", "-//W3C//DTD SVG 1.0//EN", "http://www.w3.org/TR/2001/REC-SVG-20010904/DTD/svg10.dtd")
        doc = domImpl.createDocument ("http://www.w3.org/2000/svg", "svg", doctype)
        svg = doc.documentElement
        svg.setAttribute ("width", "%g%s" % (self.width, self.unit))
        svg.setAttribute ("height", "%g%s" % (self.height, self.unit))
        svg.setAttribute ("viewBox", "%g %g %g %g" % self.view_box)
        svg.setAttribute ("version", "1.0")
        svg.setAttribute ("preserveAspectRatio", "none")
        svg.setAttribute ("xmlns", "http://www.w3.org/2000/svg")
        for child in self.children:
            svg.appendChild (child.toDOM(doc))
        return doc

    def writeSVG (self, filename, compressed=False):
        dom = self.toDOM(getDOMImplementation())
        if compressed:
            ofile = codecs.getwriter('utf-8')(gzip.open(filename, 'wb'))
        else:
            ofile = codecs.open (filename, 'w', 'utf-8')
        dom.writexml (ofile, addindent=' ', newl='\n', encoding='utf-8')
        ofile.close()

    def paint (self, canvas, zoom=1.0):
        for c in self.children:
            c.paint (canvas, zoom)

# ----------------------------------------
