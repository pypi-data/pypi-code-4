# -*- coding: utf-8 -*-
"""
Utilities for AMQP RPC classes.
"""

from repr import Repr

import amqp
import gevent
import logging


def safe_spawn(func, *args, **kwargs):
    def tmp(*args, **kwargs):
        try:
            func(*args, **kwargs)
        except Exception:
            logger = logging.getLogger("amphora")
            logger.exception("Error in %r", func)
            raise
    return gevent.spawn(tmp, *args, **kwargs)


class LazySafeRepr(object):
    """Lazy evaluation of Repr.repr. Used for debug loggers."""
    repr = Repr()
    repr.maxstring = 120

    def __init__(self, obj):
        self.obj = obj

    def __str__(self):
        return self.repr.repr(self.obj)

safe_repr = LazySafeRepr


class AbstractHandlerChain(object):
    """Optimized "Chain of responsibility" pattern."""
    def __init__(self):
        self._handlers = None

    def add_handler(self, func):
        """Add function to chain."""
        assert callable(func)
        if self._handlers is None:
            self._handlers = func
            self.call = self._handler_call_one
        elif callable(self._handlers):
            self._handlers = [self._handlers, func]
            self.call = self._handler_call_many
        else:
            self._handlers.append(func)

    def _empty_call(self, *args, **kwargs):
        """Called when no handlers added to the chain."""
        pass

    call = _empty_call

    def __call__(self, *args, **kwargs):
        return self.call(*args, **kwargs)

    def _handler_call_one(self):
        """Called when chain contains only one handler."""
        raise NotImplementedError

    def _handler_call_many(self):
        """Called when chain contains more than one handlers."""
        raise NotImplementedError


class StaticHandlerChain(AbstractHandlerChain):
    """Chain of responsibility. Arguments for handlers
    specifies once at initialization and can't be changed."""
    def __init__(self, *args, **kwargs):
        super(StaticHandlerChain, self).__init__()
        self.args = args
        self.kwargs = kwargs

    def _handler_call_one(self, *dummy_args, **dummy_kwargs):
        self._handlers(*self.args, **self.kwargs)

    def _handler_call_many(self, *dummy_args, **dummy_kwargs):
        args, kwargs = self.args, self.kwargs
        for handler in self._handlers:
            handler(*args, **kwargs)


class DynamicHandlerChain(AbstractHandlerChain):
    """Chain of responsibility. Arguments for handlers
    specifies at every call."""
    def _handler_call_one(self, *args, **kwargs):
        self._handlers(*args, **kwargs)

    def _handler_call_many(self, *args, **kwargs):
        for handler in self._handlers:
            handler(*args, **kwargs)


class FailsafeAmqpPreferences(object):
    """Base class for Publisher and Consumer"""
    def __init__(self, amqp_host='127.0.0.1', amqp_port=5672,
                 amqp_user='guest', amqp_password='guest', amqp_vhost='/'):
        self.amqp_host = amqp_host
        self.amqp_port = amqp_port
        self.amqp_user = amqp_user
        self.amqp_password = amqp_password
        self.amqp_vhost = amqp_vhost

    def make_amqp_connection(self):
        """Create new AMQP connection."""
        return amqp.Connection(
            host=self.amqp_host, port=self.amqp_port, userid=self.amqp_user,
            password=self.amqp_password, virtual_host=self.amqp_vhost)


class AmqpRpcAbstract(object):
    """Base class for server and client. Each instance must
    create attributes `publisher` and `consumer` in __init__()."""
    def __init__(self):
        self.publisher = NotImplemented
        self.consumer = NotImplemented
        self.__publisher_greenlet = None
        self.__consumer_greenlet = None

    def serve(self, nowait=True):
        """Connect to AMQP and start working.

        :param nowait: Should current greenlet being blocked until
            server stop? By default don't block.
        :type nowait: bool"""
        self.__publisher_greenlet = safe_spawn(self.publisher.serve)
        self.__consumer_greenlet = safe_spawn(self.consumer.serve)
        if not nowait:
            self.__publisher_greenlet.join()
            self.__consumer_greenlet.join()

    def stop(self):
        """Stop instance and disconnect from AMQP server. All unsent
        messages will be hold until you'll call ``serve()`` again."""
        self.publisher.stop()
        self.consumer.stop()
        self.__publisher_greenlet.get()
        self.__consumer_greenlet.get()

    def stop_publisher(self):
        """Stop publishing messages. Consuming continues working
        (if it was not stopped earlier)."""
        self.publisher.stop()
        self.__publisher_greenlet.get()

    def stop_consumer(self):
        """Stop consuming messages. Publishing continues working
        (if it was not stopped earlier)."""
        self.consumer.stop()
        self.__consumer_greenlet.get()


class PrettyCaller(object):
    """API for remote procedure execution. Translate Python objects
    and calls into path string and argument list."""
    _internal_attrs = set(['_path', '_callback', '_option_kwargs'])

    def __init__(self, callback, path='', option_kwargs=None):
        if option_kwargs is None:
            option_kwargs = {}
        self._path = path
        self._callback = callback
        self._option_kwargs = option_kwargs

    def __call__(self, *args, **kwargs):
        if not self._path:
            self._path = kwargs.pop('function_name', '')
            self._option_kwargs = kwargs
            return self
        else:
            return self._callback(
                self._path, args, kwargs, self._option_kwargs)

    def __getattr__(self, attr):
        if attr in PrettyCaller._internal_attrs:
            return self.__dict__[attr]

        path = self._path
        if not path:
            path = attr
        else:
            path += '.' + attr
        return PrettyCaller(self._callback, path, self._option_kwargs)
