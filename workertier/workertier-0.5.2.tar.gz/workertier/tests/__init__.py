#coding:utf-8
import collections

import gevent
import gevent.queue

from workertier.backends.dispatcher import Dispatcher
from workertier.backends.pool import Connection
from workertier.backends.remote.base import BaseRemoteBackend


class BreakConnection(Exception):
    pass


class TestRemote(BaseRemoteBackend):  #TODO: Test this somewhere else.
    def __init__(self, ip_lists):
        super(TestRemote, self).__init__()
        self.ip_lists = collections.deque(ip_lists)
        self.ip_lists.rotate(1)  # We're going to rotate again.

    def _get_servers_list(self):
        self.ip_lists.rotate(-1)
        return self.ip_lists[0]


class TestConnection(Connection):
    def __init__(self, queue, host=None):
        super(TestConnection, self).__init__()
        self.host = host
        self.queue = queue

    def dispatch(self, key):
        self.queue.put((key, self.host))

    def _consume(self, consumer):
        while 1:
            msg = self.queue.get()
            consumer(msg)

    def start_consumer(self, consumer):
        return gevent.spawn(self._consume, consumer)
