'''
tzinfo timezone information for America/Eirunepe.

Generated from the Olson timezone database:
    ftp://elsie.nci.nih.gov/pub/tz*.tar.gz
'''

from pytz.tzinfo import DstTzInfo
from pytz.tzinfo import memorized_datetime as datetime
from pytz.tzinfo import memorized_ttinfo as ttinfo

class Eirunepe(DstTzInfo):
    '''America/Eirunepe timezone definition. See datetime.tzinfo for details'''

    _zone = 'America/Eirunepe'

    _utc_transition_times = [
        datetime(   1,  1,  1,  0,  0,  0), # -16768     0 LMT
        datetime(1914,  1,  1,  4, 39, 28), # -18000     0 ACT
        datetime(1931, 10,  3, 16,  0,  0), # -14400  3600 ACST
        datetime(1932,  4,  1,  4,  0,  0), # -18000     0 ACT
        datetime(1932, 10,  3,  5,  0,  0), # -14400  3600 ACST
        datetime(1933,  4,  1,  4,  0,  0), # -18000     0 ACT
        datetime(1949, 12,  1,  5,  0,  0), # -14400  3600 ACST
        datetime(1950,  4, 16,  5,  0,  0), # -18000     0 ACT
        datetime(1950, 12,  1,  5,  0,  0), # -14400  3600 ACST
        datetime(1951,  4,  1,  4,  0,  0), # -18000     0 ACT
        datetime(1951, 12,  1,  5,  0,  0), # -14400  3600 ACST
        datetime(1952,  4,  1,  4,  0,  0), # -18000     0 ACT
        datetime(1952, 12,  1,  5,  0,  0), # -14400  3600 ACST
        datetime(1953,  3,  1,  4,  0,  0), # -18000     0 ACT
        datetime(1963, 12,  9,  5,  0,  0), # -14400  3600 ACST
        datetime(1964,  3,  1,  4,  0,  0), # -18000     0 ACT
        datetime(1965,  1, 31,  5,  0,  0), # -14400  3600 ACST
        datetime(1965,  3, 31,  4,  0,  0), # -18000     0 ACT
        datetime(1965, 12,  1,  5,  0,  0), # -14400  3600 ACST
        datetime(1966,  3,  1,  4,  0,  0), # -18000     0 ACT
        datetime(1966, 11,  1,  5,  0,  0), # -14400  3600 ACST
        datetime(1967,  3,  1,  4,  0,  0), # -18000     0 ACT
        datetime(1967, 11,  1,  5,  0,  0), # -14400  3600 ACST
        datetime(1968,  3,  1,  4,  0,  0), # -18000     0 ACT
        datetime(1985, 11,  2,  5,  0,  0), # -14400  3600 ACST
        datetime(1986,  3, 15,  4,  0,  0), # -18000     0 ACT
        datetime(1986, 10, 25,  5,  0,  0), # -14400  3600 ACST
        datetime(1987,  2, 14,  4,  0,  0), # -18000     0 ACT
        datetime(1987, 10, 25,  5,  0,  0), # -14400  3600 ACST
        datetime(1988,  2,  7,  4,  0,  0), # -18000     0 ACT
        datetime(1993, 10, 17,  5,  0,  0), # -14400  3600 ACST
        datetime(1994,  2, 20,  4,  0,  0), # -18000     0 ACT
        ]

    _transition_info = [
        ttinfo(-16768,      0,  'LMT'),
        ttinfo(-18000,      0,  'ACT'),
        ttinfo(-14400,   3600, 'ACST'),
        ttinfo(-18000,      0,  'ACT'),
        ttinfo(-14400,   3600, 'ACST'),
        ttinfo(-18000,      0,  'ACT'),
        ttinfo(-14400,   3600, 'ACST'),
        ttinfo(-18000,      0,  'ACT'),
        ttinfo(-14400,   3600, 'ACST'),
        ttinfo(-18000,      0,  'ACT'),
        ttinfo(-14400,   3600, 'ACST'),
        ttinfo(-18000,      0,  'ACT'),
        ttinfo(-14400,   3600, 'ACST'),
        ttinfo(-18000,      0,  'ACT'),
        ttinfo(-14400,   3600, 'ACST'),
        ttinfo(-18000,      0,  'ACT'),
        ttinfo(-14400,   3600, 'ACST'),
        ttinfo(-18000,      0,  'ACT'),
        ttinfo(-14400,   3600, 'ACST'),
        ttinfo(-18000,      0,  'ACT'),
        ttinfo(-14400,   3600, 'ACST'),
        ttinfo(-18000,      0,  'ACT'),
        ttinfo(-14400,   3600, 'ACST'),
        ttinfo(-18000,      0,  'ACT'),
        ttinfo(-14400,   3600, 'ACST'),
        ttinfo(-18000,      0,  'ACT'),
        ttinfo(-14400,   3600, 'ACST'),
        ttinfo(-18000,      0,  'ACT'),
        ttinfo(-14400,   3600, 'ACST'),
        ttinfo(-18000,      0,  'ACT'),
        ttinfo(-14400,   3600, 'ACST'),
        ttinfo(-18000,      0,  'ACT'),
        ]

Eirunepe = Eirunepe() # Singleton

