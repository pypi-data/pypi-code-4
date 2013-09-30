import os

from .exceptions import StopSession
from .search import Search
from .document import Document

from logging import debug


class Actions:
    def __init__(self, session):
        self.session = session

    def insert_character(self, doc, char):
        c, r = doc.view.cr()
        doc.change(c, r, c, r, [char])

    def up(self, doc):
        c, r = doc.view.cr()
        doc.view.move(None, max(0, r - 1))

    def down(self, doc):
        c, r = doc.view.cr()
        doc.view.move(None, r + 1)

    def scroll_up(self, doc):
        y1 = doc.view.y1
        if y1 == 0:
            return
        c, r = doc.view.pos
        if doc.view.y == y1 + doc.view.text.h - 1:
            r -= 1
            if r < 0:
                return
        doc.view.y1 -= 1
        doc.view.move(None, r)
        
    def scroll_down(self, doc):
        y1 = doc.view.y1
        if y1 == len(doc.view.lines) - 1:
            return
        c, r = doc.view.pos
        if doc.view.y == y1:
            r += 1
        doc.view.y1 += 1
        doc.view.move(None, r)
        
    def left(self, doc):
        doc.view.move(*doc.prev(*doc.view.pos))

    def right(self, doc):
        doc.view.move(*doc.next(*doc.view.pos))

    def mouse_clicked(self, doc):
        doc.view.mouse(*self.session.scr.position)
        
    def mouse_released(self, doc):
        self.mark(doc)
        doc.view.mouse(*self.session.scr.position)
        
    def home(self, doc):
        doc.view.move(0)

    def homehome(self, doc):
        doc.view.move(0, 0)

    def end(self, doc):
        doc.view.move(len(doc.lines[doc.view.r]))
    
    def endend(self, doc):
        doc.view.move(len(doc.lines[-1]), len(doc.lines) - 1)

    def page_up(self, doc):
        c, r = doc.view.cr()
        doc.view.move(None, max(0, r - doc.view.text.h))
        
    def page_down(self, doc):
        c, r = doc.view.cr()
        doc.view.move(None, r + doc.view.text.h)
        
    def bs(self, doc):
        c2, r2 = doc.view.cr()
        if c2 == 0 and r2 == 0:
            return
        c1, r1 = doc.prev(c2, r2)
        doc.change(c1, r1, c2, r2, [''])

    def delete(self, doc):
        c1, r1 = doc.view.cr()
        if doc.view.mark:
            c2, r2 = doc.view.mark
            if (r1, c1) > (r2, c2):
                r1, c1, r2, c2 = r2, c2, r1, c1
            lines = doc.change(c1, r1, c2, r2, [''])
            debug((c1,r1,c2,r2,lines))
            self.session.memory = lines
            doc.view.mark = None
        else:
            c2, r2 = doc.next(c1, r1)
            if c1 != c2 or r1 != r2:
                doc.change(c1, r1, c2, r2, [''])

    def copy(self, doc):
        if not doc.view.mark:
            return
        c1, r1 = doc.view.cr()
        c2, r2 = doc.view.mark
        if (r1, c1) > (r2, c2):
            r1, c1, r2, c2 = r2, c2, r1, c1
        doc.color.stop()
        lines = doc.delete_range(c1, r1, c2, r2)
        doc.insert_lines(c1, r1, lines)
        self.session.memory = lines

    def undo(self, doc):
        doc.history.undo(doc)

    def redo(self, doc):
        doc.history.redo(doc)

    def search_forward(self, doc):
        self.session.action_stack.append(Search(self.session, doc))

    def search_backward(self, doc):
        self.session.action_stack.append(Search(self.session, doc, -1))

    def view_files(self, doc):
        from .filelist import FileList, FileListActions
        self.session.action_stack.append(FileListActions(self.session))
        self.session.docs.append(FileList(self.session))
        self.session.docs[-1].view.update()

    def write(self, doc):
        doc.write()

    def write_as(self, doc):
        from .fileinput import FileInputActions, FileInputDocument
        self.session.action_stack.append(FileInputActions(self.session,
                                                          self.write_as_cb))
        filename = doc.filename or ''
        self.session.docs.append(FileInputDocument(doc.view, filename))

    def write_as_cb(self, filename):
        self.session.docs.pop()
        self.session.action_stack.pop()
        doc = self.session.docs[-1]
        doc.filename = filename
        doc.write()

    def open(self, doc):
        from .fileinput import FileInputActions, FileInputDocument
        self.session.action_stack.append(FileInputActions(self.session,
                                                          self.open_cb))
        self.session.docs.append(FileInputDocument(doc.view, os.path.split(doc.filename)[0]))
        
    def open_cb(self, filename):
        self.session.docs.pop()
        self.session.action_stack.pop()
        doc = Document()
        doc.view.set_screen(self.session.scr)
        doc.read(filename)
        self.session.docs.append(doc)
        
    def paste(self, doc):
        c, r = doc.view.cr()
        change = doc.change(c, r, c, r, self.session.memory)
        doc.view.mark = None

    def esc(self, doc):
        doc.view.mark = None
        
    def delete_to_end_of_line(self, doc, append=False):
        c, r = doc.view.cr()
        if (c, r) == doc.next(c, r):
            return
        if c == len(doc.lines[r]):
            lines = ['', '']    
            doc.change(c, r, 0, r + 1, [''])
        else:
            lines = [doc.lines[r][c:]]
            doc.change(c, r, len(doc.lines[r]), r, [''])
        if append:
            if self.session.memory[-1] == '':
                self.session.memory[-1:] = lines
            else:
                self.session.memory.append('')
        else:
            self.session.memory = lines

    def delete_to_end_of_line_again(self, doc):
        self.delete_to_end_of_line(doc, True)

    def mark(self, doc):
        doc.view.mark = doc.view.cr()

    def enter(self, doc):
        c, r = doc.view.cr()
        doc.change(c, r, c, r, ['', ''])
        doc.view.pos = (0, r + 1)
        self.tab(
            doc
            )
            
    def tab(self, doc):
        c, r = doc.view.cr()
        r0 = r - 1
        while r0 >= 0:
            line = doc.lines[r0]
            if line and not line.isspace():
                indent = len(line) - len(line.lstrip())
                break
            r0 -= 1
        else:
            indent = 0
            line = None
            
        if line is not None:
            if line.rstrip().endswith(':'):
                indent += 4
            else:
                p = []
                for i in range(len(line) - 1, indent - 1, -1):
                    x = line[i]
                    j = '([{'.find(x)
                    if j != -1:
                        if not p:
                            if i == len(line) - 1:
                                indent += 4
                            else:
                                indent = i + 1
                            break
                        if p.pop() != ')]}'[j]:
                            indent = 0
                            # message
                            break
                    elif x in ')]}':
                        p.append(x)
                        
        line = doc.lines[r]
        i = len(line) - len(line.lstrip())
        if i < indent:
            doc.change(0, r, 0, r, [' ' * (indent - i)])
        elif i > indent:
            doc.change(0, r, i - indent, r, [''])
        c += indent - i
        if c < indent:
            c = indent
        doc.view.move(c, r)

    def quit(self, doc):
        for doc in self.session.docs:
            if doc.modified and doc.filename is not None:
                doc.write()
        raise StopSession
