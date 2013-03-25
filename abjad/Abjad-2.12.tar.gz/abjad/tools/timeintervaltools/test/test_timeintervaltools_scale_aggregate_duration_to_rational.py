from abjad.tools.timeintervaltools import *
from abjad.tools.timeintervaltools._make_test_intervals import _make_test_intervals
from fractions import Fraction
import py.test


def test_timeintervaltools_scale_aggregate_duration_to_rational_01():
    a = TimeInterval(Fraction(-1, 2), 1)
    b = TimeInterval(2, Fraction(7, 3))
    tree = TimeIntervalTree([a, b])
    rational = 3
    result = scale_aggregate_duration_to_rational(tree, rational)
    assert result.duration == 3
    assert [x.signature for x in result] == \
        [(Fraction(-1, 2), Fraction(37, 34)), (Fraction(73, 34), Fraction(5, 2))]

def test_timeintervaltools_scale_aggregate_duration_to_rational_02():
    a = TimeInterval(Fraction(-1, 2), 1)
    b = TimeInterval(2, Fraction(7, 3))
    tree = TimeIntervalTree([a, b])
    rational = -1
    py.test.raises(AssertionError,
        "result = scale_aggregate_duration_to_rational(tree, rational)")

def test_timeintervaltools_scale_aggregate_duration_to_rational_03():
    a = TimeInterval(Fraction(-1, 2), 1)
    b = TimeInterval(2, Fraction(7, 3))
    tree = TimeIntervalTree([a, b])
    rational = 0
    py.test.raises(AssertionError,
        "result = scale_aggregate_duration_to_rational(tree, rational)")
