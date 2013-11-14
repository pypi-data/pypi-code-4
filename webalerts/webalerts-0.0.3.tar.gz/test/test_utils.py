import pytest

from webalerts.utils import cached
import webalerts.utils


def test_cached():
    now = 0
    webalerts.utils.current_time = lambda: now

    ext = 0
    @cached(30)
    def f(a, b=None, c=None, *args, **kwargs):
        return (a, b, c, ext)

    assert f(1) == (1, None, None, 0)
    ext = 42
    assert f(1) == (1, None, None, 0), "it should return cached value"
    assert f(1, None, None) == (1, None, None, 0), "it should resolve arguments"
    now = 50  # expires cache
    assert f(1) == (1, None, None, 42)
    assert f(1, 'kwarg') == (1, 'kwarg', None, 42)
    ext = 1000
    assert f(1, b='kwarg') == (1, 'kwarg', None, 42)
    assert f(1, c='kwarg') == (1, None, 'kwarg', 1000)
    assert f(1, 2, 3) == (1, 2, 3, 1000)
    ext = 1001
    assert f(1, 2, 3, 4, x=100) == (1, 2, 3, 1001)
    ext = -5
    assert f(1, 2, 3, 4, x=100) == (1, 2, 3, 1001), "it should return cached value"
    now = 100  # expires cache
    assert f(1, 2, 3, 4, x=100) == (1, 2, 3, -5)


def test_cached_no_args():
    now = 0
    webalerts.utils.current_time = lambda: now

    ext = 0
    @cached(30)
    def f():
        return ext

    assert f() == 0
    ext = 1
    assert f() == 0
    now = 50
    assert f() == 1


def test_cached_bound_function():
    now = 0
    webalerts.utils.current_time = lambda: now

    ext = 0
    class Foo(object):
        @cached(60)
        def bar(self, a):
            return (a, ext)

    foo = Foo()
    assert foo.bar(1) == (1, 0)
    ext = 99
    assert foo.bar(1) == (1, 0)
    now = 100
    assert foo.bar(1) == (1, 99)
