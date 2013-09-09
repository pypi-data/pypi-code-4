#coding:utf-8
import signal
import os
import collections
import unittest
import tempfile
import shutil

import gevent
from workertier.backends import BackendUnavailable

from workertier.backends.cache.memcluster import BaseMemcachedClusterCache
from workertier.backends.cache.memcluster.scalr import ScalrMemcachedClusterCache
from workertier.backends.cache.memory import MemoryCache


USE_SIGNALS = [signal.SIGUSR1, signal.SIGUSR2]


class TestMemcachedClusterCache(BaseMemcachedClusterCache):
    def __init__(self, ip_lists, refresh_signal=None):
        super(TestMemcachedClusterCache, self).__init__(11211, 3, refresh_signal)
        self.ip_lists = collections.deque(ip_lists)
        self.ip_lists.rotate(1)  # We're going to rotate again.

        self.test_connected_to = set()

    def _get_servers_list(self):
        self.ip_lists.rotate(-1)
        return self.ip_lists[0]

    def _create_server_connection(self, server):
        self.test_connected_to.add(server)
        return MemoryCache({})


class MemclusterTestCase(unittest.TestCase):
    # Note, this is sightly messed up: we can't detach a signal handler

    def setUp(self):
        # A few IPs lists to use
        self.ip_1 = ["1.1.1.1"]
        self.ip_2 = ["2.1.1.1", "2.1.1.2"]
        self.ip_3 = ["3.1.1.1", "3.1.1.2", "3.1.1.3"]
        self.test_dir = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.test_dir)

    def test_handling_by_signum(self):
        cache = TestMemcachedClusterCache([self.ip_1, self.ip_2, self.ip_3], signal.SIGUSR1)
        cache._refresh_server_list()
        self.assertEqual(self.ip_1, cache._ips)

        os.kill(os.getpid(), signal.SIGUSR1)
        gevent.sleep(0.1)

        self.assertEqual(self.ip_2, cache._ips)

    def test_handling_by_signame(self):
        cache = TestMemcachedClusterCache([self.ip_1, self.ip_2, self.ip_3], "SIGUSR1")
        cache._refresh_server_list()
        self.assertEqual(self.ip_1, cache._ips)

        os.kill(os.getpid(), signal.SIGUSR1)
        gevent.sleep(0.1)

        self.assertEqual(self.ip_2, cache._ips)

    def test_scalr_backend(self):
        role_name = "role-test"
        role_dir = os.path.join(self.test_dir, role_name)
        os.mkdir(role_dir)

        cache = ScalrMemcachedClusterCache(self.test_dir, role_name, 11211, 2)

        cache._refresh_server_list()
        self.assertEqual([], cache._ips)

        for ip in self.ip_3:
            with open(os.path.join(role_dir, ip), "w"):
                pass

        cache._refresh_server_list()
        self.assertEqual(self.ip_3, cache._ips)

    def test_exceptions(self):
        cache = TestMemcachedClusterCache([[]])
        self.assertRaises(BackendUnavailable, cache.get, "key")
        self.assertRaises(BackendUnavailable, cache.set, "key", "value")
        self.assertRaises(BackendUnavailable, cache.get_cache, "key")

    def test_election(self):
        cache = TestMemcachedClusterCache([self.ip_3])
        for i in range(50):
            cache.set(str(i), str(i))
        self.assertEqual(set(self.ip_3), cache.test_connected_to)
