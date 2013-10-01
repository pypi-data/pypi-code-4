'''
tzinfo timezone information for America/Belem.

Generated from the Olson timezone database:
    ftp://elsie.nci.nih.gov/pub/tz*.tar.gz
'''

from pytz.tzinfo import DstTzInfo
from pytz.tzinfo import memorized_datetime as datetime
from pytz.tzinfo import memorized_ttinfo as ttinfo

class Belem(DstTzInfo):
    '''America/Belem timezone definition. See datetime.tzinfo for details'''

    _zone = 'America/Belem'

    _utc_transition_times = [
        datetime(   1,  1,  1,  0,  0,  0), # -11636     0 LMT
        datetime(1914,  1,  1,  3, 13, 56), # -10800     0 BRT
        datetime(1931, 10,  3, 14,  0,  0), #  -7200  3600 BRST
        datetime(1932,  4,  1,  2,  0,  0), # -10800     0 BRT
        datetime(1932, 10,  3,  3,  0,  0), #  -7200  3600 BRST
        datetime(1933,  4,  1,  2,  0,  0), # -10800     0 BRT
        datetime(1949, 12,  1,  3,  0,  0), #  -7200  3600 BRST
        datetime(1950,  4, 16,  3,  0,  0), # -10800     0 BRT
        datetime(1950, 12,  1,  3,  0,  0), #  -7200  3600 BRST
        datetime(1951,  4,  1,  2,  0,  0), # -10800     0 BRT
        datetime(1951, 12,  1,  3,  0,  0), #  -7200  3600 BRST
        datetime(1952,  4,  1,  2,  0,  0), # -10800     0 BRT
        datetime(1952, 12,  1,  3,  0,  0), #  -7200  3600 BRST
        datetime(1953,  3,  1,  2,  0,  0), # -10800     0 BRT
        datetime(1963, 12,  9,  3,  0,  0), #  -7200  3600 BRST
        datetime(1964,  3,  1,  2,  0,  0), # -10800     0 BRT
        datetime(1965,  1, 31,  3,  0,  0), #  -7200  3600 BRST
        datetime(1965,  3, 31,  2,  0,  0), # -10800     0 BRT
        datetime(1965, 12,  1,  3,  0,  0), #  -7200  3600 BRST
        datetime(1966,  3,  1,  2,  0,  0), # -10800     0 BRT
        datetime(1966, 11,  1,  3,  0,  0), #  -7200  3600 BRST
        datetime(1967,  3,  1,  2,  0,  0), # -10800     0 BRT
        datetime(1967, 11,  1,  3,  0,  0), #  -7200  3600 BRST
        datetime(1968,  3,  1,  2,  0,  0), # -10800     0 BRT
        datetime(1985, 11,  2,  3,  0,  0), #  -7200  3600 BRST
        datetime(1986,  3, 15,  2,  0,  0), # -10800     0 BRT
        datetime(1986, 10, 25,  3,  0,  0), #  -7200  3600 BRST
        datetime(1987,  2, 14,  2,  0,  0), # -10800     0 BRT
        datetime(1987, 10, 25,  3,  0,  0), #  -7200  3600 BRST
        datetime(1988,  2,  7,  2,  0,  0), # -10800     0 BRT
        ]

    _transition_info = [
        ttinfo(-11636,      0,  'LMT'),
        ttinfo(-10800,      0,  'BRT'),
        ttinfo( -7200,   3600, 'BRST'),
        ttinfo(-10800,      0,  'BRT'),
        ttinfo( -7200,   3600, 'BRST'),
        ttinfo(-10800,      0,  'BRT'),
        ttinfo( -7200,   3600, 'BRST'),
        ttinfo(-10800,      0,  'BRT'),
        ttinfo( -7200,   3600, 'BRST'),
        ttinfo(-10800,      0,  'BRT'),
        ttinfo( -7200,   3600, 'BRST'),
        ttinfo(-10800,      0,  'BRT'),
        ttinfo( -7200,   3600, 'BRST'),
        ttinfo(-10800,      0,  'BRT'),
        ttinfo( -7200,   3600, 'BRST'),
        ttinfo(-10800,      0,  'BRT'),
        ttinfo( -7200,   3600, 'BRST'),
        ttinfo(-10800,      0,  'BRT'),
        ttinfo( -7200,   3600, 'BRST'),
        ttinfo(-10800,      0,  'BRT'),
        ttinfo( -7200,   3600, 'BRST'),
        ttinfo(-10800,      0,  'BRT'),
        ttinfo( -7200,   3600, 'BRST'),
        ttinfo(-10800,      0,  'BRT'),
        ttinfo( -7200,   3600, 'BRST'),
        ttinfo(-10800,      0,  'BRT'),
        ttinfo( -7200,   3600, 'BRST'),
        ttinfo(-10800,      0,  'BRT'),
        ttinfo( -7200,   3600, 'BRST'),
        ttinfo(-10800,      0,  'BRT'),
        ]

Belem = Belem() # Singleton

