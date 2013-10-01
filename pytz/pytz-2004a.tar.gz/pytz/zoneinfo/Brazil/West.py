'''
tzinfo timezone information for Brazil/West.

Generated from the Olson timezone database:
    ftp://elsie.nci.nih.gov/pub/tz*.tar.gz
'''

from pytz.tzinfo import DstTzInfo
from pytz.tzinfo import memorized_datetime as datetime
from pytz.tzinfo import memorized_ttinfo as ttinfo

class West(DstTzInfo):
    '''Brazil/West timezone definition. See datetime.tzinfo for details'''

    _zone = 'Brazil/West'

    _utc_transition_times = [
        datetime(   1,  1,  1,  0,  0,  0), # -14404     0 LMT
        datetime(1914,  1,  1,  4,  0,  4), # -14400     0 AMT
        datetime(1931, 10,  3, 15,  0,  0), # -10800  3600 AMST
        datetime(1932,  4,  1,  3,  0,  0), # -14400     0 AMT
        datetime(1932, 10,  3,  4,  0,  0), # -10800  3600 AMST
        datetime(1933,  4,  1,  3,  0,  0), # -14400     0 AMT
        datetime(1949, 12,  1,  4,  0,  0), # -10800  3600 AMST
        datetime(1950,  4, 16,  4,  0,  0), # -14400     0 AMT
        datetime(1950, 12,  1,  4,  0,  0), # -10800  3600 AMST
        datetime(1951,  4,  1,  3,  0,  0), # -14400     0 AMT
        datetime(1951, 12,  1,  4,  0,  0), # -10800  3600 AMST
        datetime(1952,  4,  1,  3,  0,  0), # -14400     0 AMT
        datetime(1952, 12,  1,  4,  0,  0), # -10800  3600 AMST
        datetime(1953,  3,  1,  3,  0,  0), # -14400     0 AMT
        datetime(1963, 12,  9,  4,  0,  0), # -10800  3600 AMST
        datetime(1964,  3,  1,  3,  0,  0), # -14400     0 AMT
        datetime(1965,  1, 31,  4,  0,  0), # -10800  3600 AMST
        datetime(1965,  3, 31,  3,  0,  0), # -14400     0 AMT
        datetime(1965, 12,  1,  4,  0,  0), # -10800  3600 AMST
        datetime(1966,  3,  1,  3,  0,  0), # -14400     0 AMT
        datetime(1966, 11,  1,  4,  0,  0), # -10800  3600 AMST
        datetime(1967,  3,  1,  3,  0,  0), # -14400     0 AMT
        datetime(1967, 11,  1,  4,  0,  0), # -10800  3600 AMST
        datetime(1968,  3,  1,  3,  0,  0), # -14400     0 AMT
        datetime(1985, 11,  2,  4,  0,  0), # -10800  3600 AMST
        datetime(1986,  3, 15,  3,  0,  0), # -14400     0 AMT
        datetime(1986, 10, 25,  4,  0,  0), # -10800  3600 AMST
        datetime(1987,  2, 14,  3,  0,  0), # -14400     0 AMT
        datetime(1987, 10, 25,  4,  0,  0), # -10800  3600 AMST
        datetime(1988,  2,  7,  3,  0,  0), # -14400     0 AMT
        datetime(1993, 10, 17,  4,  0,  0), # -10800  3600 AMST
        datetime(1994,  2, 20,  3,  0,  0), # -14400     0 AMT
        ]

    _transition_info = [
        ttinfo(-14404,      0,  'LMT'),
        ttinfo(-14400,      0,  'AMT'),
        ttinfo(-10800,   3600, 'AMST'),
        ttinfo(-14400,      0,  'AMT'),
        ttinfo(-10800,   3600, 'AMST'),
        ttinfo(-14400,      0,  'AMT'),
        ttinfo(-10800,   3600, 'AMST'),
        ttinfo(-14400,      0,  'AMT'),
        ttinfo(-10800,   3600, 'AMST'),
        ttinfo(-14400,      0,  'AMT'),
        ttinfo(-10800,   3600, 'AMST'),
        ttinfo(-14400,      0,  'AMT'),
        ttinfo(-10800,   3600, 'AMST'),
        ttinfo(-14400,      0,  'AMT'),
        ttinfo(-10800,   3600, 'AMST'),
        ttinfo(-14400,      0,  'AMT'),
        ttinfo(-10800,   3600, 'AMST'),
        ttinfo(-14400,      0,  'AMT'),
        ttinfo(-10800,   3600, 'AMST'),
        ttinfo(-14400,      0,  'AMT'),
        ttinfo(-10800,   3600, 'AMST'),
        ttinfo(-14400,      0,  'AMT'),
        ttinfo(-10800,   3600, 'AMST'),
        ttinfo(-14400,      0,  'AMT'),
        ttinfo(-10800,   3600, 'AMST'),
        ttinfo(-14400,      0,  'AMT'),
        ttinfo(-10800,   3600, 'AMST'),
        ttinfo(-14400,      0,  'AMT'),
        ttinfo(-10800,   3600, 'AMST'),
        ttinfo(-14400,      0,  'AMT'),
        ttinfo(-10800,   3600, 'AMST'),
        ttinfo(-14400,      0,  'AMT'),
        ]

West = West() # Singleton

