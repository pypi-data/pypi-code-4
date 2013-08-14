# -*- coding: latin-1 -*-


"""
Demo of Math Typesetting
~~~~~~~~~~~~~~~~~~~~~~~~

The purpose of this demo is to show how to do some non trivial
typesetting. 

Usually text is linear, i.e. it consists of characters and one
character follows the other. This is what simple text editor can
display. However in real life, text can be nested. This means that
there are certain text elements which itself contain texts. Think of
tables or math formulas.

"""

import sys
sys.path.append('..')

from textmodel import listtools
from textmodel.base import NewLine, Group, Characters, partition, group, defaultstyle
from textmodel.textmodel import TextModel
from wxtextview.layout import HBox, VBox, Row, Rect, Layout

from copy import copy as shallowcopy



class Container:
    # Im Grunde muss nur get_childs implementiert werden. Später
    # evt. get_region.

    def __len__(self):
        n = 0
        for texel in self.get_childs():
            n += len(texel)
        return n

    def get_content(self):
        return Group(self.get_childs())

    def iter(self):
        j1 = 0
        for child in self.get_childs():
            j2 = j1+len(child)
            yield j1, j2, child
            j1 = j2
        
    def get_text(self):
        return self.get_content().get_text()
        
    def get_style(self, i):
        return self.get_content().get_style(i)

    def get_linelengths(self):
        return self.get_content().get_linelengths()

    def get_styles(self, i1, i2):
        return ()

    def set_styles(self, i0, styles):
        return self

    def set_properties(self, i1, i2, properties):
        return self
        
    def split(self, i):
        return self.get_content().split(i)

    def takeout(self, i1, i2):
        k1, k2, items = listtools.get_items(self.get_childs(), i1, i2)
        if len(items) == 0:
            return self, NULL_TEXEL
        if len(items)>1:
            raise IndexError, (i1, i2)
        item = items[0]
        rest, part = item.takeout(i1-k1, i2-k1)
        return self.replace(item, rest), part

    def insert(self, i, texel):
        for j1, j2, elem in self.iter():
            if isinstance(elem, Empty):
                continue
            if j1 <= i <= j2:
                new = elem.insert(i-j1, texel)
                return self.replace(elem, new)

        if i == 0: # muss ein empty_first haben!
            return Group([texel, self])

        # muss ein empty_last haben
        assert i == len(self)
        return Group([self, texel])

    def replace(self, elem, new):
        # default: unelegant aber klappt
        found = False
        for name, value in self.__dict__.items():
            if value is elem:
                found = True
                break
        if not found:
            raise Exception, "Element not found", elem
        clone = shallowcopy(self)
        setattr(clone, name, new)
        return clone

    def simplify(self, i):
        return self



class Empty:
    style = defaultstyle
    def __repr__(self):
        return 'Empty()'
    
    def __len__(self):
        return 1

    def get_linelengths(self):
        return ()

    def get_style(self, i):
        return self.style

    def get_text(self):
        return ' '

    def simplify(self, i):
        return self


class EmptyBox:    
    width = 0
    depth = 0
    length = 1
    def __init__(self, style, layout):
        self.style = style
        self.height = layout.measure('M', style)[1]

    def __repr__(self):
        return 'EmptyBox()'

    def __len__(self):
        return self.length

    def extend_range(self, i1, i2):
        return i1, i2
    
    def draw(self, x, y, dc, styler):
        pass

    def draw_cursor(self, i, x, y, dc):
        import wx
        if 'msw' in wx.version() or 'gtk' in wx.version():
            dc.Blit(x, y, 2, self.height, dc, x, y, wx.SRC_INVERT)
        elif 'mac' in wx.version():
            dc.SetLogicalFunction(wx.INVERT)
            dc.SetBrush(wx.BLACK_BRUSH)
            dc.DrawRectangle(x, y, 2, self.height)

    def draw_selection(self, i1, i2, x, y, dc):
        pass

    def get_rect(self, i, x, y):
        return Rect(0, 0, 0, 0)

    def get_index(self, x, y):
        return 0

    def can_append(self):
        return False


