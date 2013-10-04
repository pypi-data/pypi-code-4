from __future__ import print_function

from gevent.event import AsyncResult, Event
from nose.tools import eq_

from spinoff.util.python import deferred_cleanup
from spinoff.actor import Node, actor, process


@deferred_cleanup
def test_actor_shortcut(defer):
    node = Node()
    defer(node.stop)

    msg_recvd = AsyncResult()
    ac = node.spawn(actor(lambda self, msg: msg_recvd.set((self.ref, msg))))
    ac << 'foo'

    eq_(msg_recvd.get(), (ac, 'foo'))


@deferred_cleanup
def test_process_shortcut(defer):
    node = Node()
    defer(node.stop)

    started = Event()
    node.spawn(process(lambda self: started.set()))

    started.wait()


@deferred_cleanup
def test_returned_object_looks_like_original(defer):
    node = Node()
    defer(node.stop)

    @actor
    def my_actor(self, msg):
        pass

    eq_(my_actor.__module__, 'spinoff.tests.shortcuts_test')
    eq_(my_actor.__name__, 'my_actor')

    @process
    def my_proc(self):
        pass

    eq_(my_proc.__name__, 'my_proc')
    eq_(my_proc.__module__, 'spinoff.tests.shortcuts_test')
