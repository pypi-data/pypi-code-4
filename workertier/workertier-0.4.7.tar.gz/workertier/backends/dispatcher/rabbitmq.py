#coding:utf-8
import random
import logging
import functools

import gevent
from gevent import socket
from gevent import dns
from gevent.coros import Semaphore

from haigha.connection import Connection as HaighaConnection
from haigha.exceptions import ChannelClosed
from haigha.message import Message

from workertier.backends.dispatcher import Dispatcher


logger = logging.getLogger(__name__)


CONSUMER_STATUS_CHECK_INTERVAL = 1  #TODO Configurable?


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


class Connection(object):
    def __init__(self, host, port, virtualhost, user, password, queue):
        self.conn_id = hex(int(random.random() * 2**32))

        self._conn_kwargs = {
            "host": host,
            "port": port,
            "vhost": virtualhost,
            "user": user,
            "password": password,
            "transport": "gevent",
            "close_db": self._on_disconnect,
        }
        self.queue = queue

        self._connection = None
        self._channel = None
        self.lock = Semaphore()
        self.broken = False

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

    def _read_loop(self):
    # The message pump needs to run for the connection to actually do something.
        while not self.broken:
            exec_or_break(self._connection.read_frames)()
            gevent.sleep()  # Yield to other greenlets so they don't starve

    def _start_read_loop(self):
        self.log_debug("Starting connection loop")
        gevent.spawn(self._read_loop)  # Power our connection

    @exec_or_break
    def dispatch(self, key):
        self._ensure_open()
        self._channel.basic.public(Message(key), "", self.queue)

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


class RabbitMQDispatcher(Dispatcher):
    def __init__(self, host, port, virtualhost, user, password, queue):
        self.host = host
        self.port = port
        self.virtualhost = virtualhost
        self.user = user
        self.password = password
        self.queue = queue

        self._pool = []

    def _acquire_connection(self):
        # TODO: bad design, this should be a Context Manager, or we'll eventually forget to release the Lock.
        for connection in self._pool:
            if connection.broken:
                continue
            if connection.lock.acquire(blocking=False):
                logger.debug("Reusing existing connection: %s", connection.conn_id)
                break
        else:
            connection = Connection(self.host, self.port, self.virtualhost, self.user, self.password, self.queue)
            connection.lock.acquire(blocking=False)
            self._pool.append(connection)
            logger.debug("Creating new connection: %s", connection.conn_id)

        # Clean up 10% of the time
        if random.random() < 0.1:  #TODO: Should be implemented as a Greenlet
            logger.debug("Cleaning up broken connections")
            self._pool = [connection for connection in self._pool if not connection.broken]

        return connection

    def dispatch(self, key):
        connection = self._acquire_connection()

        logger.debug("Dispatching new message: '%s' in %s", key, connection.conn_id)
        connection.dispatch(key)  #TODO: Try / except / finally here (catch socket.timeout, and raise BackendUnavailable)
        connection.lock.release()

        if connection.broken:
            logger.warning("Connection %s now broken: delivery not guaranteed.", connection.conn_id)

    def start_consumer(self, message_consumer):
        # Every time this method is called, we start a new consumer
        logger.debug("Starting new consumer")
        connection = None
        while 1:
            if connection is None or connection.broken:
                connection = self._acquire_connection()
                try:
                    connection.consume(message_consumer)
                except (socket.error, dns.DNSError) as e:
                    logger.warning("Error starting consumer on connection (%s): %s", connection.conn_id, e)
                    connection.broken = True
                finally:
                    connection.lock.release()

            gevent.sleep(CONSUMER_STATUS_CHECK_INTERVAL)
            # TODO: Add exponential backoff
