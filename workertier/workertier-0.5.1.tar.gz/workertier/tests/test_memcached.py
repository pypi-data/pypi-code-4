#coding:utf-8
import unittest

from gevent import socket
from gevent.dns import DNSError
from pymemcache.client import MemcacheIllegalInputError, MemcacheError
from workertier.backends import BackendUnavailable, InvalidKey

from workertier.backends.cache.memcached import MemcachedCache, MemcachedConnection


class TestMemcachedClient(object):
    def __init__(self):
        self.mem = {}

    def _tests(self, key):
        if key == "socket.error":
            raise socket.error()
        if key == "socket.dns":
            raise DNSError()
        if key == "memcache.illegal":
            raise MemcacheIllegalInputError()
        if key == "memcache.error":
            raise MemcacheError()

    def get(self, key):
        self._tests(key)
        return self.mem.get(key)

    def set(self, key, value):
        self._tests(key)
        self.mem[key] = value


class TestMemcachedConnection(MemcachedConnection):
    def __init__(self, *args, **kwargs):
        super(TestMemcachedConnection, self).__init__(*args, **kwargs)
        self.client = TestMemcachedClient()


class TestMemcachedCache(MemcachedCache):
    def _create_connection(self):
        return TestMemcachedConnection(self.host, self.port, self.timeout)


class MemcachedTestCase(unittest.TestCase):
    def setUp(self):
        self.cache = TestMemcachedCache("www.example.com", 11211, 3)

    def test_memcached_errors(self):
        self.assertRaises(InvalidKey, self.cache.get, "memcache.illegal")
        self.assertRaises(BackendUnavailable, self.cache.get, "memcache.error")

    def test_socket_errors(self):
        self.assertRaises(BackendUnavailable, self.cache.get, "socket.dns")
        self.assertRaises(BackendUnavailable, self.cache.get, "socket.error")

        # Check that all connections left are broken
        # We don't want to rely on implementation details, so this is very generic
        old_conns = []
        for conn in self.cache._pool:
            old_conns.append(conn)
            self.assert_(conn.broken)

        self.cache.get("ok")
        self.assert_(self.cache._pool) # Check the pool isn't empty

        # Check we didn't reuse
        for conn in self.cache._pool:
            self.assert_(conn not in old_conns)

    def test_get_set(self):
        self.assertEqual(None, self.cache.get("blah"))
        self.cache.set("blah", "hello")
        conn = self.cache._pool[0]
        self.assertEqual({"blah": "hello"}, conn.client.mem)
        self.assertEqual("hello", self.cache.get("blah"))
