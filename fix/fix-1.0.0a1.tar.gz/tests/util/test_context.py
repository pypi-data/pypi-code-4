"""Tests for the `fix.util.Context` class."""

from fix.util import Context

KWARGS = {"squee": "kapow", "boing": "thunk"}


def test_exists():
    """`fix.util.Context` function exists"""
    assert isinstance(Context, type)


def test_instantiate():
    """`Context` class can be instantiated"""
    context = Context()
    assert isinstance(context, Context)


def test_instantiate_dict():
    """`Context` class can be instantiated with a dict"""
    context = Context(KWARGS)
    assert isinstance(context, Context)


def test_instantiate_kwargs():
    """`Context` class can be instantiated with keyword arguments"""
    context = Context(**KWARGS)
    assert isinstance(context, Context)


def test_attr_access():
    """`Context` instance has attribute access"""
    context = Context(**KWARGS)
    assert context.boing == "thunk"  # pylint: disable=E1101


def test_key_access():
    """`Context` instance has key access"""
    context = Context(**KWARGS)
    assert context["squee"] == "kapow"


def test_repr():
    """`Context` instance has a sensible `repr` value"""
    kwarg_str = ", ".join("%s=%r" % kv for kv in sorted(KWARGS.items()))
    assert repr(Context(**KWARGS)) == "Context(%s)" % kwarg_str
