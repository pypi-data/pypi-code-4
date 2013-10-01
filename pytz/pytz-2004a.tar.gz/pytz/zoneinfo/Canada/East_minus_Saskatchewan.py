'''
tzinfo timezone information for Canada/East_minus_Saskatchewan.

Generated from the Olson timezone database:
    ftp://elsie.nci.nih.gov/pub/tz*.tar.gz
'''

from pytz.tzinfo import DstTzInfo
from pytz.tzinfo import memorized_datetime as datetime
from pytz.tzinfo import memorized_ttinfo as ttinfo

class East_minus_Saskatchewan(DstTzInfo):
    '''Canada/East_minus_Saskatchewan timezone definition. See datetime.tzinfo for details'''

    _zone = 'Canada/East_minus_Saskatchewan'

    _utc_transition_times = [
        datetime(   1,  1,  1,  0,  0,  0), # -25116     0 LMT
        datetime(1905,  9,  1,  6, 58, 36), # -25200     0 MST
        datetime(1918,  4, 14,  9,  0,  0), # -21600  3600 MDT
        datetime(1918, 10, 31,  8,  0,  0), # -25200     0 MST
        datetime(1930,  5,  4,  7,  0,  0), # -21600  3600 MDT
        datetime(1930, 10,  5,  6,  0,  0), # -25200     0 MST
        datetime(1931,  5,  3,  7,  0,  0), # -21600  3600 MDT
        datetime(1931, 10,  4,  6,  0,  0), # -25200     0 MST
        datetime(1932,  5,  1,  7,  0,  0), # -21600  3600 MDT
        datetime(1932, 10,  2,  6,  0,  0), # -25200     0 MST
        datetime(1933,  5,  7,  7,  0,  0), # -21600  3600 MDT
        datetime(1933, 10,  1,  6,  0,  0), # -25200     0 MST
        datetime(1934,  5,  6,  7,  0,  0), # -21600  3600 MDT
        datetime(1934, 10,  7,  6,  0,  0), # -25200     0 MST
        datetime(1937,  4, 11,  7,  0,  0), # -21600  3600 MDT
        datetime(1937, 10, 10,  6,  0,  0), # -25200     0 MST
        datetime(1938,  4, 10,  7,  0,  0), # -21600  3600 MDT
        datetime(1938, 10,  2,  6,  0,  0), # -25200     0 MST
        datetime(1939,  4,  9,  7,  0,  0), # -21600  3600 MDT
        datetime(1939, 10,  8,  6,  0,  0), # -25200     0 MST
        datetime(1940,  4, 14,  7,  0,  0), # -21600  3600 MDT
        datetime(1940, 10, 13,  6,  0,  0), # -25200     0 MST
        datetime(1941,  4, 13,  7,  0,  0), # -21600  3600 MDT
        datetime(1941, 10, 12,  6,  0,  0), # -25200     0 MST
        datetime(1942,  2,  9,  9,  0,  0), # -21600  3600 MWT
        datetime(1945,  8, 14, 23,  0,  0), # -21600     0 MPT
        datetime(1945,  9, 30,  8,  0,  0), # -25200     0 MST
        datetime(1946,  4, 14,  9,  0,  0), # -21600  3600 MDT
        datetime(1946, 10, 13,  8,  0,  0), # -25200     0 MST
        datetime(1947,  4, 27,  9,  0,  0), # -21600  3600 MDT
        datetime(1947,  9, 28,  8,  0,  0), # -25200     0 MST
        datetime(1948,  4, 25,  9,  0,  0), # -21600  3600 MDT
        datetime(1948,  9, 26,  8,  0,  0), # -25200     0 MST
        datetime(1949,  4, 24,  9,  0,  0), # -21600  3600 MDT
        datetime(1949,  9, 25,  8,  0,  0), # -25200     0 MST
        datetime(1950,  4, 30,  9,  0,  0), # -21600  3600 MDT
        datetime(1950,  9, 24,  8,  0,  0), # -25200     0 MST
        datetime(1951,  4, 29,  9,  0,  0), # -21600  3600 MDT
        datetime(1951,  9, 30,  8,  0,  0), # -25200     0 MST
        datetime(1952,  4, 27,  9,  0,  0), # -21600  3600 MDT
        datetime(1952,  9, 28,  8,  0,  0), # -25200     0 MST
        datetime(1953,  4, 26,  9,  0,  0), # -21600  3600 MDT
        datetime(1953,  9, 27,  8,  0,  0), # -25200     0 MST
        datetime(1954,  4, 25,  9,  0,  0), # -21600  3600 MDT
        datetime(1954,  9, 26,  8,  0,  0), # -25200     0 MST
        datetime(1955,  4, 24,  9,  0,  0), # -21600  3600 MDT
        datetime(1955,  9, 25,  8,  0,  0), # -25200     0 MST
        datetime(1956,  4, 29,  9,  0,  0), # -21600  3600 MDT
        datetime(1956,  9, 30,  8,  0,  0), # -25200     0 MST
        datetime(1957,  4, 28,  9,  0,  0), # -21600  3600 MDT
        datetime(1957,  9, 29,  8,  0,  0), # -25200     0 MST
        datetime(1959,  4, 26,  9,  0,  0), # -21600  3600 MDT
        datetime(1959, 10, 25,  8,  0,  0), # -25200     0 MST
        datetime(1960,  4, 24,  9,  0,  0), # -21600     0 CST
        ]

    _transition_info = [
        ttinfo(-25116,      0,  'LMT'),
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
        ttinfo(-21600,   3600,  'MDT'),
        ttinfo(-25200,      0,  'MST'),
        ttinfo(-21600,   3600,  'MDT'),
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

East_minus_Saskatchewan = East_minus_Saskatchewan() # Singleton

