# -*- coding: latin-1 -*-


"""

Simplification
~~~~~~~~~~~~~~

Nach set_properties():
    
    - Es können Objekte mit Länge Null erzeugt werden (überall)
    - möglicherweise können Characters zusammengefasts werden (überall)
    - Es wird unnötig geschachtelt g[g[c]]
   
Nach insert():
 
    - Characters können zusammengefasst werden (an Schnittkanten)
    - Gruppen können zusammengefasst werden (an Schnittkanten)
    - Gruppen können aufgelöst werden (an Schnittkante)

    Optimierungen:
    - simplify muss nicht immer an _beiden_ Schnittkanten ausgeführt werden
    -> an welcher?
    
Nach split():

    - wie insert

"""

from copy import copy as shallow_copy
from listtools import listjoin
import listtools

def hash_style(style):
    return tuple(sorted(style.items()))

style_pool = {} 
defaultstyle = {}   
def create_style(**kwds):
    global style_pool
    style = defaultstyle.copy()
    style.update(kwds)
    key = hash_style(style)
    try:
        return style_pool[key]
    except KeyError:
        style_pool[key] = style
        return style

defaultstyle = create_style(
    textcolor = 'black', 
    bgcolor = 'white', 
    fontsize = 10,
    selected = False
    )

def updated_style(style, properties):
    new = style.copy()
    new.update(properties)
    return create_style(**new)


def style_add((n1, style1), (n2, style2)):
    # Aufruf: listjoin(a, b, style_add)
    if style1 is style2:
        return [(n1+n2, style1)]
    return [(n1, style1), (n2, style2)]
    

def get_interval(container, slice):
    if slice.start is None:
        start = 0
    else:
        start = slice.start
        if start < 0:
            start = len(container)-start
            if start < 0:
                raise IndexError(slice.start)

    if slice.stop is None:
        stop = len(container)
    else:
        stop = slice.stop
        if stop < 0:
            stop = len(container)-stop
            if stop < 0:
                raise IndexError(slice.stop)
    return start, stop



def check(texel):
    return True


def checked(texel):
    assert check(texel)
    return texel

    
class CharactersBase:
    style = None
    def __len__(self):
        return len(self.data)
        
    def get_text(self):
        return self.data
        
    def get_style(self, i):
        return self.style
        
    def simplify(self, i):
        return self
        
    def get_styles(self, i1, i2):
        if i1<len(self) and i2>0:
            return [(len(self), self.style)]
        return []

    def set_styles(self, i0, styles):
        n = len(self)
        i = 0
        data = []
        while styles:
            l, style = styles[0]
            del styles[0]
            texel = self.__class__(self.data[i:i+l], style)
            data.append(texel)

            i += l
            if i > n:
                styles.insert(0, (i-n, style))
                break
            elif i >= n:
                break

        if len(data) == 1:
            return texel
        return checked(group([texel]))

    def __getitem__(self, r):
        i1, i2 = get_interval(self, r)
        clone = shallow_copy(self)
        clone.data = self.data[i1:i2]

    def takeout(self, i1, i2):
        i1 = max(0, i1)
        i2 = min(len(self), i2)
        b, c = self.split(i2)
        a, b = b.split(i1)
        return group([a, c]), b

    def dump(self, i=0):
        print (" "*i)+str(self), id(self.style)


class Characters(CharactersBase):
    def __init__(self, text, style=defaultstyle):
        unicode(text) # check proper encoding
        self.data = text
        self.style = style
        
    def __str__(self):
        return "C(%s)" % repr(self.data)

    def __repr__(self):
        return "C(%s, %s)" % (repr(self.data), repr(self.style))

    def __len(self):
        return len(self.data)
        
    def split(self, i):
        if i<0 or i>len(self):
            raise IndexError, i
        l = Characters(self.data[:i], self.style)
        r = Characters(self.data[i:], self.style)
        return l, r
        
    def set_properties(self, i1, i2, properties):
        if i1 == i2:
            return self
        style = updated_style(self.style, properties)
        if style is self.style:
            return self
        i1 = max(0, i1)
        i2 = min(len(self), i2)
        assert i2>=i1
        tmp, r = self.split(i2)
        l, tmp = tmp.split(i1)
        c = Characters(tmp.data, style)
        return checked(group([l, c, r]))

    def insert(self, i, texel):
        if isinstance(texel, Characters) and texel.style is self.style:
            text = self.data[:i]+texel.data+self.data[i:]
            return Characters(text, self.style)
        a, b = self.split(i)
        assert len(self) == len(a)+len(b)
        r = group([a, texel, b])
        assert len(r) == len(self)+len(texel)
        return r

    def get_linelengths(self):
        return []
        
