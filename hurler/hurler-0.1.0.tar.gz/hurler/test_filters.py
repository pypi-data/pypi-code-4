from __future__ import absolute_import

from .filters import filter, filter_simple


@filter
def string_length_filter(length=1):
    def filter(string):
        return len(string) > length
    return filter


@filter_simple
def always_false(*args, **kwargs):
    return False


@filter_simple
def always_true(*args, **kwargs):
    return True


@filter
def always_normal_true():
    return lambda *args, **kwargs: True


def test_simple_chaining():
    """
    Tests the ability to chain filters.
    """
    tester = lambda x: x + x

    for i in xrange(100):
        tester = always_true(tester)

    assert tester("x") == "xx"


def test_simple_non_chaining():
    """
    Tests the ability to chain filters with interruptions in the chain.
    """
    tester = lambda x: x + x

    def interrupt(func):
        def wrapper(x):
            return func(x + x)
        return wrapper

    for i in xrange(100):
        if i % 25 == 0:
            tester = interrupt(tester)
        tester = always_true(tester)

    assert tester("x") == "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"


def test_normal_chaining():
    """
    Tests the ability to chain filters.
    """
    tester = lambda x: x + x

    for i in xrange(100):
        tester = always_normal_true()(tester)

    assert tester("x") == "xx"


def test_normal_non_chaining():
    """
    Tests the ability to chain filters with interruptions in the chain.
    """
    tester = lambda x: x + x

    def interrupt(func):
        def wrapper(x):
            return func(x + x)
        return wrapper

    for i in xrange(100):
        if i % 25 == 0:
            tester = interrupt(tester)
        tester = always_normal_true()(tester)

    assert tester("x") == "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"


def test_negative_filter():
    """
    Tests if a filter returning False stops the call.
    """
    tester = lambda x: x + x

    tester = always_false(tester)

    assert tester("x") is None


def test_positive_filter():
    """
    Tests if a filter returns the normal return value if filter
    is True.
    """
    tester = lambda x: x + x

    tester = always_true(tester)

    assert tester("x") == "xx"


def test_length_filter():
    """
    Tests if a conditional non-simple filter works.
    """
    @string_length_filter(length=4)
    def tester(x):
        return x + x

    assert tester("x") is None
    assert tester("x" * 5) == "x" * 10
