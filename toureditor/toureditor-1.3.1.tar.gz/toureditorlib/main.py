# -*- coding: utf-8 -*-
# ----------------------------------------
# Copyright (C) 2010-2012  Frank Pählke
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

import sys
import datetime
from Tkinter import *
import tkFileDialog
import tkMessageBox
import tkSimpleDialog
if sys.version_info[0] >= 3:
    import tkinter.ttk as ttk
else:
    import ttk
from toureditorlib.tourfile import TourFile
from toureditorlib import tourfilesmooth

# Is the matplotlib version of TourGraph available?
try:
    from toureditorlib.tourgraph_matplotlib import TourGraph
except ImportError:
    # use standard version without matplotlib
    from toureditorlib.tourgraph import TourGraph

from toureditorlib._version import __version__

# ----------------------------------------

_encodings = [
    'iso-8859-1',
    'iso-8859-2',
    'iso-8859-3',
    'iso-8859-4',
    'iso-8859-5',
    'iso-8859-6',
    'iso-8859-7',
    'iso-8859-8',
    'iso-8859-9',
    'iso-8859-10',
    'iso-8859-11',
    'iso-8859-12',
    'iso-8859-13',
    'iso-8859-14',
    'iso-8859-15',
    'iso-8859-16',
    'utf-8'
    ]

_filetypes = [
    ('CRP', '*.crp'),
    ('CSV', '*.csv'),
    ('GPX', '*.gpx'),
    ('all', '*')
    ]

# ----------------------------------------

