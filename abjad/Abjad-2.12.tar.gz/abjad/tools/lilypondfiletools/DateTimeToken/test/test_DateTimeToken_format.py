from abjad import *


def test_DateTimeToken_format_01():

    date_time_token = lilypondfiletools.DateTimeToken()
    assert isinstance(date_time_token.lilypond_format, str)
    assert len(date_time_token.lilypond_format) == 16
