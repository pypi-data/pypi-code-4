#!/usr/bin/env python

from pymongo import MongoClient
from pymongo.database import Database
from bson.dbref import DBRef
from bson.objectid import ObjectId
from datetime import datetime
import json
import inspect
from pymongo.son_manipulator import SONManipulator
from gridfs import GridFS
from copy import copy

#####################################################################
## Errors ###########################################################


class ValidationError(Exception):
    pass


class ReservedKeyError(Exception):
    pass


class FileDocumentError(Exception):
    pass

#####################################################################
## Class Register ###################################################

class_register = dict()


def register(cls):
    class_register[cls.__name__] = cls
    return cls


def register_as_list():
    return [v for k, v in class_register.items()]

#####################################################################
## Transform SON Manipulator ########################################


def encode_dbref(obj):
    return obj.dbref


def decode_dbref(obj):
    # temp fix to read old database
    if obj.collection == 'Programs':
        obj.classname = 'Program'
    if obj.collection == 'Episodes':
        obj.classname = 'Episode'
    if obj.collection == 'People':
        obj.classname = 'Person'
    if obj.collection == 'Contracts':
        obj.classname = 'Contract'
    if obj.collection == 'Organisations':
        obj.classname = 'Organisation'
    try:
        return class_register[obj.classname](**client()[obj.database].dereference(obj))
        #return class_register[obj.classname](**client()['haystack'].dereference(obj))
    except ValueError:
        raise
    except AttributeError:
        return None
    except TypeError:
        return None


def encode_file(fd):
    if isinstance(fd.File, file) or fd.File.__class__.__name__ == '_TemporaryFileWrapper':
        fd.save()
    return {'FileDocument': {'_id': fd.File_id, 'collection': fd.collection}}


def decode_file(fd):
    fd = fd['FileDocument']
    gfs = GridFS(database(), fd['collection'])
    return FileDocument(gfs.get(fd['_id']), File_id=fd['_id'])


class Transform(SONManipulator):
    def transform_incoming(self, son, collection):
        son_copy = copy(son)

        def transform_item(item):
            if isinstance(item, FileDocument):
                return encode_file(item)
            if item.__class__ in register_as_list():
                return encode_dbref(item)
            if isinstance(item, list):
                return [transform_item(i) for i in item]
            if isinstance(item, dict):
                return self.transform_incoming(item, collection)
            else:
                return item

        for k, v in son_copy.items():
            son_copy[k] = transform_item(v)
        return son_copy

    def will_copy(self):
        return True

    def transform_outgoing(self, son, collection):
        def transform_item(item):
            if isinstance(item, FileDocument):
                return decode_file(item)
            if isinstance(item, DBRef):
                return decode_dbref(item)
            if isinstance(item, list):
                return [transform_item(i) for i in item]
            if isinstance(item, dict):
                if 'FileDocument' in v:
                    return decode_file(v)
                else:
                    return self.transform_outgoing(item, collection)
            else:
                return item

        for k, v in son.items():
            son[k] = transform_item(v)
        return son

#####################################################################
## Global vars ######################################################


def connect(*args, **kwargs):
    global __client
    __client = MongoClient(*args, **kwargs)
    make_database()
    return __client


def client():
    global __client
    return __client


def make_database(name='tests'):
    global __database
    __database = Database(client(), name)
    __database.add_son_manipulator(Transform())
    return __database


def database():
    global __database
    return __database


#####################################################################
## Field ############################################################


