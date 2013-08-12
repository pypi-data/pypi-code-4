from functools import wraps
from sample_data_utils.exception import MaxAttemptException


def infinite():
    """
        auto inc generator
    """
    i = 0
    while 1:
        yield i
        i += 1


sequence_counters = {}


def sequence(prefix, cache=sequence_counters):
    """
    generator that returns an unique string

    :param prefix: prefix of string
    :param cache: cache used to store the last used number

    >>> next(sequence('abc'))
    'abc-0'
    >>> next(sequence('abc'))
    'abc-1'
    """
    if prefix not in cache:
        cache[prefix] = infinite()
    yield "{0}-{1}".format(prefix, next(cache[prefix]))


def _get_memoized_value(func, args, kwargs):
    """Used internally by memoize decorator to get/store function results"""
    key = (repr(args), repr(kwargs))

    if not key in func._cache_dict:
        ret = func(*args, **kwargs)
        func._cache_dict[key] = ret

    return func._cache_dict[key]


def memoize(func):
    """Decorator that stores function results in a dictionary to be used on the
    next time that the same arguments were informed."""

    func._cache_dict = {}

    @wraps(func)
    def _inner(*args, **kwargs):
        return _get_memoized_value(func, args, kwargs)

    return _inner

_cache_unique = {}


def unique(func, num_args=0, max_attempts=100, cache=None):
    """
    wraps a function so that produce unique results

    :param func:
    :param num_args:

    >>> import random
    >>> choices = [1,2]
    >>> a = unique(random.choice, 1)
    >>> a,b = a(choices), a(choices)
    >>> a == b
    False
    """
    if cache is None:
        cache = _cache_unique

    @wraps(func)
    def wrapper(*args):
        key = "%s_%s" % (str(func.__name__), str(args[:num_args]))
        attempt = 0
        while attempt < max_attempts:
            attempt += 1
            drawn = cache.get(key, [])
            result = func(*args)
            if result not in drawn:
                drawn.append(result)
                cache[key] = drawn
                return result

        raise MaxAttemptException()

    return wrapper
