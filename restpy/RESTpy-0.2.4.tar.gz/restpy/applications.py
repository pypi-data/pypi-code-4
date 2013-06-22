"""This defines a basic wsgi application that provides RESTful routing."""

from werkzeug.exceptions import MethodNotAllowed


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

    def __init__(self, url_map):

        self.url_map = url_map

    def __call__(self, request):

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

        handler = Endpoint()

        if hasattr(handler, verb):

            return getattr(handler, verb)(request, **kwargs)

        # Reaching this point means the url matches a route, but did not have
        # a method matching the request. Assume `MethodNotAllowed`.
        raise MethodNotAllowed()
