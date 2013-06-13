# -*- coding: utf-8 -*-
import logging
import socket
from collections import deque

import amqp.exceptions
import gevent
from gevent.event import Event
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
        self.before_connect_handlers.add_handler(self._init_connection)

        # List of tuples
        # (queue::basestring, exchange::basestring,
        #  routing_key::basestring, x_expires::int or None,
        #  event::Event or None)
        self.__new_queue_request = deque()

        # List of tuple
        # (queue::basestring, event::Event or None)
        self.__delete_queue_request = deque()

        # List of tuples
        # (queue::basestring, exchange::basestring,
        #  routing_key::basestring, event::Event or None)
        self.__unbind_queue_request = deque()

        # Set of tuples
        # (queue::basestring, exhcange::basestring, routing_key::basestring)
        self.__bound_routes = set()

        # List of tuples
        # (message::amqp.Message, exchange::basestring,
        #  routing_key::basestring, event::Event or None)
        self.__outgoing_messages = Queue()

        # List of tuples
        # (exchange::basestring, type::basestring, event::Event or None)
        self.__declare_exchange_request = deque()

        # Set of basestrings
        self.__declared_exchanges = set()

    def serve(self):
        network_exceptions = (
            EnvironmentError, socket.error, amqp.exceptions.ConnectionForced,
            amqp.exceptions.IrrecoverableConnectionError)
        self.running = True

        try:
            while self.running:
                self.connection = None
                try:
                    self.before_connect_handlers()
                    self.logger.debug("Initializing connection")
                except network_exceptions as e:
                    self.logger.debug("Got exception %r when initialized, "
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
        except:
            self.logger.exception("Exception in publisher %r", self)
            raise

    def new_exchange(self, exchange, type_, nowait=False):
        event = None if nowait else Event()
        self.__declare_exchange_request.append((exchange, type_, event))
        if event is not None:
            event.wait()

    def stop(self):
        self.before_stop()
        self.running = False

    def new_queue(self, queue, exchange, routing_key='',
                  x_expires=None, nowait=False):
        event = None if nowait else Event()
        self.__new_queue_request.append(
            (queue, exchange, routing_key, x_expires, event))
        if event is not None:
            event.wait()

    def delete_queue(self, queue, nowait=False):
        event = None if nowait else Event()
        self.__delete_queue_request.append((queue, event))
        if event is not None:
            event.wait()

    def unbind_queue(self, queue, exchange, routing_key='', nowait=False):
        event = None if nowait else Event()
        self.__unbind_queue_request.append(
            (queue, exchange, routing_key, event))
        if event is not None:
            event.wait()

    def publish_message(self, message, exchange, routing_key='', nowait=True):
        event = None if nowait else Event()
        self.__outgoing_messages.put((message, exchange, routing_key, event))
        if event is not None:
            event.wait()

    def _init_connection(self, publisher):
        self.connection = c = self.make_amqp_connection()
        self.channel = c.channel()
        self.channel.tx_select()

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
        self._declare_new_queues()
        self._publish_messages()

    def _unbind_routing_key(self):
        try:
            queue, exchange, rk, event \
                = pack = self.__unbind_queue_request.popleft()
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
        if event is not None:
            event.set()
        return True

    def _delete_queue(self):
        try:
            queue, event = self.__delete_queue_request.popleft()
        except LookupError:
            return False

        for new_queue_pack in self.__new_queue_request:
            if new_queue_pack[0] == queue:
                self.__new_queue_request.remove(new_queue_pack)
                self.logger.debug(
                    "Deleting new queue request %s ---[%s]--> %s because "
                    "this queue is requested for deletion",
                    new_queue_pack[0], new_queue_pack[2], new_queue_pack[1])
                pack_event = new_queue_pack[3]
                if pack_event is not None:
                    pack_event.set()

        for unbind_pack in self.__unbind_queue_request:
            if unbind_pack[0] == queue:
                self.__unbind_queue_request.remove(unbind_pack)
                self.logger.debug(
                    "Deleting unbind request %s [%s] %s because "
                    "this queue is requested for deletion",
                    unbind_pack[0], unbind_pack[2], unbind_pack[1])
                pack_event = unbind_pack[3]
                if pack_event is not None:
                    pack_event.set()

        ch = self.channel
        try:
            ch.queue_delete(queue)
        except amqp.exceptions.NotFound:
            self.logger.warning("Can't delete queue %s: not found", queue)
        else:
            self.logger.debug("Queue %s deleted", queue)
        if event is not None:
            event.set()
        return True

    def _declare_new_exchange(self):
        try:
            exchange, type_, event = self.__declare_exchange_request.popleft()
        except LookupError:
            return False

        ch = self.channel
        ch.exchange_declare(
            exchange, type_, auto_delete=False, durable=True)
        self.__declared_exchanges.add(exchange)
        self.logger.debug("Declared exchange %s (%s)", exchange, type_)
        if event is not None:
            event.set()

    def _declare_new_queues(self):
        for _ in xrange(len(self.__new_queue_request)):
            pack = self.__new_queue_request[0]
            queue, exchange, rk, x_expires, event = pack

            if pack in self.__bound_routes:
                self.logger.warning("Bundle %s [%s] %s is already bound!",
                                    exchange, rk, queue)
            else:
                ch = self.channel
                arguments = {}
                if x_expires is not None:
                    arguments['x-expires'] = x_expires
                ch.queue_declare(queue, auto_delete=False, durable=True,
                                 arguments=arguments)
                ch.queue_bind(queue, exchange=exchange, routing_key=rk)
                self.__bound_routes.add(pack)
            self.__new_queue_request.popleft()
            self.logger.debug("Declared queue %s --[%s]--> %s",
                              exchange, rk, queue)
            if event is not None:
                event.set()

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

        send_later = deque()
        published_messages = deque()
        try:
            for message_pack in message_bulk:
                message, exchange, rk, _ = message_pack

                # If routing key creation queued then defer sending message
                defer_sending = False
                self.logger.debug("%s In queued to create: %s",
                                  self, len(self.__new_queue_request))
                self.logger.debug("%r %r", self, self.__new_queue_request)
                for _, queued_exchange, queued_rk, _, _ in self.__new_queue_request:
                    self.logger.debug(
                        "Message: %s[%s], queued to create: %s[%s]",
                        exchange, rk, queued_exchange, queued_rk)
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
                    published_messages.append(message_pack)
                    if self.logger.isEnabledFor(logging.DEBUG):
                        self.logger.debug(
                            "%r Published message %s into %s[%s]",
                            self, safe_repr(message.body), exchange, rk)
            ch.tx_commit()
            gevent.sleep(0)
        except:
            for message_pack in message_bulk:
                self.__outgoing_messages.put(message_pack)
            raise
        else:
            for message_pack in send_later:
                self.__outgoing_messages.put(message_pack)
            for _, _, _, event in published_messages:
                if event is not None:
                    event.set()
