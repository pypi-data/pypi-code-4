"""This defines a basic wsgi application that provides RESTful routing."""

from werkzeug.exceptions import MethodNotAllowed
from werkzeug.wrappers import Request


class RestApplication(object):
    """Base REST application.

    This object uses a werkzeug url map to route a request to the appropriate
    endpoint. Once an enpoint is found it attempts to call a method with the
    same name as the requested verb. For example, a GET request will look for
    the GET method of the endpoint to call.

    All verbs are upper-cased.

    Note::

        This application requires that it be wrapped in the `RequestMiddleware`
        found in the `wsgi` module.
    """

    def __init__(self, url_map, pre_hooks=None, post_hooks=None):

        self.url_map = url_map
        self.pre_hooks = pre_hooks or []
        self.post_hooks = post_hooks or []

    def __call__(self, environ, start_response):

        request = Request(environ)

        # Werkzeug documentation shows, but does not promise, that request
        # methods are upper case already. Since it isn't explicitly promised
        # this line was added.
        verb = request.method.upper()

        # Standard werkzeug functionality to create a `MapAdapter` object that
        # can route requests.
        urls = self.url_map.bind_to_environ(request.environ)

        # The endpoint in this case is an object constructor which is why the
        # variable is captialzied.
        # This call automatically raises a `NotFound` exception if there is no
        # match found.
        Endpoint, kwargs = urls.match()

        handler_endpoint = Endpoint()

        try:
            handler_method = getattr(handler_endpoint, verb)

        except AttributeError:
            raise MethodNotAllowed()

        for hook in self.pre_hooks:
            hook(request)

        response = handler_method(request, **kwargs)

        for hook in self.post_hooks:

            hook(request, response)

        return response
