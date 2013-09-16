import inspect
import re
from functools import partial
from itertools import cycle
from operator import attrgetter, itemgetter, methodcaller

from fresco.exceptions import BadRequest
from fresco.util.urls import join_path

__all__ = 'Pattern', 'Route', 'FormArg', 'QueryArg', 'CookieArg'


class URLGenerationError(Exception):
    """\
    Was not possible to generate the requested URL
    """


class Pattern(object):
    """\
    Patterns are matchable against URL paths using their ``match`` method. If a
    path matches, this should return a tuple of ``(positional_arguments,
    keyword_arguments)`` extracted from the URL path. Otherwise this method
    should return ``None``.

    Pattern objects may also be able to take a tuple of
    ``(positional_arguments, keyword_arguments)`` and return a corresponding
    URL path.
    """

    def match(self, path):
        """
        Should return a tuple of ``(positional_arguments, keyword_arguments)``
        if the pattern matches the given URL path, or None if it does not
        match.
        """
        raise NotImplementedError

    def pathfor(self, *args, **kwargs):
        """
        The inverse of ``match``: where possible, should generate a URL path
        for the given positional and keyword arguments.
        """
        raise NotImplementedError()

    def add_prefix(self, prefix):
        """
        Return a copy of the pattern with the given string prepended
        """
        raise NotImplementedError()


class Converter(object):
    """\
    Responsible for converting arguments to and from URL components.

    A ``Converter`` class should provide two instance methods:

    - ``to_string``: convert from a python object to a string
    - ``from_string``: convert from URL-encoded bytestring to the target
                        python type.

    It must also define the regular expression pattern that is used to extract
    the string from the URL.
    """
    pattern = '[^/]+'

    def __init__(self, pattern=None):
        """
        Initialize a ``Converter`` instance.
        """
        if pattern is not None:
            self.pattern = pattern

    def to_string(self, ob):
        """
        Convert arbitrary argument ``ob`` to a string representation
        """
        return unicode(ob)

    def from_string(self, s):
        """
        Convert string argument ``a`` to the target object representation,
        whatever that may be.
        """
        raise NotImplementedError


class IntConverter(Converter):
    """\
    Match any integer value and convert to an ``int`` value.
    """

    pattern = r'[+-]?\d+'

    def from_string(self, s):
        """
        Return ``s`` converted to an ``int`` value.
        """
        return int(s)


class UnicodeConverter(Converter):
    """\
    Match any string, not including a forward slash, and return a ``unicode``
    value
    """

    pattern = r'[^/]+'

    def to_string(self, s):
        """
        Return ``s`` converted to an ``unicode`` object.
        """
        return s

    def from_string(self, s):
        """
        Return ``s`` converted to an ``unicode`` object.
        """
        return unicode(s)


class AnyConverter(UnicodeConverter):
    """
    Match any one of the given string options.
    """

    pattern = r'[+-]?\d+'

    def __init__(self, *args):
        super(AnyConverter, self).__init__(None)
        if len(args) == 0:
            raise ValueError("Must supply at least one argument to any()")
        self.pattern = '|'.join(re.escape(arg) for arg in args)


class PathConverter(UnicodeConverter):
    """\
    Match any string, possibly including forward slashes, and return a
    ``unicode`` object.
    """
    pattern = r'.+'


class MatchAllURLsPattern(Pattern):
    """\
    A pattern matcher that matches all URLs starting with the given prefix. No
    arguments are parsed from the URL.
    """

    def __init__(self, path):
        self.path = path

    def match(self, path):
        if path.startswith(self.path):
            return (), {}
        return None

    def pathfor(self, *args, **kwargs):
        assert not args and not kwargs, \
                "MatchAllURLsPattern does not handle URL based arguments"

        return self.path

    def add_prefix(self, prefix):
        return self.__class__(join_path(prefix, self.path))

    def __unicode__(self):
        return '%s*' % (self.path,)


