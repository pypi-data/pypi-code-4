from itertools import ifilterfalse

from .wrappers import WeakFunctionProxy
from .decorators import synchronized

def oid(target):
    try:
        return (id(target.__self__), id(target.__func__))
    except AttributeError:
        return id(target)

class Beacon(object):

    def __init__(self):
        self.receivers = []

    @synchronized
    def connect(self, receiver, sender=None):
        subscription = (oid(receiver), oid(sender))
        proxy = WeakFunctionProxy(receiver, self.purge)
        self.receivers.append((subscription, proxy))

    @synchronized
    def disconnect(self, receiver, sender=None):
        subscription = (oid(receiver), oid(sender))
        self.receivers = list(ifilterfalse(
                lambda item: item[0] == subscription, self.receivers))

    @synchronized
    def purge(self, proxy):
        self.receivers = list(ifilterfalse(
            lambda item: item[1] is proxy, self.receivers))

    def notify(self, sender, **params):
        if not self.receivers:
            return []

        responses = []

        t_oid = oid(sender)

        for (r_oid, s_oid), proxy in list(self.receivers):
            if t_oid == s_oid:
                try:
                    response = proxy(beacon=self, sender=sender, **params)
                except ReferenceError:
                    pass
                except Exception as e:
                    responses.append((proxy, e))
                else:
                    responses.append((proxy, response))

        return responses
