# -*- coding: utf-8 -*-

'''An asynchronous session backend with mongodb for tornado'''

import cPickle
import base64
import motor

from uuid import uuid1
from tornado import gen
from datetime import datetime, timedelta
from tornado.web import HTTPError

VERSION = (0, 1, 1)

def get_version():
    if isinstance(VERSION[-1], basestring):
        return '.'.join(map(str, VERSION[:-1])) + VERSION[-1]
    
    return '.'.join(map(str, VERSION))

__version__ = get_version()


class Session(object):

    LIFE_LENGTH = timedelta(days=3)
    REGENERATION_INTERVAL = timedelta(minutes=3)

    def __init__(self, collection):
        self.session_collection = collection
        self.life_length = Session.LIFE_LENGTH
        self.regeneration_interval = Session.REGENERATION_INTERVAL

    @gen.coroutine
    def get(self, key):
        '''Get a value'''

        value = None
        session = yield self.session_collection.find_one(
            {'session_id': self.session_id})
        if session and key in session:
            value = cPickle.loads(str(session[key]))
        raise gen.Return(value)

    @gen.coroutine
    def set(self, key, value):
        '''Set a value'''

        result = yield self.session_collection.update(
            {'session_id': self.session_id},
            {'$set': {key: cPickle.dumps(value)}})
        raise gen.Return(value)

    @gen.coroutine
    def delete(self, key, value):
        '''Delete a key'''

        result = yield self.session_collection.update(
            {'session_id': self.session_id},
            {'$unset': {key: ''}})
        raise gen.Return(result)

    def generate_session_id(self):
        '''Generate a session id'''

        return base64.b64encode(str(uuid1()))

    @gen.coroutine
    def generate_session(self):
        '''Generate session after login'''

        now = datetime.now()
        document = {}
        document['session_id'] = self.session_id
        document['expired_time'] = cPickle.dumps(now + self.life_length)
        document['next_regeneration_time'] = cPickle.dumps(
            now + self.regeneration_interval)
        result = yield self.session_collection.insert(document)
        raise gen.Return(result)

    @gen.coroutine
    def delete_session(self):
        '''Clear session when logout'''

        result = yield self.session_collection.remove(
            {'session_id': self.session_id})
        self.session_id = None

        raise gen.Return(result)

    @gen.coroutine
    def refresh_session(self):
        '''Refresh session every other `regeneration_interval`'''

        refresh_session_id = self.generate_session_id()
        result = yield self.session_collection.update(
            {'session_id': self.session_id},
            {'$set': {'session_id': refresh_session_id}})
        self.session_id = refresh_session

        raise gen.Return(result)

    @property
    def session_id(self):
        '''Get session id'''

        if not hasattr(self, '_session_id') or self._session_id is None:
            self._session_id = self.generate_session_id()
        return self._session_id

    @session_id.setter
    def session_id(self, value):
        '''Set session id'''

        self._session_id = value

    def set_life_length(self, value):
        '''Set `life_length`, default is `Session.LIFE_LENGTH`'''

        assert isinstance(value, timedelta)
        self.life_length = value

    def set_regeneration_interval(self, value):
        '''
        Set `regeneration_interval`, default is 
        `Session.REGENERATION_INTERVAL`
        '''

        assert isinstance(value, timedelta)
        self.regeneration_interval = value

