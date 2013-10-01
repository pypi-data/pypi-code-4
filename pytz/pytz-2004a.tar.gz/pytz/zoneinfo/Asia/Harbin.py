'''
tzinfo timezone information for Asia/Harbin.

Generated from the Olson timezone database:
    ftp://elsie.nci.nih.gov/pub/tz*.tar.gz
'''

from pytz.tzinfo import DstTzInfo
from pytz.tzinfo import memorized_datetime as datetime
from pytz.tzinfo import memorized_ttinfo as ttinfo

class Harbin(DstTzInfo):
    '''Asia/Harbin timezone definition. See datetime.tzinfo for details'''

    _zone = 'Asia/Harbin'

    _utc_transition_times = [
        datetime(   1,  1,  1,  0,  0,  0), #  30404     0 LMT
        datetime(1927, 12, 31, 15, 33, 16), #  30600     0 CHAT
        datetime(1932,  2, 29, 15, 30,  0), #  28800     0 CST
        datetime(1939, 12, 31, 16,  0,  0), #  32400     0 CHAT
        datetime(1966,  4, 30, 15,  0,  0), #  30600     0 CHAT
        datetime(1980,  4, 30, 15, 30,  0), #  28800     0 CST
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
        ttinfo( 30404,      0,  'LMT'),
        ttinfo( 30600,      0, 'CHAT'),
        ttinfo( 28800,      0,  'CST'),
        ttinfo( 32400,      0, 'CHAT'),
        ttinfo( 30600,      0, 'CHAT'),
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

Harbin = Harbin() # Singleton

