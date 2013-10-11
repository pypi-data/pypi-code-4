from abc import ABCMeta
from docmongo.exceptions import FieldTypeError, NotPrimaryError, InvalidArgumentError
from docmongo.fields import BaseField, field_to_object
from docmongo.delegate import DelegatePymongo


class Document(metaclass=ABCMeta):
    """
    Attributes:
        _host: host address
        _dbname: db name
        _colname: collection name
        fields: define mongodb fields
        __data: storage data
    """
    reserved_fields = ['_id']
    fields = {}
    _host = 'localhost:27017'
    _get_key = '_id' # primary key
    _created_at = False
    _updated_at = False

    # connector
    _delegation = DelegatePymongo
    __cache = dict()

    def __init__(self, init_fields=None):
        self.__data = dict()

        if init_fields is None:
            init_fields = dict()
        self.__data_initialize(self.__class__.fields, init_fields)

    def __getattr__(self, name):
        if name in self.__class__._reserved_fields():
            return self.__data.get(name)
        elif name in self.__class__.fields:
            return self.__data[name].g()
        raise AttributeError('no attribute: {0}'.format(name))

    def __setattr__(self, name, value):
        if name in self.__class__._reserved_fields():
            self.__data[name] = value
        elif name in self.__class__.fields:
            self.__data[name].s(value)
            self.__data[name].validate()
        else:
            self.__dict__[name] = value

    @classmethod
    def get(cls, key):
        entity = cls._delegate('find_one', {cls._get_key: key})
        if entity is not None:
            entity = cls(entity)
        return entity

    @classmethod
    def items(cls):
        entities = cls._delegate("find")
        return entities.sort("created_at")

    @classmethod
    def delegation(cls):
        key = '{0}_{1}_{2}'.format(cls._host, cls._dbname, cls.colname())
        if key not in cls.__cache:
            cls.__cache[key] = cls._delegation(
                cls._host, cls._dbname, cls.colname())
        return cls.__cache[key]

    @classmethod
    def get_or_new(cls, key):
        """
        Args:
            key: primary key
        """
        entity = cls.get(key)
        if entity is None:
            d = cls._init_dict()
            d[cls._get_key] = key

            cls.insert(d)
            entity = cls.get(key)
        return entity

    @classmethod
    def _init_dict(cls):
        d = {}
        for key, value in cls.fields.items():
            if callable(value):
                value = value()
            d[key] = value.get_init_value()
        return d

    @classmethod
    def set_db(cls, db):
        """overwrite db class method
        """
        cls.db = db

    @classmethod
    def db(cls):
        return cls.delegation().db()

    @classmethod
    def all(cls):
        return cls._delegate('find')

    @classmethod
    def dict_in_fields(cls, d):
        s = set(d)
        return s.issubset(list(cls.fields.keys()) + ['_id'])

    @classmethod
    def insert(cls, d, safe=True):
        """ direct insert MongoDB

        Args:
            d: insert values, type of dict

        Return:
            generate object by insert value
        """
        if cls.dict_in_fields(d) is False:
            raise FieldTypeError('type error {0}'.format(d))
        init_dict = cls._init_dict()
        init_dict.update(d)

        if cls._created_at:
            import datetime
            init_dict['created_at'] = datetime.datetime.now()
        if cls._updated_at:
            import datetime
            init_dict['updated_at'] = datetime.datetime.now()

        cls._delegate('insert', init_dict, safe=safe)
        return cls(init_dict)

    @classmethod
    def update(cls, d, safe=True):
        """ udpate MongoDB

        d: dict
        """
        import datetime

        if not isinstance(d, dict):
            raise InvalidArgumentError('type error {0}'.format(type(d)))

        if "_id" not in d:
            raise InvalidArgumentError('not in _id {0}'.format(d))

        _id = d['_id']
        save_dict = d.copy()
        del save_dict["_id"]

        if cls._updated_at:
            save_dict['updated_at'] = datetime.datetime.now()

        cls._delegate('update', {'_id': _id}, {'$set': save_dict},
            safe=safe)

    @classmethod
    def remove(cls, obj, safe=True):
        if not isinstance(obj, dict):
            obj = obj.to_dict()
        cls._delegate('remove', obj, safe=safe)

    @classmethod
    def colname(cls):
        if hasattr(cls, '_colname'):
            return cls._colname
        name = cls.__name__
        return name[0].lower() + name[1:]

    @classmethod
    def _reserved_fields(cls):
        fields = cls.reserved_fields[:]
        if cls._created_at:
            fields.append('created_at')
        if cls._updated_at:
            fields.append('updated_at')
        return fields

    @classmethod
    def _delegate(cls, func_name, *query, **kwquery):
        return cls.delegation()._delegate(
            func_name, *query, **kwquery)

    def key(self):
        return getattr(self, self.__class__._get_key)

    def assign_dict(self, d):
        for key in d:
            if key in self.__class__.fields:
                setattr(self, key, d[key])

    def is_primary(self):
        cls = self.__class__
        entities = cls._delegate('find', {cls._get_key: self.key()})

        if entities is None:
            return True
        cal = [entity for entity in entities if entity['_id'] != self._id]
        return len(cal) == 0

    def save(self, safe=True):
        """ publish save query"""
        import datetime

        if not self.is_primary():
            raise NotPrimaryError(
                'key:{0}, {1} is duplicate value'.format(self.__class__._get_key, self.key()))

        s = {}
        for key, obj in self.__data.items():
            if key in self.__class__._reserved_fields():
                value = obj
            else:
                if obj.validate() is False:
                    raise FieldTypeError('type error {0}:{1}'.format(key, obj.get()))
                value = obj.g()
            s[key] = value

        if self.__class__._created_at and not s.get('created_at'):
            self.created_at = datetime.datetime.now()
            s['created_at'] = self.created_at
        if self.__class__._updated_at:
            self.updated_at = datetime.datetime.now()
            s['updated_at'] = self.updated_at
        self.__class__._delegate('save', s, safe=safe)

    def inc(self, key, value, safe=True):
        """ publish inc query"""
        if not hasattr(self, key):
            raise FieldTypeError('type error {0}'.format(key))
        v = getattr(self, key) + value
        setattr(self, key, v)
        query = {self.__class__._get_key: self.key()}
        self.__class__._delegate('update', query, {'$inc': {key: value}}, safe=safe)

    def to_dict(self):
        d = {}
        fields = list(self.__class__.fields.keys()) + self.__class__._reserved_fields()
        for field in fields:
            if hasattr(self, field):
                d[field] = getattr(self, field)

        return d

    def __data_initialize(self, fields, init_fields):
        for key in fields:
            if key in init_fields:
                if isinstance(init_fields[key], BaseField):
                    value = init_fields[key]
                else:
                    value = field_to_object(init_fields[key])
            else:
                if callable(fields[key]):
                    value = fields[key]()
                else:
                    value = fields[key]
            self.__data[key] = value

        for key in self.__class__._reserved_fields():
            if key in init_fields:
                self.__data[key] = init_fields[key]
