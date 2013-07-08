""" :mod:`hedwig.backends.console`
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

"""
from sys import stderr, stdout
from threading import RLock

from .base import BaseEmailBackend


class ConsoleEmailBackend(BaseEmailBackend):
    """
    Console I/O email backend implementation.
    """

    def __init__(self, stream=None, **kwargs):
        super(ConsoleEmailBackend, self).__init__(**kwargs)
        self.stream = stream or stderr
        self._lock = RLock()

    def send_messages(self, email_messages):
        if not email_messages:
            return
        for message in email_messages:
            self.stream.write('%s\n' % message.message().as_string())
            self.stream.write('-' * 79)
            self.stream.write('\n')
            self.stream.flush()
        return len(email_messages)

    def __repr__(self):
        cls = type(self)
        mod = cls.__module__
        mod = '' if __name__ == mod else mod + '.'
        if self.stream == stdout:
            stream = 'sys.stdout'
        elif self.stream == stderr:
            stream = 'sys.stderr'
        else:
            stream = repr(stream)
        kwargs = [(k, getattr(self, k)) for k in dir(self)]
        kwargs = [(k, v) for k, v in kwargs if not callable(v)]
        kwargs.append(('stream', stream))
        kwargs.sort(key=lambda (k, v): k)
        kwargs = ', '.join('{0}={1!r}'.format(k, v) for k, v in kwargs)
        return '{0}{1}({2})'.format(mod, cls.__name__, kwargs)
