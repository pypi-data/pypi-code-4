##############################################################################
#
# Copyright (c) 2007 Lovely Systems and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
"""
$Id: memcache.py 77359 2007-07-03 15:54:09Z dobe $
"""
__docformat__ = "reStructuredText"

from datetime import datetime
from datetime import timedelta

import zope.component

from p01.memcache import interfaces
from p01.memcache import client
from p01.memcache import uclient

# shared fake memcache data storage, one per memcache client with different
# servers
storage = {}
expires = {}

def getData(servers):
    return storage.setdefault(''.join(servers), {})

def getExpires(servers):
    return expires.setdefault(''.join(servers), {})

_marker = object()


class FakeMemcached(object):
    """Fake memcached server which makes sure to separate data."""

    def __init__(self, servers=['127.0.0.1:11211'], debug=0, pickleProtocol=0,
        socket_timeout=4):
        self.servers = servers
        self.debug = debug
        self.pickleProtocol = pickleProtocol
        self.resetCounts()

    @property
    def cache(self):
        return getData(self.servers)

    @property
    def expires(self):
        return getExpires(self.servers)

    def connect(self):
        return 1

    def getStats(self):
        return []

    def set(self, key, data, lifetime=0, flags=0):
        # raise an error if not a string
        str(key)
        str(data)
        if lifetime:
            expires = datetime.now()+timedelta(seconds=lifetime)
        else:
            expires = None
        self.cache[key] = (data, flags)
        self.expires[key] = expires
        self._sets += 1
        return True

    def get(self, key):
        str(key)
        data = self.cache.get(key, _marker)
        self._gets += 1
        if data is _marker:
            self._misses += 1
            return None

        expires = self.expires.get(key, _marker)
        if expires is _marker or datetime.now() < expires:
            self._hits += 1
            # python-memcache client returns single data
            return data[0]

        del self.cache[key]
        del self.expires[key]
        self._misses += 1
        return None

    def delete(self, key):
        if key in self.cache:
            del self.cache[key]
            del self.expires[key]

    def flush_all(self):
        global storage
        global expires
        storage[''.join(self.servers)] = {}
        expires[''.join(self.servers)] = {}

    def get_stats(self):
        return "Testing Stats"

    @property
    def gets(self):
        return self._gets

    @property
    def hits(self):
        return self._hits

    @property
    def misses(self):
        return self._misses

    @property
    def sets(self):
        return self._sets

    def resetCounts(self):
        self._hits = 0
        self._misses = 0
        self._gets = 0
        self._sets = 0


class FakeUltraMemcached(FakeMemcached):
    """Fake umemcache backend providing some different method signatures"""

    def get(self, key):
        str(key)
        data = self.cache.get(key, _marker)
        self._gets += 1
        if data is _marker:
            self._misses += 1
            return None

        expires = self.expires.get(key, _marker)
        if expires is _marker or datetime.now() < expires:
            self._hits += 1
            # ultramemcache library returns data, flag tuple
            return data

        del self.cache[key]
        del self.expires[key]
        self._misses += 1
        return None

    def set(self, key, data, expiration=0, flags=0, async=False):
        # raise an error if not a string
        str(key)
        str(data)
        if expiration:
            expires = datetime.now()+timedelta(seconds=expiration)
        else:
            expires = None
        self.cache[key] = (data, flags)
        self.expires[key] = expires
        self._sets += 1
        return True

    def delete(self, key, expiration=0, async=False):
        if key in self.cache:
            del self.cache[key]
            del self.expires[key]

    def flush_all(self, expiration=0, async=False):
        global storage
        global expires
        storage[''.join(self.servers)] = {}
        expires[''.join(self.servers)] = {}

    def stats(self):
        return "Testing Stats"


class FakeMemcacheClient(client.MemcacheClient):
    """A memcache client which doesn't need a running memcache daemon.
    
    This fake client also shares the data accross threads.
    
    This fake MemcacheClient can be used if you need to setup an utility in 
    a test.
    """

    _memcacheClientFactory = FakeMemcached
    _connector = None
    _client = None

    def __init__(self, servers=['127.0.0.1:11211'], debug=0, pickleProtocol=-1,
        lifetime=3600, namespace=None, timeout=4):
        super(FakeMemcacheClient, self).__init__(servers, debug,
            pickleProtocol, lifetime, namespace, timeout=timeout)
        # setup connector and client as singleton
        self._connector = self._getConnector()
        self._client = self._connector._client

    def _getConnector(self):
        if self._connector is None:
            self._connector = super(FakeMemcacheClient, self)._getConnector()
        return self._connector

    @property
    def backend(self):
        return self._connector._client

    @property
    def gets(self):
        return self.backend.gets

    @property
    def hits(self):
        return self.backend.hits

    @property
    def misses(self):
        return self.backend.misses

    @property
    def sets(self):
        return self.backend.sets

    def resetCounts(self):
        self.backend.resetCounts()


class FakeUltraMemcacheClient(FakeMemcacheClient):
    """A memcache client which doesn't need a running memcache daemon.
    
    This fake client also shares the data accross threads.
    
    This fake MemcacheClient can be used if you need to setup an utility in 
    a test.
    """

    _memcacheClientFactory = FakeUltraMemcached


def getFakeBackend(client):
    connector = client._getConnector()
    return connector._client


class Pickable(object):
    """Pickable sample object used for testing"""

    title = u'Title'


_orgMemcacheClientFactory = None

def setUpFakeMemcached(test=None):
    """Patch all existing IMemcachClient utilities.
    
    This method can be used for patch all existing memcache clients at class
    level.
    """
    global _orgMemcacheClientFactory
    global storage
    global expires
    storage = {}
    expires = {}
    _orgMemcacheClientFactory = client.MemcacheClient._memcacheClientFactory
    client.MemcacheClient._memcacheClientFactory = FakeMemcached
    # setup fake client
    fClient = FakeMemcacheClient()
    zope.component.provideUtility(fClient, interfaces.IMemcacheClient, name='')
    fClient.invalidateAll()


def tearDownFakeMemcached(test=None):
    if _orgMemcacheClientFactory is not None:
        client.MemcacheClient._memcacheClientFactory = _orgMemcacheClientFactory
    global storage
    global expires
    storage = {}
    expires = {}


_orgUltraMemcacheClientFactory = None

def setUpFakeUltraMemcached(test=None):
    """Patch UltraMemcacheClient factory.
    
    This method can be used for patch all existing memcache clients at class
    level.
    """
    global _orgUltraMemcacheClientFactory
    global storage
    global expires
    storage = {}
    expires = {}
    _orgUltraMemcacheClientFactory = uclient.UltraMemcacheClient._memcacheClientFactory
    uclient.UltraMemcacheClient._memcacheClientFactory = FakeUltraMemcached
    # setup fake client
    fClient = FakeUltraMemcacheClient()
    zope.component.provideUtility(fClient, interfaces.IMemcacheClient, name='')
    fClient.invalidateAll()


def tearDownFakeUltraMemcached(test=None):
    if _orgUltraMemcacheClientFactory is not None:
        uclient.UltraMemcacheClient._memcacheClientFactory = _orgUltraMemcacheClientFactory
    global storage
    global expires
    storage = {}
    expires = {}
