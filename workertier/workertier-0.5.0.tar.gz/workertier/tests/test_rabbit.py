#coding:utf-8
import unittest

import gevent

from workertier.backends.dispatcher.rabbitmq import RabbitMQDispatcher
from workertier.backends.pool import Connection


class TestRabbitConnection(Connection):
    def __init__(self):
        super(TestRabbitConnection, self).__init__()
        self.dispatched = []

    def start_consumer(self, consumer):
        self.consumer = consumer

    def put_message(self, message):
        self.consumer(message)

    def dispatch(self, message):
        self.dispatched.append(message)


class TestRabbitMQDispatcher(RabbitMQDispatcher):
    def _create_connection(self):
        return TestRabbitConnection()


class BaseRabbitMQConnectionPoolTestCase(unittest.TestCase):
    def setUp(self):
        self.dispatcher = TestRabbitMQDispatcher("test.com", 5672, "/", "user", "passwd", "queue")


class SimpleRabbitMQConnectionPoolTestCase(BaseRabbitMQConnectionPoolTestCase):
    def test_dispatch(self):
        # Is a connection created when we dispatch?
        self.assertEqual(0, len(self.dispatcher._pool))

        self.dispatcher.dispatch("test_message")
        self.assertEqual(1, len(self.dispatcher._pool))

        # Is the message dispatched?
        conn, = self.dispatcher._pool
        self.assertEqual(["test_message"], conn.dispatched)

    def test_consume(self):
        # Is the connection created
        self.assertEqual(0, len(self.dispatcher._pool))

        self.dispatcher.start_consumer()
        gevent.sleep()  # Let our consumer start

        self.assertEqual(1, len(self.dispatcher._pool))

        conn, = self.dispatcher._pool
        conn.put_message("Hello")

        self.assertEqual(1, self.dispatcher._messages_queue.qsize())
        self.assertEqual("Hello", next(self.dispatcher.messages))

        self.assertEqual(0, self.dispatcher._messages_queue.qsize())


class BrokenConnectionRabbitMQConnectionPoolTestCase(BaseRabbitMQConnectionPoolTestCase):
    def test_reopen_on_dispatch(self):
        self.dispatcher.dispatch("1")

        # Break our first connection
        self.assertEqual(1, len(self.dispatcher._pool))
        conn1, = self.dispatcher._pool
        self.assertEqual(["1"], conn1.dispatched)
        conn1.broken = True

        # Open our second connection
        self.dispatcher.dispatch("2")
        self.assertEqual(1, len(self.dispatcher._pool))
        conn2, = self.dispatcher._pool
        self.assertEqual(["2"], conn2.dispatched)

        self.assertNotEqual(conn1, conn2)

    def test_reuse_on_dispatch(self):
        self.dispatcher.dispatch("1")

        # Retrieve our first connection
        self.assertEqual(1, len(self.dispatcher._pool))
        conn1, = self.dispatcher._pool

        # Dispatch our second connection
        self.dispatcher.dispatch("2")

        # Check we didn't reopen
        self.assertEqual(1, len(self.dispatcher._pool))
        conn2, = self.dispatcher._pool
        self.assertEqual(conn1, conn2)

        # Check the messages were dispatched
        self.assertEqual(["1", "2"], conn1.dispatched)

    def test_reopen_on_consume(self):
        self.dispatcher.start_consumer()

        gevent.sleep()  # Let our consumer start

        self.assertEqual(1, len(self.dispatcher._pool))
        conn1, = self.dispatcher._pool
        conn1.broken = True

        gevent.sleep()

        self.assertEqual(1, len(self.dispatcher._pool))
        conn2, = self.dispatcher._pool

        self.assertNotEqual(conn1, conn2)

    def test_reuse_on_consume(self):
        self.dispatcher.start_consumer()
        gevent.sleep()  # Let our consumer start

        self.assertEqual(1, len(self.dispatcher._pool))
        conn1, = self.dispatcher._pool

        gevent.sleep()
        self.assertEqual(1, len(self.dispatcher._pool))

        conn2, = self.dispatcher._pool
        self.assertEqual(conn1, conn2)
