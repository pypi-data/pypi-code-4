from passlib.hash import sha512_crypt

from ajenti.api import plugin
from ajenti.plugins.main.api import SectionPlugin
from ajenti.ui import on
from ajenti.ui.binder import Binder

from ..mediadb import DB, Client, RootDirectory, ClientDirectoryPermission


@plugin
class MediaLibrarySection (SectionPlugin):
    def init(self):
        self.title = 'Media Library'
        self.icon = 'play-circle'
        self.category = 'Elements'
        self.append(self.ui.inflate('custom_media:admin-main'))

        def post_directory_bind(o, c, i, u):
            u.find('create-permission').on('click', self.on_create_permission, i)

        self.find('clients').delete_item = lambda i,c: self.delete_object(i)
        self.find('directories').delete_item = lambda i,c: self.delete_object(i)
        self.find('permissions').delete_item = lambda i,c: self.delete_object(i)
        self.find('directories').post_item_bind = post_directory_bind
     
        self.clients = []
        self.directories = []
        
        self.binder = Binder(self, self)
        self.binder.autodiscover()
        self.db = DB.instance()

    def on_page_load(self):
        self.refresh()

    def refresh(self):
        self.clients = self.db.list(Client)
        self.directories = self.db.list(RootDirectory)
        self.binder.unpopulate()

        self.find('user-dropdown').values = [None] + self.clients
        self.find('user-dropdown').labels = [''] + [_.username for _ in self.clients]

        self.binder.populate()

    def delete_object(self, object):
        self.save()
        self.db.delete(object)
        self.refresh()

    @on('create-client', 'click')
    def on_create_client(self):
        self.save()
        c = Client(username='unnamed', password='')
        self.db.create(c)
        self.refresh()

    @on('create-directory', 'click')
    def on_create_directory(self):
        self.save()
        d = RootDirectory(name='unnamed', path='/')
        self.db.create(d)
        self.refresh()

    def on_create_permission(self, directory):
        self.save()
        p = ClientDirectoryPermission(directory=directory, client=None)
        self.db.create(p)
        self.refresh()

    @on('save', 'click')
    def save(self):
        self.binder.update()
        
        for client in self.clients:
            if not client.password.startswith('$'):
                client.password = sha512_crypt.encrypt(client.password)
        self.db.commit()
        self.refresh()
