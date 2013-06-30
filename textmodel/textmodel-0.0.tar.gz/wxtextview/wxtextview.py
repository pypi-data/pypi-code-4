# -*- coding: latin-1 -*-


import wx


from textmodel import TextModel, NewLine, Group, Characters, defaultstyle
from textview import TextView
from layout import Layout, IterBox, TextBox, Paragraph
from math import ceil

defaultstyle.update(dict(underline=False, facename=''))


class DCStyler:
    last_style = None
    def __init__(self, dc):
        self.dc = dc
        
    def set_style(self, style):
        if style is self.last_style:
            return
        self.last_style = style
        font = wx.Font(style['fontsize'], wx.MODERN, wx.NORMAL, wx.NORMAL, 
                       style['underline'], style['facename'])
        self.dc.SetFont(font)            
        self.dc.SetTextBackground(wx.NamedColour(style['bgcolor']))
        self.dc.SetTextForeground(wx.NamedColour(style['textcolor']))





def ib_draw(self, x, y, dc, styler):
    for j1, j2, x1, y1, child in self.iter(0, x, y):
        r = wx.Rect(x1, y1, child.width, child.height)
        if dc.ClippingRect.Intersects(r):
            child.draw(x1, y1, dc, styler)

def ib_draw_cursor(self, i, x0, y0, dc):
    r = self.get_rect(i, x0, y0)
    w = 2
    dc.Blit(r.x1, r.y1, w, r.y2-r.y1, dc, r.x1, r.y1, wx.SRC_INVERT)        

def ib_draw_selection(self, i1, i2, x, y, dc):
    for j1, j2, x1, y1, child in self.iter(0, x, y):
        if i1 < j2 and j1< i2:
            r = wx.Rect(x1, y1, child.width, child.height)
            if dc.ClippingRect.Intersects(r):
                child.draw_selection(i1-j1, i2-j1, x1, y1, dc)


IterBox.draw = ib_draw
IterBox.draw_cursor = ib_draw_cursor
IterBox.draw_selection = ib_draw_selection
    

def tb_draw(self, x, y, dc, styler):
    styler.set_style(self.style)
    dc.DrawText(self.text, x, y)

def tb_draw_selection(self, i1, i2, x, y, dc):
    measure = self._layout.measure
    i1 = max(0, i1)
    i2 = min(len(self.text), i2)
    x1 = x+measure(self.text[:i1], self.style)[0]
    x2 = x+measure(self.text[:i2], self.style)[0]
    dc.Blit(x1, y, x2-x1, self.height, dc, x1, y, wx.SRC_INVERT)


TextBox.draw = tb_draw
TextBox.draw_selection = tb_draw_selection

        

def measure(self, text, style):
    font = wx.Font(style['fontsize'], wx.MODERN, wx.NORMAL, wx.NORMAL,
                   style['underline'], style['facename'])
    #print "measure", repr(text),
    # das funktioniert auf gtk nicht korrekt:
    #gc = wx.GraphicsContext_CreateMeasuringContext()
    #gc.SetFont(font)

    dc = wx.MemoryDC()
    dc.SetFont(font)
    w, h = dc.GetTextExtent(text)
    return w, h


def measure_parts(self, text, style):
    font = wx.Font(style['fontsize'], wx.MODERN, wx.NORMAL, wx.NORMAL,
                   style['underline'], style['facename'])
    dc = wx.MemoryDC()
    dc.SetFont(font)
    return dc.GetPartialTextExtents(text)

Layout.measure = measure
Layout.measure_parts = measure_parts



