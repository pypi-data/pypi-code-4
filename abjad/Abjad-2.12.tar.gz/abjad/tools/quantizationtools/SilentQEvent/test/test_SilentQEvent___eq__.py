from abjad.tools import quantizationtools


def test_SilentQEvent___eq___01():

    a = quantizationtools.SilentQEvent(1000)
    b = quantizationtools.SilentQEvent(1000)

    assert a == b


def test_SilentQEvent___eq___02():

    a = quantizationtools.SilentQEvent(1000)
    b = quantizationtools.SilentQEvent(1000, ['foo', 'bar', 'baz'])
    c = quantizationtools.SilentQEvent(9999)

    assert a != b
    assert a != c
