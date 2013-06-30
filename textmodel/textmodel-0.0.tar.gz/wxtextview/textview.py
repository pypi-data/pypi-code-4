# -*- coding: latin-1 -*-


from viewbase import ViewBase, overridable_property
from textmodel import TextModel
from layout import Layout


def undo(info):
    func = info[0]
    args = info[1:]    
    try:
        redo = apply(func, args)
        return redo
    except:
        warn_tb()


class TextView(ViewBase):
    index = overridable_property('index')
    _index = 0
    selection = overridable_property('selection') # Achtung: i2 kann
                                                  # auch kleiner i1
                                                  # sein!
    _selection = None
    maxw = overridable_property('maxw')
    _maxw = 0
    _scrollrate = 10, 10
    def __init__(self):
        ViewBase.__init__(self)
        self.layout = Layout(TextModel(''), self._maxw)

        self._undoinfo = []
        self._redoinfo = []

    def undo(self):
        if len(self._undoinfo) > 0:
            self.add_redo(undo(self._undoinfo[0]))
            del self._undoinfo[0]
                
    def add_undo(self, info, clear_redo = 1):
        if info is not None:
            self._undoinfo.insert(0, info)
            if clear_redo:
                self._redoinfo = []

    def redo(self):
        if len(self._redoinfo) > 0:
            self.add_undo(undo(self._redoinfo[0]), 0)
            del self._redoinfo[0]

    def add_redo(self, info):
        # Internal method: add a single redo info
        self._redoinfo.insert(0, info)

    def insert(self, i, textmodel):
        # Insert mit Undo und Cursorbewegung
        self.model.insert(i, textmodel)
        self.index = i+len(textmodel)
        info = self._remove, i, i+len(textmodel)
        self.add_undo(info)

    def remove(self, i1, i2):
        # Remove mit Undo und Cursorbewegung
        info = self._remove(i1, i2)
        self.add_undo(info)
        self.index = i1

    def _remove(self, i1, i2):
        old = self.model.remove(i1, i2)
        self.index = i1
        return self._undo_remove, old, i1, i2

    def _undo_remove(self, old, i1, i2):
        self.model.insert(i1, old)
        self.index = i2
        return self._remove, i1, i2

    def set_model(self, model):
        self.layout = Layout(model, self._maxw)  
        ViewBase.set_model(self, model)

    def set_maxw(self, maxw):
        if maxw == self._maxw:
            return
        self._maxw = maxw
        self.layout.set_maxw(maxw)
        self.Refresh()

    def compute_index(self, x, y):
        if y >= self.layout.height:
            return len(self.model)-1
        if y < 0:
            return 0
        return self.layout.get_index(x, y)

    def handle_action(self, action, shift=False):
        model = self.model
        index = self.index
        if index == len(model):
            if index == 0:
                style = {} # wird zum defaultstyle ergänzt
            else:
                style = model.get_style(index-1)
        else:
            style = model.get_style(index)
        row, col = self.current_position()
        rect = self.layout.get_rect(index, 0, 0)
        x = rect.x1
        y = rect.y1

        def del_selection():
            if self.has_selection():
                s1, s2 = sorted(self.selection)
                self.remove(s1, s2)

        if action == 'dump_info':
            n = min(100, len(model.texel))
            model.texel[0:n].dump()
            row, col = model.index2position(index)
            print "row=", row
            print "col=", col
            
        elif action == 'move_word_end':
            i = index
            n = len(model)
            try:
                while not model.get_text(i, i+1).isalnum():
                    i = i+1
                while model.get_text(i, i+1).isalnum():
                    i = i+1
            except IndexError:
                i = n
            self.set_index(i, shift)
        elif action == 'move_right':
            self.set_index(index+1, shift)
        elif action == 'move_word_begin':
            i = index
            try:
                while not model.get_text(i-1, i).isalnum():
                    i = i-1
                while model.get_text(i-1, i).isalnum():
                    i = i-1
            except IndexError:
                i = 0
            self.set_index(i, shift)
        elif action == 'move_left':
            self.set_index(index-1, shift)
        elif action == 'move_paragraph_end':
            i = row
            linelengths = model.texel.get_linelengths() 
            try:
                while linelengths[i] == 1:
                    i += 1
                while linelengths[i] > 1:
                    i += 1
                self.move_cursor_to(i, 0, shift)
            except IndexError:
                self.set_index(len(model), shift)                    
        elif action == 'move_down':
            self.move_cursor_to(row+1, col, shift)
        elif action == 'move_paragraph_begin':
            i = row-1
            linelengths = model.texel.get_linelengths() 
            while linelengths[i] == 1 and i>=0:
                i -= 1
            while linelengths[i] > 1 and i>=0:
                i -= 1
            self.move_cursor_to(i+1, 0, shift)
        elif action == 'move_up':
            self.move_cursor_to(row-1, col, shift)
        elif action == 'move_line_start':
            self.set_index(model.linestart(row), shift)
        elif action == 'move_line_end':
            self.set_index(model.linestart(row)+model.linelength(row)-1, shift)
        elif action == 'move_page_down':
            width, height = self.GetClientSize()
            i = self.compute_index(x, y+height)
            self.set_index(i, shift)            
        elif action == 'move_page_up':
            width, height = self.GetClientSize()
            i = self.compute_index(x, y-height)
            self.set_index(i, shift)
        elif action == 'insert_newline':
            self.insert(index, TextModel('\n', **style))
        elif action == 'backspace':
            del_selection()
            index = self.index
            if index>0:
                self.remove(index-1, index)
        elif action == 'copy':
            self.copy()
        elif action == 'paste':
            self.paste()
        elif action == 'cut':
            self.cut()
        elif action == 'undo':
            self.undo()
        elif action == 'redo':
            self.redo()
        elif action == 'del_word_left':
            # find the beginning of the word
            i = index
            try:
                while not model.get_text(i-1, i).isalnum():
                    i = i-1
                while model.get_text(i-1, i).isalnum():
                    i = i-1
            except IndexError:
                i = 0
            self.remove(i, index)
        else:                  
            #print keycode
            assert len(action) == 1 # single character
            del_selection()
            index = self.index
                
            s = TextModel(action, **style)  
            n = len(model)
            assert len(s) == 1
            self.insert(index, s)
        self.Refresh()

    def copy(self):
        raise NotImplemented()

    def paste(self):
        raise NotImplemented()

    def cut(self):
        raise NotImplemented()
         
    def select_word(self, x, y):
        i = self.layout.get_index(x, y)
        if i is None:
            return
        model = self.model
        n = len(model)
        try:
            while not model.get_text(i-1, i).isalnum():
                i = i-1
            while model.get_text(i-1, i).isalnum():
                i = i-1
        except IndexError:
            i = 0
        i1 = i
        i = i1
        try:
            while not model.get_text(i, i+1).isalnum():
                i = i+1
            while model.get_text(i, i+1).isalnum():
                i = i+1
        except IndexError:
            i = n
        i2 = i
        self.index = i2
        self.selection = (i1, i2)

    def refresh(self):
        raise NotImplemented()

    ### Signale des Models
    def properties_changed(self, model, i1, i2):
        self.layout.properties_changed(i1, i2)
        self.refresh()

    def inserted(self, model, i, n):
        self.layout.inserted(i, n)
        if i>= self.index:
            self.index += n
        self.refresh()

    def removed(self, model, i, text):
        self.layout.removed(i, len(text))
        n = len(text)
        i1 = i
        i2 = i+n
        index = self.index
        if index >= i2:
            self.index = index-n
        elif index > i1:
            self.index = i1       
        self.refresh()

    def keep_cursor_on_screen(self):
        pass
        
    ###
    def set_index(self, index, extend=False, update=True):
        if index < 0:
            index = 0
        elif index > len(self.model):
            index = len(self.model)
        if index != self._index:
            self._index = index
            if extend:
                self.extend_selection()
            elif update:
                self.start_selection()
            self.adjust_viewport()
            self.refresh()

    def get_index(self):
        return self._index

    def current_position(self):
        # gibt die Cursorposition als row, col zurück 
        model = self.model
        i = self.index
        if model is None or i == 0:
            return 0, 0
        if i < len(model):
            row, col = model.index2position(i)
            return row, col
        else:
            assert i == len(model)
            # Schwieriger Fall. Wir müssen den Cursor an die nächste
            # Einfügeposition stellen. Diese gibt es aber noch
            # nicht. Nach einem Return wäre die nächste Position am
            # Anfang der nächsten Zeile. Ansonsten einfach ein Zeichen
            # weiter rechts.
            
            row, col = model.index2position(i-1)
            if model.get_text(len(model)-1) == '\n':
                col = 0
                row = row+1
            else:
                col += 1
            return row, col


    def move_cursor_to(self, row, col, extend=False, update=True):
        # Setzt den Cursor auf row, col. Fall die Position nicht
        # existiert, wird der nächstgelegene Wert genommen. Der Scroll
        # wird so angepasst, dass der Cursor sichtbar ist.
        # extend: extend selection
        # update: update selection (bei extend wird update als True vorausgesetzt)

        model = self.model
        row = min(max(0, row), model.nlines()-1)
        col = min(max(0, col), model.linelength(row))
        self.set_index(model.position2index(row, col), extend, update)

    def get_selection(self):
        return self._selection

    def set_selection(self, selection):
        old = self._selection
        if selection == old:
            return
        if old is not None:
            i1, i2 = old
        self._selection = selection
        if selection is not None:
            i1, i2 = selection
        self.Refresh()

    def has_selection(self):
        selection = self.selection
        if selection is None:
            return False
        return selection[0] != selection[1]

    def start_selection(self):
        index = self.index
        self.selection = index, index
        
    def extend_selection(self):
        # setzt den Endpunkt der Selektion auf den Index
        selection = self.selection
        index = self.index
        if selection is None:
            self.selection = index, index
        else:
            self.selection = selection[0], index
        
        
    
if __name__ == '__main__':
    import alltests
    alltests.dotests()
