#coding:utf-8
import logging
import functools

import gevent
from gevent import socket
from gevent import dns
from gevent import queue as gevent_queue

from haigha.connection import Connection as HaighaConnection
from haigha.exceptions import ChannelClosed
from haigha.message import Message
from workertier.backends import BackendUnavailable

from workertier.backends.dispatcher import Dispatcher
from workertier.backends.pool import ConnectionPool, Connection


logger = logging.getLogger(__name__)




def exec_or_break(method):
    """
    Decorate methods so that instead of raising Exceptions, they mark the connection as broken.
    """

    @functools.wraps(method)
    def wrapped(self, *args, **kwargs):
        try:
            return method(self, *args, **kwargs)
        except (socket.error, dns.DNSError, ChannelClosed) as e:
            self.broken = True
            self.log_exception("Marking connection as broken. Error executing %s: %s.", method, e)

    return wrapped


class RabbitMQConnection(Connection):
    def __init__(self, host, port, virtualhost, user, password, queue):
        self._conn_kwargs = {
            "host": host,
            "port": port,
            "vhost": virtualhost,
            "user": user,
            "password": password,
            "transport": "gevent",
            "close_cb": self._on_disconnect,
            "logger": logger,
        }
        self.queue = queue

        self._connection = None
        self._channel = None

        super(RabbitMQConnection, self).__init__()

    def log_debug(self, msg, *args, **kwargs):
        # Ghetto log handler
        logger.debug("[Conn {0}] {1}".format(self.conn_id, msg), *args, **kwargs)

    def log_exception(self, msg, *args, **kwargs):
        logger.exception("[Conn {0}] {1}".format(self.conn_id, msg), *args, **kwargs)

    def disconnect(self):
        self.log_debug("Disconnecting")
        self.broken = True
        self._connection.disconnect()

    def _on_disconnect(self):
        self.log_debug("Received disconnect")
        self.broken = True

    def _on_channel_closed(self, channel):
        # Scrape the connection if our channel is closed.
        self.log_debug("Received channel close")
        self.disconnect()

    def _open_connection(self):
        self.log_debug("Opening RabbitMQ connection")
        self._connection = HaighaConnection(**self._conn_kwargs)
        self._start_read_loop()

    def _open_channel(self):
        # Open a channel and make sure we know if it gets closed
        self.log_debug("Opening RabbitMQ channel")
        self._channel = self._connection.channel()
        self._channel.add_close_listener(self._on_channel_closed)
        self._channel.queue.declare(self.queue, auto_delete=True)

    def _ensure_open(self):
        if self._channel is None:
            self._open_connection()
            self._open_channel()

    @exec_or_break
    def _read_frames(self):
        self._connection.read_frames()

    def _read_loop(self):
    # The message pump needs to run for the connection to actually do something.
        while not self.broken:
            self._read_frames()
            gevent.sleep()  # Yield to other greenlets so they don't starve

    def _start_read_loop(self):
        self.log_debug("Starting connection loop")
        gevent.spawn(self._read_loop)  # Power our connection

    @exec_or_break
    def _consume(self, consumer):
        def cb():
            self.log_debug("Registered as consumer")
        self._channel.basic.consume(queue=self.queue, consumer=consumer, cb=cb)

    @exec_or_break
    def start_consumer(self, consumer):
        # Start consuming messages from the queue (they will be passed to `consumer`)
        self._ensure_open()
        gevent.spawn(self._consume, consumer)

    @exec_or_break
    def dispatch(self, key):
        self._ensure_open()
        self._channel.basic.publish(Message(key), "", self.queue)


class RabbitMQDispatcher(Dispatcher, ConnectionPool):
    def __init__(self, host, port, virtualhost, user, password, queue):
        self._host = host
        self.port = port
        self.virtualhost = virtualhost
        self.user = user
        self.password = password
        self.queue = queue

        self._messages_queue = gevent_queue.Queue()

        super(RabbitMQDispatcher, self).__init__()

    @property
    def host(self):
        return self._host

    def _create_connection(self):
        return RabbitMQConnection(self.host, self.port, self.virtualhost, self.user, self.password, self.queue)

    def dispatch(self, key):
        logger.debug("Dispatching new message: '%s'", key)
        with self._acquire_connection() as connection:
            with connection.raise_if_broken(BackendUnavailable):
                connection.dispatch(key)

    def _consume(self):
        while 1:
            with self._acquire_connection() as connection:
                with connection.raise_if_broken(BackendUnavailable):
                    # We want to backoff if an error occurs here.
                    connection.start_consumer(self._messages_queue.put)

                while not connection.broken:
                    gevent.sleep()

                logger.warning("Consumer connection was closed")

    def start_consumer(self):
        # Every time this method is called, we start a new consumer
        logger.debug("Starting new consumer")
        return gevent.spawn(self._consume)  # Use link here? #TODO: switch

    @property
    def messages(self):
        while 1:
            yield self._messages_queue.get()
