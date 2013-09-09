#coding:utf-8
import os
import signal
import tempfile
import shutil
import collections
import unittest

from workertier.backends.remote.base import BaseRemoteBackend
from workertier.backends.remote.scalr import ScalrRemoteBackend


class TestRemoteBackend(BaseRemoteBackend):
    def __init__(self, ip_lists, refresh_signal=None):
        super(TestRemoteBackend, self).__init__(refresh_signal)
        self.ip_lists = collections.deque(ip_lists)
        self.ip_lists.rotate(1)  # We're going to rotate again.

    def _get_servers_list(self):
        self.ip_lists.rotate(-1)
        return self.ip_lists[0]


class RemoteTestCase(unittest.TestCase):
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
        backend = TestRemoteBackend([self.ip_1, self.ip_2, self.ip_3], signal.SIGUSR1)
        self.assertEqual(signal.SIGUSR1, backend.signal_handler.signum)

        backend._refresh_server_list()
        self.assertEqual(self.ip_1, backend.ips)
        backend.signal_handler.on_signal()
        self.assertEqual(self.ip_2, backend.ips)

    def test_handling_by_signame(self):
        backend = TestRemoteBackend([self.ip_1, self.ip_2, self.ip_3], "SIGUSR1")
        self.assertEqual(signal.SIGUSR1, backend.signal_handler.signum)

        backend._refresh_server_list()
        self.assertEqual(self.ip_1, backend.ips)
        backend.signal_handler.on_signal()
        self.assertEqual(self.ip_2, backend.ips)

    def test_scalr_backend(self):
        role_name = "role-test"
        role_dir = os.path.join(self.test_dir, role_name)
        os.mkdir(role_dir)

        backend = ScalrRemoteBackend(self.test_dir, role_name)

        backend._refresh_server_list()
        self.assertEqual([], backend.ips)

        for ip in self.ip_3:
            with open(os.path.join(role_dir, ip), "w"):
                pass

        backend._refresh_server_list()
        self.assertEqual(self.ip_3, backend.ips)
