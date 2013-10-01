'''
tzinfo timezone information for America/Hermosillo.

Generated from the Olson timezone database:
    ftp://elsie.nci.nih.gov/pub/tz*.tar.gz
'''

from pytz.tzinfo import DstTzInfo
from pytz.tzinfo import memorized_datetime as datetime
from pytz.tzinfo import memorized_ttinfo as ttinfo

class Hermosillo(DstTzInfo):
    '''America/Hermosillo timezone definition. See datetime.tzinfo for details'''

    _zone = 'America/Hermosillo'

    _utc_transition_times = [
        datetime(   1,  1,  1,  0,  0,  0), # -26632     0 LMT
        datetime(1922,  1,  1,  7,  0,  0), # -25200     0 MST
        datetime(1927,  6, 11,  6,  0,  0), # -21600     0 CST
        datetime(1930, 11, 15,  6,  0,  0), # -25200     0 MST
        datetime(1931,  5,  2,  6,  0,  0), # -21600     0 CST
        datetime(1931, 10,  1,  6,  0,  0), # -25200     0 MST
        datetime(1932,  4,  1,  7,  0,  0), # -21600     0 CST
        datetime(1942,  4, 24,  6,  0,  0), # -25200     0 MST
        datetime(1949,  1, 14,  7,  0,  0), # -28800     0 PST
        datetime(1970,  1,  1,  8,  0,  0), # -25200     0 MST
        datetime(1996,  4,  7,  9,  0,  0), # -21600  3600 MDT
        datetime(1996, 10, 27,  8,  0,  0), # -25200     0 MST
        datetime(1997,  4,  6,  9,  0,  0), # -21600  3600 MDT
        datetime(1997, 10, 26,  8,  0,  0), # -25200     0 MST
        datetime(1998,  4,  5,  9,  0,  0), # -21600  3600 MDT
        datetime(1998, 10, 25,  8,  0,  0), # -25200     0 MST
        ]

    _transition_info = [
        ttinfo(-26632,      0,  'LMT'),
        ttinfo(-25200,      0,  'MST'),
        ttinfo(-21600,      0,  'CST'),
        ttinfo(-25200,      0,  'MST'),
        ttinfo(-21600,      0,  'CST'),
        ttinfo(-25200,      0,  'MST'),
        ttinfo(-21600,      0,  'CST'),
        ttinfo(-25200,      0,  'MST'),
        ttinfo(-28800,      0,  'PST'),
        ttinfo(-25200,      0,  'MST'),
        ttinfo(-21600,   3600,  'MDT'),
        ttinfo(-25200,      0,  'MST'),
        ttinfo(-21600,   3600,  'MDT'),
        ttinfo(-25200,      0,  'MST'),
        ttinfo(-21600,   3600,  'MDT'),
        ttinfo(-25200,      0,  'MST'),
        ]

Hermosillo = Hermosillo() # Singleton

