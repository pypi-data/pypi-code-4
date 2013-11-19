from ajenti.api import *
from ajenti.plugins.main.api import SectionPlugin
from ajenti.ui import on
from ajenti.ui.binder import Binder

from pyltfs2 import LTFS, Tape, Entry

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
        self.files_binder = Binder(None, self.find('nav'))

        self.editing_tape = None
        self.creating_tape = False
        self.search_offset = 0
        self.last_query = None
        self.display_search(False)

        url = 'mysql+mysqlconnector://root:123@localhost/syslink_tapelibrary'

        self.ltfs = LTFS(url, debug=True)

        def post_tape_bind(object, collection, item, ui):
            lib = LTFSLibraryBackend()
            lib.reload()
            tapenames = [_.barcode for _ in lib.drives]
            tapenames += [_.barcode for _ in lib.slots]
            tapenames += [_.barcode for _ in lib.mailbox]

            def on_browse(tape):
                self.navigate(tape, None)

            def on_edit(tape):
                self.start_editing_tape(tape)

            def on_delete(tape):
                self.context.notify('info', "Tape deleted")
                self.ltfs.delete_tape(name=tape.name)

            ui.find('tape-warning').visible = item.name not in tapenames
            ui.find('edit').on('click', on_edit, item)
            ui.find('delete').on('click', on_delete, item)
            ui.find('browse').on('click', on_browse, item)

        self.find('tapes').post_item_bind = post_tape_bind

        def post_file_bind(object, collection, item, ui):
            def on_click(entry):
                self.navigate(item.tape, item)

            if item.is_dir:
                ui.find('name').on('click', on_click, item)

        self.find('nav_files').post_item_bind = post_file_bind

        def post_node_bind(object, collection, item, ui):
            def on_browse(entry):
                self.navigate(item.tape, item.parent)

            ui.find('browse').on('click', on_browse, item)

        self.find('nodes').post_item_bind = post_node_bind

        self.nav_files = []
        self.results = []
        #self.navigate(self.ltfs.get_tape(name='test'), None)

    def on_page_load(self):
        if not psycogreen_available:
            self.context.notify('err', "psycogreen package unavailable, large queries will time out")

    def navigate(self, tape, cwd):
        self.nav_cwd = cwd
        self.nav_files = self.ltfs.ls(tape, cwd)
        if len(self.nav_files) > 100:
            self.nav_files = self.nav_files[:100]
            #self.context.notify('info', 'Limited to 100 entries...')
        for file in self.nav_files:
            file.selected = False
            file.icon = 'folder-open' if file.is_dir else 'file'
        self.files_binder.reset(self).autodiscover().populate()
        self.find('nav-up').visible = cwd is not None

    @on('nav-up', 'click')
    def on_navigate_up(self):
        self.navigate(self.nav_cwd.tape, self.nav_cwd.parent)

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

        self.results = self.ltfs.search(query, limit=100, offset=offset)
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
        results = self.ltfs.search(self.find('search-query').value, False)
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
        self.files_binder.update()
        j = LTFSJob()
        for file in (self.results.nodes if self.results else []) + self.nav_files:
            if file.selected:
                j.source.append(LTFSSource(file.path()))
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

    @on('tape-dialog', 'button')
    def on_dialog(self, button=None):
        if button == 'cancel':
            self.find('tape-dialog').visible = False

        self.tape_binder.update()
        if button == 'save':
            found = self.ltfs.get_tape(name=self.editing_tape.name)
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
            tape = self.ltfs.get_tape(name=self.editing_tape.name)
            self.ltfs.delete_tape(name=tape.name)
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
