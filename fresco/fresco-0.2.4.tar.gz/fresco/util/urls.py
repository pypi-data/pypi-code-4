"""\
Utility functions for URL building and manipulation
"""

import fresco
from fresco.multidict import MultiDict
from urllib import quote_plus

__all__ = 'join_path', 'strip_trailing_slashes'


def join_path(a, b):
    """
    Join two URL path segments together.
    Unlike ``os.path.join``, this removes leading slashes before joining the
    paths, so absolute paths are appended as if they were relative.

    Synopsis::

        >>> join_path('/', '/abc')
        '/abc'

        >>> join_path('/', '/abc/')
        '/abc/'

        >>> join_path('/foo', '/bar/')
        '/foo/bar/'

        >>> join_path('/foo/', '/bar/')
        '/foo/bar/'

        >>> join_path('/foo', 'bar')
        '/foo/bar'
    """

    if not b:
        return a

    while a and a[-1] == '/':
        a = a[:-1]

    while b and b[0] == '/':
        b = b[1:]

    return a + '/' + b


def strip_trailing_slashes(path):
    """\
    Remove trailing slashes from the given path.

    :param path: a path, eg ``'/foo/bar/'``
    :return: The path with trailing slashes removed, eg ``'/foo/bar'``
    """
    while path and path[-1] == '/':
        path = path[:-1]
    return path


def normpath(path):
    """
    Return ``path`` normalized to remove '../' etc.

    This differs from ``posixpath.normpath`` in that:

    * trailing slashes are preserved
    * multiple consecutive slashes are always condensed to a single slash

    Examples::

        >>> normpath('/hello/../goodbye')
        '/goodbye'
        >>> normpath('//etc/passwd')
        '/etc/passwd'
        >>> normpath('../../../../etc/passwd')
        'etc/passwd'
        >>> normpath('/etc/passwd/')
        '/etc/passwd/'
    """
    segments = path.split('/')
    newpath = []
    last = len(segments) - 1
    for pos, seg in enumerate(segments):
        if seg == '.':
            seg = ''

        if seg == '':
            allow_empty = (
                pos == 0
                or pos == last and newpath and newpath[-1] != ''
                or pos == last and newpath == ['']
            )
            if not allow_empty:
                continue

        if seg == '..':
            if newpath and newpath != ['']:
                newpath.pop()
            continue

        newpath.append(seg)

    return '/'.join(newpath)


def make_query(data=None, separator=';', charset=None, **kwargs):
    """\
    Return a query string formed from the given dictionary data.

    Note that the pairs are separated using a semicolon, in accordance with
    `the W3C recommendation
<http://www.w3.org/TR/1999/REC-html401-19991224/appendix/notes.html#h-B.2.2>`_

    If no encoding is given, unicode values are encoded using the character set
    specified by ``fresco.DEFAULT_CHARSET``.

    Basic usage::

        >>> make_query({'search': u'foo bar', 'type': u'full'})
        'search=foo+bar;type=full'

        >>> make_query(search=u'foo', type=u'quick')
        'search=foo;type=quick'

    Changing the separator to '&'::

        >>> make_query({'search': u'foo', 'type': u'full'}, separator='&')
        'search=foo&type=full'

    Multiple values can be provided per key::

        >>> make_query(search=[u'foo', u'bar'])
        'search=foo;search=bar'

    Exclude values by setting them to ``None``::

        >>> make_query(x=1, y=None)
        'x=1'

    """
    if isinstance(data, MultiDict):
        items = data.allitems()
    elif isinstance(data, dict):
        items = data.items()
    elif data is None:
        items = []
    else:
        items = list(data)
    items += kwargs.items()

    if charset is None:
        charset = fresco.DEFAULT_CHARSET

    # Sort data items for a predictable order in tests
    items.sort()
    items = _repeat_keys(items)
    items = ((k, v) for k, v in items if v is not None)
    return separator.join([
        _qs_frag(k, v, charset=charset) for k, v in items
    ])


def _qs_frag(key, value, charset=None):
    u"""
    Return a fragment of a query string in the format 'key=value'.

    >>> _qs_frag('search-by', 'author, editor')
    'search-by=author%2C+editor'

    If no encoding is specified, unicode values are encoded using the character
    set specified by ``fresco.DEFAULT_CHARSET``.
    """
    if charset is None:
        charset = fresco.DEFAULT_CHARSET

    return quote_plus(_make_bytestr(key, charset)) \
            + '=' \
            + quote_plus(_make_bytestr(value, charset))


def _make_bytestr(ob, charset):
    u"""
    Return a byte string conversion of the given object. If the object is a
    unicode string, encode it with the given encoding.

    Example::

        >>> _make_bytestr(1, 'utf-8')
        '1'
        >>> _make_bytestr(u'a', 'utf-8')
        'a'
    """
    if isinstance(ob, unicode):
        return ob.encode(charset)
    return str(ob)

def _repeat_keys(iterable):
    u"""
    Return a list of ``(key, scalar_value)`` tuples given an iterable
    containing ``(key, iterable_or_scalar_value)``.

    Example::

        >>> list(
        ...     _repeat_keys([('a', 'b')])
        ... )
        [('a', 'b')]
        >>> list(
        ...     _repeat_keys([('a', ['b', 'c'])])
        ... )
        [('a', 'b'), ('a', 'c')]
    """

    for key, value in iterable:
        if isinstance(value, basestring):
            value = [value]
        else:
            try:
                value = iter(value)
            except TypeError:
                value = [value]

        for subvalue in value:
            yield key, subvalue
