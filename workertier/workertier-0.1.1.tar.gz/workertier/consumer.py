#coding:utf-8
import logging

DEFAULT_NUM_CONSUMERS = 5

logger = logging.getLogger(__name__)


class Consumer(object):
    def __init__(self, cache, dispatcher, num_consumers=DEFAULT_NUM_CONSUMERS):
        self.cache = cache
        self.dispatcher = dispatcher
        self.num_consumers = num_consumers

    def consume(self, message):
        key = message.body
        value = key.swapcase()
        self.cache.set(key, value)
        logger.debug("Processed message: '%s' -> '%s'", key, value)

    def start(self):
        for _ in xrange(self.num_consumers):
            self.dispatcher.consume(self.consume)
