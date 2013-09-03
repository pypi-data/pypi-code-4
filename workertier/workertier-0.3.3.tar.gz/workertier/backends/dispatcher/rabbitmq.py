#coding:utf-8
import random
import logging

import gevent
from gevent.coros import Semaphore

from haigha.connection import Connection as HaighaConnection
from haigha.exceptions import ChannelClosed
from haigha.message import Message

from workertier.backends.dispatcher import Dispatcher


logger = logging.getLogger(__name__)


#TODO: Understand and catch where exceptions can pop up


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
        self._start_connection_loop()

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

    def _connection_loop(self):
    # The message pump needs to run for the connection to actually do something.
        while not self.broken:
            try:
                self._connection.read_frames()  # Pump
                gevent.sleep()  # Yield to other greenlets so they don't starve
            except (ChannelClosed,):
                # If the connection loop breaks, then we should stop using this connection!
                self.broken = True #TODO
                self.log_exception("Connection loop has died")

    def _start_connection_loop(self):
        self.log_debug("Starting connection loop")
        gevent.spawn(self._connection_loop)  # Power our connection

    def publish(self, key):
        # This expects that the channel is already open.
        msg = Message(key)
        self._channel.basic.publish(msg, "", self.queue)

    def dispatch(self, key):
        self._ensure_open()
        self.publish(key)

    def consume(self, consumer):
        # Start consuming messages from the queue (they will be passed to `consumer`)
        self._ensure_open()
        def cb():
            self.log_debug("Registered as consumer")
        def consumer_wrapper(message):
            self.log_debug("Received a message: %s", message.body)
            consumer(message)
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
                logger.debug("Reusing existing connection: {0}".format(connection.conn_id))
                break
        else:
            connection = Connection(self.host, self.port, self.virtualhost, self.user, self.password, self.queue)
            connection.lock.acquire(blocking=False)
            self._pool.append(connection)
            logger.debug("Creating new connection: {0}".format(connection.conn_id))

        # Clean up 10% of the time
        if random.random() < 0.1:
            logger.debug("Cleaning up broken connections")
            self._pool = [connection for connection in self._pool if not connection.broken]

        return connection

    def dispatch(self, key):
        logger.debug("Dispatching new message: '%s'", key)
        connection = self._acquire_connection()
        connection.dispatch(key)
        connection.lock.release()

    def start_consumer(self, message_consumer):
        # Every time this method is called, we start a new consumer
        logger.debug("Starting new consumer")
        connection = self._acquire_connection()
        connection.consume(message_consumer)
        # Don't release the connection here.