class TourView (Toplevel):

    def __init__ (self, tourfile):

        Toplevel.__init__ (self)
        self.tourfile = tourfile
        self.listeners = []
        self.fixedRows = set()

        self.title('Tour Editor - '+tourfile.filename)
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        # 1st button frame
        bf = ttk.Frame (self)
        bf.grid (row=0, column=0, columnspan=2, sticky=W)

        l = ttk.Label (bf, text='Encoding:')
        l.pack (side=LEFT)

        self.encodingBox = ttk.Combobox(bf, values=_encodings)
        self.encodingBox.set (tourfile.encoding or 'iso-8859-1')
        self.encodingBox.pack (side=LEFT, fill=Y, expand=True)

        self.buttons = {}
        self.buttons['open'] = b = ttk.Button (bf, text='Open', command=self.open)
        b.pack(side=LEFT)

        self.buttons['save'] = b = ttk.Button (bf, text='Save', command=self.save, state=DISABLED)
        b.pack(side=LEFT)

        self.buttons['saveAs'] = b = ttk.Button (bf, text='Save As', command=self.saveAs)
        b.pack(side=LEFT)

        self.buttons['reload'] = b = ttk.Button (bf, text='Reload', command=self.reload, state=DISABLED)
        b.pack(side=LEFT)

        self.buttons['close'] = b = ttk.Button (bf, text='Close', command=self.close)
        b.pack(side=LEFT)

        # Treeview with scrollbars
        t = ttk.Treeview (self, columns=tourfile.columns)
        t.grid(row=1,column=0, sticky=NSEW)
        self.treeview = t
        t.column ('#0', width=60, stretch=False)
        for i in range(len(tourfile.columns)-1):
            t.column (i, width=100, stretch=False)
        t.tag_configure ('standstill', background='yellow')
        t.tag_configure ('fixed', foreground='red')

        self.vscr = ttk.Scrollbar (self, command=self.treeview.yview)
        t.config (yscrollcommand=self.vscr.set)
        self.vscr.grid(row=1,column=1, sticky=NS)

        self.hscr = ttk.Scrollbar (self, orient=HORIZONTAL, command=self.treeview.xview)
        t.config (xscrollcommand=self.hscr.set)
        self.hscr.grid(row=2,column=0, sticky=EW)

        t.bind ('<Double-Button-1>', self.doubleclick)
        self.bind ('<Control-a>', self.selectAll)
        self.bind ('<Control-n>', self.selectNone)

        # 2nd button frame
        bf = ttk.Frame (self)
        bf.grid (row=3, column=0, columnspan=2)

        self.buttons['meta'] = b = ttk.Button (bf, text='Metadata', command=self.metadata)
        b.pack(side=LEFT)

        self.buttons['hOffset'] = b = ttk.Button (bf, text='Height Offset', command=self.heightOffset)
        b.pack(side=LEFT)

        self.buttons['dOffset'] = b = ttk.Button (bf, text='Distance Offset', command=self.distanceOffset)
        b.pack(side=LEFT)

        self.buttons['delete'] = b = ttk.Button (bf, text='Delete Rows', command=self.delete)
        b.pack(side=LEFT)

        self.buttons['reverse'] = b = ttk.Button (bf, text='Reverse File', command=self.reverse)
        b.pack(side=LEFT)

        self.buttons['fix'] = b = ttk.Button (bf, text='Fix rows', command=self.fix)
        b.pack(side=LEFT)

        self.buttons['simplify'] = b = ttk.Button (bf, text='Simplify', command=self.simplify)
        b.pack(side=LEFT)

        self.buttons['smooth'] = b = ttk.Button (bf, text='Smooth', command=self.smooth)
        b.pack(side=LEFT)

        self.buttons['graph'] = b = ttk.Button (bf, text='Show Graph', command=self.graph)
        b.pack(side=LEFT)

        self.geometry ('800x600')
        self.refresh()

    def registerListener (self, listener):
        self.listeners.append (listener)

    def deregisterListener (self, listener):
        self.listeners = [l for l in self.listeners if l != listener]

    def dirty (self, isdirty):
        if isdirty:
            self.buttons['save'].config (state=NORMAL)
            self.buttons['reload'].config (state=NORMAL)
        else:
            self.buttons['save'].config (state=DISABLED)
            self.buttons['reload'].config (state=DISABLED)

    def refresh (self):
        t = self.treeview
        items = t.get_children()
        if len(items) > 0:
            t.delete (*items)
        tf = self.tourfile
        for i in range(len(tf.columns)):
            t.heading (i, text=tf.columns[i])
        for i in range(len(tf)):
            point = tf.get(i)[:]
            for j in range (len(point)):
                if point[j] == None:
                    point[j] = ''
                elif isinstance(point[j], datetime.datetime):
                    point[j] = point[j].strftime ('%H:%M:%S')
                elif isinstance(point[j], float):
                    point[j] = round(point[j], 3)
            tags = []
            if i > 0 and abs(tf.distance (i-1, i)) < .001:
                tags.append ('standstill')
            if i in self.fixedRows:
                tags.append ('fixed')
            t.insert ('', 'end', text=str(i+1), value=point, tags=tuple(tags))
        for l in self.listeners:
            l.refresh()

    def open(self):
        filename = tkFileDialog.askopenfilename (
            title='Open file', filetypes=_filetypes)
        if filename != None and filename != '':
            encoding = self.encodingBox.get()
            TourView (TourFile.read (filename, encoding))

    def save(self):
        tf = self.tourfile
        if tkMessageBox.askokcancel (title='Save Tour File', message='Really overwrite contents of '+tf.filename+'?'):
            tf.write (tf.filename, self.encodingBox.get(), tf.filetype)
            self.dirty (False)

    def saveAs(self):
        filename = tkFileDialog.asksaveasfilename (
            title='Save File', filetypes=_filetypes)
        if filename != None and filename != '':
            self.tourfile.write (filename, self.encodingBox.get())
            self.title (filename)
            self.dirty (False)

    def reload(self):
        tf = self.tourfile
        self.tourfile = TourFile.read (tf.filename, tf.encoding, tf.filetype)
        self.refresh()
        self.dirty (False)

    def close(self):
        for l in self.listeners:
            l.close()
        self.destroy()

    def delete (self):
        t = self.treeview
        tf = self.tourfile
        rows = [t.index(item) for item in t.selection()]
        rows.sort(reverse=True)
        for row in rows:
            tf.delete (row)
        self.refresh()
        self.dirty (True)

    def fix (self):
        t = self.treeview
        self.fixedRows = self.fixedRows.symmetric_difference(
            [t.index(item) for item in t.selection()])
        self.refresh()

    def doubleclick (self, event):
        t = self.treeview
        item = t.identify_row (event.y)
        col = t.identify_column (event.x)
        if item != '' and col != '#0':
            s = tkSimpleDialog.askstring (title='Enter value', prompt=t.heading(col, option='text'),
                                          initialvalue=t.set(item, col))
            t.set (item, col, s)
            self.tourfile.set (t.index(item), **{t.column(col, 'id'): s})
            self.dirty (True)
            for l in self.listeners:
                l.refresh()

    def selectAll (self, event):
        t = self.treeview
        t.selection_set (t.get_children())

    def selectNone (self, event):
        self.treeview.selection_set(())

    def metadata (self):
        metadataDialog = MetadataDialog(self)
        self.dirty (True)

    def heightOffset (self):
        t = self.treeview
        tf = self.tourfile
        offset = tkSimpleDialog.askinteger(title='Height Offset', prompt='Select offset [m] to add/subtract from height')
        if offset != None:
            rows = [ t.index(item) for item in t.selection() ]
            tf.heightOffset (offset, rows)
            self.refresh()
            self.dirty(True)

    def distanceOffset (self):
        t = self.treeview
        tf = self.tourfile
        offset = tkSimpleDialog.askfloat(title='Distance Offset', prompt='Select offset [km] to add/subtract from distance')
        if offset != None:
            rows = [ t.index(item) for item in t.selection() ]
            tf.distanceOffset (offset, rows)
            self.refresh()
            self.dirty(True)

    def reverse (self):
        self.tourfile.reverse()
        self.refresh()
        self.dirty(True)

    def simplify(self):
        self.tourfile.simplify(5.0)
        self.refresh()
        self.dirty(True)

    def smooth (self):
        smoothDialog = SmoothDialog(self)

    def graph(self):
        tf = self.tourfile
        TourGraph (self)

