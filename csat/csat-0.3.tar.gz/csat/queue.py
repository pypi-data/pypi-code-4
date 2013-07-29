import collections
import itertools

from twisted.internet import defer


class QueueClosedError(Exception):
    pass


class Consumer(object):
    def __init__(self, queue, callback, paused=False):
        self.queue = queue
        self.callback = callback
        self.paused = paused
        self._current = None

        if not self.paused:
            self._next()

    def unpause(self):
        if self.paused:
            self.paused = False
            self._next()

    def pause(self):
        if not self.paused:
            self.paused = True
            self._current.cancel()

    def _next(self, _=None):
        self._current = self.queue.get()
        self._current.addCallback(self._consume)
        self._current.addErrback(self._trapCancelled)
        self._current.addErrback(self._queueClosed)
        self._current.addErrback(self._consumeError)

    def _trapCancelled(self, failure):
        if self.paused:
            failure.trap(defer.CancelledError)
        else:
            return failure

    def _queueClosed(self, failure):
        failure.trap(QueueClosedError)
        # TODO: Log queue destroyed
        self.pause()

    def _consumeError(self, failure):
        # This can happen only when self.consume raises an error
        if not self.paused:
            self._next()
        return failure

    def _consume(self, message):
        d = defer.maybeDeferred(self.callback, message)
        d.addCallback(self._next)


class Queue(object):
    def __init__(self, broker, name):
        self.broker = broker
        self.name = name
        self.bindings = set()
        self.messages = collections.deque()
        self.waiting = collections.deque()
        self.cancelled = set()

    def dispatch(self, message):
        while self.waiting and self.waiting[0] in self.cancelled:
            self.cancelled.discard(self.waiting.popleft())

        if self.waiting:
            deferred = self.waiting.popleft()
            deferred.callback(message)
        else:
            self.messages.append(message)

    def consume(self, callback):
        return Consumer(self, callback)

    def _cancelDeferred(self, deferred):
        self.cancelled.add(deferred)

    def get(self):
        if self.messages:
            message = self.messages.popleft()
            return defer.succeed(message)
        else:
            self.waiting.append(defer.Deferred(self._cancelDeferred))
            return self.waiting[-1]

    def bind(self, exchange, routing_key=None):
        return Binding(exchange, self, routing_key)

    def close(self):
        while self.bindings:
            self.bindings.pop().unbind()

        for waiting in self.waiting:
            waiting.errback(QueueClosedError())

        self.broker._removeQueue(self.name)


class Binding(object):
    wildcard = '*'
    delimiter = '.'

    def __init__(self, exchange, queue, routing_key):
        self.exchange = exchange
        self.queue = queue
        self.routing_key = routing_key.split(self.delimiter)
        self.exchange.bindings.add(self)
        self.queue.bindings.add(self)

    def unbind(self):
        self.exchange.bindings.discard(self)
        self.queue.bindings.discard(self)

    def _matches(self, message, routing_key):
        if isinstance(routing_key, basestring):
            routing_key = routing_key.split(self.delimiter)

        if len(routing_key) != len(self.routing_key):
            return False

        else:
            for key, pattern in itertools.izip(routing_key, self.routing_key):
                if pattern not in (key, self.wildcard):
                    break
            else:
                return True
            return False

    def route(self, message, routing_key=None):
        if self._matches(message, routing_key):
            self.queue.dispatch(message)


class Exchange(object):
    def __init__(self, broker, name):
        self.broker = broker
        self.name = name
        self.bindings = set()

    def pub(self, message, routing_key=None):
        for binding in self.bindings:
            binding.route(message, routing_key)

    def bind(self, queue, routing_key=None):
        return Binding(self, queue, routing_key)

    def destroy(self):
        while self.bindings:
            self.bindings.pop().unbind()
        self.broker._removeExchange(self.name)


class Broker(object):
    def __init__(self):
        self.queues = {}
        self.exchanges = {}

    def exchange(self, name):
        if name not in self.exchanges:
            self.exchanges[name] = Exchange(self, name)
        return self.exchanges[name]

    def queue(self, name):
        if name not in self.queues:
            self.queues[name] = Queue(self, name)
        return self.queues[name]

    def _removeExchange(self, name):
        del self.exchanges[name]

    def _removeQueue(self, name):
        del self.queues[name]


if __name__ == '__main__':

    def p(i):
        def pp(m):
            print 'Sub: ', i, m
        return pp

    count = 0

    def x(i):
        global count
        count += 1

    b = Broker()

    e1 = b.exchange('ex1')
    q1 = b.queue('q1')
    b1 = q1.bind(e1, 'test')

    c = Consumer(q1, p(1))

    e1.pub('hello1', 'test')
    e1.pub('hello2', 'test')
    e1.pub('hello3', 'test')

    q1.close()

    e1.pub('hello1d', 'test')
    e1.pub('hello2', 'test')
    e1.pub('hello3', 'test')

    b1.unbind()

    e1.pub('hello1', 'test')
    e1.pub('hello2', 'test')
    e1.pub('hello3', 'test')

    e1.destroy()
