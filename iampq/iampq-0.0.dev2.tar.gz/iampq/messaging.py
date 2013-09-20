from tornado import gen
from itertools import count
import simplejson as json
import pika
from .entities import Exchange

class BrockerEntityMixin(object):

    channel = None
    channel_num = None

    def __init__(self, *args, **kwargs):
        if self.channel:
            self.channel_num = self.channel.channel_number
            self.connection.add_subscriber(self)

    @gen.coroutine
    def on_reconnect(self):
        r"""In case reconnect, brockers bound to this connection
        must be revived."""
        if not self.channel_num:
            return
        else:
            self.channel = yield self.connection.create_channel(self.channel_num)
        self.revive(self.channel)

    @property
    def connection(self):
        return self.channel.connection

class Consumer(BrockerEntityMixin):

    queues = None
    
    #: Flag for message acknowledgment disabled/enabled.
    #: Enabled by default.
    no_ack = None

    auto_declare = True   # don't use it

    # List of callbacks called in order when a message is received.
    callbacks = None

    # Optional function called whenever a message is received.
    on_message = None

    #: Callback called when a message can't be decoded.
    on_decode_error = None

    _next_tag = count(1).next     # simple counter

    late_ack = False

    def __init__(self, channel, queues=None, no_ack=None, auto_declare=None,
            callbacks=None, on_decode_error=None, on_message=None,):

        self.channel = channel
        self.queues = self.queues or [] if queues is None else queues
        self.no_ack = self.no_ack if no_ack is None else no_ack
        self.callbacks = (self.callbacks or [] if callbacks is None
                          else callbacks)
        self.on_message = on_message
        if auto_declare is not None:
            self.auto_declare = auto_declare
        if on_decode_error is not None:
            self.on_decode_error = on_decode_error
        self._active_tags = dict()  # currently consumed queues
        self.revive(self.channel)
        if self.auto_declare:
            self.declare()
        super(Consumer, self).__init__()

    def revive(self, channel):
        self.queues = [queue(channel)
                       for queue in self.queues]
        for queue in self.queues:
            queue.revive(self.channel)

    @gen.coroutine
    def declare(self, nowait=False, passive=False):
        """Declare queues, exchanges and bindings.

        This is done automatically at instantiation if :attr:`auto_declare`
        is set.

        """
        for queue in self.queues:
            yield (queue.declare(nowait=nowait, passive=passive))
            yield queue.exchange.declare(nowait=nowait, passive=passive)
            yield (queue.bind(nowait=nowait))

    def register_callback(self, callback):
        self.callbacks.append(callback)

    @gen.coroutine
    def add_queue(self, queue):
        queue = queue(self.channel)
        if self.queue_declare:
            yield (queue.declare())
        self.queues.append(queue)
        raise gen.Return(queue)

    def consume(self, no_ack=False):
        r"""Start consuming from queuees"""
        for queue in self.queues:
            self._basic_consume(queue, no_ack=no_ack, nowait=True)

    def _basic_consume(self, queue, consumer_tag=None,
            no_ack=no_ack, nowait=True):
        tag = self._active_tags.get(queue.name)
        if tag is None:
            tag = self._add_tag(queue, consumer_tag)
            queue.consume(tag, callback=self.handle_new_message,
                no_ack=no_ack, nowait=nowait)

        return tag


    def _add_tag(self, queue, consumer_tag=None):
        tag = consumer_tag or str(self._next_tag())
        self._active_tags[queue.name] = tag
        return tag

    def receive(self, msg, delivery_tag):
        """Method called when a message is received.

        This dispatches to the registered :attr:`callbacks`."""
        if not self.callbacks:
            raise NotImplementedError('Consumer does not have any callbacks')
        [callback(self, msg, delivery_tag) for callback in self.callbacks]
        if not self.late_ack:
            self.ack(delivery_tag)

    def handle_new_message(self, _channel, meth_frame, header_frame, body):
        r"""Handles new incoming message"""
        delivery_tag = meth_frame.delivery_tag
        try:
            message = self.decode_message(body)
        except Exception, exc:
            if not self.on_decode_error:
                raise exc
            self.on_decode_error(body, exc)
            self.nack(delivery_tag=delivery_tag, multiple=True)
        else:
            return self.on_message(self, message, delivery_tag) if self.on_message \
                else self.receive(message, delivery_tag)

    def decode_message(self, raw):
        return json.loads(raw)

    def ack(self, delivery_tag):
        self.channel.basic_ack(delivery_tag)

    def nack(self, delivery_tag, multiple=False, requeue=False):
        self.channel.basic_nack(delivery_tag=delivery_tag,
            multiple=multiple, requeue=requeue)

    def qos(self, prefetch_size=0, prefetch_count=0, all_channels=False):
        """Specify quality of service.

        The client can request that messages should be sent in
        advance so that when the client finishes processing a message,
        the following message is already held locally, rather than needing
        to be sent down the channel. Prefetching gives a performance
        improvement."""
        return self.channel.basic_qos(prefetch_size,
                                      prefetch_count,
                                      all_channels)


class Publisher(BrockerEntityMixin):
    r"""Message producer"""

    exchange = None
    routing_key = ''
    auto_declare = True

    def __init__(self, channel, exchange=None, routing_key=None,
            auto_declare=None):
        self.channel = channel
        self.exchange = exchange
        self.routing_key = routing_key or self.routing_key
        if self.exchange is None:
            self.exchange = Exchange('')
        if self.channel:
            self.revive(self.channel)
        if auto_declare is not None:
            self.auto_declare = auto_declare
            if self.auto_declare:
                self.declare()
        super(Publisher, self).__init__()

    @gen.coroutine
    def declare(self):
        if self.exchange.name:
            yield (self.exchange.declare())

    def revive(self, channel):
        self.exchange = self.exchange(channel)
        self.exchange.revive(channel)

    def publish(self, body, routing_key=None, delivery_mode=None,
            priority=0, content_type='application/json',
            content_encoding=None, headers=None, exchange=None,):
        headers = dict() if headers is None else headers
        routing_key = self.routing_key if routing_key is None else routing_key
        exchange = exchange or self.exchange
        if isinstance(exchange, Exchange):
            delivery_mode = delivery_mode or exchange.delivery_mode
            exchange = exchange.name
        else:
            delivery_mode = delivery_mode or self.exchange.delivery_mode
        properties = pika.BasicProperties(
            delivery_mode=delivery_mode,
            content_type=content_type,
            content_encoding=content_encoding,
            headers=headers)
        message = self._prepare_msg(body)
        self.channel.basic_publish(
            exchange=exchange,
            routing_key=routing_key,
            body=message,
            properties=properties)

    def _prepare_msg(self, body):
        return json.dumps(body)

