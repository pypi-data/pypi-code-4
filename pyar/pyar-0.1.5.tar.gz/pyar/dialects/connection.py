#-*- coding: utf-8 -*-

__author__ = 'Jefurry <jefurry@qq.com>'

import logging

PLACEHOLDER = '%s'

class ConnectPool(object):
    _pools = {}

    @classmethod
    def getPool(cls, using):
        return cls._pools.get(using, None)

    @classmethod
    def putPool(cls, using, pool):
        cls._pools.setdefault(using, pool)

class Database(object):

    placeholder = '%s'

    def __init__(self, **kwargs):
        pass

    def getconn(self):
        '''It should return a connection.'''
        raise NotImplementedError('This method should return a connection.')

    def putconn(self, conn):
        '''It should accept a connection.'''
        raise NotImplementedError('This method should accept a connection.')

    def getcur(self, conn):
        '''It lets you customize your cursor. By default, it return a cursor by the following code:

            ::
            return conn.cursor()

            .. versionadded :: 0.4
        '''
        return conn.cursor()

    def prepare(self, sql):
        raise NotImplementedError('This method should return a connection.')
