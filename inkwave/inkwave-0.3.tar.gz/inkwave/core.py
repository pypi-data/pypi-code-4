import logging
import os
import mimetypes
from collections import defaultdict

from sqlalchemy import (
    create_engine,
    Column,
    String,
    Integer,
)
from sqlalchemy.ext.declarative import (
    declarative_base,
    declared_attr,
)
from sqlalchemy.orm import sessionmaker

from inkwave.router import (
    Router,
    Route,
    Glob,
)
from inkwave.errors import EngineNotFound
from inkwave.utils import import_object


class TemplateEngine:
    """
    TemplateEngine
    """

    helpers = {}

    def render(self, name, data):
        "Render template"
        raise NotImplemented()


class FileLoader(Glob):
    def __init__(self, path, model):
        super(FileLoader, self).__init__(path)
        self.model = model

    def _load(self, path, data):
        name, ext = os.path.splitext(os.path.basename(path))

        data.update({
            'id':  path,
            'mtime': os.path.getmtime(path),
        })

        engine = env.engine('Data', ext)

        with open(path, 'r+') as fd:
            text = fd.read()

        data.update(engine(text))
        return self.model(**data)

    def load_all(self):
        for path, data in self.find(env.root):
            yield self._load(path, data)


class Resource(Route):
    def __init__(self, url, generator,
                 content_type=None, encoding=None, ext=None):
        super(Resource, self).__init__(url)
        self.generator = generator
        self.ext = ext
        self.content_type = content_type
        self.encoding = encoding

    def guess_type(self, path, default_type='application/octet-stream'):
        if self.content_type:
            return self.content_type, self.encoding or 'utf-8'

        content_type, encoding = mimetypes.guess_type(path, False)
        return (content_type or default_type,
                encoding or 'utf-8')

    def all(self):
        for data in self.generator.all():
            yield self.build_path(**data)

    def get(self, url, data, **kwargs):
        content_type, encoding = self.guess_type(url, default_type='text/html')
        data.update(self.generator.get(url, data))
        return (content_type,
                encoding,
                self.generator(url, **data))


class Generator:
    def __init__(self, fn):
        self.name = getattr(fn, 'name', None) or fn.__name__
        self.fn = fn

    def __call__(self, *args, **kwargs):
        return self.fn(*args, **kwargs)

    def all(self):
        return [{}]

    def get(self, path, data):
        return {}


class StaticDirGenerator:
    def __init__(self, path):
        self.name = path
        self.path = path

    def all(self):
        for f in os.listdir(os.path.join(env.root, self.path)):
            yield {'path': f}

    def get(self, path, data):
        return {}

    def __call__(self, url, path):
        with open(os.path.join(env.root, self.path, path), 'rb+') as fd:
            return fd.read()


class StaticFileGenerator:
    def __init__(self, path):
        self.name = path
        self.path = path

    def all(self):
        return [{}]

    def get(self, path, data):
        return {}

    def __call__(self, url):
        with open(os.path.join(env.root, self.path), 'rb+') as fd:
            return fd.read()


class FileGenerator(Generator):
    def __init__(self, fn, path, read=True, binary=True):
        super(FileGenerator, self).__init__(fn)
        self.path = Glob(path)
        self.read = read
        self.binary = binary

    def all(self):
        for path, data in self.path.find(env.root):
            yield data

    def get(self, path, data):
        fpath = self.path.build_path(**data)
        if self.read:
            flags = 'rb+' if self.binary else 'r+'
            with open(os.path.join(env.root, fpath), flags) as fd:
                return {'path': fpath, 'content': fd.read()}
        return {'path': fpath}


class QueryGenerator(Generator):
    def __init__(self, fn, query):
        super(QueryGenerator, self).__init__(fn)
        self.query = query

    def all(self):
        for i in self.query(Session()).all():
            yield dict(i.__dict__)

    def get(self, path, data):
        return {'result': self.query(env.db).filter_by(**data).one()}


class PaginateGenerator(Generator):
    def __init__(self, fn, items_per_page, offset=0):
        super(PaginateGenerator, self).__init__(fn)
        self.items_per_page = items_per_page
        self.offset = offset

    def all(self):
        page = 1
        skip = self.offset
        items = self.items_per_page
        result = []
        for i in self.fn.all():
            if skip > 0:
                skip -= 1
                continue
            result.append(i)
            items -= 1
            if items == 0:
                yield {'page': page, items: result}
                result = []
                page += 1
                items = self.items_per_page
        if result:
            yield {'page': page, items: result}

    def get(self, path, data):
        items = []
        result = {'page': data['page'], 'items': items}
        skip = self.items_per_page * data['page']
        for i in self.fn.all():
            if skip:
                skip -= 1
                continue
            items.append(i)
            if len(items) == self.items_per_page:
                break
        return result


