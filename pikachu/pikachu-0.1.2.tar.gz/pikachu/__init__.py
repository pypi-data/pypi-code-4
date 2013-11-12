# -*- coding: utf-8 -*-
import simplejson as json
import logging
import pika
import uuid


logger = logging.getLogger(__name__)


class Subscriber(object):
    def __init__(self, exchange, queue, callback, durable=True):
        self.exchange = exchange
        self.callback = callback
        self.queue = queue
        self.queue_params = dict(durable=durable)

    def amqp_callback(self, channel, method, header, body):
        try:
            self.callback(json.loads(body))
            channel.basic_ack(delivery_tag=method.delivery_tag)
        except Exception:
            logger.exception('AMQP message callback error')


class Method(Subscriber):
    def amqp_callback(self, channel, method, header, body):
        try:
            result = self.callback(json.loads(body))
            channel.basic_publish(exchange='',
                routing_key=header.reply_to,
                properties=pika.BasicProperties(
                    correlation_id=header.correlation_id,
                    content_type='application/json',
                    content_encoding='utf-8',
                ),
                body=json.dumps(result))
            channel.basic_ack(delivery_tag=method.delivery_tag)
        except Exception:
            logger.exception('AMQP message callback error')


class AmqpMethod(object):
    def __init__(self, conn_string):
        self.connection = pika.BlockingConnection(pika.URLParameters(conn_string))
        self.channel = self.connection.channel()
        result = self.channel.queue_declare(exclusive=True)
        self.callback_queue = result.method.queue
        self.channel.basic_consume(self.on_response, queue=self.callback_queue)

    def on_response(self, ch, method, props, body):
        if self.corr_id == props.correlation_id:
            self.response = body

    def call(self, exchange, method, **kwargs):
        self.response = None
        self.corr_id = str(uuid.uuid4())
        self.channel.basic_publish(exchange=exchange,
            routing_key=method,
            properties=pika.BasicProperties(
                reply_to=self.callback_queue,
                correlation_id=self.corr_id,
            ),
            body=json.dumps(kwargs))

        while self.response is None:
            self.connection.process_data_events()

        return json.loads(self.response)


class Amqp(object):
    def __init__(self, subscribers=[], methods=[]):
        self.subscribers = subscribers
        self.methods = methods

    def start(self, conn_string):
        try:
            parameters = pika.URLParameters(conn_string)
            connection = pika.SelectConnection(parameters=parameters, on_open_callback=self.on_connected)
        except:
            logger.exception('AMQP open connection error')

        try:
            connection.ioloop.start()
        except KeyboardInterrupt:
            connection.close()
            connection.ioloop.start()

    def on_connected(self, connection):
        connection.channel(self.on_channel_open)

    def on_channel_open(self, channel):
        try:
            for subscriber in self.subscribers:
                channel.exchange_declare(exchange=subscriber.exchange, type='direct')
                channel.queue_declare(queue=subscriber.queue, durable=True, callback=lambda x: 1)

                channel.queue_bind(exchange=subscriber.exchange, queue=subscriber.queue, callback=lambda x: 1)
                channel.basic_consume(subscriber.amqp_callback, queue=subscriber.queue)

        except:
            logger.exception('AMQP open channel error')
