# -*- coding: latin-1 -*-




"""
Konzept:

Es soll ein StyleText-Editor ähnlich Scite geschriebne werden. Es soll
reiner Text bearbeitet werden. Der Text kann Formatinformationen
enthalten, u.A. Schriftgröße und Farbe.  

Dieser View ist ein Experiment. Es wird zwischendem einfachen
Datenmodell und der grafischen Darstellung unterschieden. Das
Datenmodell ist wie bisher aufgebaut. Die Darstellung ist ein Baum und
enthält die Boxen. Ein Box enthält dabei Informationen über die
Position am Bildschirm, Breit, Höhe, ... .Boxen und Modell lassen sich
über den Index zuordnen.

Da das Modell nur einfachen Text und keine komplexen Container
enthält, ist der Darstellungsbaum sehr einfach aufgebaut. Er besteht
aus einer Liste von Zeilen. Eine Zeile enthält eine Liste von
Reihen. Eine Reihe wiederum besteht aus einer Liste von Boxen.

line <-> [row0, row1, row2]
mit row0 = [box0, box1, ..., boxn]
"""




from textmodel import listtools
from textmodel import TextModel, NewLine, Group, Characters, defaultstyle
from math import ceil





class Rect:
    def __init__(self, x1, y1, x2, y2):
        self.x1 = min(x1, x2)
        self.y1 = min(y1, y2)
        self.x2 = max(x1, x2)
        self.y2 = max(y1, y2)
        
    def __repr__(self):
        return 'Rect%s' % repr((self.x1, self.y1, self.x2, self.y2))



def combine_rects(r1, r2):
    if r1 is None:
        return r2
    elif r2 is None:
        return r1
    r = Rect(0, 0, 0, 0)
    r.x1 = min(r1.x1, r2.x1)
    r.x2 = max(r1.x2, r2.x2)
    r.y1 = min(r1.y1, r2.y1)
    r.y2 = max(r1.y2, r2.y2)
    return r



class IterBox:
    width = 0
    height = 0
    depth = 0
    length = 0
    childs = ()

    def __init__(self, layout):
        self._layout = layout

    def dump(self, i, x, y, indent=0):
        print " "*indent, i, i+len(self), x, y, self
        for j1, j2, x1, y1, child in self.iter(i, x, y):
            child.dump(j1, x1, y1, indent+4)
        
    def __len__(self):
        return self.length

    def iter(self, i, x, y):
        raise NotImplemented

    def riter(self, i, x, y):
        return reversed(tuple(self.iter(i, x, y)))

    def extend_range(self, i1, i2):
        for j1, j2, x1, y1, child in self.iter(0, 0, 0):
            if i1 < j2 and j1 < i2:
                k1, k2 = child.extend_range(i1-j1, i2-j1)
                i1 = min(i1, k1+j1)
                i2 = max(i2, k2+j1)
        return i1, i2

    def draw(self, x, y, dc, styler):
        raise NotImplementedError()

    def draw_cursor(self, i, x0, y0, dc):
        raise NotImplementedError()

    def draw_selection(self, i1, i2, x, y, dc):
        raise NotImplementedError()

    def get_rect(self, i, x0, y0):
        was_empty = False
        for j1, j2, x1, y1, child in self.iter(0, x0, y0):
            if i == j2 and not child.can_append():
                was_empty = True        
            elif j1 <= i <= j2:                
                return child.get_rect(i-j1, x1, y1)
            else:
                was_empty = False
        assert was_empty
        return child.get_rect(i-j1, x1, y1)

    def get_index(self, x, y):
        # Sucht die zu (x,y) nächstgelegene Indexposition. Es wird
        # immer ein Index zurückgegeben, selbst wenn (x, y) ausserhalb
        # der Box liegt.
        raise NotImplemented

    def can_append(self):
        elem = None
        for j1, j2, x, y, elem in self.iter(0, 0, 0):
            pass
        if elem is not None:
            return elem.can_append()
        return False # XXX der Container ist leer! Kann das vorkommen?
        



class HBox(IterBox):
    # Richtet seine Kinder in einer horizontalen Reihe aus
    def iter(self, i, x, y):
        height = self.height
        j1 = i
        for child in self.childs:
            j2 = j1+child.length
            yield j1, j2, x, y+height-child.height, child
            x += child.width
            j1 = j2

    def get_index(self, x, y):
        if x <= 0:
            return 0 
        child = None
        for j1, j2, x1, y1, child in self.riter(0, 0, 0):
            if x1 <= x <= x1+child.width:
                i = child.get_index(x-x1, y-y1)
                if i == len(child) and not child.can_append():
                    continue
                return j1+i
        # Keine Indexposition innerhalb eines Kinds gefunden!
        if child is None:
            # etwas umständlicher Weg um zu erfragen, ob die Box
            # Kinder hat
            return 0
        
        # x ist nicht links von der Box und in keinem keinem Kind ->
        # die nächste Indexposition ist der rechte Rand
        return len(self)



