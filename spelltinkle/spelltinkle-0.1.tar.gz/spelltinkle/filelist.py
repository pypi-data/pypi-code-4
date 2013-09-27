from .actions import Actions
from .document import Document

from logging import debug


class FileListActions(Actions):
    def __init__(self, session):
        self.session = session

    def insert_character(self, doc, c):
        if c.isdigit():
            i = int(c)
            if 0 < i < len(self.session.docs):
                self.choose(i)
                
    def choose(self, i):
        self.session.action_stack.pop()
        self.session.docs.pop()
        self.session.docs.append(self.session.docs.pop(-i))
        self.session.docs[-1].view.set_screen(self.session.scr)
        self.session.docs[-1].changes = 42

    def enter(self, doc):
        self.choose(doc.view.r + 1)

    def esc(self, doc):
        self.choose(1)
                
    def view_files(self, doc):
        self.insert_character(doc, '2')
        
            
class FileList(Document):
    def __init__(self, session):
        Document.__init__(self)
        self.view.set_screen(session.scr)
        self.change(0, 0, 0, 0, [doc.filename for doc in session.docs[::-1]])
        self.view.move(0, 2)
        "save Saveall quit/del/bs enter copy open esc"
