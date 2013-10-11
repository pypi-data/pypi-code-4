import unittest
import pytest
from docmongo.fields import (
    StringField,
    DateField,
    ListField,
    IntField
    )
from docmongo.document import Document


class Base(unittest.TestCase):
    def tearDown(self):
        from pymongo import MongoClient
        db = MongoClient('localhost:27017')['hogehogehoge']
        db.drop_collection('test')


class Test_connection_db(Base):
    def _callFUC(self):
        class DummyDB(Document):
            _host = "localhost:27017"
            _dbname = "hogehogehoge"
            _colname = "test"
            fields = {}
        return DummyDB().db()

    def test_db(self):
        db = self._callFUC()
        assert db.name == "test"


class Test_basis(Base):
    def test_colname(self):
        from docmongo.document import Document
        class Abc(Document):
            pass
        assert Abc.colname() == "abc"

        class aBC1(Document):
            pass
        assert aBC1.colname() == "aBC1"


class Test_find(Base):
    dbname = "hogehogehoge"
    colname = "test"

    def setUp(self):
        from pymongo import MongoClient
        db = MongoClient()
        self.db = db[self.dbname][self.colname]

    def _makeOne(self):
        class DummyDB(Document):
            _host = "localhost:27017"
            _dbname = self.dbname
            _colname = self.colname
            fields = {}
        return DummyDB()

    def test_get(self):
        obj = self._makeOne()

        self.db.insert({"_id": "test"})
        self.db.insert({"_id": "test2"})

        entity = obj.get("test")
        assert entity
        assert entity._id == "test"
        assert entity._id == entity.key()

        entity = obj.get("test10")
        assert entity is None

    def test_items(self):
        obj = self._makeOne()

        self.db.insert({"_id": "test"})
        self.db.insert({"_id": "test2"})

        entities = obj.items()
        assert entities.count() == 2
        assert entities[0]["_id"] == "test"

    def test_get_or_new(self):
        obj = self._makeOne()
        entity = obj.get_or_new("testtest")

        assert entity
        assert self.db.find_one("testtest")

    def test_all(self):
        obj = self._makeOne()
        assert obj.all().count() == 0

        self.db.insert({"_id": "test"})
        self.db.insert({"_id": "test2"})

        data = obj.all()
        assert data.count() == 2
        assert data[0]['_id'] in ['test', 'test2']
        assert data[1]['_id'] in ['test', 'test2']


class Test_instance(Base):
    def _makeOne(self):
        class DummyDB(Document):
            _host = "localhost:27017"
            _dbname = "hogehogehoge"
            _colname = "test"
            fields = {
                "name": StringField(),
                "comment": StringField("i love you")
            }
        return DummyDB()

    def test_init(self):
        obj = self._makeOne()
        assert obj.name is None
        assert obj.comment == "i love you"

        with pytest.raises(AttributeError):
            obj.name11

    def test_setattr(self):
        obj = self._makeOne()

        obj.name = "testtest"
        assert obj.name == "testtest"

        l = len(obj.__dict__)
        obj.name1 = "tesettest"
        assert l < len(obj.__dict__)


class Test_save_insert(Base):
    def _getTargetClass(self):
        class DummyDB(Document):
            _host = "localhost:27017"
            _dbname = "hogehogehoge"
            _colname = "test"
            fields = {
                "name": StringField(),
                "comment": StringField("i love you"),
                "dream": StringField,
                "datetime": DateField,
            }
            _get_key = "name"
        return DummyDB

    def test_save(self):
        from datetime import datetime
        target = self._getTargetClass()

        obj = target.get_or_new("gagagag")
        obj.name = "st"
        obj.save()

        entity = target.db().find_one({"name": "st"})
        assert entity
        assert entity["name"] == "st"
        assert entity["comment"] == "i love you"
        assert entity["dream"] is ""
        assert isinstance(entity["datetime"], datetime)
        assert "hohoge" not in entity

        obj = target.get_or_new("gagagaggag")
        obj.name = "stst"
        obj.save(safe=False)

        entity = target.db().find_one({"name": "stst"})
        assert entity
        assert entity["name"] == "stst"
        assert entity["comment"] == "i love you"
        assert entity["dream"] is ""
        assert isinstance(entity["datetime"], datetime)
        assert "hohoge" not in entity


    def test_is_primary(self):
        from docmongo.exceptions import NotPrimaryError
        target = self._getTargetClass()
        obj = target.get_or_new("sato")
        obj.save()
        obj.save()
        obj.save()

        obj1 = target.get_or_new("sato")
        obj1.save()

        obj1._id = "hogehoge"

        with pytest.raises(NotPrimaryError):
            obj1.save()

    def test_insert(self):
        from docmongo.exceptions import FieldTypeError

        target = self._getTargetClass()
        d = {
            "name": "test"
        }
        a = target.db().find_one({'name': 'test'})
        assert a is None

        obj = target.insert(d)
        assert obj.name == 'test'
        assert obj._id

        a = target.db().find_one({'name': 'test'})
        assert a
        assert a['name'] == 'test'

        d.update({'hogehoge': 100})

        with pytest.raises(FieldTypeError):
            target.insert(d)

    def test_insert_remove(self):
        target = self._getTargetClass()
        d = {
            "name": "test"
        }
        entity = target.db().find_one({'name': 'test'})
        assert entity is None

        obj = target.insert(d)

        entity = target.db().find_one({'name': 'test'})
        assert entity
        assert entity['name'] == 'test'

        target.remove(obj)

        entity = target.db().find_one({'name': 'test'})
        assert entity is None

    def test_update(self):
        from docmongo.exceptions import InvalidArgumentError

        target = self._getTargetClass()
        d = {
            'name': 'test',
            "dream": "coder",
            '_id': 'testtest',
        }

        target.db().insert(d, safe=True)
        c = target.db().find_one({'_id': 'testtest'})

        assert c['name'] == 'test'
        assert c['dream'] == 'coder'

        d.update({'name': 'hoge'})
        target.update(d)

        c = target.db().find_one({'_id': 'testtest'})
        assert c['name'] == 'hoge'
        assert c['dream'] == 'coder'

        with pytest.raises(InvalidArgumentError):
            d = {'name': 'hoge'}
            target.update(d)


