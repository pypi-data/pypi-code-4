"""This module contains wsgi middlewares.

All middlewares in this module are dependent on the `RequestMiddleware` which
is also included in this module.
"""

from werkzeug.exceptions import HTTPException, InternalServerError

import uuid


class UniqueEnvironMiddleware(object):
    """This middleware assigns a UUID to the WSGI environ."""

    def __init__(self, application):

        self.application = application

    def __call__(self, environ, start_response):

        environ['uuid'] = str(uuid.uuid4())

        return self.application(environ, start_response)


class ResponderMiddleware(object):
    """This middleware resolves a werkzeug `Response` object.

    The expectation is that the wrapped WSGI application will return a WSGI
    application callable, such as a werkzeug `Response` object, that in turn
    will use the `start_response` method and actually return the iterable.
    """

    def __init__(self, application):

        self.application = application

    def __call__(self, environ, start_response):

        response = self.application(environ, start_response)

        return response(environ, start_response)
