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

from xml.dom.minidom import getDOMImplementation
from svgobject.svg import *
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4

# ----------------------------------------

class PDFWriter:

    """
Writer class for exporting a svgobject drawing to PDF using the ReportLab toolkit

Example Usage:
    writer = PDFWriter(filename, title, author, subject)
    writer.writeSVG(svg1)
    writer.writeSVG(svg2)
    writer.close()

Each invocation of writeSVG() creates a new page in the PDF file.
"""

    def __init__ (self, filename, title=None, author=None, subject=None):
        self.filename = filename
        self.canvas = c = canvas.Canvas(filename)
        if title != None:
            c.setTitle (title)
        if author != None:
            c.setAuthor (author)
        if subject != None:
            c.setSubject (subject)

    # map unit(lowercase) -> number of PDF points per unit
    _units = {
        'in': 72.0,
        'cm': 72.0/2.54,
        'mm': 72.0/25.4
        }

    def writeSVG (self, svg):
        c = self.canvas
        # convert width/height to pt
        try:
            unit = self._units[svg.unit.lower()]
        except KeyError:
            unit = 1.0
        width = svg.width * unit
        height = svg.height * unit
        c.setPageSize ((width, height))
        # scale from view_box to PDF coordinates
        vb_left, vb_top, vb_width, vb_height = svg.view_box
        c.scale (width/vb_width, -height/vb_height)
        c.translate (-vb_left, -vb_height-vb_top)
        for child in svg.children:
            self.writeObject (child)
        c.showPage()

    def close(self):
        self.canvas.save()

    def setStyle (self, style):
        if style == None:
            return
        c = self.canvas
        if style.stroke_width != None:
            c.setLineWidth (style.stroke_width)
        if style.fill != None and style.fill != 'none':
            c.setFillColor (style.fill)
        if style.stroke != None and style.stroke != 'none':
            c.setStrokeColor (style.stroke)
            
    def writeObject (self, obj):
        if obj.style != None:
            self.canvas.saveState()
            self.setStyle (obj.style)
        if isinstance (obj, Group):
            self.writeGroup (obj)
        elif isinstance (obj, Rect):
            self.writeRect (obj)
        elif isinstance (obj, Line):
            self.writeLine (obj)
        elif isinstance (obj, PolyLine):
            self.writePolyLine (obj)
        elif isinstance (obj, Bezier):
            self.writeBezier (obj)
        elif isinstance (obj, Text):
            self.writeText (obj)
        if obj.style != None:
            self.canvas.restoreState()

    def writeGroup (self, group):
        c = self.canvas
        if group.translate != None or group.rotate != None:
            c.saveState()
            if group.translate != None:
                c.translate (*group.translate)
            if group.rotate != None:
                c.rotate (group.rotate)
        for child in group.children:
            self.writeObject (child)
        if group.translate != None or group.rotate != None:
            c.restoreState()

    def writeRect (self, rect):
        style = rect.full_style()
        stroke = (0 if style.stroke == None or style.stroke == 'none' else 1)
        fill = (0 if style.fill == None or style.fill == 'none' else 1)
        self.canvas.rect (rect.x, rect.y, rect.width, rect.height, stroke, fill)

    def writeLine (self, line):
        self.canvas.line (line.x1, line.y1, line.x2, line.y2)

    def writePolyLine (self, polyline):
        c = self.canvas
        style = polyline.full_style()
        stroke = (0 if style.stroke == None or style.stroke == 'none' else 1)
        fill = (0 if style.fill == None or style.fill == 'none' else 1)
        p = c.beginPath()
        p.moveTo (*polyline.coords[0])
        for xy in polyline.coords[1:]:
            p.lineTo (*xy)
        c.drawPath (p, stroke, fill)

    def writeBezier (self, bezier):
        c = self.canvas
        style = bezier.full_style()
        stroke = (0 if style.stroke == None or style.stroke == 'none' else 1)
        fill = (0 if style.fill == None or style.fill == 'none' else 1)
        p = c.beginPath()
        coords = bezier.coords
        p.moveTo (*coords[0])
        for i in range(3, len(coords), 3):
            p.curveTo (*(coords[i-2] + coords[i-1] + coords[i]))
        c.drawPath (p, stroke, fill)

    # Map (font_family (lowercase), isBold, isItalic) -> PDF font
    _fontmap = {
        ('helvetica', False, False): 'Helvetica',
        ('helvetica', False, True): 'Helvetica-Oblique',
        ('helvetica', True, False): 'Helvetica-Bold',
        ('helvetica', True, True): 'Helvetica-BoldOblique',
        ('arial', False, False): 'Helvetica',
        ('arial', False, True): 'Helvetica-Oblique',
        ('arial', True, False): 'Helvetica-Bold',
        ('arial', True, True): 'Helvetica-BoldOblique',
        ('sans-serif', False, False): 'Helvetica',
        ('sans-serif', False, True): 'Helvetica-Oblique',
        ('sans-serif', True, False): 'Helvetica-Bold',
        ('sans-serif', True, True): 'Helvetica-BoldOblique',
        ('times', False, False): 'Times',
        ('times', False, True): 'Times-Italic',
        ('times', True, False): 'Times-Bold',
        ('times', True, True): 'Times-BoldItalic',
        ('times new roman', False, False): 'Times',
        ('times new roman', False, True): 'Times-Italic',
        ('times new roman', True, False): 'Times-Bold',
        ('times new roman', True, True): 'Times-BoldItalic',
        ('serif', False, False): 'Times',
        ('serif', False, True): 'Times-Italic',
        ('serif', True, False): 'Times-Bold',
        ('serif', True, True): 'Times-BoldItalic',
        ('courier', False, False): 'Courier',
        ('courier', False, True): 'Courier-Oblique',
        ('courier', True, False): 'Courier-Bold',
        ('courier', True, True): 'Courier-BoldOblique',
        ('courier new', False, False): 'Courier',
        ('courier new', False, True): 'Courier-Oblique',
        ('courier new', True, False): 'Courier-Bold',
        ('courier new', True, True): 'Courier-BoldOblique',
        ('monospace', False, False): 'Courier',
        ('monospace', False, True): 'Courier-Oblique',
        ('monospace', True, False): 'Courier-Bold',
        ('monospace', True, True): 'Courier-BoldOblique'
        }

    def writeText (self, text):
        c = self.canvas
        style = text.full_style()
        c.saveState()
        # our canvas is scaled upside-down, and thus we must mirror the text
        c.translate (text.x, text.y)
        c.scale (1, -1)
        font_family = 'Courier' # default
        if style.font_family != None:
            isBold = (style.font_weight != None and style.font_weight.lower() == 'bold')
            isItalic = (style.font_style != None and style.font_style.lower() == 'italic')
            for font in style.font_family.lower().split(','):
                try:
                    font_family = self._fontmap[(font, isBold, isItalic)]
                    break
                except KeyError:
                    continue
        font_size = (style.font_size if style.font_size != None else 12)
        c.setFont (font_family, font_size)
        if style.text_anchor == 'start':
            c.drawString (0, 0, text.text)
        elif style.text_anchor == 'end':
            c.drawRightString (0, 0, text.text)
        else:
            c.drawCentredString (0, 0, text.text)
        c.restoreState()

# ----------------------------------------
