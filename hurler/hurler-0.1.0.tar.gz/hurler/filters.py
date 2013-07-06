"""
Implementation of a decorator to create so called `filter` decorators.

These are decorators that call the function decorated originally and
depending on their return value, which is either :const:`True` or
:const:`False` will call the decorated function. An example explains
this better than words, so here is one:

    >>> # This creates a filter that is always True
    >>> @filter_simple
    ... def always_true(*args, **kwargs):
    ...     return True
    ...
    >>> # This creates a filter that is always False
    >>> @filter_simple
    ... def always_false(*args, **kwargs):
    ...     return False
    ...
    >>> # Now we can test the filter.
    >>> @always_true
    ... def print_hello():
    ...     print("Hello World")
    ...
    >>> print_hello() # this should work fine since we filter True
    Hello World
    >>> # Now we add a filter that is always False, this should not print
    >>> does_not_print = always_false(print_hello)
    >>> does_not_print()

"""
from __future__ import unicode_literals
from __future__ import absolute_import


class Filter(object):
    """
    A class that can contain multiple filters to check against. If any
    of the filters return :const:`False` the callback is not called.
    """
    def __init__(self, filter, callback):
        super(Filter, self).__init__()

        # A list of filters we want to apply.
        self._filters = [filter]
        # The callback we want to call if all filters work
        self._callback = callback

    def check_filter(self, args, kwargs):
        """
        Calls all filters in the :attr:`_filters` list and if all of them
        return :const:`True` will return :const:`True`. If any of the filters
        return :const:`False` will return :const:`True` instead.

        This method is equal to the following snippet:
            `all(f(*args, **kwargs) for f in self.filters)`
        """
        for f in self._filters:
            if not f(*args, **kwargs):
                return False

        return True

    def add_filter(self, filter):
        """
        Adds a filter to the list of filters to be called.
        """
        self._filters.append(filter)

    def __call__(self, *args, **kwargs):
        if self.check_filter(args, kwargs):
            return self._callback(*args, **kwargs)
        return None


def filter(filter_creator):
    """
    Creates a decorator that can be used as a filter.

    .. warning::
        This is currently not compatible with most other decorators, if
        you are using a decorator that isn't part of `hurler` you should
        take caution.
    """
    filter_func = [None]

    def function_getter(function):
        if isinstance(function, Filter):
            function.add_filter(filter)

            return function
        else:
            return Filter(
                filter=filter_func[0],
                callback=function,
            )

    def filter_decorator(*args, **kwargs):
        filter_function = filter_creator(*args, **kwargs)

        filter_func[0] = filter_function

        return function_getter

    return filter_decorator


def filter_simple(filter):
    """
    A simpler version of :func:`filter`. This instead assumes the decorated
    function is already a valid filter function, and uses it directly.
    """
    def function_getter(function):
        if isinstance(function, Filter):
            function.add_filter(filter)

            return function
        else:
            return Filter(
                filter=filter,
                callback=function,
            )

    return function_getter