# ----------------------------------------

class MetadataDialog (tkSimpleDialog.Dialog):

    def body(self, master):
        self.title('Metadata')

        tf = self.parent.tourfile

        ttk.Label (master, text='Title ').grid (row=0, column=0, sticky=E)
        self.tourtitle = ttk.Entry (master, width=40)
        if tf.title != None:
            self.tourtitle.insert ('0', tf.title)
        self.tourtitle.grid (row=0, column=1, sticky=W)

        ttk.Label (master, text='Date ').grid (row=1, column=0, sticky=E)
        self.date = ttk.Entry (master, width=10)
        if tf.date != None:
            self.date.insert ('0', tf.date.strftime("%Y-%m-%d"))
        self.date.grid (row=1, column=1, sticky=W)

        ttk.Label (master, text='Copyright ').grid (row=2, column=0, sticky=E)
        self.copyright = ttk.Entry (master, width=40)
        if tf.copyright != None:
            self.copyright.insert ('0', tf.copyright)
        self.copyright.grid (row=2, column=1, sticky=W)

        ttk.Label (master, text='Length [km] ').grid (row=3, column=0, sticky=E)
        ttk.Label (master, text=tf.length(), relief=SUNKEN).grid (row=3, column=1, sticky=W)

        ttk.Label (master, text='Total height difference [m] ').grid (row=4, column=0, sticky=E)
        ttk.Label (master, text=int(round(tf.hdiff(False))), relief=SUNKEN).grid (row=4, column=1, sticky=W)

        ttk.Label (master, text='Net height difference [m] ').grid (row=5, column=0, sticky=E)
        ttk.Label (master, text=int(round(tf.hdiff(True))), relief=SUNKEN).grid (row=5, column=1, sticky=W)

        ttk.Label (master, text='Average slope [%] ').grid (row=6, column=0, sticky=E)
        ttk.Label (master, text=round(tf.slope(), 2), relief=SUNKEN).grid (row=6, column=1, sticky=W)

        ttk.Label (master, text='Maximum slope [%] ').grid (row=7, column=0, sticky=E)
        ttk.Label (master, text=round(tf.maxslope(), 2), relief=SUNKEN).grid (row=7, column=1, sticky=W)

        ttk.Label (master, text='Graph d_min [%] ').grid (row=8, column=0, sticky=E)
        self.dmin = ttk.Entry (master, width=10)
        if tf.dmin != None:
            self.dmin.insert ('0', str(tf.dmin))
        self.dmin.grid (row=8, column=1, sticky=W)

        ttk.Label (master, text='Graph d_max [%] ').grid (row=9, column=0, sticky=E)
        self.dmax = ttk.Entry (master, width=10)
        if tf.dmax != None:
            self.dmax.insert ('0', str(tf.dmax))
        self.dmax.grid (row=9, column=1, sticky=W)

        ttk.Label (master, text='Graph h_min [%] ').grid (row=10, column=0, sticky=E)
        self.hmin = ttk.Entry (master, width=10)
        if tf.hmin != None:
            self.hmin.insert ('0', str(tf.hmin))
        self.hmin.grid (row=10, column=1, sticky=W)

        ttk.Label (master, text='Graph h_max [%] ').grid (row=11, column=0, sticky=E)
        self.hmax = ttk.Entry (master, width=10)
        if tf.hmax != None:
            self.hmax.insert ('0', str(tf.hmax))
        self.hmax.grid (row=11, column=1, sticky=W)

        ttk.Label (master, text='Graph s_min [%] ').grid (row=12, column=0, sticky=E)
        self.smin = ttk.Entry (master, width=10)
        if tf.smin != None:
            self.smin.insert ('0', str(tf.smin))
        self.smin.grid (row=12, column=1, sticky=W)

        ttk.Label (master, text='Graph s_max [%] ').grid (row=13, column=0, sticky=E)
        self.smax = ttk.Entry (master, width=10)
        if tf.smax != None:
            self.smax.insert ('0', str(tf.smax))
        self.smax.grid (row=13, column=1, sticky=W)

        return None

    def apply(self):
        tf = self.parent.tourfile
        tf.title = self.tourtitle.get()
        date = self.date.get()
        if date != None and date != '':
            tf.date = datetime.datetime.strptime (date, "%Y-%m-%d")
        tf.copyright = self.copyright.get()
        dmin = self.dmin.get()
        try:
            tf.dmin = (float(dmin) if dmin != '' else None)
        except ValueError:
            pass
        dmax = self.dmax.get()
        try:
            tf.dmax = (float(dmax) if dmax != '' else None)
        except ValueError:
            pass
        hmin = self.hmin.get()
        try:
            tf.hmin = (float(hmin) if hmin != '' else None)
        except ValueError:
            pass
        hmax = self.hmax.get()
        try:
            tf.hmax = (float(hmax) if hmax != '' else None)
        except ValueError:
            pass
        smin = self.smin.get()
        try:
            tf.smin = (float(smin) if smin != '' else None)
        except ValueError:
            pass
        smax = self.smax.get()
        try:
            tf.smax = (float(smax) if smax != '' else None)
        except ValueError:
            pass
        