class WXTextView(wx.ScrolledWindow, TextView):
    _scrollrate = 10, 10
    def __init__(self, parent, id=-1,  
                 pos=wx.DefaultPosition, size=wx.DefaultSize, style=0):

        wx.ScrolledWindow.__init__(self, parent, id,
                                   pos, size,
                                   style|wx.WANTS_CHARS)

        TextView.__init__(self)

        self.Bind(wx.EVT_PAINT, self.on_paint)
        self.Bind(wx.EVT_ERASE_BACKGROUND, lambda event: None)
        self.Bind(wx.EVT_CHAR, self.on_char)
        self.Bind(wx.EVT_SIZE, self.on_size)
        self.Bind(wx.EVT_LEFT_DOWN, self.on_leftdown)
        self.Bind(wx.EVT_LEFT_UP, self.on_leftup)
        self.Bind(wx.EVT_LEFT_DCLICK, self.on_leftdclick)
        self.Bind(wx.EVT_MOTION, self.on_motion)
        self.Bind(wx.EVT_KILL_FOCUS, self.on_focus)
        self.Bind(wx.EVT_SET_FOCUS, self.on_focus)

        # key = keycode, control, alt
        self.actions = {
            (wx.WXK_ESCAPE, False, False) : 'dump_info', 
            (wx.WXK_RIGHT, True, False)  : 'move_word_end',
            (wx.WXK_RIGHT, False, False)  : 'move_right',
            (wx.WXK_LEFT, True, False)  : 'move_word_begin',
            (wx.WXK_LEFT, False, False)  : 'move_left',
            (wx.WXK_DOWN, True, False)  : 'move_paragraph_end',
            (wx.WXK_DOWN, False, False)  : 'move_down',
            (wx.WXK_UP, True, False)  : 'move_paragraph_begin',
            (wx.WXK_UP, False, False)  : 'move_up',
            (wx.WXK_HOME, False, False) : 'move_line_start',
            (wx.WXK_END, False, False) : 'move_line_end',            
            (wx.WXK_PAGEDOWN, False, False): 'move_page_down',
            (wx.WXK_PAGEUP, False, False): 'move_page_up',
            (wx.WXK_RETURN, False, False): 'insert_newline',
            (wx.WXK_BACK, False, False): 'backspace',
            (3, True, False) : 'copy',
            (22, True, False) : 'paste',
            (24, True, False) : 'cut',
            (26, True, False) : 'undo',
            (18, True, False) : 'redo',  
            (127, True, False) : 'del_word_left',   
            }

    def refresh(self):
        self.Refresh()

    def on_focus(self, event):
        # focus hat sich geändert
        self.Refresh()

    def on_char(self, event):
        keycode = event.GetKeyCode()
        ctrl = event.ControlDown()
        shift = event.ShiftDown()
        alt = event.AltDown()        
        char = event.GetUniChar()
        action = self.actions.get((keycode, ctrl, alt))
        if action is None:
            action = unichr(keycode)
        self.handle_action(action, shift)
        
    def copy(self):
        if not self.has_selection():
            return
        s1, s2 = sorted(self.selection)
        part = self.model[s1:s2]
        text = part.get_text()
        clipdata = wx.TextDataObject()
        clipdata.SetText(text)
        wx.TheClipboard.Open()
        wx.TheClipboard.SetData(clipdata)
        wx.TheClipboard.Close()

    def paste(self):
        if self.has_selection():
            s1, s2 = sorted(self.selection)
            self.model.remove(s1, s2)
            self.index = s1
        if wx.TheClipboard.IsOpened():  # may crash, otherwise
            return
        data = wx.TextDataObject()
        wx.TheClipboard.Open()
        success = wx.TheClipboard.GetData(data)
        wx.TheClipboard.Close()
        if success:
            textmodel = TextModel(data.GetText())
            self.insert(self.index, textmodel)

    def cut(self):
        if self.has_selection():
            self.copy()
            s1, s2 = sorted(self.selection)
            self.remove(s1, s2)
         
    def on_paint(self, event):
        self._update_scroll()
        self.keep_cursor_on_screen()

        pdc = wx.PaintDC(self)
        pdc.SetAxisOrientation(True, False)
        dc = wx.BufferedDC(pdc)
        if not dc.IsOk():
            return
        dc.SetBackgroundMode(wx.SOLID)
        dc.Clear()
        styler = DCStyler(dc)
        
        region = self.GetUpdateRegion()
        x, y, w, h = region.Box
        dc.SetClippingRegion(x-1, y-1, w+2, h+2)

        x, y = self.CalcScrolledPosition((0,0)) 
        self.layout.draw(x, y, dc, styler)
        if wx.Window_FindFocus() is self: 
            self.layout.draw_cursor(self.index, x, y, dc)
        if self.selection is not None:
            i1, i2 = sorted(self.selection)
            j1, j2 = self.layout.extend_range(i1, i2)
            self.layout.draw_selection(j1, j2, x, y, dc)
        styler = None
        dc = None

    def on_size(self, event):
        self.keep_cursor_on_screen()

    def on_motion(self, event):
        if not event.LeftIsDown():
            return event.Skip()
        # XXX scrollen wenn Fensterkante erreicht ist! Fehlt.
        x, y = self.CalcUnscrolledPosition(event.Position) 
        i = self.layout.get_index(x, y)
        if i is not None:
            self.set_index(i, extend=True)

    def on_leftdown(self, event):
        x, y = self.CalcUnscrolledPosition(event.Position) 
        i = self.compute_index(x, y)
        if i is not None:
            self.set_index(i, extend=event.ShiftDown())
        self.SetFocus()

    def on_leftup(self, event):
        pass

    def on_leftdclick(self, event):
        # das Wort markieren
        
        x, y = self.CalcUnscrolledPosition(event.Position) 
        self.select_word(x, y)

    ### Scroll
    def _update_scroll(self):
        layout = self.layout
        self.SetVirtualSize((layout.width, layout.height))
        self._scrollrate = 10, 10
        self.SetScrollRate(*self._scrollrate)
        
    def adjust_viewport(self):
        layout = self.layout
        r = layout.get_rect(self.index, 0, 0)
        w = layout.width
        h = layout.height
        fw, fh = self._scrollrate

        width, height = self.GetClientSize()
        firstcol, firstrow = self.ViewStart # -> Scroll in Inc-Schritten
        x = firstcol*fw
        y = firstrow*fh
        if r.y1 < y:
            y = r.y1
            firstrow = int(y/fh)
        elif r.y2 > y+height:
            y = r.y2-height
            firstrow = ceil(y/fh)
        if r.x1 < x:
            x = r.x1
            firstcol = int(x/fw)
        elif r.x2 > x+width:
            x = r.x2-width
            firstcol = ceil(x/fw)
        if (firstcol, firstrow) != self.ViewStart:
            self.Scroll(firstcol, firstrow)

    def keep_cursor_on_screen(self):
        # Die Cursorposition so verändern, dass der Cursor in dem
        # sichtbaren Ausschnitt ist.
        #rect = self.layout.get_rect(self.index, 0, 0)
        #print "keep cursor"
        return 
        fw, fh = self.charactersize
        width, height = self.GetClientSize()
        firstcol, firstrow = self.GetViewStart() # -> Scroll in Inc-Schritten
        lastrow = firstrow+height/fh-1
        lastcol = firstcol+width/fw-1

        row, col = self.current_position()
        if row < firstrow:
            row = firstrow
        elif row > lastrow:
            row = lastrow
        if col < firstcol:
            col = firstcol
        if col > lastcol:
            col = lastcol
        self.move_cursor_to(row, col, False, False)
        
        
        

