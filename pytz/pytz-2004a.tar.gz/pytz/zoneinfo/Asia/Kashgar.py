'''
tzinfo timezone information for Asia/Kashgar.

Generated from the Olson timezone database:
    ftp://elsie.nci.nih.gov/pub/tz*.tar.gz
'''

from pytz.tzinfo import DstTzInfo
from pytz.tzinfo import memorized_datetime as datetime
from pytz.tzinfo import memorized_ttinfo as ttinfo

class Kashgar(DstTzInfo):
    '''Asia/Kashgar timezone definition. See datetime.tzinfo for details'''

    _zone = 'Asia/Kashgar'

    _utc_transition_times = [
        datetime(   1,  1,  1,  0,  0,  0), #  18236     0 LMT
        datetime(1927, 12, 31, 18, 56,  4), #  19800     0 KAST
        datetime(1939, 12, 31, 18, 30,  0), #  18000     0 KAST
        datetime(1980,  4, 30, 19,  0,  0), #  28800     0 CST
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
        ttinfo( 18236,      0,  'LMT'),
        ttinfo( 19800,      0, 'KAST'),
        ttinfo( 18000,      0, 'KAST'),
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

Kashgar = Kashgar() # Singleton