class VBox(IterBox):
    # Stapelt die Kinderboxen übereinander
    def iter(self, i, x, y):
        j1 = i
        for child in self.childs:
            j2 = j1+child.length
            yield j1, j2, x, y, child
            y += child.height+child.depth
            j1 = j2
        
    def get_index(self, x, y):
        if y <= 0:
            return 0 
        child = None
        for j1, j2, x1, y1, child in self.iter(0, 0, 0):
            if y1 <= y <= y1+child.height+child.depth:
                i = child.get_index(x-x1, y-y1)
                if i == j2-j1 and not child.can_append():
                    continue
                return j1+i
        # Keine Indexposition innerhalb eines Kinds gefunden!
        if child is None:
            # etwas umständlicher Weg um zu erfragen, ob die Box
            # Kinder hat
            return 0
        
        # y ist nicht oberhalb der Box und in keinem keinem Kind ->
        # die nächste Indexposition ist der rechte untere Rand
        # x ist nicht links von der Box und in keinem keinem Kind ->
        # die nächste Indexposition ist der rechte Rand
        return len(self)
        

    
class TextBox(HBox):
    def __init__(self, text, style, layout):
        HBox.__init__(self, layout)
        self.text = text
        self.style = style
        self.update()

    def __repr__(self):
        return "TB(%s)" % repr(self.text)

    def can_append(self):
        return True
        
    def update(self):
        measure = self._layout.measure
        self.width, h = measure(self.text, self.style)
        self.height = ceil(h)
        self.length = len(self.text)

    def draw(self, x, y, dc, styler):
        raise NotImplementedError()

    def draw_selection(self, i1, i2, x, y, dc):
        raise NotImplementedError()

    def get_rect(self, i, x0, y0):
        text = self.text
        measure = self._layout.measure
        i = max(0, i)
        i = min(len(text), i)
        x1 = x0+measure(text[:i], self.style)[0]
        x2 = x1+measure('m', self.style)[0]
        return Rect(x1, y0, x2, y0+self.height)

    def removed(self, i, n):
        # XXX momentan nicht verwendet. Wäre effizienter. 
        i1 = max(0, i)
        i2 = min(i+n, self.length)
        length = self.length
        self.text = self.text[:i1]+self.text[i2:]
        self.update()
        assert self.length == length-i2+i1

    def get_index(self, x, y):
        if x<= 0:
            return 0
        measure = self._layout.measure
        x1 = 0
        for i, char in enumerate(self.text):
            x2 = x1+measure(char, self.style)[0]
            if x1 <= x and x <= x2:
                if x-x1 < x2-x:
                    return i
                return i+1
            x1 = x2
        return self.length

    def split(self, w):
        text = self.text
        parts = self._layout.measure_parts(text, self.style)
        for i, part in enumerate(parts):
            if part >= w:
                b1 = TextBox(text[:i], self.style, self._layout)
                b2 = TextBox(text[i:], self.style, self._layout)
                if b1.width > w:
                    print "split:", repr(text[:i]), repr(text[i:])
                assert b1.width <= w
                return b1, b2
        return self, TextBox(u'', self.style)


        
class NewLineBox(TextBox):
    def __init__(self, style, layout):        
        TextBox.__init__(self, '\n', style, layout)
        self.width = 0

    def can_append(self):
        return False

    def get_index(self, x, y):
        return 0



class Row(HBox):
    def __init__(self, childs, layout):
        HBox.__init__(self, layout)
        self.childs = tuple(childs)
        self.layout()

    def layout(self):
        length = w = h = d = 0
        for child in self.childs:
            length += child.length
            w += child.width
            h = max(h, child.height)
            d = max(d, child.depth)
        self.length = length
        self.width = w
        self.height = h
        self.depth = d

    def get_index(self, x, y):
        i = HBox.get_index(self, x, y)
        return min(i, len(self)-1)




