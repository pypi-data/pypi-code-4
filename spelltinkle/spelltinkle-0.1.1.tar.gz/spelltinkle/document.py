from logging import debug

from .view import View
from .history import History
from .color import Color


class Document:
    def __init__(self, view=None):
        self.lines = ['']
        self.modified = False
        self.lastsearchstring = ''
        self.changes = None
        self.view = view or View(self)
        self.views = [self.view]
        self.history = History()
        self.color = Color(self)
        self.filename = None

    def change(self, c1, r1, c2, r2, lines, remember=True):
        self.color.stop()
        c3 = c1
        r3 = r1
        if c1 != c2 or r1 != r2:
            oldlines = self.delete_range(c1, r1, c2, r2)
        else:
            oldlines = ['']
        if lines != ['']:
            self.insert_lines(c1, r1, lines)
            r3 = r1 + len(lines) - 1
            if r3 == r1:
                c3 = c1 + len(lines[0])
            else:
                c3 = len(lines[-1])

        self.modified = True
        if remember:
            change = (c1, r1, c2, r2, c3, r3, lines, oldlines)
            self.history.append(change)
        self.color.update(c1, r1, c2, r2, lines)
        self.changes = (r1, r2, r3)
        self.view.move(c3, r3)
        return oldlines
        
    def insert_lines(self, c, r, lines):
        start = self.lines[r][:c]
        end = self.lines[r][c:]
        self.lines[r] = start + lines[0]
        self.lines[r + 1:r + 1] = lines[1:]
        self.lines[r + len(lines) - 1] += end

    def delete_range(self, c1, r1, c2, r2):
        start1 = self.lines[r1][:c1]
        end1 = self.lines[r1][c1:]
        start2 = self.lines[r2][:c2]
        end2 = self.lines[r2][c2:]
        if r1 == r2:
            oldlines = [start2[c1:]]
            self.lines[r1] = start1 + end2
        else:
            oldlines = [end1]
            oldlines.extend(self.lines[r1 + 1:r2])
            oldlines.append(start2)
            self.lines[r1] = start1
            del self.lines[r1 + 1:r2 + 1]
            self.lines[r1] += end2
        return oldlines

    def prev(self, c, r):
        if c == 0:
            if r > 0:
                return (len(self.lines[r - 1]), r - 1)
            return (0, 0)
        return (c - 1, r)

    def next(self, c, r):
        if c == len(self.lines[r]):
            if r == len(self.lines) - 1:
                return (c, r)
            return (0, r + 1)
        return (c + 1, r)

    def write(self):
        with open(self.filename, 'w') as f:
            for line in self.lines[:-1]:
                print(line, file=f)
            if self.lines[-1]:
                print(self.lines[-1], file=f, end='')
        self.modified = False
        self.changes = 42

    def read(self, filename):
        self.filename = filename
        try:
            with open(filename) as f:
                lines = []
                line = '\n'
                for line in f.readlines():
                    lines.append(line[:-1])
                if line[-1] == '\n':
                    lines.append('')
            self.change(0, 0, 0, 0, lines, remember=False)
            self.modified = False
        except FileNotFoundError:
            pass