class Table:
    @declared_attr
    def __tablename__(cls):
        return cls.__name__.lower()


class FileData:
    id = Column(String, primary_key=True)
    mtime = Column(Integer)


mimetypes.init()
Base = declarative_base(cls=Table)
Session = sessionmaker()


class Environment:
    """Environment

    `root`
        Site root path

    `out`
        Build path

    `config`
        Site config module

    `data`
        Data tables

    `site`
        Site resources

    `db`
        Database

    `adddress`
        Listening address for development server.

    `port`
        Listening port for development server.

    """

    log = logging.getLogger(__name__)

    engines = {}

    engines['Template'] = {
        '.jinja':  'inkwave.plugins.jinja.JinjaTemplateEngine()',
        '.mako':   'inkwave.plugins.mako.MakoTemplateEngine()',
    }

    engines['Data'] = {
        '.txt':        'inkwave.core.load_text',
        '.md':         'inkwave.plugins.markdown.load_markdown',
        '.yaml':       'inkwave.yaml.load_yaml',
        '.json':       'inkwave.json.load_json',
        '.rst':        'inkwave.rst.DataEngine()',
        '.wiki':       'inkwave.wiki.WikiDataLoader()',
        '.jinja':      'inkwave.jinja.JinjaDataLoader()',
        '.mako':       'inkwave.mako.MakoDataLoader()',
        '.html':       '.txt',
        '__default__': '.txt',
    }

    def __init__(self):
        self.namespaces = defaultdict(dict)
        self.hooks = defaultdict(list)
        self.data = Router()
        self.resources = Router()

    def init(self, path, config):
        self.log.info('Initializing Environment')
        self.root = path
        self.out = os.path.join(path, 'build')
        self.data_path = os.path.join(path, 'data')
        self.cache_path = os.path.join(path, '.cache')
        self.config = config

        self.address = getattr(config, 'address', '127.0.0.1')
        self.port = int(getattr(config, 'port', 8000))

        for url, src in getattr(config, 'STATICS', []):
            if url[-1] == '/':
                g = StaticDirGenerator(src)
                r = Resource(url + '<path|any>', g)
            else:
                g = StaticFileGenerator(src)
                r = Resource(url, g)
            self.resources.add(r, url)

    def init_db(self):
        self.log.info('Initializing Database')
        self.db_engine = create_engine('sqlite:///:memory:', echo=False)
        Session.configure(bind=self.db_engine)
        Base.metadata.create_all(self.db_engine)

        self.db = s = Session()
        for fl in self.data.routes:
            for m in fl.load_all():
                s.add(m)
                s.commit()
        s.flush()

    def engine(self, name, ext):
        engines = self.engines.get(name, None)
        if not engines:
            raise EngineNotFound(name, ext)
        e = ext
        e = engines.get(e, None)
        while e and isinstance(e, str) and e[0] == '.':
            e = engines.get(e, None)
        if not e:
            if '__default__' in engines:
                e = engines['__default__']
            raise EngineNotFound(name, ext)
        if isinstance(e, str):
            engines[ext] = e = import_object(e)
        return e

    def build_url(self, _name, *args, **kwargs):
        "TODO: remove this method"
        return self.resources[_name].build_path(*args, **kwargs)

    def url(self, name, *args, **kwargs):
        return self.resources[name].build_path(*args, **kwargs)


env = Environment()


def load(path):
    def d(cls):
        t = FileLoader(path, cls)
        env.data.add(t)
        return cls
    return d


def load_text(text):
    return {'content': text}


def render(name, ctx={}):
    _, ext = os.path.splitext(name)
    if not ext:
        raise RuntimeError('Invalid template name')
    engine = env.engine('Template', ext)
    return engine.render(name, ctx)


def helper(fn):
    TemplateEngine.helpers[fn.__name__] = fn
    return fn


def route(url, name=None, **kwargs):
    def d(v):
        if not isinstance(v, Generator):
            v = Generator(v)
        r = Resource(url, v, **kwargs)
        env.resources.add(r, name or v.name)
        return r
    return d


def files(path):
    def d(fn):
        return FileGenerator(fn, path)
    return d


def db(query):
    def d(fn):
        return QueryGenerator(fn, query)
    return d


def paginate(items_per_page, offset=0):
    def d(fn):
        return PaginateGenerator(fn, items_per_page, offset)
    return d


class query:
    def __init__(self, *args, **kwargs):
        self.args = args
        self.kwargs = kwargs
        self.calls = []

    def __getattr__(self, key):
        def _missing(*args, **kwargs):
            self.calls.append((key, args, kwargs))
            return self
        return _missing

    def __call__(self, session):
        q = session.query(*self.args, **self.kwargs)
        for name, args, kwargs in self.calls:
            q = getattr(q, name)(*args, **kwargs)
        return q
