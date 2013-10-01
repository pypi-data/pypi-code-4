'''
tzinfo timezone information for Africa/Johannesburg.

Generated from the Olson timezone database:
    ftp://elsie.nci.nih.gov/pub/tz*.tar.gz
'''

from pytz.tzinfo import DstTzInfo
from pytz.tzinfo import memorized_datetime as datetime
from pytz.tzinfo import memorized_ttinfo as ttinfo

class Johannesburg(DstTzInfo):
    '''Africa/Johannesburg timezone definition. See datetime.tzinfo for details'''

    _zone = 'Africa/Johannesburg'

    _utc_transition_times = [
        datetime(   1,  1,  1,  0,  0,  0), #   5400     0 SAST
        datetime(1903,  2, 28, 22, 30,  0), #   7200     0 SAST
        datetime(1942,  9, 20,  0,  0,  0), #  10800  3600 SAST
        datetime(1943,  3, 20, 23,  0,  0), #   7200     0 SAST
        datetime(1943,  9, 19,  0,  0,  0), #  10800  3600 SAST
        datetime(1944,  3, 18, 23,  0,  0), #   7200     0 SAST
        ]

    _transition_info = [
        ttinfo(  5400,      0, 'SAST'),
        ttinfo(  7200,      0, 'SAST'),
        ttinfo( 10800,   3600, 'SAST'),
        ttinfo(  7200,      0, 'SAST'),
        ttinfo( 10800,   3600, 'SAST'),
        ttinfo(  7200,      0, 'SAST'),
        ]

Johannesburg = Johannesburg() # Singleton

