import gevent

from ajenti.api import *
from ajenti.plugins.main.api import SectionPlugin
from ajenti.ui import on
from ajenti.ui.binder import Binder

from backend import *
from ..tapegroups.backend import *


@plugin
class LTFSJobsPlugin (SectionPlugin):
    def init(self):
        self.title = 'Jobs'
        self.icon = 'hdd'
        self.category = 'LTFS'

        self.append(self.ui.inflate('ltfs:jobs-main'))
        self.backend = LTFSJobsBackend()
        self.tgbackend = TapeGroupBackend()

        self.binder = Binder(self.backend, self)
        self.add_binder = Binder(None, self.find('add-dialog'))

        self.adding_job = None

        def post_job_bind(object, collection, item, ui):
            ui.find('resume').visible = item.status.upper() == 'PAUSED'
            ui.find('pause').visible = item.status.upper() != 'PAUSED'
            ui.find('cancel').visible = item.status.upper() in ['FINISHED', 'PAUSED', 'ERROR']
            ui.find('log').on('click', self.on_view_log, item)
            ui.find('files').on('click', self.on_list_files, item)
            ui.find('pause').on('click', self.on_action, 'pause', item)
            ui.find('resume').on('click', self.on_action, 'resume', item)
            ui.find('cancel').on('click', self.on_action, 'cancel', item)

        self.find('jobs').post_item_bind = post_job_bind

    def refresher(self):
        while True:
            self.refresh()
            gevent.sleep(120)

    def refresh(self):
        self.backend.reload()
        self.tgbackend.reload()
        self.binder.reset().autodiscover().populate()
        if self.adding_job:
            self.add_binder.reset(self.adding_job).autodiscover().populate()

    def on_page_load(self):
        self.context.endpoint.spawn(self.refresher)
        self.refresh()

    @on('refresh', 'click')
    def on_refresh(self):
        self.refresh()

    def on_list_files(self, job):
        self.find('file-list-dialog').visible = True
        self.find('file-list-dialog').find('list').value = '\n'.join(f.path for f in job.source)

    def on_view_log(self, job):
        self.context.launch('view-log', path=self.backend.get_log_path(job))

    @on('file-list-dialog', 'button')
    def on_file_list_dialog_close(self, button=None):
        self.find('file-list-dialog').visible = False

    def on_action(self, action, job):
        self.backend.run_action(action, job)
        self.refresh()

    @on('add-job', 'click')
    def on_add(self):
        self.adding_job = LTFSJob()
        self.find('add-dialog').visible = True

        groups = [None] + [g.id for g in self.tgbackend.groups]
        groupl = ['None'] + [g.name for g in self.tgbackend.groups]

        self.find('add-dialog').find('group').values = groups
        self.find('add-dialog').find('group').labels = groupl
        self.find('add-dialog').find('group2').values = groups
        self.find('add-dialog').find('group2').labels = groupl

        self.refresh()

    @on('add-source-file', 'click')
    def on_add_file(self):
        self.add_binder.update()
        self.find('add-file-dialog').visible = True

    @on('add-source-dir', 'click')
    def on_add_dir(self):
        self.add_binder.update()
        self.find('add-dir-dialog').visible = True

    @on('add-dialog', 'button')
    def on_dialog(self, button=None):

        self.add_binder.update()
        if button == 'save':
            if len(self.adding_job.source) == 0:
                self.context.notify('error', 'Please add at least one source')
            j1 = self.adding_job
            j2 = self.adding_job.clone()
            j2.destination = j1.destination2
            j2.group = j1.group2
            j2.export = j1.export2

            if j1.group != 'null':
                self.backend.create_job(j1)

            if j2.group != 'null':
                self.backend.create_job(j2)

            if j1.group != 'null' and j2.group != 'null':
                j2.has_copy2 = 'yes'
                j2.copy2_id = j1.id
                self.backend.resave_job(j2)

                j1.has_copy2 = 'yes'
                j1.copy2_id = j2.id
                self.backend.resave_job(j1)

            self.refresh()

        self.find('add-dialog').visible = False
        self.adding_job = None

    @on('add-file-dialog', 'select')
    def on_add_file_dialog_select(self, path=None):
        self.find('add-file-dialog').visible = False
        if path:
            self.adding_job.source.append(LTFSSource(path))
            self.refresh()

    @on('add-dir-dialog', 'select')
    def on_add_dir_dialog_select(self, path=None):
        self.find('add-dir-dialog').visible = False
        if path:
            self.adding_job.source.append(LTFSSource(path))
            self.refresh()
