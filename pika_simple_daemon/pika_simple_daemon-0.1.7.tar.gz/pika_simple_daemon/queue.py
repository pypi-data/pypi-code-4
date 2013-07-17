from pika.adapters import BlockingConnection
from pika import BasicProperties, ConnectionParameters
import json
import datetime
from time import sleep
from logging import getLogger
from pika.exceptions import AMQPChannelError

class Queue(object):
    """
    A class for performing both sends and receives on a RabbitMQ server,
    using the pika library.
    """

    def __init__(self):
        self.declared_channels = []
        self.logger = getLogger(__name__)


    def set_logger(self, logger):
        self.logger = logger


    def declare_exchange(self, exchange_name, queue_options,  exchange_type="topic"):
        try:
            self.channel.exchange_declare(exchange=exchange_name, type=exchange_type, **queue_options)
        except AMQPChannelError:
            pass


    def bind_queue(self, exchange, queue_name, routing_key=None):
        kwargs = dict(
            exchange=exchange, queue=queue_name
        )
        if routing_key is not None:
            kwargs['routing_key'] = routing_key

        bind = self.channel.queue_bind(**kwargs)

    def connect(self, connection_params):
        """
        Performs the actual connection to the RabbitMQ server.

        :param connection_params: The connection parameters. See pika.ConnectionParameters for available properties
        :type connection_params: dict
        """
        connect_params_obj = ConnectionParameters(**connection_params)
        self.connection = BlockingConnection(connect_params_obj)
        self.channel = self.connection.channel()


    def declare_queue(self, queue_name=None, queue_options={}):
        """
        Declares a queue on the server. A list of declared is kept so we do not
        redeclare an existing queue.

        :param queue: Name of the queue to declare
        :type queue: string
        :param queue_options: Options for the queue, for details see pika.spec.DriverMixin.queue_declare
        :type queue_options: dict
        """

        queue_params = queue_options.copy()

        if queue_name not in self.declared_channels:
            if queue_name is not None:
                queue_params['queue'] = queue_name
            queue = self.channel.queue_declare(**queue_params)

            if queue_name is None:
                queue_name = queue.method.queue

            self.declared_channels.append(queue_name)
        return queue_name

    def disconnect(self):
        """
        Drop the connection to the RabbitMQ server
        """
        self.connection.close()

    def send(self, exchange_name, routing_key, body, exchange_type="topic"):
        """
        Put a message into the specified queue

        :param exchange_name: The name of the exchange to use
        :type exchange_name: str
        :param routing_key: The routing key to be used for this message
        :type routing_key: str
        :param body: The actual message body
        :type body: str
        :param exchange_type: Which type of exchange to use
        :type body: str
        """

        if not isinstance(body, str):
            body = json.dumps(body)

        try:
            self.channel
        except NameError:
            self.logger.error("You must connect first!")

        self.channel.basic_publish(exchange=exchange_name,
                                   routing_key=routing_key,
                                   body=body,
                                   properties=BasicProperties(content_type="text/plain", delivery_mode=2)
        )

        self.logger.info( "Message sent!")

    def receive(self, queue_name, callback, timeout=None, limit=None, finish_on_empty=True, finished_callback=None,
                exchange_name='', exchange_type="topic", routing_key="#", queue_options={}):
        """
        Receive messages from a given queue, and pass them to a callback function. This method will keep returning
        messages until one of the named break conditions is reached:

        * timeout: Stop receiving messages after x seconds
        * limit: Stop receiving messages after x messages have been consumed
        * finish_on_empty: If true, stop receiving messages when the queue is empty

        An optional finished callback can be called when the break condition has been reached.


        :param queue_name: The name of the queue to receive messages from
        :type queue_name: str
        :param callback: The callback to pass each message to
        :type callback: Callable
        :param timeout: The number of seconds before we stop receiving
        :type timeout: int
        :param limit: The number of messages received before we stop receiving
        :type limit: int
        :param finish_on_empty: Whether to finish when the queue is empty
        :type finish_on_empty: bool
        :param finished_callback: What to call when when we have finished receiving messages
        :type finished_callback: Callable
        :param queue_options: Options for the queue, for details see pika.spec.DriverMixin.queue_declare
        :type queue_options: dict
        """
        self.callback = callback
        self.timeout = timeout

        self.count = 0
        self.limit = limit
        self.finish_on_empty = finish_on_empty

        if timeout is not None:
            self.end_time = datetime.datetime.now() + datetime.timedelta(seconds=timeout)
        else:
            self.end_time = None

        keep_reading = True

        try:
            self.channel
        except NameError:
            self.logger.error( "You must connect first!")

        queue_name = self.declare_queue(queue_name, queue_options)

        if exchange_name:
            self.declare_exchange(exchange_type=exchange_type, exchange_name=exchange_name, queue_options=queue_options)
            self.bind_queue(exchange_name, queue_name, routing_key=routing_key)

        TIME_FORMAT = "%y-%m-%d %H:%M:%S"

        while keep_reading:

            if self.end_time is not None:
                now = datetime.datetime.now()
                if now > self.end_time:
                    keep_reading = False
                    self.logger.debug( "Past timeout, leaving!")
                else:
                    self.logger.debug( "{0} is before {1}, as you were".format(
                        now.strftime(TIME_FORMAT), self.end_time.strftime(TIME_FORMAT))
                    )

            if self.limit is not None:


                if self.count >= self.limit:
                    keep_reading = False
                    self.logger.debug( "Reached message limit of {0}, leaving!".format(self.limit))
                else:
                    self.logger.debug( "{0} is less than {1}, as you were".format(self.count, self.limit))

            method, header_frame, body = self.channel.basic_get(queue=queue_name)

            # Pika changed the API for this. For Basic.GetEmpty
            # they now return None, None, None
            if method is None and header_frame is None and body is None:
                if self.finish_on_empty is True:
                    keep_reading = False
                    self.logger.debug("Queue empty, leaving!")
                else:
                    sleep(1)
                continue

            else:
                self.count += 1
                self.logger.debug( "Queue not empty, as you were")


            kwargs = dict(
                routing_key=method.routing_key,
                exchange=method.exchange
            )
            try:
                callback(json.loads(body), **kwargs)
            except Exception, e:
                self.channel.basic_reject(delivery_tag=method.delivery_tag, requeue=True)
                self.logger.critical(e)
                raise e

            self.logger.debug("Acknowledging message {0}".format( method.delivery_tag))
            self.channel.basic_ack(delivery_tag=method.delivery_tag)

        if finished_callback is not None:
            finished_callback()


    @staticmethod
    def print_body(body, routing_key, exchange):
        """
        A basic callable that can be used to print out each message received


        :param body: The body of the message received
        :type body: str
        :param routing_key: The routing key of the received message
        :type routing_key: str
        :param exchange:  The exchange of the received message
        :type exchange: str
        """
        print "Printing body callback:"
        print "%s" % body
        print routing_key
