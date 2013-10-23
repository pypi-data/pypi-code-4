#coding: utf-8
import cjson, types, copy, pika
from wae.config import config
import socket, time, uuid

def connect_mq(callback=None):
    "连接到MQ"
    cred = pika.PlainCredentials(config.get('mq', 'user'), config.get('mq', 'password'))
    params = pika.ConnectionParameters(
                host = config.get('mq', 'host', 'localhost'),
                port = config.getint('mq', 'port'),
                virtual_host = config.get('mq', 'vhost'),
                credentials = cred
    )
    if callback!=None:
        mqconn=pika.AsyncoreConnection(parameters=params, on_open_callback=callback)
    else:
        mqconn=pika.BlockingConnection(params)
    return mqconn


class SignalPublisher(object):
    "信号发射器"
    def __init__(self, **kwargs):
        self._signals = {}
        self._extra_data = kwargs

    def add(self, signal, *args):
        "添加信号"
        lst = []
        for a in args:
            if type(a) in (types.ListType, types.TupleType):
                lst += list(a)
            else:
                lst.append(a)

        if signal in self._signals:
            for a in lst:
                if not a in self._signals[signal]:
                    self._signals[signal].append(a)
        else:
            self._signals[signal] = lst

    def drop(self, signal):
        "删除消息"
        if signal in self._signals:
            del self._signals[signal]

    def reset(self):
        "清除消息"
        self._signals = {}

    def connect():
        "阻塞连接MQ"
        cred = pika.PlainCredentials(config.get('mq', 'user'), config.get('mq', 'password'))
        params = pika.ConnectionParameters(
                host = config.get('mq', 'host', 'localhost'),
                port = config.getint('mq', 'port'),
                virtual_host = config.get('mq', 'vhost'),
                credentials = cred
                )
        mqconn=pika.BlockingConnection(params)
        return mqconn

    def publish(self):
        if len(self._signals)>0:
            exchange = config.get('mq', 'exchange')
            queue = config.get('mq', 'queue')

            mqconn = connect_mq()

            cnt = 1
            try:
                channel = mqconn.channel()
            except socket.error:
                channel = None
                cnt += 1
                if cnt>5:
                    raise
                else:
                    time.sleep(0.1) 
            assert channel!=None

            channel.exchange_declare(exchange=exchange, type='direct')
            channel.queue_declare(queue=queue, durable=True, exclusive=False, auto_delete=False)
            channel.queue_bind(exchange=exchange, queue=queue)

            content = copy.copy(self._extra_data)
            content["token"] = str(uuid.uuid1())
            content["signals"] = self._signals.items()
            channel.basic_publish(exchange=exchange, routing_key='', body=cjson.encode(content), properties=pika.BasicProperties(content_type='application/json', delivery_mode=1))

            #for sig, args in self._signals.items():
            #    a = {'signal':sig, 'args':args, 'token':token}
            #    if len(self._extra_data)>0: a.update(self._extra_data)
            #    channel.basic_publish(exchange=exchange, routing_key='', body=cjson.encode(a), properties=pika.BasicProperties(content_type='application/json', delivery_mode=1))

            mqconn.close()
            self.reset()


class SignalHandler(object):
    "信号处理器"

    def on_connected(self, connection):
        connection.channel(self.on_channel_open)

    def on_channel_open(self, channel):
        self.channel = channel
        queue = config.get('mq', 'queue')
        exchange = config.get('mq', 'exchange')

        channel.exchange_declare(exchange=exchange, type='direct')
        channel.queue_declare(queue=queue, durable=True, exclusive=False, auto_delete=False, callback=self.on_queue_declared)

    def on_queue_declared(self, frame):
        queue = config.get('mq', 'queue')
        exchange = config.get('mq', 'exchange')
        self.channel.queue_bind(queue=queue, exchange=exchange)
        self.channel.basic_consume(self._callback, queue=queue)

    def close(self):
        self.mqconn.close()
        self.mqconn = self.channel = None

    def _callback(self, ch, method, props, body):
        if body=='quit':
            tag = method.consumer_tag
            ch.basic_cancel(tag)
            ch.basic_ack(delivery_tag=method.delivery_tag)
            self.close()
        else:
            data = cjson.decode(body)

            token = data['token']
            signals = data['signals']   # [(signal, args)]
            extra_data = dict((k,v) for k,v in data.items() if k not in ('signals', 'token'))

            try:
                self.handle(token, signals, **extra_data)
                ch.basic_ack(delivery_tag=method.delivery_tag)
            except:
                raise

    def handle(self, token, signals, **kwargs):
        "处理信号"
        raise NotImplementedError

    def listen(self):
        "启动监听服务"
        self.mqconn = connect_mq(self.on_connected)
        try:
            self.mqconn.ioloop.start()
        except KeyboardInterrupt:
            self.mqconn.close()
            self.mqconn.ioloop.start()

