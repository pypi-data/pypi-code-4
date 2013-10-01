'''
tzinfo timezone information for PRC.

Generated from the Olson timezone database:
    ftp://elsie.nci.nih.gov/pub/tz*.tar.gz
'''

from pytz.tzinfo import DstTzInfo
from pytz.tzinfo import memorized_datetime as datetime
from pytz.tzinfo import memorized_ttinfo as ttinfo

class PRC(DstTzInfo):
    '''PRC timezone definition. See datetime.tzinfo for details'''

    _zone = 'PRC'

    _utc_transition_times = [
        datetime(   1,  1,  1,  0,  0,  0), #  29152     0 LMT
        datetime(1927, 12, 31, 15, 54,  8), #  28800     0 CST
        datetime(1940,  6,  2, 16,  0,  0), #  32400  3600 CDT
        datetime(1940,  9, 30, 15,  0,  0), #  28800     0 CST
        datetime(1941,  3, 15, 16,  0,  0), #  32400  3600 CDT
        datetime(1941,  9, 30, 15,  0,  0), #  28800     0 CST
        datetime(1986,  5,  3, 16,  0,  0), #  32400  3600 CDT
        datetime(1986,  9, 13, 15,  0,  0), #  28800     0 CST
        datetime(1987,  4, 11, 16,  0,  0), #  32400  3600 CDT
        datetime(1987,  9, 12, 15,  0,  0), #  28800     0 CST
        datetime(1988,  4,  9, 16,  0,  0), #  32400  3600 CDT
        datetime(1988,  9, 10, 15,  0,  0), #  28800     0 CST
        datetime(1989,  4, 15, 16,  0,  0), #  32400  3600 CDT
        datetime(1989,  9, 16, 15,  0,  0), #  28800     0 CST
        datetime(1990,  4, 14, 16,  0,  0), #  32400  3600 CDT
        datetime(1990,  9, 15, 15,  0,  0), #  28800     0 CST
        datetime(1991,  4, 13, 16,  0,  0), #  32400  3600 CDT
        datetime(1991,  9, 14, 15,  0,  0), #  28800     0 CST
        ]

    _transition_info = [
        ttinfo( 29152,      0,  'LMT'),
        ttinfo( 28800,      0,  'CST'),
        ttinfo( 32400,   3600,  'CDT'),
        ttinfo( 28800,      0,  'CST'),
        ttinfo( 32400,   3600,  'CDT'),
        ttinfo( 28800,      0,  'CST'),
        ttinfo( 32400,   3600,  'CDT'),
        ttinfo( 28800,      0,  'CST'),
        ttinfo( 32400,   3600,  'CDT'),
        ttinfo( 28800,      0,  'CST'),
        ttinfo( 32400,   3600,  'CDT'),
        ttinfo( 28800,      0,  'CST'),
        ttinfo( 32400,   3600,  'CDT'),
        ttinfo( 28800,      0,  'CST'),
        ttinfo( 32400,   3600,  'CDT'),
        ttinfo( 28800,      0,  'CST'),
        ttinfo( 32400,   3600,  'CDT'),
        ttinfo( 28800,      0,  'CST'),
        ]

PRC = PRC() # Singleton