NULL_TEXEL = Characters('')
        
class NewLine(CharactersBase):
    data = '\n'
    def __init__(self, style=defaultstyle):
        self.style = style
        
    def __repr__(self):
        return 'NL'

    def __str__(self):
        return 'NL'
    
    def split(self, i):
        if i<0 or i>len(self):
            raise IndexError, i
        if i==0:
            return NULL_TEXEL, self
        return self, NULL_TEXEL
        
    def set_properties(self, i1, i2, properties):
        style = updated_style(self.style, properties)
        return checked(NewLine(style=style))
        
    def insert(self, i, texel):
        if i<0 or i>1:
            raise IndexError, i
        if i==0:
            return group([texel, self])
        return group([self, texel])
        
    def get_linelengths(self):
        return [1]

    def dump(self, i=0):
        print (" "*i)+str(self)

NL = NewLine()

maxlength = 5

def partition(content):
    if len(content)<=maxlength:
        return content

    l = []
    while len(content):
        l.append(Group(content[:maxlength]))
        content = content[maxlength:]
    return partition(l)


def group(content):
    if len(content) == 1:
        return content[0]
    return Group(content)


class Group:
    def __init__(self, content):
        content = partition(content)
        self.data = data = []
        length = 0
        for texel in content:
            n = len(texel)
            if not n:
                continue
            length += n            
            if isinstance(texel, Group) and len(data)+len(texel.data)<maxlength:
                data.extend(texel.data)
            else:
                data.append(texel)
        self._length = length

    def __len__(self):
        return self._length
        
    def __repr__(self):
        return "G(%s)" % repr(self.data)

    def __str__(self):
        return "G([%s])" % ', '.join(map(str, self.data))

    def __getstate__(self):
        state = self.__dict__.copy()
        if '_length' in state:
            del state['_length']
        return state

    def __setstate__(self, state):
        self.__dict__ = state
        self._length = sum([len(texel) for texel in self.data])

    def get_text(self):
        return u''.join(texel.get_text() for texel in self.data)
        
    def get_style(self, i):
        for texel in self.data:
            n = len(texel)
            if n>i:
                return texel.get_style(i)
            i -= n

    def get_linelengths(self):
        linelengths = []
        n = 0 # Länge der letzten (nicht abgeschlossenen) Zeile 
        for i, texel in enumerate(self.data):
            l = texel.get_linelengths()
            if l:
                linelengths.append(n+l[0])
                linelengths.extend(l[1:])
                n = len(texel)-sum(l)
            else:
                n += len(texel)
        return linelengths

    def get_styles(self, i1, i2):
        styles = []
        for texel in self.data:
            n = len(texel)
            if i1<n and i2>=0:
                styles = listjoin(styles, texel.get_styles(i1, i2), style_add)
            i1 -= n
            i2 -= n
        return styles

    def set_styles(self, i0, styles):
        data = []
        for texel in self.data:
            data.append(texel.set_styles(i0, styles).simplify(0))
            if not styles:
                break
            i0 += len(texel)
        return group(data)            

    def set_properties(self, i1, i2, properties):
        assert i2 >= i1
        r = []
        i = 0
        for texel in self.data:
            n = len(texel)
            if i1<n and i2>0:
                r.append(texel.set_properties(i1, i2, properties))
            else:
                r.append(texel)
            i1 -= n
            i2 -= n
        return checked(group(r))
        
    def split(self, i):
        if i<0 or i>len(self):
            raise IndexError(i)
        l = []
        r = []
        for texel in self.data:
            n = len(texel)
            if i<=0:
                r.append(texel)
            elif i>=n:
                l.append(texel)
            elif n>i:
                a, b = texel.split(i)
                l.append(a)
                r.append(b)
            i -= n
        return group(l), group(r)

    def __getitem__(self, r):
        i1, i2 = get_interval(self, r)
        b, c = self.split(i2)
        a, b = b.split(i1)
        return b

    def takeout(self, i1, i2):
        rest = []
        part = []
        for j1, j2, item in listtools.iter(self.data):
            if i1 <= j1 and j2<= i2: # item liegt in [i1, i2]
                part.append(item)
            elif i1 < j2 and j1 < i2: # item schneidet [i1, i2]
                _rest, _part = item.takeout(i1-j1, i2-j1)
                rest.append(_rest)
                part.append(_part)
            else: # item hat keine Schnittmenge mit [i1, i2]
                rest.append(item)
        return group(rest), group(part)
        
    def insert(self, i, texel):
        
        # Die folgende Schleife untersucht nicht den Fall, dass hinter
        # dem letzten Element eingefügt wird oder dass data leer
        # ist. Beide Fälle werden hier behandelt.
        if i == len(self):
            return group(self.data+[texel])

        # Die restlichen Fälle werden mit der Schleife abgedeckt.
        data = []
        for elem in self.data:
            n = len(elem)
            if i<0: # Texel wurde schon eingefügt
                data.append(elem)
            elif i>=n: # Texel wird später eingefügt
                data.append(elem)
            else:
                data.append(elem.insert(i, texel))
            i -= n
        assert len(self)+len(texel) == len(Group(data))
        return group(data)
        
    def simplify(self, i):
        # Gruppen werden zusammengefasst, wenn die Länge von self
        # nicht maxlength übersteigen würde.

        data = []
        rest = list(self.data)
        while rest:
            elem, rest = rest[0], rest[1:]
            n = len(elem)
            assert n>0
            # leere Elemente wurden schon im Group-Konstruktor entfernt
            
            if i == n:
                # elem ist das linke Element!
                elem = elem.simplify(i)
                if isinstance(elem, Group) and len(elem.data)<maxlength:
                    data.extend(elem.data[:-1])
                    rest.insert(0, elem.data[-1])
                    i -= n-len(elem.data[-1])
                else:
                    data.append(elem)
                    i -= n
            elif i >= 0 and i<n:
                # elem enthält i oder grenzt rechts daran an
                elem = elem.simplify(i)
                if isinstance(elem, Group) and len(elem.data)<maxlength:
                    rest = elem.data[1:]+rest
                    elem = elem.data[0]

                # Anfügen von elem
                if not data:
                    data = [elem]
                    i -= len(elem)
                else:
                    data, l = data[:-1], data[-1]
                    # Stringverkettung möglich?
                    if isinstance(elem, Characters) and \
                            isinstance(l, Characters) and \
                            elem.style is l.style:
                        new = Characters(l.data+elem.data, elem.style)
                        data.append(new)
                        i -= len(elem)
                    
                    # Gruppenverketting möglich?
                    elif isinstance(elem, Group) and \
                            isinstance(l, Group) and len(elem.data)+len(l.data)<maxlength:
                        new = group(l.data+elem.data)
                        data.append(new)
                        i -= len(elem)

                    # Keine Verkettung möglich
                    else:
                        data.append(l)
                        data.append(elem)
                        i -= len(elem)                
            else:
                data.append(elem)
                i -= len(elem)

        if len(data) == 1:
            tmp = data[0]
        else:
            tmp = group(partition(data))

        assert len(tmp) == len(self)
        return checked(tmp)
        
    def dump(self, i=0):
        print (" "*i)+"G(["
        for texel in self.data:
            texel.dump(i+4)
        print (" "*i)+"])"



