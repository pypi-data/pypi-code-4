from abjad import *


def test_Timespan_starts_at_or_after_offset_01():
    timespan = timespantools.Timespan(0, 10)
    offset = durationtools.Offset(-5)
    assert timespan.starts_at_or_after_offset(offset)

def test_Timespan_starts_at_or_after_offset_02():
    timespan = timespantools.Timespan(0, 10)
    offset = durationtools.Offset(0)
    assert timespan.starts_at_or_after_offset(offset)

def test_Timespan_starts_at_or_after_offset_03():
    timespan = timespantools.Timespan(0, 10)
    offset = durationtools.Offset(5)
    assert not timespan.starts_at_or_after_offset(offset)

def test_Timespan_starts_at_or_after_offset_04():
    timespan = timespantools.Timespan(0, 10)
    offset = durationtools.Offset(10)
    assert not timespan.starts_at_or_after_offset(offset)

def test_Timespan_starts_at_or_after_offset_05():
    timespan = timespantools.Timespan(0, 10)
    offset = durationtools.Offset(15)
    assert not timespan.starts_at_or_after_offset(offset)


