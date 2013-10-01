'''
tzinfo timezone information for America/Swift_Current.

Generated from the Olson timezone database:
    ftp://elsie.nci.nih.gov/pub/tz*.tar.gz
'''

from pytz.tzinfo import DstTzInfo
from pytz.tzinfo import memorized_datetime as datetime
from pytz.tzinfo import memorized_ttinfo as ttinfo

class Swift_Current(DstTzInfo):
    '''America/Swift_Current timezone definition. See datetime.tzinfo for details'''

    _zone = 'America/Swift_Current'

    _utc_transition_times = [
        datetime(   1,  1,  1,  0,  0,  0), # -25880     0 LMT
        datetime(1905,  9,  1,  7, 11, 20), # -25200     0 MST
        datetime(1918,  4, 14,  9,  0,  0), # -21600  3600 MDT
        datetime(1918, 10, 31,  8,  0,  0), # -25200     0 MST
        datetime(1942,  2,  9,  9,  0,  0), # -21600  3600 MWT
        datetime(1945,  8, 14, 23,  0,  0), # -21600     0 MPT
        datetime(1945,  9, 30,  8,  0,  0), # -25200     0 MST
        datetime(1946,  4, 28,  9,  0,  0), # -21600  3600 MDT
        datetime(1946, 10, 13,  8,  0,  0), # -25200     0 MST
        datetime(1947,  4, 27,  9,  0,  0), # -21600  3600 MDT
        datetime(1947,  9, 28,  8,  0,  0), # -25200     0 MST
        datetime(1948,  4, 25,  9,  0,  0), # -21600  3600 MDT
        datetime(1948,  9, 26,  8,  0,  0), # -25200     0 MST
        datetime(1949,  4, 24,  9,  0,  0), # -21600  3600 MDT
        datetime(1949,  9, 25,  8,  0,  0), # -25200     0 MST
        datetime(1957,  4, 28,  9,  0,  0), # -21600  3600 MDT
        datetime(1957, 10, 27,  8,  0,  0), # -25200     0 MST
        datetime(1959,  4, 26,  9,  0,  0), # -21600  3600 MDT
        datetime(1959, 10, 25,  8,  0,  0), # -25200     0 MST
        datetime(1960,  4, 24,  9,  0,  0), # -21600  3600 MDT
        datetime(1960,  9, 25,  8,  0,  0), # -25200     0 MST
        datetime(1961,  4, 30,  9,  0,  0), # -21600  3600 MDT
        datetime(1961,  9, 24,  8,  0,  0), # -25200     0 MST
        datetime(1972,  4, 30,  9,  0,  0), # -21600     0 CST
        ]

    _transition_info = [
        ttinfo(-25880,      0,  'LMT'),
        ttinfo(-25200,      0,  'MST'),
        ttinfo(-21600,   3600,  'MDT'),
        ttinfo(-25200,      0,  'MST'),
        ttinfo(-21600,   3600,  'MWT'),
        ttinfo(-21600,      0,  'MPT'),
        ttinfo(-25200,      0,  'MST'),
        ttinfo(-21600,   3600,  'MDT'),
        ttinfo(-25200,      0,  'MST'),
        ttinfo(-21600,   3600,  'MDT'),
        ttinfo(-25200,      0,  'MST'),
        ttinfo(-21600,   3600,  'MDT'),
        ttinfo(-25200,      0,  'MST'),
        ttinfo(-21600,   3600,  'MDT'),
        ttinfo(-25200,      0,  'MST'),
        ttinfo(-21600,   3600,  'MDT'),
        ttinfo(-25200,      0,  'MST'),
        ttinfo(-21600,   3600,  'MDT'),
        ttinfo(-25200,      0,  'MST'),
        ttinfo(-21600,   3600,  'MDT'),
        ttinfo(-25200,      0,  'MST'),
        ttinfo(-21600,   3600,  'MDT'),
        ttinfo(-25200,      0,  'MST'),
        ttinfo(-21600,      0,  'CST'),
        ]

Swift_Current = Swift_Current() # Singleton

