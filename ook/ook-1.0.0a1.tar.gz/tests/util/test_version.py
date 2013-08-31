"""Tests for the `ook.util.Version` class."""

from operator import eq
from operator import ge
from operator import gt
from operator import le
from operator import lt
from operator import ne

from nose.tools import raises

from ook.util import Version

from tests import VERSION_ARGS


def test_exists():
    """`Version` class exists"""
    assert isinstance(Version, type)


def check_instantiate(version):
    """`Version` class can be instantiated"""
    assert isinstance(version, Version)


def test_instantiate():
    """`Version` class can be instantiated"""
    for version in map(Version, VERSION_ARGS):
        yield check_instantiate, version


def check_repr(version):
    """`Version` instance has a sensible `repr` value"""
    assert repr(version) == "Version(%r)" % str(version)


def test_repr():
    """`Version` instances have sensible `repr` values"""
    for version in map(Version, VERSION_ARGS):
        yield check_repr, version


def check_mmm(version, index, attr):
    """`Version` instance has sensible `major`|`minor`|`micro` attributes"""
    try:
        expected_value = int(str(version).split(".")[index])
    except IndexError:
        expected_value = None
    except ValueError:
        expected_value = float("inf")
    assert attr == expected_value


def test_mmm():
    """`Version` instances have sensible `major`|`minor`|`micro` attributes"""
    attrs = ("major", "minor", "micro")
    for version in map(Version, VERSION_ARGS):
        for index, attr in enumerate(getattr(version, a) for a in attrs):
            yield check_mmm, version, index, attr


def check_compare(oper, ver1, ver2):
    """``Version` instances compare as expected"""
    assert oper(ver1, ver2) == oper(ver1.truncate(ver2), ver2.truncate(ver1))


def test_compare():
    """``Version` instances compare as expected"""
    for ver1 in map(Version, VERSION_ARGS):
        for ver2 in map(Version, VERSION_ARGS):
            for oper in (eq, ge, gt, le, lt, ne):
                yield check_compare, oper, ver1, ver2


@raises(TypeError)
def check_compare_unorderable(oper, version, nonversion):
    """Comparing `Version` instance against non-`Version` fails"""
    oper(version, nonversion)


def test_compare_unorderable():
    """Comparing `Version` instances against non-`Version`s fails"""
    for nonversion in VERSION_ARGS:
        if isinstance(nonversion, Version):
            continue
        for version in map(Version, VERSION_ARGS):
            for oper in (ge, gt, le, lt):
                yield check_compare_unorderable, oper, version, nonversion
