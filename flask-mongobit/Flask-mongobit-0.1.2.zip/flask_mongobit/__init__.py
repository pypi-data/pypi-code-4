#!/usr/bin/env python
#-*- coding: utf-8 -*-

'''
    flaskext.mongobit
    ~~~~~~~~~~~~~~~~~

    MongoBit support in Flask.

    :copyright: (c) 2012 by Lix Xu.
    :license: BSD, see LICENSE for more details.

'''

import mongobit
from mongobit import Model, fields


class MongoBit(object):
    def __init__(self, app=None):
        if app is not None:
            self.init_app(app)

    def init_app(self, app):
        app.config['alias'] = app.name
        self.app = app
        self.mongo = mongobit.MongoBit(app.config)

        class _Model(Model):
            _db_alias = app.name

        self.model = _Model

        self.str = fields.str
        self.string = fields.string
        self.unicode = fields.unicode
        self.text = fields.text
        self.list = fields.list
        self.dict = fields.dict
        self.tuple = fields.tuple
        self.int = fields.int
        self.float = fields.float
        self.date = fields.date
        self.datetime = fields.datetime
        self.objectid = fields.objectid
        self.bool = fields.bool
        self.any = fields.any

    @property
    def connection(self):
        return self.mongo.connection

    @property
    def database(self):
        return self.mongo.database

    def close(self):
        self.connection.disconnect()
