import subprocess
import cPickle
import json
import os
from slugify import slugify

import ajenti
from ajenti.api import *
from ajenti.api.http import HttpPlugin, url
from ajenti.plugins.main.api import SectionPlugin
from ajenti.plugins.services.api import ServiceMultiplexor
from ajenti.ui import on
from ajenti.ui.binder import Binder
from ajenti.plugins import manager

from reconfigure.configs import SambaConfig, ExportsConfig, NetatalkConfig
import reconfigure.items.samba
import reconfigure.items.netatalk
import reconfigure.items.exports


SHARE_NAME = '__projects'
IDENTIFICATION_COMMENT = 'Created by Elements Storage, do not edit'
ROOT = '/mnt/snfs1/.projects'


class ElementsProject (object):
    def __init__(self):
        self.name = ''
        self.directory = ''
        self.permissions = []
        self.verify()

    @property
    def path(self):
        return os.path.join(ROOT, self.directory)

    def verify(self):
        if not hasattr(self, 'directory') or not self.directory:
            self.directory = slugify(self.name)
        defaults = {
            'lock': None,
            'emulate_avid': False,
            'share_nfs': False,
            'share_afp': False,
            'share_smb': False,
            'quota_size_soft': 0,
            'quota_size_hard': 0,
        }
        for k, v in defaults.iteritems():
            if not hasattr(self, k):
                setattr(self, k, v)

        if self.directory and not os.path.exists(self.path):
            os.mkdir(self.path)

    def json(self):
        return {
            'name': self.name,
            'path': self.path,
            'directory': self.directory,
            'lock': self.lock,
            'emulate_avid': self.emulate_avid,
        }

    def is_allowed_for(self, user):
        for p in self.permissions:
            if p.user == user:
                return True
        return False


class ElementsProjectPermission (object):
    def __init__(self):
        self.project = None
        self.user = 'root'


@plugin
class ElementsProjectManager (BasePlugin):
    default_classconfig = {'projects': ''}
    classconfig_root = True

    def init(self):
        self.smb_config = SambaConfig(path='/etc/samba/smb.conf')
        self.afp_config = NetatalkConfig(path='/etc/afp.conf')
        self.nfs_config = ExportsConfig(path='/etc/exports')

        if not os.path.exists(ROOT):
            os.mkdir(ROOT)

        try:
            self.projects = cPickle.loads(str(self.classconfig['projects']))
        except:
            self.projects = []

        for p in self.projects:
            p.verify()

    def get_project(self, name):
        for p in self.projects:
            if p.name == name:
                return p
        return None

    def lock(self, name, user):
        p = self.get_project(name)
        if p.lock and p.lock != user:
            return False
        p.lock = user
        return True

    def unlock(self, name, user):
        p = self.get_project(name)
        if not p.lock or p.lock == user:
            p.lock = None
            return True
        return False

    def __call_quota(self, p, args):
        d = subprocess.check_output(['snquota', '-F', 'snfs1', '-d', '.projects/' + p.directory] + args)
        print d
        return d

    def _parse_quotasize(self, s):
        sfx = s[-1]
        i = float(s[:-1])
        if sfx == 'K':
            i *= 1024
        if sfx == 'M':
            i *= 1024 ** 2
        if sfx == 'G':
            i *= 1024 ** 3
        if sfx == 'T':
            i *= 1024 ** 4
        return i / (1024 ** 3)

    def save(self):
        self.smb_config.load()
        self.nfs_config.load()
        self.afp_config.load()

        for share in self.smb_config.tree.shares:
            if share.name == SHARE_NAME:
                self.smb_config.tree.shares.remove(share)
                continue
            if share.comment == IDENTIFICATION_COMMENT:
                try:
                    self.smb_config.tree.shares.remove(share)
                except:
                    pass

        for share in self.nfs_config.tree.exports:
            if share.comment == IDENTIFICATION_COMMENT:
                self.nfs_config.tree.exports.remove(share)

        for share in self.afp_config.tree.shares:
            if share.comment == IDENTIFICATION_COMMENT:
                self.afp_config.tree.shares.remove(share)

        s = reconfigure.items.samba.ShareData()
        s.name = SHARE_NAME
        s.path = ROOT
        s.browseable = False
        s.read_only = False
        s.guest_ok = True
        self.smb_config.tree.shares.append(s)

        for p in self.projects:
            self.__call_quota(p, ['-C'])
            if p.quota_size_hard:
                self.__call_quota(p, ['-S', '-h', '%sg' % p.quota_size_hard, '-s', '%sg' % p.quota_size_soft, '-t', '1d'])

            if p.share_smb:
                s = reconfigure.items.samba.ShareData()
                s.name = p.name
                s.comment = IDENTIFICATION_COMMENT
                s.path = os.path.join(ROOT, p.directory)
                s.read_only = False
                s.guest_ok = True
                self.smb_config.tree.shares.append(s)
            if p.share_nfs:
                s = reconfigure.items.exports.ExportData()
                s.name = os.path.join(ROOT, p.directory)
                c = reconfigure.items.exports.ClientData()
                c.name = '*'
                c.options = 'rw,insecure,no_subtree_check,rsize=2097152,wsize=2097152,async,tcp'
                s.comment = IDENTIFICATION_COMMENT
                s.clients.append(c)
                self.nfs_config.tree.exports.append(s)
            if p.share_afp:
                s = reconfigure.items.netatalk.ShareData()
                s.name = p.name
                s.comment = IDENTIFICATION_COMMENT
                s.path = os.path.join(ROOT, p.directory)
                s.read_only = False
                s.valid_users = 'root,client'
                self.afp_config.tree.shares.append(s)

        # Read quota status
        q = json.loads(subprocess.check_output(['snquota', '-L', '-Fsnfs1', '-ojson']))
        q = q['directoryQuotas']
        for e in q:
            if e['type'] == 'dir':
                for p in self.projects:
                    if e['name'] == '/.projects/' + p.directory:
                        p.quota_size_status = e['status']
                        try:
                            p.quota_size_current = self._parse_quotasize(e['curSize'])
                            p.quota_size_usage = p.quota_size_current / p.quota_size_hard
                        except:
                            p.quota_size_current = 0
                            p.quota_size_usage = 0

        self.smb_config.save()
        self.nfs_config.save()
        self.afp_config.save()

        ServiceMultiplexor.get().get_one('smb' if ajenti.platform == 'centos' else 'smbd').command('reload')
        subprocess.call(['exportfs', '-a'])
        #ServiceMultiplexor.get().get_one('nfs' if ajenti.platform == 'centos' else 'nfs-kernel-server').restart()
        #ServiceMultiplexor.get().get_one('netatalk').restart()
        subprocess.check_output(['/etc/init.d/netatalk', 'restart'])

        self.classconfig['projects'] = cPickle.dumps(self.projects)
        self.save_classconfig()


