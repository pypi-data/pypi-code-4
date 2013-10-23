from .base import CloneableObject, ChannelBasedEntity
import conf
from .utils import gen_queue_name
from tornado import gen

class Exchange(CloneableObject, ChannelBasedEntity):
    name = ''
    type = 'direct'
    durable = True
    auto_delete = False
    delivery_mode = conf.PERSISTENT_DELIVERY_MODE

    attrs = (
        ('name', None),
        ('type', None),
        ('durable', bool),
        ('auto_delete', bool),
        ('delivery_mode', None),
    )

    def __init__(self, name='', type='', channel=None, **kwargs):
        super(Exchange, self).__init__(**kwargs)
        self.name = name or self.name
        self.type = type or self.type
        self.maybe_bind(channel)
        
    def __hash__(self):
        return hash('E|%s' % (self.name, ))

    @gen.coroutine
    def declare(self, nowait=False, passive=False):
        """Creates the exchange on the broker.

        :keyword nowait: If set the server will not respond, and a
            response will not be waited for. Default is :const:`False`."""
        
        _frame_ok = yield gen.Task(
            self.channel.exchange_declare,
            exchange=self.name, durable=self.durable,
            auto_delete=self.auto_delete, type=self.type,
            nowait=nowait, passive=passive,)
        raise gen.Return(_frame_ok)


    def delete(self, if_unused=False, nowait=False, callback=None):
        self.channel.exchange_delete(
            callback=callback,
            exchange=self.name,
            if_unused=if_unused,
            nowait=nowait)

    def when_bound(self):
        pass


class Queue(CloneableObject, ChannelBasedEntity):

    name = ''
    exchange = Exchange('')
    routing_key= ''

    durable = True
    exclusive = False
    auto_delete = False
    no_ack = False

    attrs = (
        ('name', None),
        ('exchange', None),
        ('routing_key', None),
        ('durable', bool),
        ('exclusive', bool),
        ('auto_delete', bool),
        ('no_ack', None),
        ('alias', None),)

    def __init__(self, name='', exchange=None, routing_key='',
            channel=None, **kwargs):
        super(Queue, self).__init__(**kwargs)
        self.name = name or self.name
        self.exchange = exchange or self.exchange
        self.routing_key = routing_key or self.routing_key

        # exclusive implies auto-delete
        if self.exclusive:
            self.auto_delete = True
        self.maybe_bind(channel)

    def __hash__(self):
        return hash('Q|%s' % (self.name, ))

    def when_bound(self):
        """Rebound queue exchange"""
        if self.exchange:
            self.exchange = self.exchange(self.channel)

    @gen.coroutine
    def declare(self, nowait=False, passive=False):
        """Declare queue on the server.

        :keyword nowait: Do not wait for a reply.
        :keyword passive: If set, the server will not create the queue.
            The client can use this to check whether a queue exists
            without modifying the server state.

        """
        if not self.name:
            self.name = gen_queue_name()
        _frame_ok = yield gen.Task(self.channel.queue_declare,
            queue=self.name, durable=self.durable,
            exclusive=self.exclusive, auto_delete=self.auto_delete,
            nowait=nowait, passive=passive)
        raise gen.Return(_frame_ok)

    @gen.coroutine
    def bind(self, nowait=False):
        _frame_ok = yield self.bind_to(
            exchange_name=self.exchange.name,
            routing_key=self.routing_key,
            nowait=nowait)
        raise gen.Return(_frame_ok)
    
    @gen.coroutine
    def bind_to(self, exchange_name='', routing_key='', nowait=False):
        _frame_ok = yield gen.Task(self.channel.queue_bind,
            queue=self.name, exchange=exchange_name,
            routing_key=routing_key, nowait=nowait,)
        raise gen.Return(_frame_ok)

    def delete(self, if_unused=False, is_empty=False):
        self.channel.queue_delete(
            queue=self.name, if_unused=if_unused,
            is_empty=is_empty, nowait=True)

    def purge(self):
        self.channel.queue_purge(queue=self.name, nowait=True)

    def get(self, no_ack=None, callback=None):
        if no_ack is None:
            no_ack = self.no_ack
        self.channel.basic_get(callback=callback, queue=self.name,
            no_ack=no_ack)

    def consume(self, consumer_tag='', no_ack=None,
            callback=None, nowait=False):
        if no_ack is None:
            no_ack = self.no_ack
        self.channel.basic_consume(
            consumer_callback=callback, queue=self.name,
            no_ack=no_ack, exclusive=self.exclusive,
            consumer_tag=consumer_tag,)