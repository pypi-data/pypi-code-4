from tornado import gen
import pika
from pika.credentials import PlainCredentials
from pika import adapters
import yieldpoints
import functools
import datetime
import contextlib
import logging
log = logging.getLogger()
logging.getLogger().setLevel(logging.DEBUG)

class GameAMQPConnection(adapters.TornadoConnection):

    connection_attempts = 5
    
    retry_delay = 5

    default_channel = None

    subscribers = set() # contains :entity. instances

    channels = dict() # channels that are not default

    def __init__(self, vhost='/', username='guest', password='guest',
            host='127.0.0.1', port=5672, **kwargs):
        conn_attempts = kwargs.get('connection_attempts', None) or self.connection_attempts
        retry_delay = kwargs.get('retry_delay', None) or self.retry_delay
        credentials = PlainCredentials(
            username=username,
            password=password)
        params = pika.ConnectionParameters(
            host=host,
            port=port,
            virtual_host='/',
            credentials=credentials,
            retry_delay=retry_delay,
            connection_attempts=conn_attempts)
        super(GameAMQPConnection, self).__init__(
            parameters=params,
            on_open_callback=self.conn_established,
            on_close_callback=self.conn_closed,
            on_open_error_callback=self.conn_impossible,
        )

    @gen.coroutine
    def ensure_connection(self):
        if self.is_open:
            raise gen.Return('ok')
        cb = yield gen.Callback('key')
        self.ioloop.add_timeout(datetime.timedelta(seconds=1),
            functools.partial(self._ensure, cb))
        res = yield gen.Wait('key')
        raise gen.Return(res)

    def _ensure(self, callback=None):
        if not self.is_open:
            self.ioloop.add_timeout(datetime.timedelta(seconds=1),
                functools.partial(self._ensure, callback))
        else:
            callback('ok')

    @gen.coroutine
    def ensure(self):
        """Returns context manager than ensures connection to amqp.
            
            Example:
            --------
               with (yield conn.ensure()):
                   # your target staff starts here
        """

        res = yield self.ensure_connection()

        @contextlib.contextmanager
        def f(msg):
            try:
                yield msg
            finally:
                pass

        raise gen.Return(f(res))

    @gen.coroutine
    def connect(self):
        KEYS = ['key']
        cb = yield gen.Callback(KEYS[0])

        self.ioloop.add_timeout(
            datetime.timedelta(seconds=1),
            functools.partial(self.tail_connection, cb))
        super(GameAMQPConnection, self).connect()
        try:
            key, result = yield yieldpoints.WithTimeout(
                deadline=datetime.timedelta(
                    seconds=self.connection_attempts * self.retry_delay * 2),
                yield_point=yieldpoints.WaitAny(KEYS),
                io_loop=self.ioloop)
            log.debug('AMQP CONNECTION ESTABLISHED')
        except yieldpoints.TimeoutException:
            log.error('Timeout Error. Connection could not be established')
            raise gen.Return("Timeout exception")
            
    @gen.coroutine
    def tail_connection(self, callback):
        try:
            if not self.is_open:
                self.ioloop.add_timeout(
                    datetime.timedelta(seconds=1),
                    functools.partial(self.tail_connection, callback))
            else:
                callback('ok')
        except Exception, e:
            print str(e.message)

    @gen.coroutine
    def create_channel(self, channel_number):
        r"""Creates new channel defined by `channel_number`."""
        cb = yield gen.Callback('key')
        self.channel(on_open_callback=cb, channel_number=channel_number)
        new_channel = yield gen.Wait('key')
        self.channels[channel_number] = new_channel
        raise gen.Return(new_channel)

    def conn_established(self, conn):
        r"""After conn established creates new channel."""

        def on_ok(channel):
            self.default_channel = channel
            self.when_bound()

        self.channel(on_ok, 1)

    def conn_impossible(self, conn):
        log.warning("AMQP CONNECTION FAILED.")

    def conn_closed(self, conn, code, text):
        log.error('AMQP CONNECITON CLOSED: %s' % (text,))

    def when_bound(self):
        r"""Notifies subscribers that channel is bound"""
        for sub in self.subscribers:
            if hasattr(sub, 'on_reconnect'):
                fun = getattr(sub, 'on_reconnect')
                fun()

    def add_subscriber(self, subscr):
        self.subscribers.add(subscr)