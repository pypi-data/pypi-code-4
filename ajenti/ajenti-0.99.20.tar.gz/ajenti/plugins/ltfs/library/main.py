from ajenti.api import *
from ajenti.plugins.main.api import SectionPlugin
from ajenti.ui import on
from ajenti.ui.binder import Binder

from backend import *


@plugin
class LTFSLibraryPlugin (SectionPlugin):
    def init(self):
        self.title = 'Library'
        self.icon = 'reorder'
        self.category = 'LTFS'

        self.append(self.ui.inflate('ltfs:library-main'))
        self.backend = LTFSLibraryBackend()

        self.binder = Binder(self.backend, self)

        def post_drive_bind(object, collection, item, ui):
            ui.find('unload').on('click', self.on_unload, item)

        self.find('drives').post_item_bind = post_drive_bind

    def refresh(self):
        self.backend.reload()
        self.binder.reset().autodiscover().populate()

        l = list(set(self.backend.slots + self.backend.mailbox))
        l = sorted(l, key=lambda x: int(x.drive))

        def make_props(l):
            labels = ['%s [%s] (%s)' % (_.drive, _.status, _.barcode) for _ in l]
            values = [_.drive for _ in l]
            return labels, values

        list_empty = filter(lambda x: x.status == 'Empty', l)
        list_full = filter(lambda x: x.status == 'Full', l)
        self.find('source-slot').labels, self.find('source-slot').values = make_props(list_full)
        self.find('dest-slot').labels, self.find('dest-slot').values = make_props(list_empty)

    def _find_slot(self, id):
        for s in self.backend.slots + self.backend.mailbox:
            if s.drive == id:
                return s

    def on_page_load(self):
        self.refresh()

    @on('refresh', 'click')
    def on_refresh(self):
        self.refresh()

    @on('inquiry', 'click')
    def on_inquiry(self):
        self.backend.run_action('libstatus')
        self.context.notify('info', 'Inquiry started')

    @on('load', 'click')
    def on_load(self):
        item = self._find_slot(self.find('source-slot').value)
        self.backend.run_action('loadtape', item.barcode)
        self.context.notify('info', 'Loading. Please wait and refresh!')
        self.refresh()

    def on_unload(self, item):
        self.backend.run_action('unloadtape', item.drive)
        self.context.notify('info', 'Unloading. Please wait and refresh!')
        self.refresh()

    @on('move', 'click')
    def on_move(self):
        item = self._find_slot(self.find('source-slot').value)
        ditem = self._find_slot(self.find('dest-slot').value)
        self.backend.run_action('movetape', item.drive, ditem.drive)
        self.context.notify('info', 'Moving. Please wait and refresh!')
        self.refresh()

    @on('format', 'click')
    def on_format(self):
        item = self._find_slot(self.find('source-slot').value)
        self.backend.run_action('formattape', item.barcode)
        self.context.notify('info', 'Formatting. Please wait and refresh!')
        self.refresh()

    @on('fsck', 'click')
    def on_fsck(self):
        item = self._find_slot(self.find('source-slot').value)
        self.backend.run_action('fscktape', item.barcode)
        self.context.notify('info', 'Checking. Please wait and refresh!')
        self.refresh()
