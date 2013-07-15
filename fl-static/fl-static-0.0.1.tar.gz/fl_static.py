from werkzeug.serving import run_simple
from werkzeug.wsgi import DispatcherMiddleware
import jinja2
import static


try: from pkg_resources import resource_filename, Requirement
except: pass


class Cling(DispatcherMiddleware):

    cling_class = static.Cling

    def __init__(self, app, **kw):
        if app:
            self.app = app
            self.init_app(app, **kw)

    def init_app(self, app, **kw):
        self.root = app.config.get('STATIC_ROOT', kw.pop('root'))
        self.url = app.config.get('STATIC_URL', kw.pop('url', '/static'))
        for option in ('block_size', 'index_file'):
            val = app.config.get('STATIC_%s' % option.upper())
            if val:
                kw[option] =val
        super(Cling, self).__init__(
            app,
            {self.url: self.cling_class(self.root, **kw)},
        )

    def run(self, hostname='localhost', port=5000, **kw):
        kw.setdefault('use_reloader', kw.pop('debug', False))
        run_simple(hostname, port, self, **kw)


def cling_wrap(package_name, dir_name, **kw):
    resource = Requirement.parse(package_name)
    return Cling(resource_filename(resource, dir_name), **kw)


class Shock(Cling):

    cling_class = static.Shock


class Jinja2Magic(static.StringMagic):

    extension = '.jinja'

    def __init__(self, *args, **kw):
        super(Jinja2Magic, self).__init__(*args, **kw)

    def body(self, environ, file_like):
        return [jinja2.Template(
            file_like.read(),
        ).render(
            environ=environ,
            **self.variables
        ).encode('utf-8')]
