# -*- coding: utf-8 -*-
import logging
import socket
from weakref import WeakValueDictionary
try:
    from weakref import WeakSet
except ImportError:
    from weakrefset import WeakSet
from collections import deque
from time import time

import amqp.exceptions
import gevent
from gevent.event import Event, AsyncResult

from base import (
    FailsafeAmqpPreferences, StaticHandlerChain,
    DynamicHandlerChain, safe_repr)


class Consume(object):
    def __init__(self, queue=None, consumer_tag=None, channel=None):
        self.queue = queue
        self.consumer_tag = consumer_tag
        self.channel = channel
        self.acks_remained = 0
        self.dying = False
        self.destroyed = False

    def __repr__(self):
        return u"<Consume {0} [{1}] {2}, {4}{3} acks remained{5}>".format(
            self.queue, self.consumer_tag, self.channel,
            self.acks_remained, ('', 'dying, ')[self.dying],
            ("", ", connection is None")[self.channel.connection is None])


class MessageProxy(object):
    _proxy_members = ('_message', 'consume', '_consumer', 'ack', 'reject')

    def __init__(self, message, consume, consumer):
        self._message = message
        self.consume = consume
        self._consumer = consumer

    @property
    def consumer_tag(self):
        return self.consume.consumer_tag

    @property
    def queue(self):
        return self.consume.queue

    def ack(self):
        self._consumer._ack_message(self._message, self.consume)

    def reject(self):
        self._consumer._reject_message(self._message, self.consume)

    def __getattr__(self, attr):
        if attr in MessageProxy._proxy_members:
            return self.__dict__[attr]
        return getattr(self.__dict__['_message'], attr)

    def __setattr__(self, attr, value):
        if attr in MessageProxy._proxy_members:
            self.__dict__[attr] = value
        setattr(self.__dict__['_message'], attr, value)

    def __delattr__(self, attr):
        if attr in MessageProxy._proxy_members:
            del self.__dict__[attr]
        delattr(self.__dict__['_message'], attr)


