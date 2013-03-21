#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4


from rapidsms.backends.base import BackendBase

from .models import HttpTesterMessage
from .storage import store_message


class HttpTesterCacheBackend(BackendBase):
    """ Simple backend that stores messages in a cache """

    def send(self, msg):
        store_message(HttpTesterMessage.OUTGOING, msg.connection.identity,
                msg.text)
        return True

    def start(self):
        """ Override BackendBase.start(), which never returns """
        self._running = True
