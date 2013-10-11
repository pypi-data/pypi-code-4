import unittest
import pytest
from docmongo.fields import StringField, IntField
from docmongo.document import Document


class Test_User(unittest.TestCase):
    dbname = "test1"
    colname = "user"

    def setUp(self):
        from pymongo import MongoClient
        db = MongoClient()
        self.db = db[self.dbname][self.colname]
        if self.db:
            self.db.drop()

    def tearDown(self):
        if self.db:
            self.db.drop()

    def test_user(self):
        class Base(Document):
            _host = "localhost:27017"
            _dbname = "test1"

        class User(Base):
            fields = {
                "name": StringField,
                "age": IntField
            }
            _get_key = "name"

        user = User.get_or_new("sato")
        user.age = 100
        assert user.age == 100
        user.save()

        get_user = self.db.find_one({"name": "sato"})
        assert get_user
        assert get_user["name"] == "sato"
        assert get_user["age"] == 100

        obj_user = User(get_user)

        assert obj_user
        assert obj_user.name == "sato"
        assert obj_user.age == 100

        with pytest.raises(TypeError):
            obj_user.age = "100"

        with pytest.raises(TypeError):
            obj_user.name = 100