class Paragraph(VBox):
    # Ein Paragraph enthält eine Textzeile bis zu einem NewLine. Der
    # Paragraph wird in eine oder mehrere Zeilen (Rows) umgebrochen.

    _maxw = 0 #  Max Zeilenbreite. Bei 0 wird nicht umgebrochen.
    def __init__(self, textboxes, layout, maxw=0):
        assert isinstance(layout, Layout)
        self._layout = layout
        self._maxw = maxw
        self.textboxes = textboxes
        self.layout()

    def properties_changed(self, model, i0, i1, i2):
        boxes = self.textboxes
        j1, j2 = listtools.get_envelope(boxes, i1, i2)
        new = self._layout.create_boxes(model.texel, i0+j1, i0+j2)
        self.textboxes = listtools.replace(boxes, j1, j2, new)
        self.layout()

    def inserted(self, model, i0, i, n):
        # XXX momentan nicht verwendet. Wäre effizienter. 
        layout = self._layout
        length = self.length
        textboxes = self.textboxes

        j1, j2 = listtools.get_interval(textboxes, i)
        boxes = self._layout.create_boxes(model.texel, i0+j1, i0+j2+n)
        assert listtools.calc_length(boxes) == j2+n-j1
        textboxes = listtools.replace(textboxes, j1, j2, boxes)
        assert length+n == listtools.calc_length(textboxes)        
        r = []
        p = []
        maxw = self._maxw
        for box in textboxes:
            p.append(box)
            if isinstance(box, NewLineBox):
                r.append(Paragraph(p, layout, maxw=maxw))
                p = []
        if p:
            r.append(Paragraph(p, layout, maxw=maxw))
        assert length+n == listtools.calc_length(r)
        return tuple(r)

    def set_maxw(self, maxw):
        if self._maxw == maxw:
            return
        self._maxw = maxw
        self.layout()
        
    def removed(self, i, n):
        # XXX momentan nicht verwendet. Wäre effizienter. 
        length = self.length
        i1 = max(0, i)
        i2 = min(length, i+n)
        #print "paragraph removed", i1, i2
        j1 = 0
        new = []
        for box in self.textboxes:
            j2 = j1+len(box)
            if j2<=i1 or j1>=i2: # außerhalb
                new.append(box)
            elif j1>=i1 and j2<= i2: # innerhalb
                pass
            else: # geschnitten
                box.removed(i-j1, n)
                new.append(box)
            j1 = j2
        self.textboxes = tuple(new)
        self.layout()
        assert self.length == length-i2+i1
                        
    def layout(self):
        # Die Paragraphen in Zeilen umbrechen
        layout = self._layout
        maxw = self._maxw
        rows = []
        l = []
        w = 0
        for box in self.textboxes:
            while maxw and w+box.width > maxw:
                # neue Reihe anfangen
                a, b = box.split(maxw-w)

                if a.length > 1:
                    # Könnte gebrochen werden
                    if not a.width <= maxw-w:
                        print "Wrong split:", repr(a.text)
                    assert a.width <= maxw-w

                if a.length:
                    l.append(a)
                box = b
                row = Row(l, layout)
                if maxw and row.length>1:
                    if row.width > maxw:
                        print "___"
                        for child in row.childs:
                            print child.width, child
                    assert row.width <= maxw
                rows.append(row)
                l = []
                w = 0
            if box.length:
                l.append(box)
                w += box.width
                if maxw:
                    assert w <= maxw
        if l:
            row = Row(l, self._layout)
            if maxw: 
                assert row.width <= maxw
            rows.append(row)

        length = w = h = 0
        for row in rows:
            w = max(w, row.width)
            h += row.height
            length += row.length
            if maxw:
                assert w <= maxw
            
        self.width = w
        self.height = h
        if rows:
            self.depth = rows[-1].depth
        else:
            self.depth = 0
        self.length = length
        self.childs = tuple(rows)




# XXX wenn das modell leer ist oder auf eine NL endet, dann wird ein
# zusätzlicher leerer Paragraph eingfügt. Der leere Paragraph nimmt Anfügungen am 
# Textende an. Paragraph sollten can_append auf False haben, wenn Sie mit NL enden, 
# ansonsten auf True