class Field(object):
    def __init__(
            self,
            required=False,
            default=None,
            test=None,
            maximum=None,
            minimum=None,
            unique=False,
            auto_inc=0):
        self.required = required
        self.default = default
        self.test = test
        self.maximum = maximum
        self.minimum = minimum
        self.unique = unique
        self.auto_inc = auto_inc

    def validate(self, value):
        """
        Validates the value of a field based on the test.  Returns either the value
        or a ValidationError.
        """
        # if required but no value, raise error
        if self.required and not value:
            raise ValidationError('%s - %s is a required field' % (self, value))

        # if no value and not required, no problem
        if not self.required and not value:
            return value

        if not self.test and not self.maximum and not self.minimum:
            return value

        # strip white space from strings
        if self.test in [unicode, str]:
            try:
                value = value.strip()
            except AttributeError:
                pass

        # test maximum for strings
        if self.maximum and isinstance(value, (str, unicode)) and self.maximum < len(value):
            raise ValidationError('"%s" is greater than %s' % (value, self.maximum))

        # test minimum for strings
        if self.minimum and isinstance(value, (str, unicode)) and self.minimum > len(value):
            raise ValidationError('"%s" is less than %s' % (value, self.minimum))

        # test maximum for numbers
        if self.maximum and isinstance(value, (long, int, float)) and self.maximum < value:
            raise ValidationError('"%s" is greater than %s' % (value, self.maximum))

        # test minimum for numbers
        if self.minimum and isinstance(value, (long, int, float)) and self.minimum > value:
            raise ValidationError('"%s" is greater than %s' % (value, self.minimum))

        # test registered types
        if self.test in register_as_list() and not isinstance(value, self.test):
            raise ValidationError('"%s" is not a %s' % (value, self.test))

        # test types by trying to coerce the value into the test type
        if self.test.__class__ is type or isinstance(self.test, tuple):
            try:
                self.test(value)
            except TypeError:
                pass
            except ValueError:
                raise ValidationError('"%s" cannot be made into a %s' % (value, self.test))

        return value

#####################################################################
## Document #########################################################


