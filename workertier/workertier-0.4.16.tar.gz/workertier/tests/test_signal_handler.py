#coding:utf-8
import os
import unittest
import signal
import gevent

from workertier.utils.signal_handler import SignalHandler, find_signum


class TestObj(object):
    def __init__(self):
        self.n_calls = 0

    def call_me(self):
        self.n_calls += 1


def signal_to_self(signum):
    os.kill(os.getpid(), signum)
    gevent.sleep()
    gevent.sleep()


class SignalHandlerTestCase(unittest.TestCase):
    def test_active_signal_handler(self):
        o = TestObj()
        SignalHandler(signal.SIGUSR1, o.call_me)
        self.assertEqual(0, o.n_calls)
        signal_to_self(signal.SIGUSR1)
        self.assertEqual(1, o.n_calls)

    def test_inactive_signal_handler(self):
        o = TestObj()
        handler = SignalHandler(signal.SIGUSR1, o.call_me)
        handler.active = False
        self.assertEqual(0, o.n_calls)
        signal_to_self(signal.SIGUSR1)
        self.assertEqual(0, o.n_calls)

    def test_find_signum(self):
        self.assertEqual(signal.SIGUSR1, find_signum("SIGUSR1"))
        self.assertEqual(signal.SIGUSR2, find_signum("SIGUSR2"))