testtext = u"""Ein männlicher Briefmark erlebte
Was Schönes, bevor er klebte.
Er war von einer Prinzessin beleckt.
Da war die Liebe in ihm geweckt.
Er wollte sie wiederküssen,
Da hat er verreisen müssen.
So liebte er sie vergebens.
Das ist die Tragik des Lebens.

(Joachim Ringelnatz)"""

def init_testing(redirect=True):
    app = wx.App(redirect=redirect)
    model = TextModel(testtext)
    model.set_properties(15, 24, fontsize=14)
    model.set_properties(249, 269, fontsize=14)

    frame = wx.Frame(None)
    win = wx.Panel(frame, -1)
    view = WXTextView(win, -1, style=wx.SUNKEN_BORDER)
    view.model = model
    layout = view.layout
    box = wx.BoxSizer(wx.VERTICAL)
    box.Add(view, 1, wx.ALL|wx.GROW, 1)
    win.SetSizer(box)
    win.SetAutoLayout(True)

    frame.Show()    
    return locals()


def test_00():
    app = wx.App(redirect = False)
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
    app = wx.App(redirect = False)
    model = TextModel(testtext)
    layout = Layout(model)

    n = len(model)
    assert len(layout) == n
    model.insert(10, TextModel('XXX'))
    assert len(model) == n+3
    
    layout.inserted(10, 3)
    assert len(layout) == n+3
    
    
