from ajenti.api import *
from ajenti.plugins.main.api import SectionPlugin
from ajenti.ui import on
from ajenti.ui.binder import Binder

from backend import *


@plugin
class LTFSTapegroupsPlugin (SectionPlugin):
    def init(self):
        self.title = 'Tape Groups'
        self.icon = 'hdd'
        self.category = 'LTFS'

        self.append(self.ui.inflate('ltfs:tapegroups-main'))
        self.tgbackend = TapeGroupBackend()

        self.tgbinder = Binder(self.tgbackend, self.find('tapegroups'))
        self.find('groups').new_item = lambda c: TapeGroup()
        self.find('tapes').new_item = lambda c: Tape()

        def post_tape_bind(object, collection, item, ui):
            def move():
                self.tgbinder.update()
                for g in self.tgbackend.groups:
                    if item in g.tapes:
                        g.tapes.remove(item)
                    if g.id == ui.find('destination').value:
                        g.tapes.append(item)
                self.tgbinder.populate()
            ui.find('move').on('click', move)
            ui.find('destination').labels = [g.name for g in self.tgbackend.groups]
            ui.find('destination').values = [g.id for g in self.tgbackend.groups]

        self.find('tapes').post_item_bind = post_tape_bind

    def refresh(self):
        self.tgbackend.reload()
        self.tgbinder.reset().autodiscover().populate()

    def on_page_load(self):
        self.refresh()

    @on('refresh', 'click')
    def on_refresh(self):
        self.refresh()

    @on('save', 'click')
    def on_save(self):
        self.tgbinder.update()
        self.tgbackend.save()
        self.refresh()
