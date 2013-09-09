#coding:utf-8
import logging

import gevent


DEFAULT_NUM_CONSUMERS = 5
#TODO: Make this configurable


logger = logging.getLogger(__name__)


class Consumer(object):
    def __init__(self, cache, dispatcher, num_consumers=DEFAULT_NUM_CONSUMERS):
        self.cache = cache
        self.dispatcher = dispatcher
        self.num_consumers = num_consumers

    def consume_message(self, message):  #TODO: Create a thicker layer on messages
        key = str(message.body)
        value = key.swapcase()
        self.cache.set(key, value)
        logger.debug("Processed message: '%s' -> '%s'", key, value)

    def start(self):
        for _ in xrange(self.num_consumers):
            gevent.spawn(self.dispatcher.start_consumer, self.consume_message)
        gevent.sleep()  # Yield to the other greenlets