class Test_Operator(Base):
    def _makeOne(self):
        class DummyDB(Document):
            _host = "localhost:27017"
            _dbname = "hogehogehoge"
            _colname = "test"
            fields = {
                "name": StringField(),
                "comment": StringField("i love you"),
                "dream": StringField,
                "integer": IntField,
            }
            _get_key = "name"
        return DummyDB

    def test_assign_dict(self):
        target = self._makeOne()

        obj = target.get_or_new("sato")
        assign = {
            "name": "hogehoge",
            "comment": "i dont love you",
            "dream": "i have big dream!!",
            "hdummy": 100
        }

        assert obj.name != assign["name"]
        assert obj.comment != assign["comment"]
        assert obj.dream != assign["dream"]

        obj.assign_dict(assign)

        assert obj.name == assign["name"]
        assert obj.comment == assign["comment"]
        assert obj.dream == assign["dream"]

    def test_inc(self):
        target = self._makeOne()
        target.db().save({'name': "hogehoge", 'integer': 100})

        assert target.db().find_one({'name': 'hogehoge'})['integer'] == 100

        obj = target.get_or_new('hogehoge')

        assert obj.integer == 100

        obj.inc('integer', 101)
        assert obj.integer == 201
        assert target.db().find_one({'name': 'hogehoge'})['integer'] == 201

        obj.inc('integer', -150, safe=False)
        assert target.db().find_one({'name': 'hogehoge'})['integer'] == 51


class Test_init(Base):
    def _makeOne(self):
        class DummyDB(Document):
            _host = "localhost:27017"
            _dbname = "hogehogehoge"
            _colname = "test"
            fields = {
                "name": StringField(),
                "comment": StringField("i love you"),
                "list": ListField,
            }
        return DummyDB()

    def test_init(self):
        obj = self._makeOne()
        assert obj.list == []
        assert len(obj.list) == 0
        obj.list.append(1)
        assert obj.list[0] == 1


class TestCreatedAt(Base):
    def _makeOne(self):
        class DummyDB(Document):
            _host = "localhost:27017"
            _dbname = "hogehogehoge"
            _colname = "test"
            fields = {
                "name": StringField(),
            }
            _created_at = True
        return DummyDB()

    def test_have_created_at(self):
        obj = self._makeOne()
        datas = obj.all()
        assert datas.count() == 0

        obj.insert({"name": "Ken"})
        datas = obj.all()

        assert datas.count() == 1

        data = datas[0]
        assert 'created_at' in data

    def test_continuance_save(self):
        obj = self._makeOne()
        datas = obj.all()
        assert datas.count() == 0

        obj.insert({"name": "Ken"})
        datas = obj.all()

        assert datas.count() == 1
        data = obj.get(datas[0]['_id'])
        data.save()


class TestUpdateAt(Base):
    def _makeOne(self):
        class DummyDB(Document):
            _host = "localhost:27017"
            _dbname = "hogehogehoge"
            _colname = "test"
            fields = {
                "name": StringField(),
            }
            _get_key = "name"
            _updated_at = True
        return DummyDB()

    def test_have_update_at(self):
        obj = self._makeOne()
        datas = obj.all()
        assert datas.count() == 0

        obj.insert({"name": "Ken"})
        datas = obj.all()

        assert datas.count() == 1

        data = datas[0]
        assert 'updated_at' in data
        updated_at = data['updated_at']

        obj.insert({'name': 'Tom'})
        tom = obj.get('Tom')
        assert tom
        assert tom.updated_at > updated_at
        updated_at = tom.updated_at
        tom.save()

        assert tom.updated_at > updated_at


class TestToDict(Base):
    def _makeOne(self):
        class DummyDB(Document):
            _host = "localhost:27017"
            _dbname = "hogehogehoge"
            _colname = "test"
            fields = {
                "name": StringField(),
                "money": IntField(),
            }
            created_at = True
        return DummyDB()

    def test_to_dict(self):
        obj = self._makeOne()
        obj.name = 'dummy'
        obj.money = 100
        dic = obj.to_dict()
        assert dic['name'] == 'dummy'
        assert dic['money'] == 100
        assert '_id' in dic
