# -*- coding: utf-8 -*-
"""
    flask_kale
    ~~~~~~~~~~

    Makes it easy to hook kale up to mongodb in Flask.

    :copyright: uniphil 2013
    :license: dwtfyw with optional coffee stipulation (one large dark black)
"""


import kale


def _not_a_dbgetter():
    raise NotImplementedError('no dbgetter function registered')


def _make_model(flask_kale):

    class Model(kale.Model):
        @kale.classproperty
        @classmethod
        def _database(cls):
            return flask_kale.db_getter_func()

    return Model


class Kale(object):

    def __init__(self, app=None):
        self.db_getter_func = _not_a_dbgetter
        self.Model = _make_model(self)
        if app is not None:
            self.init_app(app)

    def init_app(self, app):
        pass

    def dbgetter(self, fn):
        self.db_getter_func = fn
        return fn
