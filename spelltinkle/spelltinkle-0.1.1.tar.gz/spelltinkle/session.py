from time import time
import os
import collections
import curses.ascii
from logging import debug

from .keys import keynames, doubles, repeat, again
from .actions import Actions
from .document import Document


class Session:
    def __init__(self, filenames, scr, input):
        dct = self.read()
        if filenames:
            self.docs = []
            for filename in filenames:
                doc = Document()
                doc.view.set_screen(scr)
                row = dct.get(filename)
                if ':' in filename:
                    filename, row = filename.split(':')
                    row = int(row) - 1
                doc.read(filename)
                doc.view.move(0, row or 0)
                self.docs.append(doc)
        else:
            self.docs = [Document()]
            self.docs[0].view.set_screen(scr)

        self.scr = scr

        if input is None:
            input = scr.input
        else:
            # This is a self-test and it needs the session object:
            input.session = self

        self.input = input

        self.action_stack = [Actions(self)]
        self.lastkey = None
        self.lasttime = 0.0
        self.memory = ['']

    def run(self):
        while True:
            self.loop()

    def loop(self):
        for doc in self.docs:
            for view in doc.views:
                view.update()
            if doc.changes:
                doc.color.run()
            doc.changes = None

        doc = self.docs[-1]
        actions = self.action_stack[-1]

        key = self.input()
        if len(key) == 1:
            actions.insert_character(doc, key)
        elif key == 'resize':
            self.scr.resize()
            for doc in self.docs:
                doc.changes = 42
        else:
            if key in doubles:
                key2 = self.input()
                key = doubles[key].get(key2)
                if key is None:
                    return
            else:
                key = keynames.get(key, key)
                if key is None:
                    return
                if key[0] == '^':
                    return
            if isinstance(key, list):
                self.scr.keys.extend(key)
                return
            if key in again and key == self.lastkey:
                key += '_again'
            elif (key in repeat and key == self.lastkey and
                  time() < self.lasttime + 0.3):
                key += key
            method = getattr(actions, key, None)
            if method is None:
                actions.unknown(doc, key)
            else:
                method(doc)
            if key.endswith('_again'):
                key = key[:-6]
        self.lastkey = key
        self.lasttime = time()

    def read(self):
        dct = collections.OrderedDict()
        with open(os.path.expanduser('~/.spelltinkle/session.txt')) as fd:
            for line in fd:
                name, r = line.rsplit(maxsplit=1)
                dct[name] = int(r)
        return dct

    def save(self):
        dct = self.read()
        for doc in self.docs:
            dct[doc.filename] = doc.view.r
        with open(os.path.expanduser('~/.spelltinkle/session.txt'), 'w') as fd:
            for name, r in dct.items():
                print(name, r, file=fd)

