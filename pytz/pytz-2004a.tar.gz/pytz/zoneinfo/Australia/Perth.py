'''
tzinfo timezone information for Australia/Perth.

Generated from the Olson timezone database:
    ftp://elsie.nci.nih.gov/pub/tz*.tar.gz
'''

from pytz.tzinfo import DstTzInfo
from pytz.tzinfo import memorized_datetime as datetime
from pytz.tzinfo import memorized_ttinfo as ttinfo

class Perth(DstTzInfo):
    '''Australia/Perth timezone definition. See datetime.tzinfo for details'''

    _zone = 'Australia/Perth'

    _utc_transition_times = [
        datetime(   1,  1,  1,  0,  0,  0), #  28800     0 WST
        datetime(1916, 12, 31, 16,  1,  0), #  32400  3600 WST
        datetime(1917,  3, 24, 17,  0,  0), #  28800     0 WST
        datetime(1941, 12, 31, 18,  0,  0), #  32400  3600 WST
        datetime(1942,  3, 28, 17,  0,  0), #  28800     0 WST
        datetime(1942,  9, 26, 18,  0,  0), #  32400  3600 WST
        datetime(1943,  3, 27, 17,  0,  0), #  28800     0 WST
        datetime(1974, 10, 26, 18,  0,  0), #  32400  3600 WST
        datetime(1975,  3,  1, 18,  0,  0), #  28800     0 WST
        datetime(1983, 10, 29, 18,  0,  0), #  32400  3600 WST
        datetime(1984,  3,  3, 18,  0,  0), #  28800     0 WST
        datetime(1991, 11, 16, 18,  0,  0), #  32400  3600 WST
        datetime(1992,  2, 29, 18,  0,  0), #  28800     0 WST
        ]

    _transition_info = [
        ttinfo( 28800,      0,  'WST'),
        ttinfo( 32400,   3600,  'WST'),
        ttinfo( 28800,      0,  'WST'),
        ttinfo( 32400,   3600,  'WST'),
        ttinfo( 28800,      0,  'WST'),
        ttinfo( 32400,   3600,  'WST'),
        ttinfo( 28800,      0,  'WST'),
        ttinfo( 32400,   3600,  'WST'),
        ttinfo( 28800,      0,  'WST'),
        ttinfo( 32400,   3600,  'WST'),
        ttinfo( 28800,      0,  'WST'),
        ttinfo( 32400,   3600,  'WST'),
        ttinfo( 28800,      0,  'WST'),
        ]

Perth = Perth() # Singleton

