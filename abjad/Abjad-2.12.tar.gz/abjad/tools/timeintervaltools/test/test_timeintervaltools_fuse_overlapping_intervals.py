from abjad.tools.timeintervaltools import *
from abjad.tools.timeintervaltools._make_test_intervals import _make_test_intervals
from fractions import Fraction
import py.test


def test_timeintervaltools_fuse_overlapping_intervals_01():
    tree = TimeIntervalTree(_make_test_intervals())
    fused_tree = fuse_overlapping_intervals(tree)
    target_signatures = [(0, 3), (5, 13), (15, 23), (25, 30), (32, 34), (34, 37)]
    actual_signatures = [interval.signature for interval in fused_tree]
    assert target_signatures == actual_signatures
    assert tree.duration == fused_tree.duration