def empty_handler(self, texel, i1, i2):
    tb = EmptyBox(texel.style, self)
    return [tb]
Layout.Empty_handler = empty_handler


class Fraction(Container):
    def __init__(self, denominator=(), nominator=()):
        self.empty1 = Empty()
        self.denominator = group(denominator)
        self.empty2 = Empty()
        self.nominator = group(nominator)
        self.empty3 = Empty()        

    def get_childs(self):
        return self.empty1, self.denominator, self.empty1, \
            self.nominator, self.empty2


class FractionBox(VBox):
    def __init__(self, texel, i1, i2, factory):
        c0 = factory.create_boxes(texel.empty1)
        c1 = factory.create_boxes(texel.denominator)
        c2 = factory.create_boxes(texel.empty2)
        c3 = factory.create_boxes(texel.nominator)
        c4 = factory.create_boxes(texel.empty3)
        self.childs = c0+(Row(c1+c2, self), Row(c3+c4, self))
        self.layout()

    def iter(self, i, x, y):
        j1 = i
        height = self.height
        width = self.width
        for child in self.childs:
            j2 = j1+child.length
            if not isinstance(child, EmptyBox):
                yield j1, j2, x+0.5*(width-child.width), y, child
                y += max(10, child.height)
            else:
                yield j1, j2, x, y, child
            j1 = j2

    def can_append(self):
        return False
            
    def layout(self):
        # w, h und length bestimmen
        assert len(self.childs)
        self.height = self.width = 0 # Trick
        n = w = 0
        for j1, j2, x, y, child in self.iter(0, 0, 0):
            n += child.length
            w = max(child.width, w)
            y += child.height
        self.width = w
        self.depth = self.childs[0].height/2
        self.height = y-self.depth
        self.length = n

    def draw(self, x, y, dc, styler):
        VBox.draw(self, x, y, dc, styler)
        h = self.childs[1].height
        dc.DrawLine(x, y+h, x+self.width, y+h)

    def extend_range(self, i1, i2):
        for j1, j2, x, y, child in self.iter(0, 0, 0):
            if not (i1<j2 and j1<i2):
                continue
            if isinstance(child, EmptyBox):
                i1 = min(i1, 0)
                i2 = max(i2, len(self))
            else:
                k1, k2 = child.extend_range(i1-j1, i2-j1)
                i1 = min(i1, k1+j1)
                i2 = max(i2, k2+j1)
        return i1, i2

        
def fraction_handler(self, texel, i1, i2):
    return [FractionBox(texel, i1, i2, self)]
Layout.Fraction_handler = fraction_handler



class Root(Container):
    def __init__(self, content=()):
        self.empty1 = Empty()
        self.content = group(content)
        self.empty2 = Empty()

    def get_childs(self):
        return self.empty1, self.content, self.empty2


class RootBox(HBox):
    def __init__(self, texel, i1, i2, factory):
        c0 = factory.create_boxes(texel.empty1)
        c0[0].width = 10
        c1 = factory.create_boxes(texel.content)
        c2 = factory.create_boxes(texel.empty2)
        self.childs = c0+(Row(c1, self),)+c2
        self.layout()

    def can_append(self):
        return False
            
    def layout(self):
        # w, h und length bestimmen
        assert len(self.childs)
        self.height = self.width = 0 # Trick
        n = w = 0
        for j1, j2, x, y, child in self.iter(0, 0, 0):
            n += child.length
            w += child.width
            y = max(y, child.height)
        self.width = w
        self.depth = self.childs[1].depth
        self.height = y+5
        self.length = n

    def draw(self, x, y, dc, styler):
        HBox.draw(self, x, y, dc, styler)
        w = self.width
        h = self.height
        w1 = self.childs[0].width
        w2 = self.childs[1].width
        points = [
            (x, y+h/2), 
            (x+w1/2, y+h),
            (x+w1, y),
            (x+w1+w2, y),
            ]
        dc.DrawLines(points)

    def extend_range(self, i1, i2):
        for j1, j2, x, y, child in self.iter(0, 0, 0):
            if not (i1<j2 and j1<i2):
                continue
            if isinstance(child, EmptyBox):
                i1 = min(i1, 0)
                i2 = max(i2, len(self))
            else:
                k1, k2 = child.extend_range(i1-j1, i2-j1)
                i1 = min(i1, k1+j1)
                i2 = max(i2, k2+j1)
        return i1, i2
        
