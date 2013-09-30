import glob
import itertools

from .document import Document
from .actions import Actions
from .view import View


class FileInputDocument(Document):
    def __init__(self, view, filename):
        Document.__init__(self, view=View(self, has_info_line=False,
                                          show_line_numbers=False))
        self.view.set_screen(view.info)
        self.change(0, 0, 0, 0, [filename])
        self.view.move(len(filename), 0)
        

class FileInputActions(Actions):
    def __init__(self, session, callback):
        self.session = session
        self.callback = callback
        
    def enter(self, doc):
        self.callback(doc.lines[0])

    def esc(self, doc):
        self.session.docs.pop()
        self.session.action_stack.pop()
        
    def tab(self, doc):
        filename = doc.lines[0]

        names = []
        for name in glob.iglob(filename + '*'):
            if name.endswith('.pyc'):
               continue
            names.append(name)
            if len(names) == 1001:
                break
                
        if not names:
            return
            
        i = len(filename)
        while True:
            name0 = names[0][:i + 1]
            if len(name0) == i:
                return
            for name in names[1:]:
                if not name.startswith(name0):
                    return
            doc.change(i, 0, i, 0, [name0[i]])
            i += 1
            doc.view.move(i, 0)
