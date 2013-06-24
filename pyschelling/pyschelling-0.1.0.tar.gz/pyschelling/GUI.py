import logging
import pygtk
pygtk.require('2.0')
import gtk

from model import Model
from random import random

from gobject import timeout_add
import cairo

class gtkGrid(gtk.DrawingArea):
    def __init__(self, grid):
        super(gtk.DrawingArea, self).__init__()
        self.grid = grid
        self.connect("expose_event", self.expose)

    def expose(self, widget, event):
        self.context = widget.window.cairo_create()
        self.context.rectangle(event.area.x, event.area.y, event.area.width, event.area.height)
        self.context.clip()
        self.draw(self.context)

    def draw(self, cr):
        rect = self.get_allocation()
        cr.set_source_rgb(0, 0, 0)
        cr.rectangle(0, 0, rect.width, rect.height)
        cr.fill()
        cr.set_line_width(0.25)
        coefficients = float(rect.width)/self.grid.width, float(rect.height)/self.grid.height
        for cell in self.grid.cells:
            cell.draw(cr, *coefficients)

class GUI(object):
    def __init__(self, width, height, density=0.5, types=['R', 'G', 'B'], minth=0.3, maxth=0.6, timeout=200):
        window = gtk.Window()
        window.resize(600, 600)
        window.set_position(gtk.WIN_POS_CENTER)
        window.set_title("Schelling segregation")
        window.connect("destroy", gtk.main_quit)
        self.model = Model(width=width, height=height, density=density, types=types, minth=minth, maxth=maxth)
        self.grid = gtkGrid(self.model.grid)
        window.add(self.grid)
        window.show_all()
        timeout_add(timeout, self.step)

    def step(self):
        self.model.step()
        self.grid.queue_draw()
        return True

def main():
    th = (random(), random())
    minth, maxth = min(th), max(th)
    density = 0.7 + random() * 0.3
    print "(%4.2f - %4.2f) @ %4.2f" % (minth, maxth, density)
    gui = GUI(75, 75, density=density, minth=minth, maxth=maxth, timeout=350)
    gtk.main()

if __name__ == "__main__":
    main()
