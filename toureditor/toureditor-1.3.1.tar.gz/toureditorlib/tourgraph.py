# -*- coding: utf-8 -*-
# ----------------------------------------
# Copyright (C) 2010-2011  Frank Pählke
#
# This file is part of TourEditor.
#
# TourEditor is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# TourEditor is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with TourEditor.  If not, see <http://www.gnu.org/licenses/>.
# ----------------------------------------

import array
import math
from Tkinter import *
import tkFileDialog
from svgobject.svg import *
try:
    from svgobject.pdf import PDFWriter
    _no_pdf = False
except ImportError:
    _no_pdf = True

class TourGraph(Toplevel):

    def __init__ (self, parent):
        Toplevel.__init__ (self)
        self.parent = parent
        parent.registerListener (self)

        self.zoom = 1.0
        self.grid_rowconfigure (1, weight=1)
        self.grid_columnconfigure (0, weight=1)
        self.buttons = {}

        # button frame
        bf = Frame (self);
        bf.grid (row=0, column=0, columnspan=2, pady=1)

        self.buttons['close'] = b = Button (bf, text='Close', command=self.close)
        b.pack (side=LEFT)

        self.buttons['zoomIn'] = b = Button (bf, text="Zoom in", command=self.zoomIn)
        b.pack (side=LEFT)

        self.buttons['zoomOut'] = b = Button (bf, text="Zoom out", command=self.zoomOut)
        b.pack (side=LEFT)

        self.zoomlabel = Label (bf) # text will be set in self.repaint()
        self.zoomlabel.pack (side=LEFT)

        self.buttons['exportSVG'] = b = Button (bf, text="Export SVG", command=self.exportSVG)
        b.pack (side=LEFT)

        if not _no_pdf:
            self.buttons['exportPDF'] = b = Button (bf, text="Export PDF", command=self.exportPDF)
            b.pack (side=LEFT)
            
        self.canvas = Canvas (self, width=640, height=300,
                              borderwidth=2, relief=SUNKEN)
        self.canvas.grid (sticky=NSEW)

        self.scrollY = Scrollbar (self, command=self.canvas.yview)
        self.canvas.config (yscrollcommand=self.scrollY.set)
        self.scrollY.grid (row=1, column=1, sticky=NS)

        self.scrollX = Scrollbar(self, command=self.canvas.xview, orient=HORIZONTAL)
        self.canvas.config (xscrollcommand=self.scrollX.set)
        self.scrollX.grid (row=2, column=0, sticky=EW)

        self.refresh()

    def refresh (self):
        "repaint graph from tourfile data"
        tf = self.parent.tourfile       
        self.dscale = None #tf.dscale 
        self.hscale = None #tf.hscale
        self.sscale = None #tf.sscale
        self.title (tf.title)
        self.svg = SVG (640, 300, unit="px")
        self.drawSVG (self.svg)
        self.repaint()

    def repaint(self):
        "repaint canvas after zoom factor has changed"
        self.zoomlabel.config (text="Zoom: "+str(int(round(100*self.zoom)))+"%")
        self.canvas.delete (ALL)
        self.canvas.config (scrollregion=(0, 0, self.zoom*self.svg.width, self.zoom*self.svg.height))
        self.svg.paint (self.canvas, self.zoom)

    def zoomIn(self):
        self.zoom = self.zoom * math.sqrt(2)
        self.repaint()

    def zoomOut(self):
        self.zoom = self.zoom / math.sqrt(2)
        self.repaint()

    def close(self):
        self.parent.deregisterListener (self)
        self.destroy()

    def exportPDF(self):
        filename = tkFileDialog.asksaveasfilename (
            title='Export PDF', filetypes=[('PDF', '*.pdf')])
        if filename != None:
            tf = self.parent.tourfile
            svg = SVG (297, 210, unit="mm", view_box=(-51.25, -112.5, 742.5, 525))
            self.drawSVG (svg)
            writer = PDFWriter (filename, tf.title, tf.copyright)
            writer.writeSVG (svg)
            writer.close()

    def exportSVG(self):
        filename = tkFileDialog.asksaveasfilename (
            title='Export SVG',
            filetypes=[('SVG', '*.svg'), ('Compressed SVG', '*.svgz')])
        if filename != None:
            svg = SVG (640, 300, unit='pt')
            self.drawSVG (svg)
            if filename.lower().endswith ('z'):
                svg.writeSVG (filename, True)
            else:
                svg.writeSVG (filename, False)

    def drawSVG (self, svg):
        "draw graph into SVG object"
        tf = self.parent.tourfile
        if tf.is_smoothed:
            dist = tf.getcolumn ('smooth_distance')
            height = tf.getcolumn ('smooth_height')
        else:
            dist = tf.getcolumn ('distance')
            height = tf.getcolumn ('height')
 
        graph = Group (svg, style=Style (font_family="Arial,Helvetica,sans-serif", font_size="14"))

        # calculate slope
        slope = [ ((b-a)/(d-c)/10.0 if d != c else 0) for a,b,c,d in
                  zip(height[0:-1], height[1:], dist[0:-1], dist[1:]) ]

        # calculate scales
        d0,d1,dIntv = self.calcXScale(dist)
        h0,h1,hIntv,s0,s1,sIntv = self.calcYScale(height,slope)
        dTics = int((d1-d0)/dIntv)
        hTics = (h1-h0)/hIntv
        sTics = (s1-s0)/sIntv

        # background
        Rect (graph, 0, 0, 639, 299,
              style=Style (fill="#ffffff", stroke="#000000", stroke_width="1"))

        # title
        if tf.title != None:
            Text (graph, 320, 30, tf.title,
                  style=Style (text_anchor="middle", font_weight="bold", font_size="16"))
        # copyright
        if tf.copyright != None:
            Text (graph, 636, 296, tf.copyright,
                  style=Style (text_anchor="end", font_size="10", fill="#999999"))

        # canvas
        svgcanvas = Group (graph, translate=(80,50))
        Rect (svgcanvas, 0, 0, 500, 200, style=Style(fill="#cccccc"))

        # X minor grid
        if dTics <= 12:
            g = Group (svgcanvas, style=Style (stroke="#999999",stroke_width=1))
            for i in range (dTics):
                d = d0 + (i+0.5)*dIntv;
                x = int(round(self.scale(d, d0, d1, 0, 500)))
                Line (g, x, 0, x, 200)

        # Y minor grid
        if sTics <= 7:
            g = Group (svgcanvas, style=Style (stroke="#999999",stroke_width=1))
            for i in range (sTics):
                s = s0 + (i+0.5)*sIntv;
                y = int(round(self.scale(s, s0, s1, 200, 0)))
                Line (g, 0, y, 500, y)

        # X grid
        g = Group (svgcanvas, style=Style (stroke="#000000",stroke_width=1))
        for i in range (dTics+1):
            d = d0 + i*dIntv;
            x = int(round(self.scale(d, d0, d1, 0, 500)))
            Line (g, x, 0, x, 205)

        # X labels
        g = Group (svgcanvas, style=Style (text_anchor="middle"))
        Text (g, 250, 240, "Strecke [km]")
        for i in range (dTics+1):
            d = d0 + i*dIntv
            x = int(round(500 * float(d-d0) / float(d1-d0)))
            Text (g, x, 220, str(round(d,1)))

        # Y grid
        g = Group (svgcanvas, style=Style (stroke="#000000",stroke_width=1))
        for i in range (hTics+1):
            h = h0 + i*hIntv
            s = s0 + i*sIntv
            y = round(self.scale(h, h0, h1, 200, 0))
            if (s == 0) or (h == 0): # zero axis
                Line (g, -5, y, 505, y, style=Style(stroke_width=2))
            else:
                Line (g, -5, y, 505, y)

        # Y labels (primary)
        g = Group (svgcanvas, translate=(-55,100), rotate=-90)
        Text (g, 0, 0, u"blau: Höhe [m]", style=Style(text_anchor="middle"))
        g = Group (svgcanvas, style=Style(text_anchor="end"))
        for i in range (hTics+1):
            h = h0 + i*hIntv
            y = round(self.scale(h, h0, h1, 200, 0))
            Text (g, -10, y+5, str(int(round(h)))) # TODO: dy="0.5ex"

        # Y labels (secondary)
        g = Group (svgcanvas, translate=(545,100), rotate=-90)
        Text (g, 0, 0, "rot: Steigung [%]", style=Style(text_anchor="middle"))
        g = Group (svgcanvas, style=Style(text_anchor="start"))
        for i in range (sTics+1):
            s = s0 + i*sIntv
            y = round(self.scale(s, s0, s1, 200, 0))
            Text (g, 510, y+5, str(int(round(s)))) # TODO: dy="0.5ex"

        # slope curve (first, i.e. behind height curve)
        dist2 = map((lambda x,y: (x+y)/2), dist[0:-1], dist[1:])
        self.drawCurve (svgcanvas, dist2, d0, d1, slope, s0, s1, "#ff0000")

        # height curve (second, i.e. before slope curve)
        self.drawCurve (svgcanvas, dist, d0, d1, height, h0, h1, "#0000ff")

    # calculate scaling parameters X axis
    # returns: dBottom, dTop, dIntv

    def calcXScale (self, dist):
        if self.dscale != None:
            (dMin, dMax) = string.split(self.dscale, ',')
            dMin = float(dMin)
            dMax = float(dMax)
        else:
            dMin = min(dist)
            dMax = max(dist)

        # determine scale
        for dIntv in [0.1, 0.2, 0.5, 1, 2, 4, 5]:
            # round up/down
            dBottom = dIntv * math.floor(dMin/dIntv)
            dTop = dIntv * math.ceil(dMax/dIntv)
            dTics = int(round((dTop-dBottom) / dIntv))
            if (dTics <= 15):
                break # we have found a suitable scale
        return dBottom, dTop, dIntv

    # calculate scaling parameters for primary and secondary Y axis
    # returns: hBottom, hTop, hIntv, sBottom, sTop, sIntv

    def calcYScale (self, height, slope):
        if self.hscale != None:
            (hMin, hMax) = map(float, string.split(self.hscale, ','))
        else:
            hMin = float(min(height))
            hMax = float(max(height))
        if self.sscale != None:
            (sMin, sMax) = map(float, string.split(self.sscale, ','))
        else:
            # always include zero axis into slope scale
            sMin = float(min(slope+[0]))
            sMax = float(max(slope+[0]))
        # determine scale for primary axis only
        for hIntv in [5, 10, 20, 50, 100, 200, 400]:
            # round up/down
            hBottom = hIntv*int(math.floor(hMin/hIntv))
            hTop = hIntv*int(math.ceil(hMax/hIntv))
            # hBottom and hTop are integer!
            hTics = (hTop-hBottom) / hIntv
            if (hTics <= 8):
                break # we have found a suitable scale
        
        # determine scale for secondary axis only
        for sIntv in [1, 2, 4]:
            # round up/down
            sBottom = sIntv*int(math.floor(sMin/sIntv))
            sTop = sIntv*int(math.ceil(sMax/sIntv))
            # sBottom and sTop are integer!
            sTics = (sTop-sBottom) / sIntv
            if (sTics <= 8):
                break # we have found a suitable scale

        # adjust scales to match each other
        if (sTics > hTics):
            # adjust height scale
            d = sTics - hTics
            hBottom -= hIntv * (d/2)
            hTop += hIntv * (d/2)
            if d%2 == 1: # odd number
                if (hTop-hMax < hMin-hBottom):
                    hTop += hIntv
                else:
                    hBottom -= hIntv
            hTics = sTics
        elif (hTics > sTics):
            # adjust slope scale
            d = hTics - sTics
            if sBottom == 0:
                sTop += sIntv * d
            else:
                sBottom -= sIntv * (d/2)
                sTop += sIntv * (d/2)
                if d%2 == 1: # odd number
                    if (sTop-sMax < sMin-sBottom):
                        sTop += sIntv
                    else:
                        sBottom -= sIntv
            sTics = hTics
        return hBottom, hTop, hIntv, sBottom, sTop, sIntv

    # print actual graph

    def drawCurve(self, parent, x, xMin, xMax, y, yMin, yMax, color):
        # calculate derivatives for Bezier points
        x1 = self.derive(x)
        y1 = self.derive(y)
        # first point
        coords = [ self.scaleCanvas (x[0], xMin, xMax, y[0], yMin, yMax) ]
        # remaining points
        for i in range(1,len(x)):
            # bezier segment: first control point
            sx,sy = self.scaleCanvas (x[i-1] + x1[i-1]/3.0, xMin, xMax,
                                 y[i-1] + y1[i-1]/3.0, yMin, yMax)
            coords.append ((round(sx,2), round(sy,2)))
            # second control point
            sx,sy = self.scaleCanvas (x[i] - x1[i]/3.0, xMin, xMax,
                                 y[i] - y1[i]/3.0, yMin, yMax)
            coords.append ((round(sx,2), round(sy,2)))
            # end point
            sx,sy = self.scaleCanvas (x[i], xMin, xMax, y[i], yMin, yMax)
            coords.append ((round(sx,2), round(sy,2)))
        Bezier (parent, coords, style=Style(stroke=color,stroke_width=1.5,fill="none"))

    # scale coordinate such that the interval [x0,x1] is mapped
    # to [u0,u1]

    def scale (self, x, x0, x1, u0, u1):
        return u0+(u1-u0)*float(x-x0)/(x1-x0)

    # scale point to fit SVG canvas (0,0)-(500,200)

    def scaleCanvas (self, x, x0, x1, y, y0, y1):
        sx = self.scale (x, x0, x1, 0, 500)
        sy = self.scale (y, y0, y1, 200, 0)
        return sx,sy

    # approximate derivative of an array of data points
    # using quadratic interpolation between consecutive points

    def derive (self, d):
        n = len(d) # number of points
        if n <= 1:
            return d
        elif n == 2:
            return [d[1]-d[0], d[1]-d[0]]
        else:
            d1 = array.array('d') # result

            # calculate d1[0] from quadratic interpolation of d[0..2]
            d1.append((4*d[1] - 3*d[0] - d[2]) / 2.0)
            for i in range(1, n-1):
                # calculate d1[i] from adjacent points
                if (d[i+1] - d[i] >= 0 and d[i]-d[i-1] <= 0) \
                   or (d[i+1] - d[i] <= 0 and d[i]-d[i-1] >= 0):
                    di = 0.0
                else:
                    di = (d[i+1] - d[i-1]) / 2.0
                d1.append(di)
            # calculate d1[n-1] from quadratic interpolation of d[n-3..n-1]
            d1.append((3*d[n-1] + d[n-3] - 4*d[n-2]) / 2.0)
            return d1
