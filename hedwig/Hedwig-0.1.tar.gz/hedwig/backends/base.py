""" :mod:`hedwig.backends.base`
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~

"""
from threading import RLock


class BaseEmailBackend(object):
    """
    Base class ofr email backend implementation.
    """

    def __init__(self, **kwargs):
        self.opened = 0
        self._lock = RLock()

    def open(self):
        self.opened += 1

    def close(self):
        if self.opened:
            self.opened -= 1
        else:
            raise RuntimeError('already closed')

    def send_messages(self, email_messages):
        raise NotImplementedError()

    def __enter__(self):
        if not self.opened:
            self._lock.acquire()
            self.open()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.close()
        self._lock.release()

    def __repr__(self):
        cls = type(self)
        mod = cls.__module__
        mod = '' if __name__ == mod else mod + '.'
        kwargs = ((k, getattr(self, k)) for k in dir(self)
                                        if not k.startswith('_'))
        kwargs = [(k, v) for k, v in kwargs if not callable(v)]
        kwargs.sort(key=lambda (k, v): k)
        kwargs = ', '.join('{0}={1!r}'.format(k, v) for k, v in kwargs)
        return '{0}{1}({2})'.format(mod, cls.__name__, kwargs)
