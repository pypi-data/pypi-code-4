'''
tzinfo timezone information for Singapore.

Generated from the Olson timezone database:
    ftp://elsie.nci.nih.gov/pub/tz*.tar.gz
'''

from pytz.tzinfo import DstTzInfo
from pytz.tzinfo import memorized_datetime as datetime
from pytz.tzinfo import memorized_ttinfo as ttinfo

class Singapore(DstTzInfo):
    '''Singapore timezone definition. See datetime.tzinfo for details'''

    _zone = 'Singapore'

    _utc_transition_times = [
        datetime(   1,  1,  1,  0,  0,  0), #  24925     0 SMT
        datetime(1905,  5, 31, 17,  4, 35), #  25200     0 MALT
        datetime(1932, 12, 31, 17,  0,  0), #  26400  1200 MALST
        datetime(1935, 12, 31, 16, 40,  0), #  26400     0 MALT
        datetime(1941,  8, 31, 16, 40,  0), #  27000     0 MALT
        datetime(1942,  2, 15, 16, 30,  0), #  32400     0 JST
        datetime(1945,  9, 11, 15,  0,  0), #  27000     0 MALT
        datetime(1965,  8,  8, 16, 30,  0), #  27000     0 SGT
        datetime(1981, 12, 31, 16, 30,  0), #  28800     0 SGT
        ]

    _transition_info = [
        ttinfo( 24925,      0,  'SMT'),
        ttinfo( 25200,      0, 'MALT'),
        ttinfo( 26400,   1200, 'MALST'),
        ttinfo( 26400,      0, 'MALT'),
        ttinfo( 27000,      0, 'MALT'),
        ttinfo( 32400,      0,  'JST'),
        ttinfo( 27000,      0, 'MALT'),
        ttinfo( 27000,      0,  'SGT'),
        ttinfo( 28800,      0,  'SGT'),
        ]

Singapore = Singapore() # Singleton

