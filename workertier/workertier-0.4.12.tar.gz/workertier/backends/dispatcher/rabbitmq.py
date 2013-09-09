#coding:utf-8
import logging
import random
import functools

import gevent
from gevent import socket
from gevent import dns

from haigha.connection import Connection as HaighaConnection
from haigha.exceptions import ChannelClosed
from haigha.message import Message
from workertier.backends import BackendUnavailable

from workertier.backends.dispatcher import Dispatcher
from workertier.backends.pool import ConnectionPool, Connection


logger = logging.getLogger(__name__)


CONSUMER_STATUS_CHECK_INTERVAL = 1  #TODO Configurable?
CONSUMER_REOPEN_INTERVAL = 5


def exec_or_break(method):
    """
    Decorate methods so that instead of raising Exceptions, they mark the connection as broken.
    """

    @functools.wraps(method)
    def wrapped(self, *args, **kwargs):
        try:
            method(self, *args, **kwargs)
        except (socket.error, dns.DNSError, ChannelClosed) as e:
            self.broken = True
            self.log_exception("Marking connection as broken. Error executing %s: %s.", method, e)

    return wrapped


class RabbitMQConnection(Connection):
    def __init__(self, host, port, virtualhost, user, password, queue):
        self.conn_id = hex(int(random.random() * 2**32))

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
    def dispatch(self, key):
        self._ensure_open()
        self._channel.basic.publish(Message(key), "", self.queue)

    @exec_or_break
    def consume(self, consumer):
        # Start consuming messages from the queue (they will be passed to `consumer`)
        def cb():
            self.log_debug("Registered as consumer")

        def consumer_wrapper(message):
            self.log_debug("Received a message: %s", message.body)
            consumer(message)

        self._ensure_open()
        self._channel.basic.consume(queue=self.queue, consumer=consumer_wrapper, cb=cb)


class RabbitMQDispatcher(Dispatcher, ConnectionPool):
    def __init__(self, host, port, virtualhost, user, password, queue):
        self.host = host
        self.port = port
        self.virtualhost = virtualhost
        self.user = user
        self.password = password
        self.queue = queue

        super(RabbitMQDispatcher, self).__init__()

    def _create_connection(self):
        return RabbitMQConnection(self.host, self.port, self.virtualhost, self.user, self.password, self.queue)

    def dispatch(self, key):
        with self._acquire_connection() as connection:
            logger.debug("Dispatching new message: '%s' in %s", key, connection.conn_id)
            with connection.raise_if_broken(BackendUnavailable):
                connection.dispatch(key)

    def start_consumer(self, message_consumer):
        # Every time this method is called, we start a new consumer
        logger.debug("Starting new consumer")

        while 1:
            with self._acquire_connection() as connection:
                connection.consume(message_consumer)
                while 1:
                    if connection.broken:
                        break
                    gevent.sleep(CONSUMER_STATUS_CHECK_INTERVAL)
                gevent.sleep(CONSUMER_REOPEN_INTERVAL)
