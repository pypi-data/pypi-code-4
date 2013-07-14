from ajenti.api import *
from ajenti.plugins.main.api import SectionPlugin
from ajenti.ui import on
from ajenti.ui.binder import Binder

import pyLTFS

try:
    import psycogreen.gevent
    psycogreen.gevent.patch_psycopg()
    psycogreen_available = True
except:
    psycogreen_available = False


from ..jobs.backend import LTFSJobsBackend, LTFSJob, LTFSSource
from ..library.backend import LTFSLibraryBackend

CHECKSUM_FILE = '/var/lib/syslink/archive/checksums'


@plugin
class LTFSArchivePlugin (SectionPlugin):
    def init(self):
        self.title = 'Archive'
        self.icon = 'list'
        self.category = 'LTFS'

        self.append(self.ui.inflate('ltfs:archive-main'))
        self.binder = Binder(None, self.find('search-results'))
        self.restore_binder = Binder(None, self.find('restore-dialog'))
        self.tape_binder = Binder(None, self.find('tape-dialog'))
        self.editing_tape = None
        self.creating_tape = False
        self.search_offset = 0
        self.last_query = None
        self.display_search(False)

        self.ltfs = pyLTFS.TapeLibraryHandler()
        self.ltfs.options["iMaxDepth_sqlamp"] = 9999
        self.ltfs.options["iLogLevel"] = 2
        self.ltfs.lic_InitDB(
            sUser="dbuser",
            sPass="syslink",
            sDBName="syslink_tapelibrary",
            sDBType="postgresql"
        )

        def post_tape_bind(object, collection, item, ui):
            lib = LTFSLibraryBackend()
            lib.reload()
            tapenames = [_.barcode for _ in lib.drives]
            tapenames += [_.barcode for _ in lib.slots]
            tapenames += [_.barcode for _ in lib.mailbox]

            ui.find('tape-warning').visible = item.name not in tapenames
            ui.find('edit').on('click', self.on_edit, item)
            ui.find('delete').on('click', self.on_delete, item)

        self.find('tapes').post_item_bind = post_tape_bind

        def post_file_bind(object, collection, item, ui):
            ui.find('pad').text = '&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;' * item.depth + ('&lfloor;' if item.depth else '')

        self.find('nodes').post_item_bind = post_file_bind

    def on_page_load(self):
        if not psycogreen_available:
            self.context.notify('err', "psycogreen package unavailable, large queries will time out")

    @on('search-files', 'click')
    def on_search_files(self):
        q = self.find('search-query').value
        if q or len(q) > -2:
            self.search(q)
        else:
            self.context.notify('error', 'Search query is too short!')

    def search(self, query=None, offset=0):
        self.search_offset = offset
        query = query or self.last_query
        self.last_query = query

        self.results = self.ltfs.lic_FilterSearchTerm(query, limit=100, offset=offset)
        for file in self.results.nodes:
            file.selected = False
        self.binder.reset(self.results).autodiscover().populate()

        self.find('page-indicator').text = 'Page %i (%i results total)' % (offset / 100 + 1, self.results.total)
        self.display_search(True, len(self.results.nodes) > 99 or self.search_offset != 0)

    def display_search(self, visible=True, paging=True):
        self.find('page-indicator').visible = visible
        self.find('page-next').visible = visible and paging
        self.find('page-prev').visible = visible and paging
        self.find('select-all').visible = visible
        self.find('clear').visible = visible
        self.find('restore').visible = visible

    @on('select-all', 'click')
    def on_select_all(self):
        for file in self.results.nodes:
            file.selected = True
        self.binder.populate()

    @on('page-prev', 'click')
    def on_page_prev(self):
        if self.search_offset > 0:
            self.search(offset=self.search_offset - 100)

    @on('page-next', 'click')
    def on_page_next(self):
        self.search(offset=self.search_offset + 100)

    @on('clear', 'click')
    def on_clear_search(self):
        self.display_search(False)
        self.binder.reset(None)

    @on('search-tapes', 'click')
    def on_search_tapes(self):
        results = self.ltfs.lic_FilterSearchTerm(self.find('search-query').value, False)
        self.binder.reset(results).autodiscover().populate()

    @on('add', 'click')
    def on_add(self):
        tape = self.ltfs.DBContentTape()
        tape.name = 'New tape'
        tape.root = '/'
        self.creating_tape = True
        self.start_editing_tape(tape)

    @on('restore', 'click')
    def on_restore(self):
        self.binder.update()
        j = LTFSJob()
        for file in self.results.nodes:
            if file.selected:
                j.source.append(LTFSSource(file.path))
                j.selected_tape = file.tape.name
        j.type = 'RESTORE'

        self.creating_job = j
        self.restore_binder.reset(self.creating_job).autodiscover().populate()
        self.find('restore-dialog').visible = True

    @on('restore-dialog', 'button')
    def on_restore_dialog(self, button=None):
        self.restore_binder.update()
        self.find('restore-dialog').visible = False

        if button == 'ok':
            LTFSJobsBackend().create_job(self.creating_job)
            self.context.notify('info', 'Job created')

    @on('restore-destination-select', 'click')
    def on_restore_destination_select(self):
        self.restore_binder.update()
        self.find('restore-destination-dialog').visible = True

    @on('restore-destination-dialog', 'select')
    def on_restore_destination_selected(self, path=None):
        self.find('restore-destination-dialog').visible = False
        self.creating_job.destination = path
        self.restore_binder.reset().autodiscover().populate()

    def on_edit(self, tape):
        self.start_editing_tape(tape)

    def on_delete(self, tape):
        self.context.notify('info', "Tape deleted")
        self.ltfs.lic_deleteTape(tape.name)

    @on('tape-dialog', 'button')
    def on_dialog(self, button=None):
        if button == 'cancel':
            self.find('tape-dialog').visible = False

        self.tape_binder.update()
        if button == 'save':
            found = self.ltfs.lic_getTape(sName=self.editing_tape.name)
            if found and found != self.editing_tape:
                self.context.notify('error', "This tape already exists. Pick a different name or press Reindex to re-index contents")
            else:
                if self.creating_tape:
                    self.creating_tape = False
                    self.ltfs.lic_CreateTape(
                        self.editing_tape.root,
                        self.editing_tape.name,
                        self.editing_tape.custom_a,
                        self.editing_tape.custom_b,
                        self.editing_tape.custom_c,
                        self.editing_tape.custom_d,
                    )
                    self.context.notify('info', "Indexing complete")
                else:
                    self.ltfs.session.merge(self.editing_tape)
                    self.ltfs.session.commit()
                self.editing_tape = None
                self.find('tape-dialog').visible = False
        if button == 'reindex':
            self.find('tape-dialog').visible = False
            tape = self.ltfs.lic_getTape(sName=self.editing_tape.name)
            self.ltfs.lic_deleteTape(tape.name)
            self.ltfs.lic_CreateTape(
                self.editing_tape.root,
                tape.name,
                tape.custom_a,
                tape.custom_b,
                tape.custom_c,
                tape.custom_d,
            )
            self.editing_tape = None
            self.context.notify('info', "Re-indexing complete")

    def start_editing_tape(self, tape):
        self.editing_tape = tape
        if not hasattr(tape, 'root'):
            tape.root = '/'
        self.tape_binder.reset(self.editing_tape).autodiscover().populate()
        self.find('tape-dialog').visible = True