class ExtensiblePattern(Pattern):
    """\
    An extensible URL pattern matcher.

    Synopsis::

        >>> from pprint import pprint
        >>> p = ExtensiblePattern(r"/<:unicode>/<year:int>/<title:unicode>")
        >>> pprint(p.match('/archive/1999/blah'))
        ((u'archive',), {'title': u'blah', 'year': 1999})

    Patterns are split on slashes into components. A component can either be a
    literal part of the path, or a pattern component in the form::

        <identifier>:<converter>

    ``identifer`` can be any python name, which will be used as the name of a
    keyword argument to the matched function. If omitted, the argument will be
    passed as a positional arg.

    ``converter`` must be the name of a pre-registered converter. Converters
    must support ``to_string`` and ``from_string`` methods and are used to
    convert between URL segments and python objects.

    By default, the following converters are configured:

    - ``int`` - converts to an integer
    - ``path`` - any path (ie can include forward slashes)
    - ``unicode`` - any unicode string (not including forward slashes)
    - ``any`` - a string matching a list of alternatives

    Some examples::

        >>> p = ExtensiblePattern(r"/images/<:path>")
        >>> p.match('/images/thumbnails/02.jpg')
        ((u'thumbnails/02.jpg',), {})

        >>> p = ExtensiblePattern("/<page:any('about', 'help')>.html")
        >>> p.match('/about.html')
        ((), {'page': u'about'})

        >>> p = ExtensiblePattern("/entries/<id:int>")
        >>> p.match('/entries/23')
        ((), {'id': 23})

    Others can be added by calling ``ExtensiblePattern.register_converter``
    """

    preset_patterns = (
        ('int', IntConverter),
        ('unicode', UnicodeConverter),
        ('path', PathConverter),
        ('any', AnyConverter),
    )
    pattern_parser = re.compile("""
        <
            (?P<name>\w[\w\d]*)?
            :
            (?P<converter>\w[\w\d]*)
            (?:
                \(
                         (?P<args>.*?)
                \)
            )?
        >
    """, re.X)

    class Segment(object):
        """
        Represent a single segment of a URL, storing information about hte
        ``source``, ``regex`` used to pattern match the segment, ``name`` for
        named parameters and the ``converter`` used to map the value to a URL
        parameter if applicable
        """

        def __init__(self, source, regex, name, converter):
            self.source = source
            self.regex = regex
            self.name = name
            self.converter = converter

    def __init__(self, pattern, name=''):
        """
        Initialize a new ``ExtensiblePattern`` object with pattern ``pattern``
        and an optional name.
        """
        super(ExtensiblePattern, self).__init__()

        self.name = name
        self.preset_patterns = dict(self.preset_patterns)
        self.pattern = unicode(pattern)

        self.segments = list(self._make_segments(pattern))
        self.args = [item
                     for item in self.segments
                     if item.converter is not None]
        self.regex = re.compile(''.join(segment.regex
                                        for segment in self.segments) + '$')

    def _make_segments(self, s):
        r"""
        Generate successive Segment objects from the given string.

        Each segment object represents a part of the pattern to be matched, and
        comprises ``source``, ``regex``, ``name`` (if a named parameter) and
        ``converter`` (if a parameter)
        """

        for item in split_iter(self.pattern_parser, self.pattern):
            if isinstance(item, unicode):
                yield self.Segment(item, re.escape(item), None, None)
                continue
            groups = item.groupdict()
            name, converter, args = (groups['name'], groups['converter'],
                                     groups['args'])
            if isinstance(name, unicode):
                # Name must be a Python identifiers
                name = name.encode("ASCII")
            converter = self.preset_patterns[converter]
            if args:
                args, kwargs = self.parseargs(args)
                converter = converter(*args, **kwargs)
            else:
                converter = converter()
            yield self.Segment(item.group(0),
                               '(%s)' % converter.pattern, name, converter)

    def parseargs(self, argstr):
        """
        Return a tuple of ``(args, kwargs)`` parsed out of a string in the
        format ``arg1, arg2, param=arg3``.

        Synopsis::

            >>> ep =  ExtensiblePattern('')
            >>> ep.parseargs("1, 2, 'buckle my shoe'")
            ((1, 2, 'buckle my shoe'), {})
            >>> ep.parseargs("3, four='knock on the door'")
            ((3,), {'four': 'knock on the door'})

        """
        return eval('(lambda *args, **kwargs: (args, kwargs))(%s)' % argstr)

    def match(self, uri):
        """
        Test ``uri`` and return a tuple of parsed ``(args, kwargs)``, or
        ``None`` if there was no match.
        """
        mo = self.regex.match(uri)
        if not mo:
            return None
        groups = mo.groups()
        assert len(groups) == len(self.args), (
                "Number of regex groups does not match expected count. "
                "Perhaps you have used capturing parentheses somewhere? "
                "The pattern matched was %r." % self.regex.pattern
        )

        try:
            groups = [
                (segment.name, segment.converter.from_string(value))
                  for value, segment in zip(groups, self.args)
            ]
        except ValueError:
            return None

        args = tuple(value for name, value in groups if not name)
        kwargs = dict((name, value) for name, value in groups if name)
        return args, kwargs

    def pathfor(self, *args, **kwargs):
        """
        Example usage::

            >>> p = ExtensiblePattern("/view/<name:unicode>/<revision:int>")
            >>> p.pathfor(name='important_document.pdf', revision=299)
            u'/view/important_document.pdf/299'

            >>> p = ExtensiblePattern("/view/<:unicode>/<:int>")
            >>> p.pathfor('important_document.pdf', 299)
            u'/view/important_document.pdf/299'
        """

        args = list(args)
        result = []
        for seg in self.segments:
            if not seg.converter:
                result.append(seg.source)
            elif seg.name:
                try:
                    result.append(seg.converter.to_string(kwargs[seg.name]))
                except IndexError:
                    raise URLGenerationError(
                        "Argument %r not specified for url %r" % (
                            seg.name, self.pattern
                        )
                    )
            else:
                try:
                    result.append(seg.converter.to_string(args.pop(0)))
                except IndexError:
                    raise URLGenerationError(
                        "Not enough positional arguments for url %r" % (
                            self.pattern,
                        )
                    )
        return ''.join(result)

    def add_prefix(self, prefix):

        return self.__class__(
            join_path(prefix, self.pattern),
            self.name
        )

    @classmethod
    def register_converter(cls, name, converter):
        """
        Register a preset pattern for later use in URL patterns.

        Example usage::

            >>> from datetime import date
            >>> from time import strptime
            >>> class DateConverter(Converter):
            ...     pattern = r'\d{8}'
            ...     def from_string(self, s):
            ...         return date(*strptime(s, '%d%m%Y')[:3])
            ...
            >>> ExtensiblePattern.register_converter('date', DateConverter)
            >>> ExtensiblePattern('/<:date>').match('/01011970')
            ((datetime.date(1970, 1, 1),), {})
        """
        cls.preset_patterns += ((name, converter),)

    def __repr__(self):
        return '<%s %r>' % (self.__class__, self.pattern)

    def __unicode__(self):
        return u'%s' % (self.pattern,)


