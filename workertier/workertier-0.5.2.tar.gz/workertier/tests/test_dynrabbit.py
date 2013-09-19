#coding:utf-8
import collections
import unittest

import gevent
import gevent.queue

from workertier.backends import BackendUnavailable
from workertier.backends.dispatcher.dynrabbit import DynamicRabbitMQDispatcher, ExponentialBackoffStrategy

from workertier.tests import TestRemote, TestConnection



class TestExponentialBackoffStrategy(ExponentialBackoffStrategy):
    def __init__(self, *args, **kwargs):
        super(TestExponentialBackoffStrategy, self).__init__(*args, **kwargs)
        self.success = 0
        self.failures = 0

    def failed(self):
        super(TestExponentialBackoffStrategy, self).failed()
        self.failures += 1

    def succeeded(self):
        super(TestExponentialBackoffStrategy, self).succeeded()
        self.success += 1

    def wait(self):
        gevent.sleep()  # Return control to our test


class TestDynRabbitMQDispatcher(DynamicRabbitMQDispatcher):
    consumer_reopen_interval = 0
    consumer_status_check_interval = 0

    def __init__(self, queue, ip_lists):
        super(TestDynRabbitMQDispatcher, self).__init__(5672, "/", "user", "passwd", "queue")
        self.queue = queue
        self.remote = TestRemote(ip_lists)
        self.backoff_strategy = TestExponentialBackoffStrategy()

    def _create_connection(self):
        return TestConnection(self.queue, self.host)

    def _get_remote(self):
        return self.remote


class DynRabbitTestCase(unittest.TestCase):
    def setUp(self):
        self.ip_ok_1 = ["1.1.1.1"]
        self.ip_ok_2 = ["2.2.2.2"]
        self.ip_ko = []
        self.ip_warn = ["2.2.2.1", "2.2.2.2"]

        self.queue = gevent.queue.Queue()

    def test_failed_dispatch(self):
        dispatcher = TestDynRabbitMQDispatcher(self.queue, [self.ip_ko])
        dispatcher.dispatch("msg")
        gevent.sleep()
        self.assertIsNotNone(dispatcher.backoff_strategy.delay)

    def test_failed_consume(self):
        dispatcher = TestDynRabbitMQDispatcher(self.queue, [self.ip_ko])
        dispatcher.start_consumer()
        gevent.sleep()
        self.assertIsNotNone(dispatcher.backoff_strategy.delay)

    def test_dispatch(self):
        dispatcher = TestDynRabbitMQDispatcher(self.queue, [self.ip_ok_1])
        dispatcher.dispatch("kEy")
        gevent.sleep()

        self.assert_(hasattr(dispatcher._pool[0], "queue"))
        self.assertEqual(collections.deque([("kEy", "1.1.1.1")]), self.queue.queue)

    def test_consume(self):
        dispatcher = TestDynRabbitMQDispatcher(self.queue, [self.ip_ok_1])

        dispatcher.start_consumer()
        gevent.sleep()

        dispatcher.dispatch("blah")
        gevent.sleep()

        self.assertEqual(collections.deque([("blah", "1.1.1.1")]), dispatcher._messages_queue.queue)

    def test_consume_switch(self):
        dispatcher = TestDynRabbitMQDispatcher(self.queue, [self.ip_ok_1, self.ip_ok_2])
        dispatcher.start_consumer()

        dispatcher.dispatch("blah")
        gevent.sleep()

        dispatcher.remote._refresh_server_list()  # Rotate the IPs
        map(lambda conn: setattr(conn, "broken", True), dispatcher._pool)

        dispatcher.dispatch("blah")
        gevent.sleep()

        self.assertEqual(collections.deque([("blah", "1.1.1.1"), ("blah", "2.2.2.2")]),
                         dispatcher._messages_queue.queue)

        self.assertIsNone(dispatcher.backoff_strategy.delay)
        self.assertEqual(0, dispatcher.backoff_strategy.failures)  # We didn't break on connect (=> instant reconnect)
        self.assertEqual(2, dispatcher.backoff_strategy.success)   # Our two dispatcher connections

    def test_dispatch_switch(self):
        dispatcher = TestDynRabbitMQDispatcher(self.queue, [self.ip_ok_1, self.ip_ok_2])
        dispatcher.dispatch("blah")
        gevent.sleep()

        dispatcher.remote._refresh_server_list()  # Rotate the IPs
        map(lambda conn: setattr(conn, "broken", True), dispatcher._pool)

        dispatcher.dispatch("blah")
        gevent.sleep()

        self.assertEqual(collections.deque([("blah", "1.1.1.1"), ("blah", "2.2.2.2")]), self.queue.queue)
