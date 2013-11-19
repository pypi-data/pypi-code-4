import os
from passlib.hash import sha512_crypt
from mako.lookup import TemplateLookup

from ajenti.api import plugin, BasePlugin
from ajenti.api.http import HttpPlugin, url
from ajenti.plugins import manager
from ..mediadb import DB, RootDirectory, Comment
from ajenti.plugins.elements.proxyfs import ProxyFS


@plugin
class ClientUIServer (BasePlugin, HttpPlugin):
    def init(self):
        self.db = DB.instance()
        self.templates = TemplateLookup(directories=manager.resolve_path('custom_media') + '/content/static/clientui')

    def require_login(fx):
        def wrapper(self, context, **kwargs):
            username = context.session.data.get('username', None)
            if not username:
                return context.redirect('/media/auth')
            else:
                kwargs['client'] = self.db.get_client(username)
            return fx(self, context, **kwargs)
        return wrapper

    def render(self, template, **args):
        return str(self.templates.get_template(template).render(**args))

    @url('/media/auth')
    def handle_auth(self, context):
        if 'username' in context.query:
            username = context.query['username'].value
            client = self.db.get_client(username)
            if client:
                password = context.query['password'].value
                if sha512_crypt.verify(password, client.password):
                    context.session.data['username'] = username
                    return context.redirect('/media')
        context.add_header('Content-Type', 'text/html')
        context.respond_ok()
        return self.open_content('static/clientui/auth.html').read()

    @url('/media/logout')
    def handle_logout(self, context):
        if 'username' in context.session.data:
            del context.session.data['username']
        return context.redirect('/media')

    @url('/media(/)?')
    @require_login
    def handle_root(self, context, client=None):
        context.add_header('Content-Type', 'text/html')
        context.respond_ok()
        return self.open_content('static/clientui/index.html').read()

    @url('/media/ajax/directory-list')
    @require_login
    def handle_directory_list(self, context, client=None):
        context.add_header('Content-Type', 'text/html')
        context.respond_ok()
        return self.render(
            'partial/directory-list.html',
            directories=[_.directory for _ in client.directory_permissions],
        )
 
    @url('/media/ajax/directory/(?P<id>\d+)')
    @require_login
    def handle_directory(self, context, id=None, client=None):
        directory = self.db.get_by_id(RootDirectory, id)
        context.add_header('Content-Type', 'text/html')
        context.respond_ok()
        return self.render(
            'partial/directory.html',
            directory=directory,
        )

    @url('/media/ajax/browse/(?P<id>\d+)/(?P<path>.+)')
    @require_login
    def handle_browse(self, context, id=None, path=None, client=None):
        directory = self.db.get_by_id(RootDirectory, id)

        context.add_header('Content-Type', 'text/html')
        context.respond_ok()
        directories = []
        files = []
        path = '/' + path.strip('/')
        fs = ProxyFS.get()

        basepath = os.path.join(directory.path, path.strip('/'))
        realpath = fs.proxy_path(basepath)

        if os.path.isdir(realpath):
            for i in list(fs.listdir(basepath)):
                fullpath = os.path.join(basepath, i)
                if os.path.isdir(fs.proxy_path(fullpath)):
                    directories.append(i)
                else:
                    files.append(i)
            return self.render(
                'partial/browse.html',
                current_directory=directory,
                path=path,
                directories=sorted(directories),
                files=sorted(files),
            )
        else:
            file = self.db.get_file(directory, path)
            if 'comment' in context.query:
                c = Comment(
                    file=file,
                    client=client,
                    text=context.query['comment'].value,
                    time=context.query['time'].value,
                )
                self.db.create(c)
                context.respond_ok()
                return ''

            return self.render(
                'partial/view.html',
                filename=os.path.split(path)[1],
                directory=directory,
                path=path,
                file=file,
            )

    @url('/media/stream/(?P<id>\d+)/(?P<path>.+)')
    @require_login
    def handle_stream(self, context, id=None, path=None, client=None):
        if '..' in path:
            return context.respond_forbidden()

        directory = self.db.get_by_id(RootDirectory, id)
        fs = ProxyFS.get()

        is_stream = False
        if path.endswith('mp4'):
            path = path[:-4]
            is_stream = True
        path = fs.proxy_path(os.path.join(directory.path, path))

        if not os.path.exists(path):
            return context.respond_not_found()

        context.add_header('Content-Type', 'video/mp4')
        return context.file(path, stream=is_stream)