class Document(object):
    database = None
    collection = None
    structure = {}
    created = None
    pre_save = None
    post_save = None

    #set_denorm = None
    #denorm = {}
    #_keep_versions = False
    #_keep_version_log = False
    #_referenced = []

    def __init__(self, **kwargs):
        self.database = database() or None
        self.collection = self.database[self.collection or u'%s_collection' % self.__class__.__name__]
        self.pre_save = self.pre_save
        self.version_collection = u'%s_history' % self.collection.name
        self.version_log = []
        self.removed = False
        self.save_data = {}
        self.omitted = [
            'collection',
            'count',
            'database',
            'dbref',
            'dict',
            'find',
            'find_one',
            'json',
            'keys',
            'omitted',
            'post_save',
            'pre_save',
            'remove',
            'render',
            'save',
            'static',
            'structure'
        ]
        for key, field in self.structure.items():
            if key in self.omitted:
                raise ReservedKeyError('%s is a reserved key. Use something else' % key)
            setattr(self, key, field.default)
            if isinstance(field.test, list):
                setattr(self, key, [])
        self.__dict__.update(
            {k: v for k, v in kwargs.items() if k == '_id' or not k.startswith('_') and not k in self.omitted})

    def __eq__(self, other):
        return self._id == other._id

    def __ne__(self, other):
        return self.__dict__ != other.__dict__

    def prep_save(self, data=None):
        data = data or self.save_data
        new_data = {}
        try:
            new_data['_id'] = data.get('_id', getattr(self, '_id'))
        except AttributeError:
            pass
        for key, field in self.structure.items():
            try:
                new_data[key] = field.validate(data.get(key, getattr(self, key)))
            except ValidationError:
                raise
            if field.auto_inc and not new_data[key]:
                new_data[key] = self.database['%s_counters' % self.collection.name].find_and_modify({'_id': key}, {
                    '$inc': {'seq': field.auto_inc}}, new=True, upsert=True)['seq']
                self.__setattr__(key, new_data[key])
            if field.unique:
                try:
                    exists = self.find({key: new_data[key], '$not': {'_id': self._id}})
                except AttributeError:
                    exists = self.find({key: new_data[key]})
                if exists:
                    raise ValidationError(
                        '"%s, %s is not unique' % (key, new_data[key]))
        new_data['created'] = self.created or datetime.utcnow()
        return new_data

    def save(self, data=None):
        data = data or self.save_data
        if not self.removed:
            if self.pre_save:
                self.pre_save()
            valid_data = self.prep_save(data)
            valid_data['modified'] = datetime.utcnow()
            self.created = valid_data['created']
            self.modified = valid_data['modified']
            self._id = self.collection.save(valid_data)
            if self.post_save:
                self.post_save()
            return self

    def find_and_modify(self, query=None, data=None, upsert=True):
        query = query or {'_id': self._id}
        data = self.prep_save(data or self.save_data or self.dict)
        try:
            del data['_id']
        except KeyError:
            pass
        try:
            self.__dict__.update(self.collection.find_and_modify(
                query=query,
                update={'$set': data},
                new=True,
                upsert=upsert
            ))
        except:
            raise

    def find(self, query=None, ref_query=None, history=False, count=False, limit=0, sort=('_id', 1)):
        ref_objects = []
        if ref_query:
            for k, v in ref_query.items():
                k1, k2 = k.split('.')
            ref = getattr(self, k1)
            if ref:
                ref_objects.extend([o for o in ref.collection.find({k2: v})])
                if ref_objects:
                    query['$or'] = [
                        {k1: DBRef(ref.collection.name, r['_id'], ref.database, classname=ref.__class__.__name__)}
                        for r in ref_objects]
            else:
                return None
        collection = self.collection
        if history:
            collection = self.version_collection
        cursor = collection.find(query).limit(limit).sort(sort[0], sort[1])
        if count:
            return cursor.count()
        try:
            return [class_register[self.__class__.__name__](**i) for i in cursor]
        except:
            raise
            #return []

    def find_one(self, query={}, ref_query={}, history=False):
        ref_objects = []
        if ref_query:
            for k, v in ref_query.items():
                k1, k2 = k.split('.')
            ref = getattr(self, k1)
            if ref:
                ref_objects.extend([o for o in ref.collection.find({k2: v})])
                if ref_objects:
                    query['$or'] = [{k1: DBRef(ref.collection.name, r['_id'],
                                               ref.database.name, classname=ref.__class__.__name__)}
                                    for r in ref_objects]
            else:
                return None
        collection = self.collection
        if history:
            collection = self.version_collection
        found = collection.find_one(query)
        if found:
            return class_register[self.__class__.__name__](**found)

    def count(self, query=None, ref_query=None, history=False):
        return self.find(query, ref_query, count=True, history=history)

    def remove(self):
        try:
            self.collection.remove({'_id': self._id})
            del self._id
            self.removed = True
        except:
            raise

    """
    @property
    def created(self):
        try:
            return self._id.generation_time
        except AttributeError:
            return self.created
    """

    @property
    def dbref(self):
        try:
            return DBRef(
                database=self.database.name,
                collection=self.collection.name,
                id=self._id,
                classname=self.__class__.__name__)
        except AttributeError:
            return None

    @property
    def dict(self):

        d = {}
        try:
            d['_id'] = self._id
        except AttributeError:
            pass
        for i in dir(self):
            if not i in self.omitted and not i.startswith('_'):
                try:
                    a = getattr(self, i)
                    if not inspect.ismethod(a):
                        if isinstance(a, list):
                            try:
                                a = [o.database.dereference(o.dbref) for o in a]
                            except AttributeError:
                                pass
                        if isinstance(a, dict):
                            for k, v in a.items():
                                try:
                                    a[k] = v.database.dereference(v.dbref)
                                except AttributeError:
                                    pass
                        if a.__class__ in register_as_list():
                            d[i] = a.database.dereference(a.dbref)
                        else:
                            d[i] = a
                except TypeError:
                    continue
        return d

    # _static returns a dict for only those keys which are stored in db
    @property
    def static(self):
        return {k: getattr(self, k) for k in self.structure}

    @property
    def json(self):
        class ComplexEncoder(json.JSONEncoder):
            def default(self, obj):
                if isinstance(obj, datetime):
                    return obj.isoformat()
                if isinstance(obj, ObjectId):
                    return str(obj)
                if isinstance(obj, DBRef):
                    return None
                if obj.__class__ in register_as_list():
                    return None
                return json.JSONEncoder.default(self, obj)

        return json.dumps(self.static, cls=ComplexEncoder, encoding='utf-8')

    # needed to convert the json string to objects angularjs can understand
    @property
    def render(self):
        return json.loads(self.json)

    @property
    def keys(self):
        return [k for k, v in self.dict.items()]


#####################################################################
## FileDocument #####################################################


class FileDocument(file):
    """Contains either a Python file or a GridFS GridOut object which can
    be saved to the database using GridFS"""
    _collection = u'Files'

    def __init__(self, File, File_id=None, **kwargs):
        self._client = client() or None
        self._database = database() or None
        self.File = File
        self.Filename = File.name
        self.File_id = File_id
        self.__dict__.update(kwargs)

    def _save(self):
        gfs = GridFS(self._database, self._collection)
        if gfs.exists(self.File_id):
            gfs.delete(self.File_id)
        if self.File_id:
            try:
                gfs.put(
                    self.File,
                    _id=self.File_id,
                    filename=self.Filename,
                    uploadedby=self.UploadedBy)
            except:
                raise
        else:
            try:
                self.File_id = gfs.put(
                    self.File,
                    filename=self.Filename)
            except:
                raise

    def __repr__(self):
        return "<FileDocument '%s'>" % self.Filename
