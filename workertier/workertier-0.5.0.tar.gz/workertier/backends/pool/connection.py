#coding:utf-8
import contextlib
import logging
import random

from gevent.coros import Semaphore


logger = logging.getLogger(__name__)


class Connection(object):
    def __init__(self):
        self.broken = False  # Implement a callback for this
        self.lock = Semaphore()
        self.conn_id = hex(int(random.random() * 2**32))  #TODO: Fix "L"


    @contextlib.contextmanager
    def raise_if_broken(self, exc_class):
        #TODO: Not too happy with not throwing by default
        was_broken = self.broken
        yield
        if was_broken or self.broken:
            raise exc_class()
