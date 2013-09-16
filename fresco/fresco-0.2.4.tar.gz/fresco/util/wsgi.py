"""\
Utilities for managing WSGI requests and responses
"""

from io import BytesIO


class StartResponseWrapper(object):
    """\
    Wrapper class for the ``start_response`` callable, allowing middleware
    applications to intercept and interrogate the proxied start_response
    arguments.

    Synopsis::

        >>> def my_wsgi_app(environ, start_response):
        ...     start_response('200 OK', [('Content-Type', 'text/plain')])
        ...     return ['Whoa nelly!']
        ...
        >>> def my_other_wsgi_app(environ, start_response):
        ...     responder = StartResponseWrapper(start_response)
        ...     result = my_wsgi_app(environ, responder)
        ...     print "Got status", responder.status
        ...     print "Got headers", responder.headers
        ...     responder.call_start_response()
        ...     return result
        ...
        >>> from flea import TestAgent
        >>> result = TestAgent(my_other_wsgi_app).get('/')
        Got status 200 OK
        Got headers [('Content-Type', 'text/plain')]

    See also ``Response.from_wsgi``, which takes a wsgi callable, environ and
    start_response, and returns a ``Response`` object, allowing the client to
    further interrogate and customize the WSGI response.

    Note that it is usually not advised to use this directly in middleware as
    start_response may not be called directly from the WSGI application, but
    rather from the iterator it returns. In this case the middleware may need
    logic to accommodate this. It is usually safer to use
    ``Response.from_wsgi``, which takes this into account.
    """

    def __init__(self, start_response):
        self.start_response = start_response
        self.status = None
        self.headers = []
        self.called = False
        self.buf = BytesIO()
        self.exc_info = None

    def __call__(self, status, headers, exc_info=None):
        """
        Dummy WSGI ``start_response`` function that stores the arguments for
        later use.
        """
        self.status = status
        self.headers = headers
        self.exc_info = exc_info
        self.called = True
        return self.buf.write

    def call_start_response(self):
        """
        Invoke the wrapped WSGI ``start_response`` function.
        """
        try:
            write = self.start_response(
                self.status,
                self.headers,
                self.exc_info
            )
            write(self.buf.getvalue())
            return write
        finally:
            # Avoid dangling circular ref
            self.exc_info = None


class ClosingIterator(object):
    """\
    Wrap a WSGI iterator to allow additional close functions to be called on
    application exit.

    Synopsis::

        >>> class filelikeobject(object):
        ...
        ...     def read(self):
        ...         print "file read!"
        ...         return ''
        ...
        ...     def close(self):
        ...         print "file closed!"
        ...
        >>> def app(environ, start_response):
        ...     f = filelikeobject()
        ...     start_response('200 OK', [('Content-Type', 'text/plain')])
        ...     return ClosingIterator(iter(f.read, ''), f.close)
        ...
        >>> from flea import TestAgent
        >>> m = TestAgent(app).get('/')
        file read!
        file closed!

    """

    def __init__(self, iterable, *close_funcs):
        """
        Initialize a ``ClosingIterator`` to wrap iterable ``iterable``, and
        call any functions listed in ``*close_funcs`` on the instance's
        ``.close`` method.
        """
        self.__dict__['_iterable'] = iterable
        self.__dict__['_next'] = iter(self._iterable).next
        self.__dict__['_close_funcs'] = close_funcs
        iterable_close = getattr(self._iterable, 'close', None)
        if iterable_close is not None:
            self.__dict__['_close_funcs'] = (iterable_close,) + close_funcs
        self.__dict__['_closed'] = False

    def __iter__(self):
        """
        ``__iter__`` method
        """
        return self

    def next(self):
        """
        Return the next item from ``iterator``
        """
        return self._next()

    def close(self):
        """
        Call all close functions listed in ``*close_funcs``.
        """
        self.__dict__['_closed'] = True
        for func in self._close_funcs:
            func()

    def __getattr__(self, attr):
        return getattr(self._iterable, attr)

    def __setattr__(self, attr, value):
        return getattr(self._iterable, attr, value)

    def __del__(self):
        """
        Emit a warning if the iterator is deleted with ``close`` having been
        called.
        """
        if not self._closed:
            import warnings
            warnings.warn("%r deleted without close being called" % (self,))
