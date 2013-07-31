#coding=utf-8
# $Id: models.py 641 2012-09-13 13:03:32Z anton $

from settings import DB
from ramen.rules import Rules
from ramen.admin import admin
from ramen.trigger import *
from mongoq import Q
import re

class classproperty(object):
    def __init__(self, getter):
        self.getter = getter
    def __get__(self, instance, owner):
        return self.getter(owner)

class ActiveRecordException(Exception):
    pass

class Rowset(DB, list):
    """Rowset - database pattern"""

    _loaded = False
    _index = -1
    _skip = 0
    _limit = 0

    def __init__(self, collection, model, fields=None):
        self.collection = collection
        self.model = model
        self.cond = dict(model._auto)
        self._loaded = False
        self._fields = fields
        self._skip = 0
        self._limit = 0
        self._sorting = []

    def load(self):
        if not self._loaded:
            self.__setslice__(0, self.__len__(), self.collection.find(self.cond, fields=self._fields, skip=self._skip, limit=self._limit, sort=self._sorting))
            self._loaded = True

        return self

    def count(self, full = False):
        return self.collection.find(self.cond, fields=self._fields, skip=self._skip, limit=self._limit).count(with_limit_and_skip=True)

    def __len__(self):
        return self.count()

    def __iter__(self):
        self.load()
        self._index = -1
        return self

    def fields(self, fields):
        self._fields = fields
        self._loaded = False
        return self

    def limit(self, lim):
        self._limit = lim
        self._loaded = False
        return self

    def skip(self, sk):
        self._skip = sk
        self._loaded = False
        return self

    def all(self):
        self.cond = self.model._auto
        self._loaded = False
        return self

    def filter(self, cond):
        self.cond.update(cond)
        self._loaded = False
        return self

    def sort(self, sorting):
        self._sorting = sorting
        self._loaded = False
        return self

    def aggregate(self, *args):
        return self.collection.aggregate(args).get('result', [])

    def next(self):
        try:
            self._index += 1
            return self[self._index]
        except:
            raise StopIteration

    def __getitem__(self, index):
        self.load()
        return self.model.init(super(Rowset, self).__getitem__(index))

    def __repr__(self):
        self.load()
        return super(Rowset, self).__repr__()


class Storage(dict):

    def __init__(self, model):
        self.model = model

    def get(self, key):
        return self[key]

    def load(self, condition = {}, key = '_id'):
        for item in self.model.objects.filter(condition):
            self[item[key]] = item
        return self