try:
    ElementsProjectManager.get().save()
except Exception, e:
    print e


@plugin
class ElementsProjects (SectionPlugin):
    def init(self):
        self.title = 'Projects'
        self.icon = 'suitcase'
        self.category = 'Elements'
        self.append(self.ui.inflate('elements:projects-main'))

        #def post_graph_bind(o, c, i, u):
        #    for plot in u.nearest(lambda x: x.typeid == 'munin:plot'):
        #        plot.on('widget', self.on_add_widget, i)
        #
        #self.find('graphs').post_item_bind = post_graph_bind

        self.find('projects').new_item = lambda c: ElementsProject()
        self.find('permissions').new_item = lambda c: ElementsProjectPermission()
        self.find('user-dropdown').labels = self.find('user-dropdown').values = list(ajenti.config.tree.users)

        self.mgr = ElementsProjectManager.get(manager.context)
        self.binder = Binder(None, self)

    def on_page_load(self):
        self.refresh()

    def refresh(self):
        self.binder.reset(self.mgr).autodiscover().populate()

    @on('new-project', 'click')
    def on_new_project(self):
        self.save()
        p = ElementsProject()
        p.name = self.find('new-project-name').value
        if p.name:
            self.mgr.projects.append(p)
            p.verify()
            self.mgr.save()
            self.refresh()
            self.find('new-project-name').value = ''

    @on('save', 'click')
    def save(self):
        self.binder.update()
        self.mgr.save()


@plugin
class ElementsProjectServer (HttpPlugin):
    def init(self):
        self.mgr = ElementsProjectManager.get(manager.context)

    @url('/elements/projects/(?P<endpoint>.+)')
    def get_page(self, context, endpoint):
        if context.session.identity is None:
            context.respond_forbidden()

        context.respond_ok()

        endpoint = endpoint.split('/')

        if endpoint[0] == 'test':
            return 'ok'

        if endpoint[0] == 'lock-project':
            self.mgr.lock(endpoint[1], context.session.identity)
            return 'ok'

        if endpoint[0] == 'unlock-project':
            self.mgr.unlock(endpoint[1], context.session.identity)
            return 'ok'

        if endpoint[0] == 'unlock-all':
            for p in self.mgr.projects:
                self.mgr.unlock(p.name, context.session.identity)
            return 'ok'

        if endpoint[0] == 'list-projects':
            return json.dumps([p.json() for p in self.mgr.projects if p.is_allowed_for(context.session.identity)])
