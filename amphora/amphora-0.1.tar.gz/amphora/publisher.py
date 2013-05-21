# -*- coding: utf-8 -*-
import logging
import socket
from collections import deque

import amqp.exceptions
import gevent
from gevent.queue import Queue, Empty

from base import FailsafeAmqpPreferences, StaticHandlerChain, safe_repr


class FailsafeAmqpPublisher(FailsafeAmqpPreferences):
    def __init__(self, iteration_timeout=0.5, **kwargs):
        super(FailsafeAmqpPublisher, self).__init__(**kwargs)
        self.iteration_timeout = iteration_timeout

        self.logger = logging.getLogger('amphora.FailsafeAmqpPublisher')
        self.running = False
        self.connection = None
        self.channel = None

        self.before_connect_handlers = StaticHandlerChain(self)
        self.before_start_cycle = StaticHandlerChain(self)
        self.after_cycle_finish = StaticHandlerChain(self)
        self.before_stop = StaticHandlerChain(self)
        self.before_connect_handlers.add_handler(self.init_connection)

        # List of tuples
        # (queue::basestring, exchange::basestring, routing_key::basestring)
        self.__new_queue_request = deque()

        # List of str
        self.__delete_queue_request = deque()

        # List of tuples
        # (queue::basestring, exchange::basestring, routing_key::basestring)
        self.__unbind_queue_request = deque()

        # Set of tuples
        # (queue::basestring, exhcange::basestring, routing_key::basestring)
        self.__bound_routes = set()

        # List of tuples
        # (message::amqp.Message, exchange::basestring,
        #  routing_key::basestring)
        self.__outgoing_messages = Queue()

        # List of tuples
        # (exchange::basestring, type::basestring)
        self.__declare_exchange_request = deque()

        # Set of basestrings
        self.__declared_exchanges = set()

    def serve(self):
        network_exceptions = (
            EnvironmentError, socket.error, amqp.exceptions.ConnectionForced,
            amqp.exceptions.IrrecoverableConnectionError)
        self.running = True

        while self.running:
            self.connection = None
            try:
                self.before_connect_handlers()
                self.logger.debug("Initializing connection")
            except network_exceptions as e:
                self.logger.debug("Got exception %s when initialized, "
                                  "retry initialize", e)
                gevent.sleep(0.2)
            else:
                try:
                    self.before_start_cycle()
                    self.logger.debug("Starting publisher cycle")
                    return self.cycle()
                except network_exceptions:
                    continue
                finally:
                    self.after_cycle_finish()

    def new_exchange(self, exchange, type_):
        self.__declare_exchange_request.append((exchange, type_))

    def stop(self):
        self.before_stop()
        self.running = False

    def new_queue(self, queue, exchange, routing_key=''):
        self.__new_queue_request.append((queue, exchange, routing_key))

    def delete_queue(self, queue):
        self.__delete_queue_request.append(queue)

    def unbind_queue(self, queue, exchange, routing_key=''):
        self.__unbind_queue_request.append((queue, exchange, routing_key))

    def publish_message(self, message, exchange, routing_key=''):
        self.__outgoing_messages.put((message, exchange, routing_key))

    def init_connection(self, publisher):
        self.connection = c = self.make_amqp_connection()
        self.channel = c.channel()

    def cycle(self):
        while self.running:
            self._iteration()

    def _iteration(self):
        if self._unbind_routing_key():
            return
        if self._delete_queue():
            return
        if self._declare_new_exchange():
            return
        if self._declare_new_queue():
            return
        self._publish_messages()

    def _unbind_routing_key(self):
        try:
            queue, exchange, rk = pack = self.__unbind_queue_request.popleft()
        except LookupError:
            return False

        if pack not in self.__bound_routes:
            self.logger.warning("Bundle %s [%s] %s is already unbound!",
                                exchange, rk, queue)
            return True

        try:
            self.channel.queue_unbind(queue, exchange, rk)
        except amqp.exceptions.NotFound:
            self.logger.warning("Queue %s not found (%s)", queue, exchange)
        self.__bound_routes.remove(pack)
        self.logger.debug("Unbound: %s [%s] %s", exchange, rk, queue)
        return True

    def _delete_queue(self):
        try:
            queue = self.__delete_queue_request.popleft()
        except LookupError:
            return False

        for new_queue_pack in self.__new_queue_request:
            if new_queue_pack[0] == queue:
                self.__new_queue_request.remove(new_queue_pack)
                self.logger.debug(
                    "Deleting new queue request %s ---[%s]--> %s because "
                    "this queue is requested for deletion",
                    new_queue_pack[0], new_queue_pack[2], new_queue_pack[1])

        for unbind_pack in self.__unbind_queue_request:
            if unbind_pack[0] == queue:
                self.__unbind_queue_request.remove(unbind_pack)
                self.logger.debug(
                    "Deleting unbind request %s [%s] %s because "
                    "this queue is requested for deletion",
                    unbind_pack[0], unbind_pack[2], unbind_pack[1])

        ch = self.channel
        try:
            ch.queue_delete(queue)
        except amqp.exceptions.NotFound:
            self.logger.warning("Can't delete queue %s: not found", queue)
        else:
            self.logger.debug("Queue %s deleted", queue)
        return True

    def _declare_new_exchange(self):
        try:
            exchange, type_ = self.__declare_exchange_request.popleft()
        except LookupError:
            return False

        ch = self.channel
        ch.exchange_declare(
            exchange, type_, auto_delete=False, durable=True)
        self.__declared_exchanges.add(exchange)
        self.logger.debug("Declared exchange %s (%s)", exchange, type_)

    def _declare_new_queue(self):
        try:
            queue, exchange, rk = pack = self.__new_queue_request.popleft()
        except LookupError:
            return False

        if pack in self.__bound_routes:
            self.logger.warning("Bundle %s [%s] %s is already bound!",
                                exchange, rk, queue)
            return True

        ch = self.channel
        ch.queue_declare(queue, auto_delete=False, durable=True)
        ch.queue_bind(queue, exchange=exchange, routing_key=rk)
        self.__bound_routes.add(pack)
        self.logger.debug("Declared queue %s --[%s]--> %s",
                          exchange, rk, queue)
        return True

    def _publish_messages(self):
        ch = self.channel

        message_bulk = deque()
        try:
            while True:
                message_bulk.append(self.__outgoing_messages.get(
                    block=not message_bulk,
                    timeout=self.iteration_timeout))
        except Empty:
            pass

        if not message_bulk:
            return False

        ch.tx_select()
        send_later = deque()
        try:
            for message_pack in message_bulk:
                message, exchange, rk = message_pack

                # If routing key creation queued then defer sending message
                defer_sending = False
                for _, queued_exchange, queued_rk in self.__new_queue_request:
                    if queued_exchange == exchange and queued_rk == rk:
                        defer_sending = True
                        break

                if defer_sending:
                    if self.logger.isEnabledFor(logging.DEBUG):
                        self.logger.debug(
                            "Routing key %s is not declared. "
                            "Resend %s later (%s)",
                            rk, safe_repr(message.body), exchange)
                    send_later.append(message_pack)
                else:
                    ch.basic_publish(message, exchange=exchange,
                                     routing_key=rk or '')
                    if self.logger.isEnabledFor(logging.DEBUG):
                        self.logger.debug(
                            "Published message %s into %s[%s]",
                            safe_repr(message.body), exchange, rk)
            ch.tx_commit()
            gevent.sleep(0)
        except:
            for message_pack in message_bulk:
                self.__outgoing_messages.put(message_pack)
            raise
        else:
            for message_pack in send_later:
                self.__outgoing_messages.put(message_pack)
