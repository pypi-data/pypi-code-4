#coding:utf-8
import shutil
import tempfile
import unittest
from workertier.backends import BackendUnavailable

from workertier.backends.dispatcher.dynrabbit import BaseRemoteDynRabbitDispatcher
from workertier.backends.dispatcher.memory import MemoryDispatcher
from workertier.tests import TestRemote


class TestDynRabbitDispatcher(BaseRemoteDynRabbitDispatcher):
    def __init__(self, ip_lists):
        super(BaseRemoteDynRabbitDispatcher, self).__init__(5672, "/", "user", "passwd", "queue")
        self.remote = TestRemote(ip_lists)

    def _create_backend_connection(self, server):
        return MemoryDispatcher({}, lambda s: s.swapcase())

    def _get_remote(self):
        return self.remote


class DynRabbitTestCase(unittest.TestCase):
    def setUp(self):
        self.ip_ok = ["1.1.1.1"]
        self.ip_ko = []
        self.ip_warn = ["2.2.2.1", "2.2.2.2"]
        self.test_dir = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.test_dir)

    def test_exceptions(self):
        dispatcher = TestDynRabbitDispatcher([self.ip_ko])
        self.assertRaises(BackendUnavailable, dispatcher.dispatch, "msg")
        self.assertRaises(BackendUnavailable, dispatcher.start_consumer, lambda msg: msg)
        self.assertRaises(BackendUnavailable, dispatcher._get_backend_connection)

    def test_dispatch(self):
        dispatcher = TestDynRabbitDispatcher([self.ip_ok])
        dispatcher.dispatch("kEy")
        self.assertEqual({"kEy": "KeY"}, dispatcher._clients.values()[0]._store)

    def test_consume(self):
        class TestMessageConsumer(object):
            def __init__(self):
                self.messages = []
            def __call__(self, message):
                self.messages.append(message)

        c = TestMessageConsumer()

        dispatcher = TestDynRabbitDispatcher([self.ip_ok])
        dispatcher.start_consumer(c)
        dispatcher.dispatch("blah")
        self.assertEqual(["blah"], c.messages)

    def test_switch(self):
        dispatcher = TestDynRabbitDispatcher([self.ip_ok, self.ip_warn])
        dispatcher.dispatch("kEy")
        dispatcher.remote._refresh_server_list()
        dispatcher.dispatch("kEy")
        self.assertEqual(set(["1.1.1.1", "2.2.2.1"]), set(dispatcher._clients.keys()))
        self.assertEqual(2, len(dispatcher._clients))
