import curses
from math import log10

from .screen import Screen

from logging import debug


class View:
    def __init__(self, doc, has_info_line=True, show_line_numbers=True):
        self.doc = doc
        self.has_info_line = has_info_line
        self.show_line_numbers = show_line_numbers
        
        self.y1 = 0
        self.x = 0
        self.y = 0
        self.c = 0
        self.r = 0
        self.c0 = None
        
        self.ys1 = 0
        self.ys2 = 0

        self.mark = None

        self.message = None

        self.moved = False
        self.scrolled = True

        self.lines = None
        self.wn = None

    def set_screen(self, scr):
        if self.has_info_line:
            self.text = scr.subwin(scr.h - 1, scr.w, 0, 0)
            self.info = scr.subwin(1, scr.w, scr.h - 1, 0)
        else:
            self.text = scr
            self.info = None

    @property
    def pos(self):
        return self.c, self.r
        
    @pos.setter
    def pos(self, p):
        self.c, self.r = p
        
    def cr(self):
        return self.c, self.r

    def move(self, c, r=None, later=True):
        if later:
            self.moved = (c, r)
            return

        if c is None:
            if self.c0 is None:
                self.c0 = self.c
            c = self.c0
        else:
            self.c0 = None
            
        if r is None:
            r = self.r
        L = len(self.doc.lines) 
        if r >= L:
            r = L - 1
            c = len(self.doc.lines[r])
        c = min(c, len(self.doc.lines[r]))
        
        self.c = c
        self.r = r
 
        w = self.text.w - self.wn - 1
        self.y = 0
        for row, c1, c2 in self.lines:
            if row == r and c1 <= c <= c2:
                self.x = c - c1 
                if self.x == w:
                    self.y += 1
                    self.x = 0
                break
            self.y += 1
        
        h = self.text.h
        if self.y < self.y1:
            self.y1 = self.y
            self.scrolled = True
        elif self.y >= self.y1 + h:
            self.y1 = self.y + 1 - h 
            self.scrolled = True

        Y = len(self.lines)
        s1 = self.y1 / Y
        s2 = min(h, Y) / Y
        self.ys1 = int(s1 * min(h, Y))
        self.ys2 = self.ys1 + max(1, int(round(s2 * min(h, Y))))

        self.moved = False

        return self.pos

    def mouse(self, x, y):
        r, c1, c2 = self.lines[min(self.y1 + y, len(self.lines) - 1)]
        c = min(c1 + max(0, x - self.wn - 1), c2)
        self.move(c, r)

    def build(self):
        self.wn = int(log10(len(self.doc.lines))) + 1
        w = self.text.w - self.wn - 1
        self.lines = []
        for r, line in enumerate(self.doc.lines):
            c = len(line)
            for i in range(1 + c // w):
                self.lines.append((r, i * w, min((i + 1) * w, c)))

    def update(self):
        if self.doc.changes or self.lines is None:
            self.build()
        elif not self.moved:
            return

        if self.moved:
            self.move(*self.moved, later=False)

        if self.has_info_line:
            self.update_info_line()

        if self.mark:
            ca, ra = self.mark
            cb, rb = self.pos
            if (ra, ca) > (rb, cb):
                ra, ca, rb, cb = rb, cb, ra, ca
        else:
            ra = 10000
            rb = -1

        text = self.text
        
        text.erase()
        y2 = self.y1 + self.text.h
        w = text.w - self.wn - 1
        i = 0
        for r, c1, c2 in self.lines[self.y1:y2]:
            text.move(i, 0)
            cn = 15
            if self.ys1 <= i < self.ys2:
                cn = 16
            if c1 == 0:
                text.write('{:{w}} '.format(r + 1, w=self.wn), cn)
            else:
                text.write(' ' * (self.wn + 1), cn)

            line = self.doc.lines[r][c1:c2]
            try:
                colors = self.doc.color.colors[r][c1:c2]
            except IndexError:
                colors = [0] * len(line)
            m = w - len(line)
            line += ' ' * m
            colors = colors + [0] * m
            if r == self.r:
                colors = [c + 5 for c in colors]
            if ra <= r <= rb:
                if r > ra:
                    ca = 0
                if r == rb:
                    cc = cb
                else:
                    cc = len(colors)
                for c in range(ca, cc):
                    colors[c] = colors[c] % 5 + 10
            text.write(line, colors)
            i += 1
        
        if i + self.y1 == len(self.lines):
            text.move(i - 1, self.wn + 1 + c2 - c1)
            text.write(' ' * (w - c2 + c1), 17)
            
        while i < self.text.h:
            text.move(i, 0)
            text.write(' ' * w, 17)
            i += 1
        
        text.move(self.y - self.y1, self.x + self.wn + 1)
        text.refresh()
        self.scrolled = False
        self.moved = False

    def update_info_line(self):
        line = self.message

        if not line:
            if self.doc.modified:
                status = '[modified]'
            else:
                status = ''
            c, r = self.doc.view.cr()
            name = self.doc.filename
            if name is None:
                name = '[no name]'
            line = 'line:{:{w}} col:{:2} {} {}'.format(r + 1, c + 1, name,
                                                       status, w=self.wn)
        line += ' ' * (self.info.w - len(line))
        self.info.erase()
        self.info.move(0, 0)
        self.info.write(line, 17)
        self.info.refresh()