def check_split(texel):
    for i in range(len(texel)+1):
        a, b = texel.split(i)
        assert len(texel) == len(a)+len(b)
    try:
        texel.split(-1)
        assert False
    except IndexError:
        pass
    try:
        texel.split(len(texel)+1)
        assert False
    except IndexError:
        pass
    return True



text1 = "0123456789"
text2 = "abcdefghijklmnopqrstuvwxyz"
text3 = "01\n345\n\n89012\n45678\n"

def test_00():
    "Characters"
    s = Characters(text1)
    check_split(s)
    checked(s)


def test_01():
    "Group"
    s = Characters(text1)
    s1 = Characters(text1)
    s2 = Characters(text1)

    s1 = Characters(text1)
    s2 = Characters(text1, style=create_style(fontsize=4))

    c = Group([s1, s2])
    checked(c)
    check_split(c)

    c1 = Group([c, c])
    checked(c1)
    check_split(c1)

    c1 = Group([c, Characters("X"), c])
    checked(c1)
    check_split(c1)

    # 20 Kinder sind ok
    c1 = Group([c]*20)
    checked(c1)
    check_split(c1)


    c1 = Group([c]*100)
    checked(c1)
    check_split(c1)

    c1 = Group([c]*10000)


def test_02():
    "insert and simplify"
    t1 = Characters(text1)
    t2 = Characters(text2)
    
    # Text wird beim einfügen in Text mit gleichem Style immer
    # zusammengeführt
    for i in range(len(t1)+1):
        t = t1.insert(i, t2)
        assert isinstance(t, Characters)

    g = Group([t2])
    # Die Gruppe wird durch simplify aufgelöst
    for i in range(len(t1)+1):
        i = 5
        t = t1.insert(i, g)
        t = t.simplify(i)
        t = t.simplify(i+len(g))
        assert isinstance(t, Characters)

    # Simplify wird rekursiv angewand
    for i in range(5):
        g = Group([g])
    t = g.simplify(0)
    assert isinstance(t, Characters)


