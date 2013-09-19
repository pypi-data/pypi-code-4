#coding:utf-8
import unittest

import gevent
from gevent import queue

from workertier.consumer import Consumer
from workertier.backends.dispatcher import Dispatcher
from workertier.backends.cache.memory import MemoryCache


class TestDispatcher(Dispatcher):
    def __init__(self):
        self.started = 0
        self.queue = queue.Queue()

    def start_consumer(self):
        self.started += 1

    @property
    def messages(self):
        while 1:
            yield self.queue.get()


class TestMessage(object):
    def __init__(self, body):
        self.body = body


class ConsumerTestCase(unittest.TestCase):
    def test_launch(self):
        n_consumers = 8
        dispatcher = TestDispatcher()
        consumer = Consumer(None, dispatcher, n_consumers)
        consumer._start_consumers()
        gevent.sleep() # Switch dispatcher.start_consumer
        self.assertEqual(n_consumers, dispatcher.started)

    def test_message_received(self):
        store = {}

        num_consumers = 8

        dispatcher = TestDispatcher()
        consumer = Consumer(MemoryCache(store), dispatcher, num_consumers)  # Don't need to start 5 non-processes...

        # Check that the dispatcher listeners get started.
        gevent.spawn(consumer.start)  # Run in a separate greenlet to test it.
        gevent.sleep()
        self.assertEqual(num_consumers, dispatcher.started)

        # Simulate an operation from the dispatcher, and make sure that we get it in the Consumer
        key, value = "mSg", "MsG"  #TODO: Our operation is a swapcase : l
        dispatcher.queue.put(TestMessage(key))
        gevent.sleep()  # Give control back

        self.assertEqual(value, store.get(key))

