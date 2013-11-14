from datetime import datetime
from functools import wraps
import inspect
import time
import urllib

from lxml.etree import XMLSyntaxError
import lxml.html

from .exceptions import ParseError


def current_time():
    """
    Returns the time in seconds since the epoch as a floating point number.

    """
    return time.time()


def sleep(seconds):
    """
    Delays execution for a given number of seconds.

    """
    time.sleep(seconds)


def utcnow():
    return datetime.utcnow()


def cached(timeout):
    """
    Returns a decorator that caches results of function calls. Cached results
    are kept at most *timeout* seconds.

    """
    def decorator(f):
        cache = {}
        argspec = inspect.getargspec(f)
        defaults = argspec.defaults or tuple()
        num_args = len(argspec.args)
        num_defaults = len(defaults)
        arg_indices = {name: i for i, name in enumerate(argspec.args)}

        def make_key(args, kwargs):
            resolved_args = [None] * num_args
            resolved_args[-num_defaults:] = defaults
            resolved_args[:len(args)] = args
            for k in kwargs:
                if k in arg_indices:
                    resolved_args[arg_indices[k]] = kwargs[k]
            key = (tuple(resolved_args),
                    frozenset((k, kwargs[k]) for k in kwargs if k not in arg_indices))
            return key

        @wraps(f)
        def wrapper(*args, **kwargs):
            now = current_time()
            key = make_key(args, kwargs)
            if key in cache:
                value, cached_time = cache[key]
                if cached_time + timeout > now:
                    return value
            value = f(*args, **kwargs)
            cache[key] = (value, now)
            return value

        return wrapper
    return decorator


def parse_html(html):
    try:
        return lxml.html.fromstring(html)
    except XMLSyntaxError:
        raise ParseError('Unable to parse HTML')


def urlencode_utf8(query):
    if hasattr(query, 'items'):
        # mapping objects
        query = query.items()
    query_utf8 = []
    for key, value in query:
        try:
            query_utf8.append((key, str(value)))
        except UnicodeEncodeError:
            query_utf8.append((key, unicode(value).encode('UTF-8')))
    return urllib.urlencode(query_utf8)