def test_03():    
    "ungroup"
    G = Group
    C = Characters
    t = G([G([C('0123456789'), G([C('0123456789')]), C('')])])
    assert isinstance(t.simplify(10), Characters)


def test_04():
    "split"
    c = Characters(text1)
    g = Group([c])
    n = NL
    items = [c, g, n]
    for item in items:
        n = len(item)
        for i in range(len(item)+1):
            item1, item2 = item.split(i)
            assert len(item1)+len(item2) == n

            
def test_05():
    "insert"
    c = Characters(text1)
    g = Group([c])
    n = NL
    items = [c, g, n]
    for item in items:
        for other in items:
            n = len(item)
            no = len(other)
            item_text = item.get_text()
            other_text = other.get_text()
            for i in range(len(item)+1):
                r = item.insert(i, other)
                assert len(r) == n+no
                assert r.get_text() == item_text[:i]+other_text+item_text[i:]


def test_06():
    "simplify"
    C = Characters
    G = Group
    t = G([C("01234"), C(""), C("56789")])
    assert str(t.simplify(5)) == "C('0123456789')"


    t = G([C("01234"), G([ C(""), C("56789")])])
    assert str(t.simplify(5)) == "C('0123456789')"

    t = G([G([C("01234"), C(""), C("")]), G([ C(""), C("56789")])])
    #print t.simplify(5)
    assert str(t.simplify(5)) == "C('0123456789')"

    
def test_07():
    "set properties"
    texel = Characters('0123')
    from random import randrange, choice

    defaultstyle.clear()
    defaultstyle['s'] = 10

    n = len(texel)
    for j in range(10000):
        i1 = randrange(n)
        i2 = randrange(n)
        i1, i2 = sorted([i1, i2])
        size = choice([10, 14])
        #print str(texel)
        
        new = texel.set_properties(i1, i2, {'s':size}).simplify(i1).simplify(i2)
        assert not "C(u'')" in str(texel)
        assert not "C(u'')" in str(new)    
        texel = new


def test_08():
    "get/set styles"

    s0 = defaultstyle
    s1 = create_style(bgcolor='red')

    t = Characters(text1)
    assert t.get_styles(0, len(t)) == [(len(t), s0)]

    t = t.set_properties(3, 5, {'bgcolor':'red'})
    styles = t.get_styles(0, len(t))
    assert styles == [
        (3, s0),
        (2, s1),
        (5, s0),
        ]

    # Styling überschreiben 
    t = t.set_styles(0, [(len(t), s0)])
    assert t.get_styles(0, len(t)) == [(len(t), s0)]

    # Und wieder herstellen
    t = t.set_styles(0, styles)
    styles = t.get_styles(0, len(t))
    assert styles == [
        (3, s0),
        (2, s1),
        (5, s0),
        ]

    # Zusammenfassen von Styles:
    styles = Group([Characters(text1), Characters(text1)]).get_styles(0, 2*len(text1))
    assert len(styles) == 1
    assert styles[0][0] == 2*len(text1)


if __name__=='__main__':
    import alltests
    alltests.dotests()
    
