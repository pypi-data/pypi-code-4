from operator import attrgetter, itemgetter, methodcaller
from fresco.exceptions import BadRequest
from itertools import cycle

__all__ = ('FormArg', 'GetArg', 'QueryArg', 'PostArg', 'CookieArg',
           'SessionArg', 'RequestObject', 'FormData')

_marker = []


class RouteKwarg(object):
    """
    RouteKwarg objects can be used as keyword arguments in a route definition.
    RouteKwargs can extract information from the request and make it available
    to the view.

    For example a RouteKwarg could be developed that reads information from the
    request cookie::

        Route('/', GET, affiliate=CookieArg())

    A naive implementation ``CookieArg`` could look like this::

        class CookieArg(RouteKwarg):

            def __call__(self, request):
                try:
                    return request.cookies[self.name].value
                except KeyError,
                    return None

    When the route is constructed the RouteKwarg's ``configure`` method will
    be called with the Route object and the keyword name.

    At every request, the RouteKwarg instance will be called and expected to
    supply the value for its argument.
    """

    route = None
    name = None

    def configure(self, route, name):
        self.route = route
        self.name = name

    def __call__(self, request):
        return None


class RequestArg(RouteKwarg):
    """\
    Extract a view keyword argument from the request object.
    """

    query = attrgetter('query')
    form = attrgetter('form')
    cookies = attrgetter('cookies')
    session = attrgetter('session')

    #: Source for the request variable
    source = form

    #: Exceptions that signal the converter could not do its job due to invalid
    #: input
    converter_exceptions = (ValueError, TypeError)

    def __init__(self, converter=None, key=None,
                 default=_marker, exception=BadRequest):

        self.formkey = key
        self.default = default
        self.required = default is _marker
        self.exception = exception
        self.is_list = isinstance(converter, list)
        if self.is_list:
            self.converter = lambda vs: [c(v)
                                         for c, v in zip(cycle(converter), vs)]
        else:
            self.converter = converter

    def configure(self, route, name):
        if self.formkey is None:
            self.formkey = name
        if self.is_list:
            self.getter = methodcaller('getlist', self.formkey)
        else:
            self.getter = itemgetter(self.formkey)

    def __call__(self, request):
        try:
            value = self.getter(self.source(request))
        except KeyError:
            if self.required:
                raise self.exception('No value provided for %s' %
                                     (self.formkey,))
            return self.default

        try:
            if self.converter is not None:
                value = self.converter(value)
        except self.converter_exceptions:
            raise self.exception('%r is not a valid value for %s' %
                                 (value, self.formkey,))

        return value


class RequestObject(RouteKwarg):
    """\
    Make the request object itself available as a view argument.

    Example::

        @app.route('/form', POST, request=RequestObject())
        def view(formdata):
            ...
    """
    def __call__(self, request):
        return request


class FormData(RouteKwarg):
    """\
    Make the request form data MultiDict available as a view argument.

    Example::

        @app.route('/form', POST, data=FormData())
        def view(formdata):
            ...
    """

    def __call__(self, request):
        return request.form


class CookieArg(RequestArg):
    """\
    Extract a view keyword argument from ``request.cookies``.

    Example::

        @app.route('/', GET, message=CookieArg(key='msg', default=None))
        def view(message):
            return Response([message])
    """
    source = RequestArg.cookies

    def getter(self, cookies):
        if self.is_list:
            return [c.value for c in cookies.getlist(self.formkey)]
        else:
            return cookies[self.formkey].value

    def configure(self, route, name):
        if self.formkey is None:
            self.formkey = name


class QueryArg(RequestArg):
    """\
    Extract a view keyword argument from ``request.query``.

    Example::

        @app.route('/add', GET, a=QueryArg(int), b=QueryArg(int))
        def view(a, b):
            return Response(['a + b = %d' % (a + b)])
    """
    source = RequestArg.query

#: Synonym for QueryArg
GetArg = QueryArg


class FormArg(RequestArg):
    """\
    Extract a view keyword argument from ``request.form``.

    Example::

        @app.route('/mul', POST, a=FormArg(int), b=FormArg(int))
        def view(a, b):
            return Response(['a * b = %d' % (a * b)])

    """
    source = RequestArg.form

#: Synonym for FormArg
PostArg = FormArg


class SessionArg(RequestArg):
    """\
    Extract a view keyword argument from ``request.form``.

    Example::

        @app.route('/mul', POST, a=FormArg(int), b=FormArg(int))
        def view(a, b):
            return Response(['a * b = %d' % (a * b)])

    """
    source = RequestArg.session
