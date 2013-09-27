import keyword
import tokenize
import threading
import builtins
from logging import debug


keywords = frozenset(keyword.kwlist + list(builtins.__dict__.keys()))


class NoColor:
    def __init__(self):
        self.colors = [[]]

    def stop(self):
        pass

    def update(self, c1, r1, c2, r2, lines):
        pass

    def run(self):
        pass


class Color(NoColor):
    def __init__(self, doc):
        NoColor.__init__(self)
        self.doc = doc
        self.r = None
        self._stop = None
        self.thread = None

    def stop(self):
        self._stop = True
        if self.thread:
            self.thread.join()

    def update(self, c1, r1, c2, r2, lines):
        if c1 != c2 or r1 != r2:
            start = self.colors[r1][:c1]
            end = self.colors[r2][c2:]
            if r1 == r2:
                self.colors[r1] = start + end
            else:
                self.colors[r1] = start
                del self.colors[r1 + 1:r2 + 1]
                self.colors[r1] += end
        if lines != ['']:
            start = self.colors[r1][:c1]
            end = self.colors[r1][c1:]
            self.colors[r1] = start + [0] * len(lines[0])
            self.colors[r1 + 1:r1 + 1] = [[0] * len(line)
                                          for line in lines[1:]]
            self.colors[r1 + len(lines) - 1] += end

    def run(self):
        self._stop = False
        self.thread = threading.Thread(target=self.target)
        self.thread.start()
           
    def readline(self):
        if self._stop:
            raise StopIteration
        try:
            line = self.doc.lines[self.r] + '\n'
        except IndexError:
            raise StopIteration
        self.colors[self.r] = [0] * (len(line) - 1)
        self.r += 1
        return line.encode('utf-8')

    def target(self):
        try:
            self.paint()
        except (tokenize.TokenError, IndentationError):
            pass
        
    def paint(self):
        self.r = 0

        tokenizer = tokenize.tokenize(self.readline)
        for t in tokenizer:
            if self._stop:
                break
            color = {tokenize.NAME: 0,
                     tokenize.NUMBER: 2,
                     tokenize.STRING: 3,
                     tokenize.COMMENT: 4}.get(t.type)
            if color is not None:
                if color == 0 and (t.string in keywords or
                                   t.string.startswith('__') and
                                   t.string.endswith('__')):
                    color = 1
                r1, c1 = t.start
                r2, c2 = t.end
                r1 -= 1
                r2 -= 1
                while r1 < r2:
                    line = self.colors[r1]
                    line[c1:] = [color] * (len(line) - c1)
                    r1 += 1
                    c1 = 0
                line = self.colors[r1]
                line[c1:c2] = [color] * (c2 - c1)
                debug(line)
