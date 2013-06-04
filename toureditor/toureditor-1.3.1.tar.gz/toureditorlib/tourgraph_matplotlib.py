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
import matplotlib
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2TkAgg

_figsize = (10, 6.25)
_figdpi = 96

class TourFileFigure:
    """
    matplotlib figure displaying a TourFile
    """

    def __init__ (self, tourfile):
        self.tourfile = tourfile
        self.figure = plt.figure(1, figsize=_figsize, facecolor='white', edgecolor='black', linewidth=1, frameon=True)
        self.figure.clear()
        self.draw ()

    def draw(self):
        """draw graph into Figure object self.fig"""
        fig = self.figure
        ax = fig.add_subplot(111)
        ax.patch.set_facecolor('0.9') # light grey
        tf = self.tourfile
        if tf.is_smoothed:
            dist = tf.getcolumn ('smooth_distance')
            height = tf.getcolumn ('smooth_height')
        else:
            dist = tf.getcolumn ('distance')
            height = tf.getcolumn ('height')

        ax.plot (dist, height, color='blue', zorder=2)

        # calculate slope
        dist2 = [ (a+b)/2.0 for a,b in zip(dist[0:-1], dist[1:]) ]
        slope = [ ((b-a)/(d-c)/10.0 if d != c else 0) for a,b,c,d in
                  zip(height[0:-1], height[1:], dist[0:-1], dist[1:]) ]

        ax2 = ax.twinx()
        ax2.plot (dist2, slope, color="red", zorder=3)

        ax.set_xlabel ('Entfernung [km]')
        ax.set_ylabel (u'blau: Höhe [m]')
        ax2.set_ylabel ('rot: Steigung [%]')

        # calculate scales
        d0,d1,dIntv = self.calcXScale(dist)
        h0,h1,hIntv,s0,s1,sIntv = self.calcYScale(height,slope)
        dTics = int(round((d1-d0)/dIntv))
        hTics = int(round((h1-h0)/hIntv))
        sTics = int(round((s1-s0)/sIntv))
        ax.set_xlim (d0, d1)
        ax.set_ylim (h0, h1)
        ax2.set_xlim (d0, d1)
        ax2.set_ylim (s0, s1)

        # draw grid
        ax.set_xticks ( [d0+i*dIntv for i in range(dTics+1)] )
        ax.set_yticks ( [h0+i*hIntv for i in range(hTics+1)] )
        ax2.set_xticks ( [d0+i*dIntv for i in range(dTics+1)] )
        ax2.set_yticks ( [s0+i*sIntv for i in range(sTics+1)] )
        ax.grid(True)
        if h0 < 0 and h1 > 0:
            ax.axhline (0, color='black', zorder=1)
        if s0 < 0 and s1 > 0:
            ax2.axhline (0, color='black', zorder=1)

        # title
        if tf.title != None:
            ax.set_title (tf.title)

        # copyright
        if tf.copyright != None:
            ax.text (0.99, 0.016, tf.copyright, ha='right', va='bottom',
                     transform=fig.transFigure, size='small', color='0.5')                     
        

    # calculate scaling parameters X axis
    # returns: dBottom, dTop, dIntv

    def calcXScale (self, dist):
        tf = self.tourfile
        if tf.dmin != None:
            dMin = tf.dmin
        else:
            dMin = min(dist)
        if tf.dmax != None:
            dMax = tf.dmax
        else:
            dMax = max(dist)
        # determine scale
        for dIntv in [0.1, 0.2, 0.5, 1, 2, 4, 5]:
            # round up/down
            dBottom = dIntv * math.floor(dMin/dIntv)
            dTop = dIntv * math.ceil(dMax/dIntv)
            dTics = int(round((dTop-dBottom) / dIntv))
            if (dTics <= 20):
                break # we have found a suitable scale
        return dBottom, dTop, dIntv

    # calculate scaling parameters for primary and secondary Y axis
    # returns: hBottom, hTop, hIntv, sBottom, sTop, sIntv

    def calcYScale (self, height, slope):
        tf = self.tourfile
        if tf.hmin != None:
            hMin = tf.hmin
        else:
            hMin = float(min(height))
        if tf.hmax != None:
            hMax = tf.hmax
        else:
            hMax = float(max(height))
        if tf.smin != None:
            sMin = tf.smin
        else:
            sMin = float(min(slope+[0]))
        if tf.smax != None:
            sMax = tf.smax
        else:
            # always include zero axis into slope scale
            sMax = float(max(slope+[0]))
        # determine scale for primary axis only
        for hIntv in [5, 10, 20, 50, 100, 200, 400]:
            # round up/down
            hBottom = hIntv*int(math.floor(hMin/hIntv))
            hTop = hIntv*int(math.ceil(hMax/hIntv))
            # hBottom and hTop are integer!
            hTics = (hTop-hBottom) / hIntv
            if (hTics <= 10):
                break # we have found a suitable scale
        
        # determine scale for secondary axis only
        for sIntv in [1, 2, 4]:
            # round up/down
            sBottom = sIntv*int(math.floor(sMin/sIntv))
            sTop = sIntv*int(math.ceil(sMax/sIntv))
            # sBottom and sTop are integer!
            sTics = (sTop-sBottom) / sIntv
            if (sTics <= 10):
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

    def save(self, filename):
        self.figure.set_size_inches(*_figsize)
        self.figure.savefig(filename, dpi=_figdpi, papertype='a4')

class NavigationToolbar(NavigationToolbar2TkAgg):

    def save_figure(self):
        # reset figsize to original value
        self.canvas.figure.set_size_inches(*_figsize)
        matplotlib.rcParams['savefig.dpi'] = _figdpi
        NavigationToolbar2TkAgg.save_figure(self)
        self.canvas.draw()

class TourGraph(Toplevel):
    """
    Tkinter frontend for TourFileFigure
    """

    def __init__ (self, parent):
        Toplevel.__init__ (self)
        self.parent = parent
        parent.registerListener (self)
        self.fig = TourFileFigure(self.parent.tourfile)

        self.zoom = 1.0
        self.buttons = {}

        # button frame
        bf = Frame (self);
        bf.pack (side=TOP)

        self.buttons['close'] = b = Button (bf, text='Close', command=self.close)
        b.pack (side=LEFT)

        self.canvasframe = cf = Frame (self)
        cf.pack(side=TOP, fill=BOTH, expand=1)

        self.canvas = c = FigureCanvasTkAgg(self.fig.figure, cf)
        c.show()
        c.get_tk_widget().pack(side=TOP, fill=BOTH, expand=1)

        self.toolbar = tb = NavigationToolbar(c, cf)
        tb.update()
        c._tkcanvas.pack(side=TOP, fill=BOTH, expand=1)

        self.fig.draw()
        self.canvas.draw()

    def close(self):
        self.parent.deregisterListener (self)
        self.destroy()
