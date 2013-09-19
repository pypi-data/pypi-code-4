#coding:utf-8
import unittest
import tempfile
import shutil
import signal

from workertier.backends import BackendUnavailable

from workertier.backends.cache.memcluster import BaseRemoteMemcachedClusterCache
from workertier.backends.cache.memcluster.scalr import ScalrMemcachedClusterCache
from workertier.backends.cache.memory import MemoryCache
from workertier.tests import TestRemote


class TestMemcachedClusterCache(BaseRemoteMemcachedClusterCache):
    def __init__(self, ip_lists):
        super(TestMemcachedClusterCache, self).__init__(11211, 3)
        self.remote = TestRemote(ip_lists)

    def _create_backend_connection(self, server):
        return MemoryCache({})

    def _get_remote(self):
        return self.remote


class MemclusterTestCase(unittest.TestCase):
    # Note, this is sightly messed up: we can't detach a signal handler

    def setUp(self):
        # A few IPs lists to use
        self.ip_1 = ["1.1.1.1"]
        self.ip_1_alt = ["1.1.1.2"]
        self.ip_2 = ["2.1.1.1", "2.1.1.2"]
        self.ip_3 = ["3.1.1.1", "3.1.1.2", "3.1.1.3"]
        self.test_dir = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.test_dir)

    def test_exceptions(self):
        cache = TestMemcachedClusterCache([[]])
        self.assertRaises(BackendUnavailable, cache.get, "key")
        self.assertRaises(BackendUnavailable, cache.set, "key", "value")
        self.assertRaises(BackendUnavailable, cache._get_backend_connection, "key")

    def test_election(self):
        cache = TestMemcachedClusterCache([self.ip_3])
        for i in range(50):
            cache.set(str(i), str(i))
        self.assertEqual(set(self.ip_3), set(cache._clients.keys()))

    def test_get(self):
        cache = TestMemcachedClusterCache([self.ip_1])
        self.assertEqual(None, cache.get("key"))
        cache._clients["1.1.1.1"]._store["key"] = "value"
        self.assertEqual("value", cache.get("key"))

    def test_set(self):
        cache = TestMemcachedClusterCache([self.ip_1])
        cache._get_backend_connection("key")  # Create the connection (lazily created)
        self.assertEqual({}, cache._clients["1.1.1.1"]._store)
        cache.set("key", "value")
        self.assertEqual({"key": "value"}, cache._clients["1.1.1.1"]._store)

    def test_switch(self):
        cache = TestMemcachedClusterCache([self.ip_1, self.ip_1_alt])
        cache._get_backend_connection("key")
        cache.remote._refresh_server_list()
        cache._get_backend_connection("key")

        self.assertEqual(set(self.ip_1 + self.ip_1_alt), set(cache._clients.keys()))


    def test_scalr_memcluster(self):
        # We already test the functionality somewhere else, just make sure we initialize properly
        cache = ScalrMemcachedClusterCache("scalr", "myrole", 11211, 2, "SIGUSR1")
        self.assertEqual("scalr", cache.remote.ip_list_home)
        self.assertEqual("myrole", cache.remote.role_name)
        self.assertEqual(11211, cache.port)
        self.assertEqual(2, cache.timeout)
        self.assertEqual(signal.SIGUSR1, cache.remote.signal_handler.signum)

        cache.remote.signal_handler.active = False
