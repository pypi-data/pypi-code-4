'''
tzinfo timezone information for Jamaica.

Generated from the Olson timezone database:
    ftp://elsie.nci.nih.gov/pub/tz*.tar.gz
'''

from pytz.tzinfo import DstTzInfo
from pytz.tzinfo import memorized_datetime as datetime
from pytz.tzinfo import memorized_ttinfo as ttinfo

class Jamaica(DstTzInfo):
    '''Jamaica timezone definition. See datetime.tzinfo for details'''

    _zone = 'Jamaica'

    _utc_transition_times = [
        datetime(   1,  1,  1,  0,  0,  0), # -18432     0 KMT
        datetime(1912,  2,  1,  5,  7, 12), # -18000     0 EST
        datetime(1974,  4, 28,  7,  0,  0), # -14400  3600 EDT
        datetime(1974, 10, 27,  6,  0,  0), # -18000     0 EST
        datetime(1975,  2, 23,  7,  0,  0), # -14400  3600 EDT
        datetime(1975, 10, 26,  6,  0,  0), # -18000     0 EST
        datetime(1976,  4, 25,  7,  0,  0), # -14400  3600 EDT
        datetime(1976, 10, 31,  6,  0,  0), # -18000     0 EST
        datetime(1977,  4, 24,  7,  0,  0), # -14400  3600 EDT
        datetime(1977, 10, 30,  6,  0,  0), # -18000     0 EST
        datetime(1978,  4, 30,  7,  0,  0), # -14400  3600 EDT
        datetime(1978, 10, 29,  6,  0,  0), # -18000     0 EST
        datetime(1979,  4, 29,  7,  0,  0), # -14400  3600 EDT
        datetime(1979, 10, 28,  6,  0,  0), # -18000     0 EST
        datetime(1980,  4, 27,  7,  0,  0), # -14400  3600 EDT
        datetime(1980, 10, 26,  6,  0,  0), # -18000     0 EST
        datetime(1981,  4, 26,  7,  0,  0), # -14400  3600 EDT
        datetime(1981, 10, 25,  6,  0,  0), # -18000     0 EST
        datetime(1982,  4, 25,  7,  0,  0), # -14400  3600 EDT
        datetime(1982, 10, 31,  6,  0,  0), # -18000     0 EST
        datetime(1983,  4, 24,  7,  0,  0), # -14400  3600 EDT
        datetime(1983, 10, 30,  6,  0,  0), # -18000     0 EST
        ]

    _transition_info = [
        ttinfo(-18432,      0,  'KMT'),
        ttinfo(-18000,      0,  'EST'),
        ttinfo(-14400,   3600,  'EDT'),
        ttinfo(-18000,      0,  'EST'),
        ttinfo(-14400,   3600,  'EDT'),
        ttinfo(-18000,      0,  'EST'),
        ttinfo(-14400,   3600,  'EDT'),
        ttinfo(-18000,      0,  'EST'),
        ttinfo(-14400,   3600,  'EDT'),
        ttinfo(-18000,      0,  'EST'),
        ttinfo(-14400,   3600,  'EDT'),
        ttinfo(-18000,      0,  'EST'),
        ttinfo(-14400,   3600,  'EDT'),
        ttinfo(-18000,      0,  'EST'),
        ttinfo(-14400,   3600,  'EDT'),
        ttinfo(-18000,      0,  'EST'),
        ttinfo(-14400,   3600,  'EDT'),
        ttinfo(-18000,      0,  'EST'),
        ttinfo(-14400,   3600,  'EDT'),
        ttinfo(-18000,      0,  'EST'),
        ttinfo(-14400,   3600,  'EDT'),
        ttinfo(-18000,      0,  'EST'),
        ]

Jamaica = Jamaica() # Singleton