class ActiveRecord(DB, Rules):
    """ActiveRecord - database pattern"""

    _collection = 'test'
    _auto = {}

    _relation_regex = re.compile(r'^(?P<coll>[A-Za-z0-9_]+)(?P<dir>\<|\>)(?P<field>[A-Za-z0-9\._]+)$')

    @classproperty
    def objects(cls):
        return Rowset(cls.collection, cls)

    @classproperty
    def storage(cls):
        return Storage(cls)

    @classproperty
    def collection(cls):
        return cls._db[cls._collection]

    @classmethod
    def fetch(cls, _id):
        c = cls.find_first({'_id':_id})
        return c

    @classmethod
    def blank(cls):
        t = cls()
        return t

    @classmethod
    def init(cls, data):
        tmp = cls()
        tmp.update(data)
        return tmp

    @classmethod
    def find_first(cls, condition):
        condition.update(cls._auto)
        row = cls._db[cls._collection].find_one(condition)
        if row:
            return cls.init(row)

        return None

    @classmethod
    def connectby(cls, primary_key, parent_key, value_key):
        r = Rowset(cls.collection, cls)
        c = cls.collection.find_one({primary_key:value_key})
        while c != None:
            r.append(c)
            c = cls.collection.find_one({primary_key:c[parent_key]})
        r._loaded = True
        return r

    @classmethod
    def is_exists(cls, _id):
        _id = int(_id)
        return cls._db[cls._collection].find_one({'_id' : _id}) != None

    def __init__(self, **kwargs):
        super(ActiveRecord, self).__init__()
        self['_id'] = kwargs.get('_id')
        self.update(self._auto)
        self.update(kwargs)

    def lang(self, lang = 'en'):
        self._lang = lang

    def rel(self, rule, one = False, model = None):
        match = self._relation_regex.match(rule)
        if match:
            coll, dir, field = match.groups()
        else:
            if re.match(r'^[A-Za-z0-9\_]+$', rule):
                coll = rule
                if self.has_key('%s_id' % rule):
                    dir = '<'
                    field = '%s_id' % rule

                else:
                    dir = '>'
                    field = '%s_id' % self._collection
            else:
                raise ActiveRecordException('Wrong relation rule')

        if not model:
            model = ActiveRecordFactory(coll)

        if dir == '>':
            if one:
                return Rowset(self._db[coll], model).filter({field:self['_id']})[0]
            else:
                return Rowset(self._db[coll], model).filter({field:self['_id']})
        elif dir == '<':
            if '.' in field:
                field, subfield = field.split('.')
                selector = type(self[field]) == list and {'$in':[x[subfield] for x in self[field]]} or self[field][subfield]
            else:
                selector = type(self[field]) == list and {'$in':self[field]} or self[field]

            if one:
                rs = Rowset(self._db[coll], model).filter({'_id':selector})
                if rs.count():
                    return rs[0]
            else:
                return Rowset(self._db[coll], model).filter({'_id':selector})

    def save(self):
        if self['_id'] == None:
            self['_id'] = int(self._db.system_js.nextid(self.collection.name))
            Trigger.on_trigger(self, TGOP_INSERT, TGEV_BEFORE)
            self.collection.insert(self)
            Trigger.on_trigger(self, TGOP_INSERT, TGEV_AFTER)
        else:
            Trigger.on_trigger(self, TGOP_UPDATE, TGEV_BEFORE)
            self.collection.update({'_id' : self['_id']}, self, upsert=True)
            Trigger.on_trigger(self, TGOP_UPDATE, TGEV_AFTER)

    def load(self):
        self.update(self.collection.find_one({'_id': self['_id']}))

    def delete(self):
        Trigger.on_trigger(self, TGOP_DELETE, TGEV_BEFORE)
        self.collection.remove({'_id' : self['_id']})
        Trigger.on_trigger(self, TGOP_DELETE, TGEV_AFTER)





def ActiveRecordFactory(collection):
    try:
        return admin.get_class_for_name(collection)
    except:
        class ActiveRecordMeta(ActiveRecord):
            _collection = collection
        return ActiveRecordMeta


#class Film(ActiveRecord):
#    _collection = 'film'
#    _choza = 'qwerty'

#class Cinema(ActiveRecord):
#    _collection = 'cinema'

#class AdminUsers(ActiveRecord):
#    _collection = 'users'

# print AdminUsers.objects.all()
# print AdminUsers.objects.filter({'_id':{'$gt':1}})

#r = AdminUsers.find_first({'login':'admin'})
#if r:
#    print r
#else:
#    print 'not found'

#c = Cinema.fetch(2)

#if Film.is_exists('1'):
#    m = Film.fetch('1')
#else:
#    m = Film.blank()


# for f in Film.filter({'_id':{'$gt':1}}):
#     print type(f)

#f = Film.fetch(10)

#print c.rel('film')
# f.name = 'Alibek 2: Return'
# f.director = 'Eroha2'
# f.actors = ['Sirozha', 'Aza', 'Olzhik']
# f.save()

#for i, f in enumerate(Film.filter({'_id':{'$lt':10}})):
#    f.title = 'Santa-Barbara %d' % (i+1)
#    print f.save()


# for i, f in enumerate(c.rel('film')):
#     f.title = 'Sherlock %d' % (i+1)
#     print f.save()

# for i, cc in enumerate(f.rel('cinema<release.cinema')):
#     cc.title = 'CINEMA %d' % (i+1)
#     print cc
#     print cc.save()


# for f in c.rel('film'):

#     f.save()
#     print type(f)

#print ActiveRecord.collection

#print '----------------'
#print f.rel('cinema<release.cinema')

#class Cafe(ActiveRecord):
#    rules = {
#        'title':['xss_strip','integer', 'integer>10','length>5','maxlength>255','required','fk=cinema'],
#        'info': {
#
#        },
#        'email' :['unique=cafe[email]']
#    }

#print
#for x in ActiveRecordFactory('menu_category').connectby('_id', 'parent_id', 23):
#    print x['_id'], x['parent_id'], x['title']
#print