class Route(object):
    """\
    Represent a URL routing pattern
    """

    __slots__ = 'tag', 'pattern', 'methods', 'view', 'view_kwargs',\
                'predicate', 'decorators', 'original_view'

    #: The default class to use for URL pattern matching
    pattern_class = ExtensiblePattern

    def __init__(self, pattern, methods, view, view_kwargs=None,
                 tag='__default__', predicate=None, decorators=None, **kwargs):

        """
        :param pattern:     A string that can be compiled into a path pattern
        :param methods:     The list of HTTP methods the view is bound to
                            ('GET', 'POST', etc)
        :param view:        The view function.
        :param view_kwargs: A dictionary of default keyword arguments to pass
                            to the view callable
        :param tag:         A tag that can later be used to retrieve the route
                            for URL generation
        :param predicate:   A callable that is used to decide whether to match
                            this pattern. The callable must take a ``Request``
                            object as its only parameter and return a boolean.
        :param decorators:  Decorator functions to apply to the view callable
                            before invoking it
        :param kwargs:      Other keyword aruments passed through to the view
                            callable.
        """

        if not isinstance(pattern, Pattern):
            pattern = self.pattern_class(pattern)

        if isinstance(methods, basestring):
            methods = [methods]

        self.pattern = pattern
        self.methods = set(methods)
        self.view_kwargs = dict(view_kwargs or {}, **kwargs)
        for name, arg in self.view_kwargs.items():
            if isinstance(arg, RouteKwarg):
                arg.configure(self, name)
        self.tag = tag
        self.predicate = predicate
        self.decorators = decorators or []
        self.set_view(view)

    def __unicode__(self):
        return u'%s %s => %r\n' % (
            ' '.join(self.methods),
            unicode(self.pattern),
            self.original_view
        )

    def __repr__(self):
        return u'<%s %s %r %s>' % (
            self.__class__.__name__,
            ','.join(self.methods),
            unicode(self.pattern),
            self.original_view
        )

    def set_view(self, view):
        decorated_view = view
        for d in (self.decorators or []):
            decorated_view = d(decorated_view)

        self.original_view = view
        self.view = decorated_view

    def resolve_view(self, instance):
        """
        Resolve a view spec string to the actual callable.
        """
        if callable(self.original_view):
            return
        self.set_view(getattr(instance, self.original_view))

    def add_prefix(self, path):
        """
        Return a copy of the Route object with the given path prepended to the
        routing pattern.
        """
        return self.__class__(self.pattern.add_prefix(path), self.methods,
                              view=self.original_view,
                              view_kwargs=self.view_kwargs, tag=self.tag,
                              predicate=self.predicate,
                              decorators=self.decorators)

    def url(self, *args, **kwargs):
        """\
        Return a URL corresponding to the route

        :param _request: the current request object.
        :param _scheme: the URL scheme to use (eg 'https' or 'http').
        :param _netloc: the network location to use (eg 'localhost:8000').
        :param _script_name: the SCRIPT_NAME path component
        :param _query: any query parameters, as a dict or list of
                       ``(key, value)`` tuples.
        :param _fragment: a URL fragment to append.

        Any other arguments or keyword args are fed to the ``pathfor`` method
        of the pattern>
        """
        from fresco import context

        request = kwargs.pop('_request', None)
        scheme = kwargs.pop('_request', None)
        netloc = kwargs.pop('_netloc', None)
        query = kwargs.pop('_query', {})
        script_name = kwargs.pop('_script_name', None)
        fragment = kwargs.pop('_fragment', None)

        if request is None:
            request = context.request

        return request.make_url(scheme=scheme, netloc=netloc,
                                PATH_INFO=self.pattern.pathfor(*args,
                                                               **kwargs),
                                SCRIPT_NAME=script_name, parameters='',
                                query=query, fragment=fragment)


