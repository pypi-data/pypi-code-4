"""Tests for the `ook.decorators.patch` function."""

try:
    reload
except NameError:
    from imp import reload  # pylint: disable=E0611,W0622

import itertools

from types import FunctionType

from ook import patch
from ook.decorators import PY_VERSION
from ook.util import Version

import tests.decorators.examples

from tests import VERSION_ARGS


def test_exists():
    """`ook.patch` function exists"""
    assert isinstance(patch, FunctionType)


def test_undecorated():
    """`tests.decorators.examples.example()` returns 'undecorated'"""
    reload(tests.decorators.examples)
    assert tests.decorators.examples.example() == "undecorated"


def check_version_args(kwargs, *args):
    """`ook.patch` function respects version arguments"""
    reload(tests.decorators.examples)

    @patch(tests.decorators.examples, *args, **kwargs)
    def example():
        """Return version arguments."""
        return args, kwargs

    ge_min = ("min" not in kwargs) or (PY_VERSION >= Version(kwargs["min"]))
    le_max = ("max" not in kwargs) or (PY_VERSION <= Version(kwargs["max"]))
    matches_specified = (not args) or (PY_VERSION in map(Version, args))
    if matches_specified and ge_min and le_max:
        assert tests.decorators.examples.example == example
        assert tests.decorators.examples.example() == (args, kwargs)
    else:
        assert tests.decorators.examples.example != example
        assert tests.decorators.examples.example() == "undecorated"


def test_version_args():
    """`ook.patch` function respects groups of version arguments"""
    for nargs in range(len(VERSION_ARGS) + 1):
        # pylint: disable=E1101
        for args in itertools.combinations(VERSION_ARGS, nargs):
            kwargs = {}
            for keys in ([], ["min"], ["max"], ["min", "max"]):
                for key in keys:
                    for value in VERSION_ARGS:
                        kwargs[key] = value
                yield (check_version_args, kwargs) + tuple(args)
