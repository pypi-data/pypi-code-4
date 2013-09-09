#coding:utf-8
import contextlib
import logging

from gevent.coros import Semaphore


logger = logging.getLogger(__name__)


class Connection(object):
    def __init__(self):
        self.broken = False
        self.lock = Semaphore()

    @contextlib.contextmanager
    def raise_if_broken(self, exc_class):
        #TODO: Not too happy with not throwing by default
        was_broken = self.broken
        yield
        if was_broken or self.broken:
            raise exc_class()
