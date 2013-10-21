#
# GingaCanvasGtk.py -- classes for the display of FITS files in
#                             Matplotlib FigureCanvas
# 
# Eric Jeschke (eric@naoj.org)
#
# Copyright (c)  Eric R. Jeschke.  All rights reserved.
# This is open-source software licensed under a BSD license.
# Please see the file LICENSE.txt for details.

import matplotlib
matplotlib.use('GTKCairo')
from  matplotlib.backends.backend_gtkcairo import FigureCanvasGTKCairo \
     as FigureCanvas

import gtk
import gobject

class GingaCanvas(FigureCanvas):
    """Ultimately, this is a QWidget (as well as a FigureCanvasAgg, etc.).
    """
    def __init__(self, fig, parent=None, width=5, height=4, dpi=100):
        FigureCanvas.__init__(self, fig)
        
        self.fitsimage = None
        
        # For message drawing
        self._msg_timer = 0

        # For optomized redrawing
        self._defer_timer = 0

        w = self
        w.set_can_focus(True)
        w.connect("configure-event", self.configure_event)
        w.connect("size-request", self.size_request)
        
    def configure_event(self, widget, event):
        rect = widget.get_allocation()
        x, y, width, height = rect.x, rect.y, rect.width, rect.height

        if self.fitsimage != None:
            #print "RESIZE %dx%d" % (width, height)
            self.fitsimage.configure(width, height)
        return True

    def size_request(self, widget, requisition):
        """Callback function to request our desired size.
        """
        width, height = 300, 300
        if self.fitsimage != None:
            width, height = self.fitsimage.get_desired_size()

        requisition.width, requisition.height = self.desired_size
        return True

    def set_fitsimage(self, fitsimage):
        self.fitsimage = fitsimage
        
        self._msg_timer.timeout.connect(fitsimage.onscreen_message_off)
        self._defer_timer.timeout.connect(fitsimage.delayed_redraw)

    def onscreen_message(self, text, delay=None, redraw=True):
        if self._msg_timer:
            try:
                gobject.source_remove(self._msg_timer)
            except:
                pass

        if self.fitsimage != None:
            self.fitsimage.message = text
            if redraw:
                self.fitsimage.redraw(whence=3)
            if delay:
                ms = int(delay * 1000.0)
                self._msg_timer = gobject.timeout_add(ms,
                                                      self.onscreen_message,
                                                      None)
    def reschedule_redraw(self, time_sec):
        try:
            gobject.source_remove(self._defer_timer)
        except:
            pass
        if self.fitsimage != None:
            self._defer_timer = gobject.timeout_add(time_ms,
                                                    self.fitsimage.delayed_redraw)


#END
