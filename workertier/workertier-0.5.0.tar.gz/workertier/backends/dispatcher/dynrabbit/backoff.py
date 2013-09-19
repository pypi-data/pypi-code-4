#coding:utf-8
import logging

import gevent


logger = logging.getLogger(__name__)


DEFAULT_BASE_DELAY = 1
DEFAULT_BACKOFF_EXPONENT = 1.1


class ExponentialBackoffStrategy(object):
    """
    A stateful object to manage exponential backoff
    """
    def __init__(self, base_delay=DEFAULT_BASE_DELAY, backoff_exponent=DEFAULT_BACKOFF_EXPONENT):
        self.base_delay = base_delay
        self.backoff_exponent = backoff_exponent

        self.delay = None

    def failed(self):
        if self.delay is None:
            self.delay = self.base_delay
        self.delay *= self.backoff_exponent

    def succeeded(self):
        self.delay = None

    def wait(self):
        if self.delay is not None:
            logger.info("Sleeping for %ss", self.delay)
        gevent.sleep(self.delay or 0)