# ----------------------------------------

class SmoothDialog (tkSimpleDialog.Dialog):

    _smoothMethods = (
        ('Curve length', tourfilesmooth.TFLength),
        ('2nd derivative', tourfilesmooth.TFD2Square)
        )

    def body(self, master):
        self.title('Smoothing')

        tf = self.parent.tourfile

        self.scaleFlag = IntVar(value=0)
        cb = ttk.Checkbutton (master, text='Scale height', variable=self.scaleFlag, command=self.cbScaleFlag)
        cb.grid(row=1, column=0)

        self.startHeight = IntVar(value=tf.get(0, 'height'))
        ttk.Label (master, text='Start height:').grid (row=2, column=0)
        self.entryStartHeight = e = ttk.Entry (master, textvariable=self.startHeight, state=DISABLED )
        e.grid (row=2, column=1)

        self.endHeight = IntVar(value=tf.get(-1, 'height'))
        ttk.Label (master, text='End height:').grid (row=3, column=0)
        self.entryEndHeight = e = ttk.Entry (master, textvariable=self.endHeight, state=DISABLED)
        e.grid (row=3, column=1)

        ttk.Label (master, text='Smooth method:').grid (row=4, column=0)
        self.cbSmoothMethod = cb = ttk.Combobox (
            master, state='readonly', values=tuple([sm[0] for sm in self._smoothMethods]))
        cb.set (self._smoothMethods[0][0])
        cb.grid (row=4, column=1)
        return None

    def cbScaleFlag(self):
        if self.scaleFlag.get():
            state=NORMAL
        else:
            state=DISABLED
        self.entryStartHeight.config (state=state)
        self.entryEndHeight.config (state=state)

    def apply(self):
        scaleFlag = bool(self.scaleFlag.get())
        if scaleFlag:
            startHeight = int(self.entryStartHeight.get())
            endHeight = int(self.entryEndHeight.get())
        smDict = dict(self._smoothMethods)
        tf = smDict[self.cbSmoothMethod.get()]
        # do it!
        p = self.parent
        if scaleFlag:
            p.tourfile.smooth (p.fixedRows, tf, startHeight, endHeight)
        else:
            p.tourfile.smooth (p.fixedRows, tf)
        p.refresh()
        p.dirty(True)

# ----------------------------------------

class AboutBox (Toplevel):

    def __init__(self, parent):
        Toplevel.__init__(self, parent)
        self.title('About TourEditor')
        self.transient(parent)
        ttk.Label(self, text='TourEditor '+__version__).grid (row=0, column=0)
        ttk.Label(self, text=u'© 2010-2012 Frank Pählke <frank@kette-links.de>').grid (row=1, column=0)
        ttk.Label(self, borderwidth=2, relief=SUNKEN,
                  text="""TourEditor is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

TourEditor is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with TourEditor.  If not, see <http://www.gnu.org/licenses/>.""").grid (row=2, column=0)
        ttk.Button(self, text='OK', command=self.destroy).grid(row=3, column=0)
        self.grab_set()
        self.wait_window()

# ----------------------------------------

class TourEditor (Tk):
    "main application window"

    def __init__ (self):
        Tk.__init__ (self)
        self.title ('Tour Editor')
        l = ttk.Label (text='Encoding:')
        l.pack (side=LEFT)
        c = ttk.Combobox(values=_encodings)
        c.set ('iso-8859-1')
        c.pack (side=LEFT)
        self.encodingBox = c
        b = ttk.Button (text='Open File', command=self.open)
        b.pack (side=LEFT)
        b = ttk.Button (text='About', command=self.about)
        b.pack (side=LEFT)
        b = ttk.Button (text='Exit', command=self.quit)
        b.pack (side=LEFT)

    def open (self):
        filename = tkFileDialog.askopenfilename (
            title='Open File', filetypes=_filetypes)
        if filename != None and filename != '':
            encoding = self.encodingBox.get()
            TourView (TourFile.read (filename, encoding))

    def about (self):
        aboutBox = AboutBox(self)

# ----------------------------------------
