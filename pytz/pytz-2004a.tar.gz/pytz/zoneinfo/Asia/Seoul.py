'''
tzinfo timezone information for Asia/Seoul.

Generated from the Olson timezone database:
    ftp://elsie.nci.nih.gov/pub/tz*.tar.gz
'''

from pytz.tzinfo import DstTzInfo
from pytz.tzinfo import memorized_datetime as datetime
from pytz.tzinfo import memorized_ttinfo as ttinfo

class Seoul(DstTzInfo):
    '''Asia/Seoul timezone definition. See datetime.tzinfo for details'''

    _zone = 'Asia/Seoul'

    _utc_transition_times = [
        datetime(   1,  1,  1,  0,  0,  0), #  30600     0 KST
        datetime(1904, 11, 30, 15, 30,  0), #  32400     0 KST
        datetime(1927, 12, 31, 15,  0,  0), #  30600     0 KST
        datetime(1931, 12, 31, 15, 30,  0), #  32400     0 KST
        datetime(1954,  3, 20, 15,  0,  0), #  28800     0 KST
        datetime(1960,  5, 14, 16,  0,  0), #  32400  3600 KDT
        datetime(1960,  9, 12, 15,  0,  0), #  28800     0 KST
        datetime(1961,  8,  9, 16,  0,  0), #  30600     0 KST
        datetime(1968,  9, 30, 15, 30,  0), #  32400     0 KST
        datetime(1987,  5,  9, 15,  0,  0), #  36000  3600 KDT
        datetime(1987, 10, 10, 14,  0,  0), #  32400     0 KST
        datetime(1988,  5,  7, 15,  0,  0), #  36000  3600 KDT
        datetime(1988, 10,  8, 14,  0,  0), #  32400     0 KST
        ]

    _transition_info = [
        ttinfo( 30600,      0,  'KST'),
        ttinfo( 32400,      0,  'KST'),
        ttinfo( 30600,      0,  'KST'),
        ttinfo( 32400,      0,  'KST'),
        ttinfo( 28800,      0,  'KST'),
        ttinfo( 32400,   3600,  'KDT'),
        ttinfo( 28800,      0,  'KST'),
        ttinfo( 30600,      0,  'KST'),
        ttinfo( 32400,      0,  'KST'),
        ttinfo( 36000,   3600,  'KDT'),
        ttinfo( 32400,      0,  'KST'),
        ttinfo( 36000,   3600,  'KDT'),
        ttinfo( 32400,      0,  'KST'),
        ]

Seoul = Seoul() # Singleton