class Layout(VBox):
    # Das Layout ist eine Liste von Paragraphen, die
    # untereinandergestapelt werden.
    _maxw = 0
    def __init__(self, model, maxw=0):
        self._maxw = maxw
        self._model = model
        self.inserted(0, len(model))
        self.layout()

    def properties_changed(self, i1, i2):
        for j1, j2, child in listtools.intersecting_items(self.childs, i1, i2):
            child.properties_changed(self._model, j1, i1-j1, i2-j1)

    def create_paragraphs(self, i1, i2):
        return Paragraph((), self, maxw=self._maxw).\
            inserted(self._model, i1, 0,i2-i1)        

    def inserted(self, i, n):
        # Nicht besonders effizient: bei jeder Einfügung wird der
        # entsprechende Paragraph komplett neu erzeugt. Dabei könnten
        # die meisten TextBoxes wiederverwendet werden.
        length = self.length
        paragraphs = self.childs
        model = self._model
        j1, j2 = listtools.get_interval(paragraphs, i)
        if i == len(self) and len(self):
            child = self.childs[-1]
            if child.can_append():
                j1 -= len(child)
        new = self.create_paragraphs(j1, j2+n)
        self.childs = listtools.replace(paragraphs, j1, j2, new)
        self.layout()
        assert self.length == length+n

    def removed(self, i, n):
        length = self.length
        paragraphs = self.childs
        model = self._model
        j1, j2 = listtools.get_envelope(paragraphs, i, i+n+1) # +1 wg NewLine!
        assert j2-j1 >= n
        new = self.create_paragraphs(j1, j2-n)
        self.childs = listtools.replace(paragraphs, j1, j2, new)
        self.layout()
        assert self.length == length-n

    def set_maxw(self, maxw):
        if maxw == self._maxw:
            return
        self._maxw = maxw
        for paragraph in self.childs:
            paragraph.set_maxw(maxw)
        self.layout()

    def measure(self, text, style):
        return len(text), 1

    def measure_parts(self, text, style):
        return tuple(range(1, len(text)))

    def get_laststyle(self):
        model = self._model
        if len(model):
            return model.get_style(len(model)-1)
        return defaultstyle
        
    def layout(self):
        # w, h, length bestimmen
        measure = self.measure
        w = h = length = 0
        box = None
        for box in self.childs:
            length += box.length
            w = max(w, box.width)
            h = h+box.height
        if box is None or not box.can_append():
            # Die Box ist None oder hört mit einem NL auf
            _w, _h = measure('M', self.get_laststyle())
            h += _h
        self.width = w
        self.height = h
        self.length = length

    def get_rect(self, i, x0, y0):
        assert i >= 0
        assert i <= len(self)
        if i == len(self):
            if len(self) == 0:
                w, h = self.measure('M', self.get_laststyle())
                return Rect(0, 0, w, h)

            for j1, j2, x1, y1, child in self.iter(i, x0, y0):
                pass

            if not child.can_append():
                r = VBox.get_rect(self, i, x0, y0)
                w = r.x2-r.x1
                h = r.y2-r.y1
                return Rect(0, r.y2, w, r.y2+h)
        return VBox.get_rect(self, i, x0, y0)

    def create_boxes(self, texel, i1=None, i2=None):
        if i1 is None:
            assert i2 is None
            i1 = 0 
            i2 = len(texel)
        else:
            assert i1 <= i2
            i1 = max(0, i1)
            i2 = min(len(texel), i2)
        name = texel.__class__.__name__+'_handler'
        handler = getattr(self, name)
        boxes = handler(texel, i1, i2)
        assert i2-i1 == listtools.calc_length(boxes)
        return tuple(boxes)

    def Group_handler(self, texel, i1, i2):
        r = []
        j1 = 0
        for child in texel.data:
            j2 = j1+len(child)
            if i1 < j2 and j1 < i2: # Test auf Überlapp -> Alle Texel,
                                    # die im Intervall [i1, i2] liegen
                                    # oder es schneiden
                r.extend(self.create_boxes(child, i1-j1, i2-j1))
            j1 = j2
        return r

    def Characters_handler(self, texel, i1, i2):
        return [TextBox(texel.data[i1:i2], texel.style, self)]

    def NewLine_handler(self, texel, i1, i2):
        return [NewLineBox(texel.style, self)] # XXX: Hmmmm



testtext = u"""Ein männlicher Briefmark erlebte
Was Schönes, bevor er klebte.
Er war von einer Prinzessin beleckt.
Da war die Liebe in ihm geweckt.
Er wollte sie wiederküssen,
Da hat er verreisen müssen.
So liebte er sie vergebens.
Das ist die Tragik des Lebens.

(Joachim Ringelnatz)"""


def test_00():
    model = TextModel(testtext)
    layout = Layout(model)
    i1 = 0
    for paragraph in layout.childs:
        i2 = i1+paragraph.length
        assert isinstance(paragraph, Paragraph)
        #print i1, i2, repr(model.get_text(i1, i2))
        j1 = i1
        for row in paragraph.childs:
            j2 = j1+row.length
            j1 = j2
        i1 = i2
    assert i2 == len(model)


def test_01():
    model = TextModel(testtext)
    layout = Layout(model)

    n = len(model)
    assert len(layout) == n
    model.insert(10, TextModel('XXX'))
    assert len(model) == n+3

    layout.inserted(10, 3)
    assert len(layout) == n+3


def test_06():
    "empty model"
    model = TextModel(u'')
    layout = Layout(model)
    assert layout.height == 1
    r = layout.get_rect(0, 0, 0)
    assert r.y2 == 1
    model.insert_text(0, '\n')
    layout.inserted(0, 1)
    assert layout.height == 2
    r = layout.get_rect(1, 0, 0)
    assert not layout.can_append()


    
if __name__ == '__main__':
    import alltests
    alltests.dotests()
