from tornado import gen, ioloop
from iampq import GameAMQPConnection, Exchange, Publisher, Consumer, Queue
import logging
import datetime
log = logging.getLogger()
logging.getLogger().setLevel(logging.WARNING)


def on_message(consumer, msg, delivery_tag):
    print msg, delivery_tag, 'accepted'

@gen.coroutine
def makeconn():
    conn = GameAMQPConnection(ioloop=ioloop.IOLoop.current())
    log.warning("AMPQ Connection established")
    publisher = yield launch_publisher(conn)
    log.warning('PUBLISHER launched%s' % (publisher,))
    consumer = yield launch_consumer(conn)
    log.warning('CONSUMER launched %s' % (consumer,))
    body = {
        'name': 'testmessage',
        'desc': 'hi'
    }
    conn.ioloop.add_timeout(datetime.timedelta(seconds=2), consumer.consume)
    publisher.publish(body=body, routing_key='test-queue', serializer='json')

@gen.coroutine
def launch_publisher(conn):
    with (yield conn.ensure()):
        channel = yield conn.create_channel(hash('gamepublisher') % 1000)
        exchange = Exchange(name='test', type='direct')
        publisher = Publisher(channel=channel,
            exchange=exchange, routing_key='test-queue')
        yield publisher.declare()
    raise gen.Return(publisher)

@gen.coroutine
def launch_consumer(conn):
    with (yield conn.ensure()):
        channel = yield conn.create_channel(hash('gameconsumer') % 1000)
        exchange = Exchange(name='test', type='direct')
        queue = Queue('test-queue', exchange=exchange, routing_key='test-queue')
        consumer = Consumer(channel=channel,
            queues=[queue], callbacks=[on_message])
        yield consumer.declare()
    raise gen.Return(consumer)

if __name__=='__main__':
    ioloop.IOLoop.current().run_sync(makeconn)
    ioloop.IOLoop.instance().start()
