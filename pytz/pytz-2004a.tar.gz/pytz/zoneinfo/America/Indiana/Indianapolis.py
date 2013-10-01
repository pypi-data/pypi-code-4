'''
tzinfo timezone information for America/Indiana/Indianapolis.

Generated from the Olson timezone database:
    ftp://elsie.nci.nih.gov/pub/tz*.tar.gz
'''

from pytz.tzinfo import DstTzInfo
from pytz.tzinfo import memorized_datetime as datetime
from pytz.tzinfo import memorized_ttinfo as ttinfo

class Indianapolis(DstTzInfo):
    '''America/Indiana/Indianapolis timezone definition. See datetime.tzinfo for details'''

    _zone = 'America/Indiana/Indianapolis'

    _utc_transition_times = [
        datetime(   1,  1,  1,  0,  0,  0), # -21600     0 CST
        datetime(1918,  3, 31,  8,  0,  0), # -18000  3600 CDT
        datetime(1918, 10, 27,  7,  0,  0), # -21600     0 CST
        datetime(1919,  3, 30,  8,  0,  0), # -18000  3600 CDT
        datetime(1919, 10, 26,  7,  0,  0), # -21600     0 CST
        datetime(1941,  6, 22,  8,  0,  0), # -18000  3600 CDT
        datetime(1941,  9, 28,  7,  0,  0), # -21600     0 CST
        datetime(1942,  2,  9,  8,  0,  0), # -18000  3600 CWT
        datetime(1945,  8, 14, 23,  0,  0), # -18000     0 CPT
        datetime(1945,  9, 30,  7,  0,  0), # -21600     0 CST
        datetime(1946,  4, 28,  8,  0,  0), # -18000  3600 CDT
        datetime(1946,  9, 29,  7,  0,  0), # -21600     0 CST
        datetime(1947,  4, 27,  8,  0,  0), # -18000  3600 CDT
        datetime(1947,  9, 28,  7,  0,  0), # -21600     0 CST
        datetime(1948,  4, 25,  8,  0,  0), # -18000  3600 CDT
        datetime(1948,  9, 26,  7,  0,  0), # -21600     0 CST
        datetime(1949,  4, 24,  8,  0,  0), # -18000  3600 CDT
        datetime(1949,  9, 25,  7,  0,  0), # -21600     0 CST
        datetime(1950,  4, 30,  8,  0,  0), # -18000  3600 CDT
        datetime(1950,  9, 24,  7,  0,  0), # -21600     0 CST
        datetime(1951,  4, 29,  8,  0,  0), # -18000  3600 CDT
        datetime(1951,  9, 30,  7,  0,  0), # -21600     0 CST
        datetime(1952,  4, 27,  8,  0,  0), # -18000  3600 CDT
        datetime(1952,  9, 28,  7,  0,  0), # -21600     0 CST
        datetime(1953,  4, 26,  8,  0,  0), # -18000  3600 CDT
        datetime(1953,  9, 27,  7,  0,  0), # -21600     0 CST
        datetime(1954,  4, 25,  8,  0,  0), # -18000  3600 CDT
        datetime(1954,  9, 26,  7,  0,  0), # -21600     0 CST
        datetime(1955,  4, 24,  8,  0,  0), # -18000     0 EST
        datetime(1957,  9, 29,  7,  0,  0), # -21600     0 CST
        datetime(1958,  4, 27,  8,  0,  0), # -18000     0 EST
        datetime(1969,  4, 27,  7,  0,  0), # -14400  3600 EDT
        datetime(1969, 10, 26,  6,  0,  0), # -18000     0 EST
        datetime(1970,  4, 26,  7,  0,  0), # -14400  3600 EDT
        datetime(1970, 10, 25,  6,  0,  0), # -18000     0 EST
        ]

    _transition_info = [
        ttinfo(-21600,      0,  'CST'),
        ttinfo(-18000,   3600,  'CDT'),
        ttinfo(-21600,      0,  'CST'),
        ttinfo(-18000,   3600,  'CDT'),
        ttinfo(-21600,      0,  'CST'),
        ttinfo(-18000,   3600,  'CDT'),
        ttinfo(-21600,      0,  'CST'),
        ttinfo(-18000,   3600,  'CWT'),
        ttinfo(-18000,      0,  'CPT'),
        ttinfo(-21600,      0,  'CST'),
        ttinfo(-18000,   3600,  'CDT'),
        ttinfo(-21600,      0,  'CST'),
        ttinfo(-18000,   3600,  'CDT'),
        ttinfo(-21600,      0,  'CST'),
        ttinfo(-18000,   3600,  'CDT'),
        ttinfo(-21600,      0,  'CST'),
        ttinfo(-18000,   3600,  'CDT'),
        ttinfo(-21600,      0,  'CST'),
        ttinfo(-18000,   3600,  'CDT'),
        ttinfo(-21600,      0,  'CST'),
        ttinfo(-18000,   3600,  'CDT'),
        ttinfo(-21600,      0,  'CST'),
        ttinfo(-18000,   3600,  'CDT'),
        ttinfo(-21600,      0,  'CST'),
        ttinfo(-18000,   3600,  'CDT'),
        ttinfo(-21600,      0,  'CST'),
        ttinfo(-18000,   3600,  'CDT'),
        ttinfo(-21600,      0,  'CST'),
        ttinfo(-18000,      0,  'EST'),
        ttinfo(-21600,      0,  'CST'),
        ttinfo(-18000,      0,  'EST'),
        ttinfo(-14400,   3600,  'EDT'),
        ttinfo(-18000,      0,  'EST'),
        ttinfo(-14400,   3600,  'EDT'),
        ttinfo(-18000,      0,  'EST'),
        ]

Indianapolis = Indianapolis() # Singleton

