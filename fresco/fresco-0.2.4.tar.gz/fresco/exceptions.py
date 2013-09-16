__all__ = 'ResponseException', 'NotFound', 'NotFoundFinal', 'Unauthorized',\
          'Forbidden', 'BadRequest', 'Redirect', 'RedirectTemporary',\
          'RedirectPermanent'

from fresco.response import Response


class ResponseException(Exception):
    """\
    An exception class with an associated :class:`fresco.response.Response`
    instance that will render a suitable error page.
    """
    response = None


class _NotFound(ResponseException):
    response = Response.not_found()


class NotFound(_NotFound):
    """\
    Raised when a view needs to signal a 404 not found condition. Other routes
    will be given the opportunity to handle the request, if no others are able
    to, 404 not found response will be returned. """


class NotFoundFinal(_NotFound):
    """\
    Return a 404 response directly, even if there may be other views available
    to handle the request.
    """


class BadRequest(ResponseException):
    """\
    Return a 400 Bad Request response
    """
    response = Response(['Bad request'], status=400)


class Unauthorized(ResponseException):
    """\
    Return a 401 Unauthorized response.

    Use this when you want to flag that the user does not have permission to
    access a resource but may be able to gain access, eg by logging in.
    """
    response = Response(['Unauthorized'], status=401)


class Forbidden(ResponseException):
    """\
    Return a 403 Forbidden response

    Use this when you want to flag that the user does not have permission to
    access a resource and that there is no possiblity to do so (eg they are
    already logged in, but their account does not have the right access
    permissions)
    """
    response = Response(['Forbidden'], status=403)


class RedirectTemporary(ResponseException):
    """\
    Return a 302 Found response. Example::

        raise RedirectTemporary('http://example.org/')
    """
    def __init__(self, *args, **kwargs):
        self.response = Response.redirect(*args, **kwargs)

Redirect = RedirectTemporary


class RedirectPermanent(ResponseException):
    """\
    Return a 301 Moved Permanently response. Example::

        raise RedirectPermanent('http://example.org/')

    """
    def __init__(self, *args, **kwargs):
        self.response = Response.redirect_permanent(*args, **kwargs)


class RequestParseError(BadRequest):
    """\
    An error was encountered while parsing the HTTP request.
    """
