# -*- coding: utf-8 -*-
"""render html stright from python.

'stright from' means without involving a templating language or 'engine'.
Sometimes you just don't want to involve a whole 'engine' and a language just to render html.

Note: this renderer generates ugly, invalid html. It's only good for quick'n'dirty personal 
reporting.  For externally visible documents, use one of the many production worthy templating engines.

### 
     with r.Table():
         for k,v in data.items():
             with r.Tr():
                 with r.Td():
                     r.text(k)
                 with r.Td():
                     r.text(v)
### todo:
* make an effort to comply..
* should build a tree, then render for better control.
"""
import cgi

class Node(object):

    def __init__(self, renderer, name, **opt):
        self.renderer=renderer
        self.name=name

    def __repr__(self):
        return '<%s />' % self.name

    def __enter__(self):
        self.out(self.open())
        self.renderer.path.append(self)

    def __exit__(self, typ, value, tb):
        n=self.renderer.path.pop()
        assert n==self, (n, self)
        self.out(self.close())

    def tag(self):
        return self.name.lower()

    def open(self):
        return '<%s %s>' % (self.tag(), '')

    def close(self):
        return '</%s>' % self.tag()

    def out(self, *vals):
        self.renderer.out(self.renderer.prefix(), *vals)

def dump(line):
    print line

class Render(object):

    capital=set(map(chr,range(ord('A'), ord('Z'))))

    def __init__(self, out=None):
        self.path=[]
        self._lines=[]
        if out:
            self._out=out
        else:
            self._out=self._lines.append

    def lines(self):
        """returned the generated document as lines.
        not available if 'out' arg was used.
        """
        return self._lines

    def __getattr__(self, a):
        if a[0] in self.capital:
            # type('SubClass', (EntityResource,), {})
            return lambda : Node(self, a)
        raise AttributeError(a)

    def text(self, val):
        self.out(cgi.escape(str(val)))

    def prefix(self):
        return ' ' * len(self.path)

    def out(self, *vals):
        self._out(' '.join(map(str,filter(None,vals))))
