class History:
    def __init__(self):
        self.changes = []
        self.undoes = 0

    def append(self, change):
        if self.undoes > 0:
            del self.changes[-self.undoes:]
            self.undoes = 0
        self.changes.append(change)
        if len(self.changes) == 51:
            self.changes.pop(0)

    def undo(self, doc):
        i = len(self.changes) - 1 - self.undoes
        if i < 0:
            return
        c1, r1, c2, r2, c3, r3, newlines, oldlines = self.changes[i]
        doc.change(c1, r1, c3, r3, oldlines, remember=False)
        doc.view.move(c3, r3)
        self.undoes += 1

    def redo(self, doc):
        if self.undoes == 0:
            return
        i = -self.undoes
        c1, r1, c2, r2, c3, r3, newlines, oldlines = self.changes[i]
        doc.change(c1, r1, c2, r2, newlines, remember=False)
        doc.view.move(c3, r3)
        self.undoes -= 1
