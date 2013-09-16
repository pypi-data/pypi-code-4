from collections import defaultdict
from functools import wraps, partial
from thread import get_ident
from urlparse import urlparse

from .request import Request
from .util.wsgi import ClosingIterator

class RequestContext(object):
    """\
    A local storage class that maintains different values for each request
    context in which it is used.

    Requires an ``ident_func`` that returns a hashable identifier that will
    give a different value per request. In a threaded environment this would be
    ``thread.get_ident``. If using a different execution model, a different
    strategy would need to be found.
    """

    def __init__(self, ident_func=get_ident):
        object.__setattr__(self, '_contexts', defaultdict(list))
        object.__setattr__(self, '_ident_func', ident_func)
        self.push()

    def push(self, **bindnames):
        contexts = self._contexts[self._ident_func()]
        c = dict(contexts[-1] if contexts else {}, **bindnames)
        self._contexts[self._ident_func()].append(c)

    def pop(self):
        ident = self._ident_func()
        self._contexts[ident].pop()
        if not self._contexts[ident]:
            del self._contexts[ident]

    def currentcontext(self):
        return self._contexts[self._ident_func()][-1]

    def __getattr__(self, item):
        try:
            return self.currentcontext()[item]
        except (KeyError, IndexError):
            raise AttributeError(item)

    def __setattr__(self, item, ob):
        self.currentcontext()[item] = ob

    def __delattr__(self, item):
        try:
            del self.currentcontext()[item]
        except KeyError:
            raise AttributeError(item)

    def get(self, item, default=None):
        return self.currentcontext().get(item, default)

    def __repr__(self):
        return "<%s depth=%d; current=%r>" % (self.__class__.__name__,
                                              len(self._contexts),
                                              self.currentcontext())