class FailsafeAmqpConsumer(FailsafeAmqpPreferences):
    _redelivered_flush_frequency = 1

    def __init__(self, iteration_timeout=0.5, **kwargs):
        super(FailsafeAmqpConsumer, self).__init__(**kwargs)
        self.iteration_timeout = iteration_timeout

        self.logger = logging.getLogger('amphora.FailsafeAmqpConsumer')
        self.running = False
        self.connection = None
        self.dont_consume = False

        self.before_connect_handlers = StaticHandlerChain(self)
        self.before_start_cycle = StaticHandlerChain(self)
        self.after_cycle_finish = StaticHandlerChain(self)
        self.before_stop = StaticHandlerChain(self)
        self.on_message = DynamicHandlerChain()

        # Lists of tuples
        # (message::amqp.Message, consume::Consume)
        self.__ack_this_messages = deque()
        self.__reject_this_messages = deque()

        # Set of Consume
        self.__consumes = set()  # active consumes only
        self.__all_consumes = WeakSet()  # all consumes in cycle

        # Dicts, values are Comsume
        self.__consume_by_tag = WeakValueDictionary()
        self.__consume_by_queue = WeakValueDictionary()
        self.__consume_by_channel = WeakValueDictionary()

        # Set of tuple
        # (queue::str, async_result::AsyncResult or None)
        self.__start_consume_request = deque()

        # List of tuple
        # (Consume, event::Event or None, qos::int or None)
        self.__stop_consume_request = deque()

        # List of tuples
        # (queue::basestring, exchange::basestring or None,
        #  routing_key::basestring, x_expires::int or None,
        #  event::Event or None)
        self.__new_queue_request = deque()

        # List of tuples
        # (exchange::basestring, type::basestring,
        #  event::Event or None)
        self.__new_exchange_request = deque()

        # Sometimes RabbitMQ can resend messages too frequently
        # When consumer can't close channel and rejects any incoming messages
        # RabbitMQ can redeliver one message infinitely, so both
        # AmqpRpc and RabbitMQ eats 100% CPU.
        # If message redelivered twice, we delay rejecting it.

        # Set of str
        self.__recently_rejected_message_ids = set()
        self.__last_redeliver_flush_time = time()

    def init_connection(self):
        self.connection = self.make_amqp_connection()

    def serve(self):
        network_exceptions = (
            EnvironmentError, socket.error, amqp.exceptions.ConnectionForced,
            amqp.exceptions.IrrecoverableConnectionError)
        self.running = True
        self.dont_consume = False

        try:
            while self.running:
                self.connection = None
                try:
                    self.before_connect_handlers()
                    self.init_connection()
                    self.logger.debug("Initializing connection")
                except network_exceptions as e:
                    self.logger.debug("Got exception %r when initialized, "
                                      "retry initialize", e)
                    gevent.sleep(0.2)
                else:
                    try:
                        self.before_start_cycle()
                        self.logger.debug("Starting consumer cycle")
                        return self.cycle()
                    except network_exceptions as e:
                        self.logger.debug("Got exception %r when cycled, "
                                          "retry initialize", e)
                        continue
                    finally:
                        self.after_cycle_finish()
        except:
            self.logger.exception("Exception in consumer %r", self)
            raise

    def stop(self):
        self.before_stop()
        self.running = False

    def prepare_stop(self):
        self.dont_consume = True

    def new_queue(self, queue, exchange=None, routing_key='',
                  x_expires=None, nowait=False):
        event = None if nowait else Event()
        self.__new_queue_request.append(
            (queue, exchange, routing_key, x_expires, event))
        if event is not None:
            event.wait()

    def new_exchange(self, exchange, type_, nowait=False):
        event = None if nowait else Event()
        self.__new_exchange_request.append((exchange, type_, event))
        if event is not None:
            event.wait()

    def start_consume(self, queue, qos=None, nowait=True):
        if queue not in self.__start_consume_request:
            async_result = None if nowait else AsyncResult()
            self.__start_consume_request.append((queue, async_result, qos))
            if async_result is not None:
                return async_result.get()

    def stop_consume(self, tag, nowait=True):
        try:
            consume = self.__consume_by_tag[tag]
        except KeyError:
            self.logger.warning("Trying to stop consume unknown tag %r", tag)
            if nowait:
                raise
        event = None if nowait else Event()
        self.__finish_consume(consume, event)
        self.logger.debug("Request for stop consuming %r", safe_repr(consume))
        if event is not None:
            event.wait()

    def _ack_message(self, message, consume):
        self.logger.debug("ACK %s %r", safe_repr(message.body), consume)
        self.__ack_this_messages.append((message, consume))

    def _reject_message(self, message, consume):
        self.logger.debug("REJECT %s %r", safe_repr(message.body), consume)
        self.__reject_this_messages.append((message, consume))

    def cycle(self):
        self.__ack_this_messages.clear()
        self.__reject_this_messages.clear()
        self.__restart_consumes()

        while self.running:
            self._iteration()

    def _iteration(self):
        self.__send_acks()
        if not self.running:
            return
        self.__send_rejects()

        self.__declare_queues_and_exchanges()
        self.__stop_consume_queues()
        self.__start_consume_queues()
        self.__get_messages()

    def __send_acks(self):
        while self.__ack_this_messages:
            message, consume = self.__ack_this_messages.popleft()
            if consume.destroyed:
                if self.logger.isEnabledFor(logging.DEBUG):
                    self.logger.debug("Consume %r is destroyed, don't ack %s",
                                      consume, safe_repr(message.body))
                continue
            ch = consume.channel

            if ch is None:
                if self.logger.isEnabledFor(logging.DEBUG):
                    self.logger.debug(
                        "Consume %r has no channel, don't ack %s",
                        consume, safe_repr(message.body))
                continue

            ch.basic_ack(message.delivery_info['delivery_tag'])
            if self.logger.isEnabledFor(logging.DEBUG):
                self.logger.debug("Acked message %s (from %r)",
                                  safe_repr(message.body), consume)

            consume.acks_remained -= 1
            if consume.dying and consume.acks_remained <= 0:
                self.__destroy_consume(consume)

    def __send_rejects(self):
        self.__check_recently_redelivered()

        for _ in xrange(len(self.__reject_this_messages)):
            message, consume = self.__reject_this_messages.popleft()
            if consume.destroyed:
                if self.logger.isEnabledFor(logging.DEBUG):
                    self.logger.debug(
                        "Consume %r is destroyed, don't reject %s",
                        consume, safe_repr(message.body))
                continue
            ch = consume.channel

            if ch is None:
                if self.logger.isEnabledFor(logging.DEBUG):
                    self.logger.debug(
                        "Consume %r has no channel, don't reject %s",
                        consume, safe_repr(message.body))
                continue

            message_id = message.properties['message_id']
            if message_id in self.__recently_rejected_message_ids:
                if self.logger.isEnabledFor(logging.DEBUG):
                    self.logger.debug(
                        "Message %s in %r delivered too frequently, "
                        "reject later.", safe_repr(message.body), consume)
                self.__reject_this_messages.append((message, consume))
                continue

            ch.basic_reject(message.delivery_info['delivery_tag'], True)
            self.__recently_rejected_message_ids.add(message_id)
            if self.logger.isEnabledFor(logging.DEBUG):
                self.logger.debug("Rejected message %s (from %r)",
                                  safe_repr(message.body), consume)
            consume.acks_remained -= 1
            if consume.dying and consume.acks_remained <= 0:
                self.__destroy_consume(consume)

    def __check_recently_redelivered(self):
        last_time = self.__last_redeliver_flush_time
        frequency = self._redelivered_flush_frequency
        now = time()
        if last_time + frequency < now:
            self.__last_redeliver_flush_time = now
            self.__recently_rejected_message_ids.clear()

    def __declare_queues_and_exchanges(self):
        if not self.__new_queue_request and not self.__new_exchange_request:
            return

        ch = self.connection.channel()
        while self.__new_exchange_request:
            exchange, type_, event = self.__new_exchange_request.popleft()
            ch.exchange_declare(exchange, type_,
                                auto_delete=False, durable=True)
            self.logger.debug("Declared exchange %s (%s)", exchange, type_)
            if event is not None:
                event.set()

        while self.__new_queue_request:
            pack = self.__new_queue_request.popleft()
            queue, exchange, rk, x_expires, event = pack

            arguments = {}
            if x_expires is not None:
                arguments['x-expires'] = x_expires
            ch.queue_declare(queue, auto_delete=False, durable=True,
                             arguments=arguments)
            self.logger.debug("Declared queue %s", queue)
            if exchange is not None:
                ch.queue_bind(queue, exchange=exchange, routing_key=rk)
                self.logger.debug("Bound queue %s --[%s]--> %s",
                                  exchange, rk, queue)
            if event is not None:
                event.set()
        ch.close()

    def __start_consume_queues(self):
        # __start_consume_request can be accessed by another greenlet
        # when trying to start consuming queue. Each queue should
        # be removed from __start_consume_queue only when it successfully
        # became consumed.
        for _ in xrange(len(self.__start_consume_request)):
            try:
                queue, async_result, qos = self.__start_consume_request[0]
            except IndexError:
                break

            ch = self.connection.channel()
            consume = Consume(queue=queue, channel=ch)
            self.__all_consumes.add(consume)
            if qos is not None and qos > 0:
                ch.basic_qos(0, qos, False)
            callback = self.__on_message_deco_factory(consume)
            try:
                tag = ch.basic_consume(queue, callback=callback)
            except amqp.NotFound:
                self.logger.warning(
                    "Can't consume queue %s: it does not exist", queue)
                self.__destroy_consume(consume)
                self.__start_consume_request.popleft()
                if async_result is not None:
                    async_result.set_exception(ValueError(queue))
            else:
                consume.consumer_tag = tag
                self.logger.debug("Start consuming from %r", consume)
                self.__add_consume(consume)
                self.__start_consume_request.popleft()
                if async_result is not None:
                    async_result.set(tag)

    def __get_messages(self):
        try:
            self.connection.drain_events(timeout=self.iteration_timeout)
        except socket.timeout:
            pass
        except amqp.exceptions.ConsumerCancelled as e:
            tag = e.args[0]
            self.logger.warning("Consumer %s suddenly cancelled", tag)
            try:
                consume = self.__consume_by_tag[tag]
            except KeyError:
                # Will be destroyed authomatically
                pass
            else:
                self.__finish_consume(consume, None)

    def __on_message_deco_factory(self, consume):
        def tmp(message):
            return self._on_message(message, consume)
        return tmp

    def __stop_consume_queues(self):
        while self.__stop_consume_request:
            consume, event = self.__stop_consume_request.popleft()
            if consume.destroyed:
                if event is not None:
                    event.set()
                continue
            consume.channel.basic_cancel(consume.consumer_tag)
            self.logger.debug("Stopped consuming from %r", consume)
            if consume.acks_remained <= 0:
                self.__destroy_consume(consume)
                if event is not None:
                    event.set()

    def _on_message(self, message, consume):
        if not self.running or self.dont_consume:
            self.logger.debug(
                "AmqpRpcConsumer is terminating, rejecting %s",
                safe_repr(message.body))
            self.__reject_this_messages.append((message, consume))
        elif consume.dying:
            self.logger.debug(
                "Consumer %r is dying, rejecting %s",
                consume, safe_repr(message.body))
            self.__reject_this_messages.append((message, consume))
        else:
            consume.acks_remained += 1
            if self.logger.isEnabledFor(logging.DEBUG):
                self.logger.debug(
                    "Consumed message %s from %r (routing key %r)",
                    safe_repr(message.body), consume,
                    message.delivery_info['routing_key'])
            # If server goes down, message can be delivered twice, sorry
            self.on_message(MessageProxy(message, consume, self))
            # Handler can make some changes with consumer,
            # they should run first
            gevent.sleep(0)

    def __add_consume(self, consume):
        self.__consumes.add(consume)
        self.__consume_by_tag[consume.consumer_tag] = consume
        self.__consume_by_queue[consume.queue] = consume
        self.__consume_by_channel[consume.channel] = consume

    def __finish_consume(self, consume, event):
        self.__consumes.remove(consume)
        del self.__consume_by_tag[consume.consumer_tag]
        del self.__consume_by_queue[consume.queue]
        del self.__consume_by_channel[consume.channel]
        consume.dying = True
        self.__stop_consume_request.append((consume, event))

    def __destroy_consume(self, consume):
        consume.destroyed = True
        consume.channel.close()
        self.logger.debug("Destroyed %r", consume)

    def __restart_consumes(self):
        self.__consumes.clear()
        self.__consume_by_tag.clear()
        self.__consume_by_queue.clear()
        self.__consume_by_channel.clear()
        for consume in self.__all_consumes:
            consume.dying = consume.destroyed = True
            consume.channel = None