def split_iter(pattern, string):
    """
    Generate alternate strings and match objects for all occurances of
    ``pattern`` in ``string``.
    """
    matcher = pattern.finditer(string)
    match = None
    pos = 0
    for match in matcher:
        yield string[pos:match.start()]
        yield match
        pos = match.end()
    yield string[pos:]


def resolve_viewspec(viewspec, stack_depth):
    """
    Resolve the given view spec

    :param viewspec: View specification (eg ``'mypackage.views:my_view'``)
    :param stack_depth: How far back to look in the stack for the caller's
                        context, for resolving imports relative to the caller.
    """
    if not isinstance(viewspec, basestring):
        return viewspec

    try:
        module_spec, attr_spec = viewspec.split(':')
    except ValueError:
        raise ValueError("Expected string like 'package.module:view_func';"\
                         " got %r'" % viewspec)

    ob = __import__(module_spec)
    for mod in module_spec.split('.')[1:]:
        ob = getattr(ob, mod)

    for attr in attr_spec.split('.'):
        ob = getattr(ob, attr)
    return ob


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
    """
    Extract a view keyword argument from the request object.

    """
    query = attrgetter('query')
    form = attrgetter('form')
    cookies = attrgetter('cookies')

    #: Source for the request variable
    source = form

    #: Exceptions that signal the converter could not do its job due to invalid
    #: input
    converter_exceptions = (ValueError, TypeError)

    _marker = object()

    def __init__(self, converter=None, key=None,
                 default=_marker, exception=BadRequest):

        self.formkey = key
        self.default = default
        self.required = default is self._marker
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
                raise self.exception('No value provided for %s' %\
                                     (self.formkey,))
            return self.default

        try:
            if self.converter is not None:
                value = self.converter(value)
        except self.converter_exceptions:
            raise self.exception('%r is not a valid value for %s' %\
                                 (value, self.formkey,))

        return value


class CookieArg(RequestArg):
    """\
    Extract a view keyword argument from ``request.cookies``.

    Example::

        @app.route('/', GET, message=CookieArg(key='msg', default=None))
        def view(request, message):
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
        def view(request, a, b):
            return Response(['a + b = %d' % (a + b)])
    """
    source = RequestArg.query


class FormArg(RequestArg):
    """\
    Extract a view keyword argument from ``request.form``.

    Example::

        @app.route('/mul', POST, a=FormArg(int), b=FormArg(int))
        def view(request, a, b):
            return Response(['a * b = %d' % (a * b)])

    """
    source = RequestArg.form
