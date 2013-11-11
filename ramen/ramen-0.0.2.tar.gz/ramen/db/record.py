from .fields import *
from .proxy import DBProxy

from tornado import gen

__all__ = [
    'Record'
]


class MetaRecord(type):
    """
    MetaRecord
    """

    def __new__(mcs, name, bases, attrs):

        klass = type.__new__(mcs, name, bases, attrs)

        fields = []
        for base in klass.__mro__:
            for attr_name, attr in base.__dict__.items():
                if isinstance(attr, Field):
                    attr.set_key(attr_name)

                    if isinstance(attr, ForeignKey):
                        attr.install_relation(klass, name)

                    setattr(klass, attr_name, attr)
                    fields.insert(0, attr)

        fields = [f for i, f in enumerate(fields) if not f in fields[:i]]

        setattr(klass, '_fields', fields)

        return klass

def gen_task(fn):
    def wrapper(*args, **kwargs):
        return gen.Task(fn, *args, **kwargs)
    return wrapper

class Query(object):

    def __init__(self, klass, db):
        self.klass = klass
        self.db = db

        self._i = 0
        self._total = 0

        self._col = self.db[self.klass._collection]

        #self.statement = connection.get_statement()
        #self.statement.set_FROM(self.klass._collection)

        self.objects = []

        self._loaded = False
        self._query = {}
        self._limit = 100
        self._skip = 0
        self._sort = []


    def fetch_wrapper(self, obj, error, callback):
        self.objects = obj
        callback(self)

    @gen_task
    def fetch(self, callback):
        if not self._loaded:
            self._col.find(
                self._query,
                skip=self._skip,
                limit=self._limit,
                sort=self._sort
            ).to_list(callback = lambda o,e:self.fetch_wrapper(o, e, callback))
            self._loaded = True

    def __iter__(self):
        self._i = 0
        self._total = len(self.objects)
        return self

    def next(self):
        if self._i < self._total:
            self._i += 1
            return self.klass.init(self.objects[self._i - 1])
        else:
            raise StopIteration

    def result_wrapper(self, obj, error, callback):
        callback(self.klass.init(obj))

    @gen_task
    def get(self, *args, **kwargs):

        callback = kwargs.pop('callback')

        if len(args) == 1:
            obj = self._col.find_one(args[0], callback=lambda o,e:self.result_wrapper(o, e, callback))
        else:
            obj = self._col.find_one(kwargs, callback=lambda o,e:self.result_wrapper(o, e, callback))

    def filter(self, _query=None, **kwargs):
        query = kwargs or _query
        self._query.update(query)
        return self

    def skip(self, skip):
        self._skip = skip
        return self

    def limit(self, limit):
        self._limit = limit
        return self

    def sort(self, **kwargs):
        self._sort.extend(kwargs.items())

        return self



class ConnectionDescriptor(object):

    client = None

    def __init__(self):
        self.client = DBProxy().db

    def __get__(self, obj, owner):
        return self.client


class classproperty(object):
    def __init__(self, getter):
        self.getter = getter
    def __get__(self, instance, owner):
        return self.getter(owner)

class Record(dict):
    """
    Record
    """

    __metaclass__ = MetaRecord
    _collection = None
    _dbclient = ConnectionDescriptor()

    id = Field(default=None, alias='_id')

    def __init__(self, **kwargs):
        super(Record, self).__init__()
        self.update(kwargs)

        for f in self._fields:
            f.init(self)

    @classmethod
    def init(cls, attrs):
        obj = cls()
        obj.update(attrs)
        return obj

    @classproperty
    def Q(cls):
        return Query(cls, cls._dbclient)

    def _save_callback(self, new_id, error, callback):
        callback(new_id)

    def _generate_id_callback(self, next, error, callback):
        self.id = next['next']
        self._dbclient[self._collection].insert(self, callback=lambda o,e:self._save_callback(self.id,e,callback))

    @gen_task
    def save(self, callback):

        is_valid = all(f.validate(self) for f in self._fields)

        if is_valid:
            if self.id == None:
                self._dbclient['_sequences'].find_and_modify(
                    {'_id':self._collection},
                    {'$inc':{'next':1}},
                    True,
                    new=True,
                    callback=lambda o,e:self._generate_id_callback(o,e,callback)
                )
            else:
                self._dbclient[self._collection].update(
                    {'_id' : self.id},
                    self,
                    upsert=True,
                    callback=lambda o,e:self._save_callback(self.id,e,callback)
                )

        callback(is_valid)