def root_handler(self, texel, i1, i2):
    return [RootBox(texel, i1, i2, self)]
Layout.Root_handler = root_handler





def mk_textmodel(texel):
    model = TextModel()
    model.texel = texel
    model.linelengths = texel.get_linelengths()
    return model

def test_00():
    ns = init_testing(False)
    frac = Fraction([Characters(u'Zähler')], [Characters(u'Nenner')])
    from wxtextview.layout import Layout
    model = TextModel(u'')
    layout = Layout(model)
    box = fraction_handler(layout, frac, 0, len(frac))[0]
    print box
    for j1, j2, x, y, child in box.iter(0, 0, 0):
        print j1, j2, x, y, child
    #assert box.is_empty(0)

def test_01():
    ns = init_testing(False)
    model = ns['model']
    model.remove(0, len(model))
    model.insert(0, TextModel(__doc__))

    text = """Below you see a fraction, which is a special text element and which
contains other text in the nominator and denominator.

Try to edit the following formula:

        tan(x) = """
    model.insert(len(model), TextModel(text))
    frac = Fraction([Characters(u'sin(x)')], [Characters(u'cos(x)')])
    model.insert(len(model), mk_textmodel(frac))
    text = """
Ok, it is not perfect yet. But I hope you get an idea of what is 
possible. 
"""
    model.insert(len(model), TextModel(text))

    view = ns['view']
    view.cursor = len(model)
    return ns

def test_02():
    "insert/remove"
    ns = init_testing(False)
    model = ns['model']
    frac = Fraction([Characters(u'Zähler')], [Characters(u'Nenner')])
    model.insert(5, mk_textmodel(frac))
    model.insert_text(6, 'test')
    model.remove(6, 7)

def test_03():
    ns = init_testing(False)
    model = mk_textmodel(Characters('0123456789'))
    frac = mk_textmodel(Fraction([Characters(u'Zähler')], [Characters(u'Nenner')]))
    tmodel = model.get_text()
    tfrac = frac.get_text()
    for i in range(len(tfrac)):
        frac.insert(i, model)

        tmp = tfrac[:i]+tmodel+tfrac[i:]
        #print repr(frac.get_text()), repr(tmp)
        assert tmp == frac.get_text()

        frac.remove(i, i+len(model))
        assert tfrac == frac.get_text()

def test_04():
    ns = init_testing(False)
    model = ns['model']
    frac = Fraction([Characters(u'Zähler')], [Characters(u'Nenner')])
    model.insert(5, mk_textmodel(frac))
    root = Root([Characters(u'1+x')])
    model.insert(20, mk_textmodel(root))

    view = ns['view']
    view.cursor = 5
    view.selection = 3, 6    
    return ns


def test_05():
    ns = init_testing(True)
    model = ns['model']
    model.remove(0, len(model))
    model.insert_text(0, '\n')
                 
    frac = Fraction([Characters(u'Zähler')], [Characters(u'Nenner')])
    model.insert(1, mk_textmodel(frac))
    model.insert_text(1, 'Bruch = ')
    n = len(model)
    root = Root([Characters(u'1+x')])
    model.insert(n, mk_textmodel(root))
    model.insert_text(n, '\nWurzel = ')

    view = ns['view']
    view.cursor = 5
    view.selection = 3, 6    
    return ns




def demo_00():
    ns = test_01()
    from wxtextview import testing
    testing.pyshell(ns)    
    ns['app'].MainLoop()


def demo_01():
    ns = test_05()
    import testing
    testing.pyshell(ns)    
    ns['app'].MainLoop()
    
if __name__ == '__main__':
    from wxtextview.wxtextview import init_testing
    if 0:
        import alltests
        alltests.dotests()
    else:
        demo_00()