def test_02():
    ns = init_testing(redirect=True)
    view = ns['view']
    view.cursor = 5
    view.selection = 3, 6    
    return ns


def test_03():
    ns = init_testing()
    model = ns['model']
    view = ns['view']
    model.set_properties(10, 20, fontsize=15)

    n = len(model)
    text = '\n12345\n'
    model.insert_text(5, text)
    model.remove(5, 5+len(text))
    assert len(model) == n
    assert len(view.layout) == n
    return locals()


def test_04():
    "insert/remove"
    ns = init_testing()
    model = ns['model']
    view = ns['view']
    text = model.get_text()
    n = len(model)
    for i in range(len(text)):
        model.insert_text(i, 'X')
        assert len(model) == n+1
        model.remove(i, i+1)
        assert len(model) == n

def test_05():
    "remove"
    ns = init_testing()
    model = ns['model']
    view = ns['view']
    text = model.get_text()
    n = len(model)
    for i in range(len(text)-1):
        old = model.remove(i, i+1)
        assert len(model) == n-1
        model.insert(i, old)
        assert len(model) == n






def test_09():
    "linebreak"
    ns = init_testing(redirect=False)
    model = ns['model']
    view = ns['view']
    text = model.get_text()
    layout = view.layout
    layout.set_maxw(100)
    return ns
    

def demo_00():
    "simple demo"
    ns = test_02()
    import testing
    testing.pyshell(ns)    
    ns['app'].MainLoop()


def demo_01():
    "colorize demo"
    app = wx.App(redirect = False)
    frame = wx.Frame(None)
    win = wx.Panel(frame, -1)
    view = WXTextView(win, -1, style=wx.SUNKEN_BORDER)
    box = wx.BoxSizer(wx.VERTICAL)
    box.Add(view, 1, wx.ALL|wx.GROW, 1)
    win.SetSizer(box)
    win.SetAutoLayout(True)

    from textmodel.textmodel import pycolorize
    filename = 'textview.py'
    rawtext = open(filename).read() 
    model = pycolorize(rawtext)
    #model = TextModel(rawtext.decode('latin-1'))
    view.set_model(model)
    frame.Show()
    app.MainLoop()


def demo_02():
    "empty text"
    app = wx.App(redirect = True)
    frame = wx.Frame(None)
    win = wx.Panel(frame, -1)
    view = WXTextView(win, -1, style=wx.SUNKEN_BORDER)
    box = wx.BoxSizer(wx.VERTICAL)
    box.Add(view, 1, wx.ALL|wx.GROW, 1)
    win.SetSizer(box)
    win.SetAutoLayout(True)
    model = TextModel(u'')
    view.set_model(model)
    frame.Show()
    app.MainLoop()


def demo_03():
    "line break"
    ns = test_09()
    import testing
    testing.pyshell(ns)    
    ns['app'].MainLoop()


    
if __name__ == '__main__':
    import alltests
    alltests.dotests()
