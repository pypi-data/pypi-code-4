##############################################################################
#
# Copyright (c) 2008 Projekt01 GmbH and Contributors.
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
$Id: uclient.py 3799 2013-07-18 03:32:25Z roger.ineichen $
"""
__docformat__ = "reStructuredText"

import sys
import time
import types
import socket
import errno
import contextlib
import Queue
import logging
import cPickle
from hashlib import md5

import umemcache

import zope.interface
from zope.schema.fieldproperty import FieldProperty

import p01.memcache.connector
from p01.memcache import interfaces


#TLOCAL = threading.local()

log = logging.getLogger('p01.memcache')


EMPTY_SLOT = (sys.maxint, None)



class UltraMemcacheClient(object):
    """Non persistent ultramemcached client usaable as global utility.
    
    Note: this implementation uses a ultramemcached client icnluding queue
    pooling instead of threading local caching like ti python memcache
    implementation
    """

    zope.interface.implements(interfaces.IUltraMemcacheClient)

    _memcacheClientFactory = umemcache.Client
    _connectorFactory = p01.memcache.connector.UltraConnector

    servers = FieldProperty(interfaces.IUltraMemcacheClient['servers'])
    debug = FieldProperty(interfaces.IUltraMemcacheClient['debug'])
    namespace = FieldProperty(interfaces.IUltraMemcacheClient['namespace'])
    pickleProtocol = FieldProperty(
        interfaces.IUltraMemcacheClient['pickleProtocol'])

    # connection setup
    timeout = FieldProperty(interfaces.IUltraMemcacheClient['timeout'])
    delay = FieldProperty(interfaces.IUltraMemcacheClient['delay'])
    retries = FieldProperty(interfaces.IUltraMemcacheClient['retries'])
    lifetime = FieldProperty(interfaces.IUltraMemcacheClient['lifetime'])

    # connection pool queue
    queuetime = FieldProperty(interfaces.IUltraMemcacheClient['queuetime'])
    pooltime = FieldProperty(interfaces.IUltraMemcacheClient['pooltime'])
    maxPoolSize = FieldProperty(interfaces.IUltraMemcacheClient['maxPoolSize'])

    # server handling
    blacktime = FieldProperty(interfaces.IUltraMemcacheClient['blacktime'])

    def __init__(self, servers=['127.0.0.1:11211'], debug=0, pickleProtocol=-1,
        lifetime=3600, namespace=None, timeout=3, delay=1, retries=3,
        pooltime=60, queuetime=1, blacktime=60, maxPoolSize=50):
        self.servers = servers
        self.debug = debug
        self.pickleProtocol = pickleProtocol
        if lifetime is None:
            lifetime = 0
        self.lifetime = lifetime
        if namespace is not None:
            self.namespace = namespace

        # pool
        self.maxPoolSize = maxPoolSize
        self.pooltime = pooltime
        self.queuetime = queuetime
        self.blacktime = blacktime
        self.timeout = timeout
        self.pool = Queue.PriorityQueue(self.maxPoolSize)
        # If there is a maxPoolSize, prime the queue with empty slots.
        if maxPoolSize is not None:
            for _ in xrange(maxPoolSize):
                self.pool.put(EMPTY_SLOT)

        # server blacklist
        self._blacklist = {}
        self.retries = retries
        self._pick_index = 0

    # server handling
    def _blackListServer(self, server):
        self._blacklist[server] = time.time()

    def _getServer(self):
        # update the blacklist
        for server, age in self._blacklist.items():
            if time.time() - age > self.blacktime:
                del self._blacklist[server]

        # build the list of available servers
        choices = list(set(self.servers) ^ set(self._blacklist.keys()))

        if not choices:
            return None

        if self._pick_index >= len(choices):
            self._pick_index = 0

        choice = choices[self._pick_index]
        self._pick_index += 1
        return choice

    # connector pool handling
    def _getConnector(self):
        server = self._getServer()
        if not server:
            # reset blacklisted servers
            self._blacklist = {}
            # and try again
            server = self._getServer()
        last_error = None

        def createConnector(server):
            return self._connectorFactory(self._memcacheClientFactory,
                server, debug=self.debug, timeout=self.timeout,
                retries=self.retries, delay=self.delay)

        while server is not None:
            connector = createConnector(server)
            try:
                connector.connect()
                return connector
            except (socket.timeout, socket.error), e:
                if not isinstance(e, socket.timeout):
                    if e.errno != errno.ECONNREFUSED:
                        raise

                # blacklist this server and try again
                self._blackListServer(server)
                server = self._getServer()
                last_error = e

        if last_error is not None:
            raise last_error
        else:
            raise socket.timeout('No server left in the pool')

    def _checkout_connection(self):
        # we only wait if we have a max pool size
        blocking = self.maxPoolSize is not None
        # Loop until we get a non-stale connection, or we create a new one.
        while True:
            try:
                ts, connector = self.pool.get(blocking, self.queuetime)
            except Queue.Empty:
                if blocking:
                    #timeout
                    raise Exception("No connections available in the pool")
                else:
                    # No maxPoolSize and no free connections, create a new one.
                    # XXX TODO: we should be using a monotonic clock here.
                    now = int(time.time())
                    return now, self._getConnector()
            else:
                now = int(time.time())
                # If we got an empty slot placeholder, create a new connection.
                if connector is None:
                    try:
                        return now, self._getConnector()
                    except Exception, e:
                        if self.maxPoolSize is not None:
                            # return slot to queue
                            self.pool.put(EMPTY_SLOT)
                        raise e
                # If the connection is not stale, go ahead and use it.
                if ts + self.pooltime > now:
                    return ts, connector
                # Otherwise, the connection is stale.
                # Close it, push an empty slot onto the queue, and retry.
                connector.disconnect()
                self.pool.put(EMPTY_SLOT)
                continue

    def _checkin_connection(self, ts, connector):
        """Return a connection to the pool."""
        # If the connection is now stale, don't return it to the pool.
        # Push an empty slot instead so that it will be refreshed when needed.
        now = int(time.time())
        if ts + self.pooltime > now:
            self.pool.put((ts, connector))
        else:
            if self.maxPoolSize is not None:
                self.pool.put(EMPTY_SLOT)

    @contextlib.contextmanager
    def connector(self):
        """Get a connector from the pool (queue)"""
        ts, connector = self._checkout_connection()
        try:
            yield connector
        finally:
            self._checkin_connection(ts, connector)

    # client api
    def buildKey(self, key):
        """Builds a (md5) memcache key based on the given key

        - if the key is a string, the plain key get used as base

        - if the key is unicode, the key get converted to UTF-8 as base

        - if the key is an int, the key get converted to string as base

        - if key is a persistent object its _p_oid is used as base

        - anything else will get pickled (including unicode)
        
        Such a base key get converted to an md5 hexdigest if a namespace is
        used, the namespace is used as key prefix.

        """
        if isinstance(key, (types.IntType, types.StringType)):
            bKey = str(key)
        elif isinstance(key, types.UnicodeType):
            bKey = key.encode('UTF-8')
        elif getattr(key, '_p_oid', None):
            bKey = getattr(key, '_p_oid')
        else:
            bKey = cPickle.dumps(key, protocol=self.pickleProtocol)

        if self.namespace is not None:
            bKey = '%s%s' % (self.namespace, bKey)
        mKey = md5(bKey)
        return mKey.hexdigest()

    def set(self, key, data, lifetime=0, raw=False):
        bKey = self.buildKey(key)
        if not lifetime:
            lifetime = self.lifetime
        if raw:
            if not isinstance(data, types.StringType):
                raise ValueError(
                    "Data must be a string %s given" % type(data), data)
        else:
            data = cPickle.dumps(data, protocol=self.pickleProtocol)
        if self.debug:
            log.debug('set: %r -> %s, %r, %r, %r' % (key, bKey, len(data),
                self.namespace, lifetime))

        with self.connector() as conn:
            if conn.set(bKey, data, lifetime):
                return bKey

        return None

    def query(self, key, raw=False, default=None):
        bKey = self.buildKey(key)
        with self.connector() as conn:
            res = conn.get(bKey)
            if res is not None and self.debug:
                log.debug('query: %r, %r, %r, %r' % (key, len(res), self.namespace,
                    raw))
            if res is None:
                return default
            if raw:
                return res
            return cPickle.loads(res)

    def invalidate(self, key):
        bKey = self.buildKey(key)
        if self.debug:
            log.debug('invalidate: %r -> %s, %r '% (key, bKey, self.namespace))
        with self.connector() as conn:
            conn.delete(bKey)

    def invalidateAll(self):
        if self.debug:
            log.debug('invalidateAll')
        with self.connector() as conn:
            conn.flush_all()

    def getStatistics(self):
        with self.connector() as conn:
            return conn.get_stats()
