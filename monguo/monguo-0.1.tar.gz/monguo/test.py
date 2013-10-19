# -*- coding: utf-8 -*-

import motor
import sys

from bson.objectid import ObjectId
from bson.dbref import DBRef
from tornado import gen
from tornado.concurrent import Future, TracebackFuture
from tornado.ioloop import IOLoop, TimeoutError

from document import Document, EmbeddedDocument
from connection import Connection
from field import *
from manipulator import MonguoSONManipulator
from pymongo.son_manipulator import SONManipulator


class BookDocument(EmbeddedDocument):
    name  = StringField(required=True)
    pages = IntegerField(required=True)


class SkillDocument(EmbeddedDocument):
    name = StringField(required=True)


class PetDocument(Document):
    name = StringField(required=True)
    say  = StringField()

    meta = {
        'collection': 'pet'
    }


class UserDocument(Document):
    name   = StringField(required=True, unique=True)
    sex    = StringField(required=True, default='male')
    age    = IntegerField(required=True)
    skills = ListField(DictField(SkillDocument), required=True)
    book   = EmbeddedDocumentField(BookDocument, required=True)
    pet = ReferenceField(PetDocument)

    meta = {
        'collection': 'user'
    }

    def insert_user():
        user = {
            'name': 'Lime',
            'age': 100,
            'skills': [{'name': 'python'}, {'name': 'Web Programming'}],
            'book': {'name': 'I am a bad guy', 'pages': '888'},
        }
        user_id = yield UserDocument.save(user)
        raise gen.Return(user_id)


@gen.coroutine
def test():
    Connection.connect('test')

    yield PetDocument.remove()
    yield UserDocument.remove()

    pet_id = yield PetDocument.insert({'name': 'dog'})
    pet = yield PetDocument.find_one({'_id': ObjectId(pet_id)})
    print pet

    user_id = yield UserDocument.insert_user()
    user = yield UserDocument.find_one({'name': 'Lime'})
    print user

    dbref = DBRef(PetDocument.meta['collection'], ObjectId(pet_id))
    yield UserDocument.update({'name': 'Lime'}, {'$set': {'pet': dbref}})
    user = yield UserDocument.find_one({'name': 'Lime'})
    print user

IOLoop.instance().run_sync(test)

   
