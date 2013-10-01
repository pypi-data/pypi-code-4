'''
tzinfo timezone information for Atlantic/Reykjavik.

Generated from the Olson timezone database:
    ftp://elsie.nci.nih.gov/pub/tz*.tar.gz
'''

from pytz.tzinfo import DstTzInfo
from pytz.tzinfo import memorized_datetime as datetime
from pytz.tzinfo import memorized_ttinfo as ttinfo

class Reykjavik(DstTzInfo):
    '''Atlantic/Reykjavik timezone definition. See datetime.tzinfo for details'''

    _zone = 'Atlantic/Reykjavik'

    _utc_transition_times = [
        datetime(   1,  1,  1,  0,  0,  0), #  -5268     0 RMT
        datetime(1908,  1,  1,  1, 27, 48), #  -3600     0 IST
        datetime(1917,  2, 20,  0,  0,  0), #      0  3600 ISST
        datetime(1917, 10, 21,  1,  0,  0), #  -3600     0 IST
        datetime(1918,  2, 20,  0,  0,  0), #      0  3600 ISST
        datetime(1918, 11, 16,  1,  0,  0), #  -3600     0 IST
        datetime(1939,  4, 30,  0,  0,  0), #      0  3600 ISST
        datetime(1939, 11, 29,  2,  0,  0), #  -3600     0 IST
        datetime(1940,  2, 25,  3,  0,  0), #      0  3600 ISST
        datetime(1940, 11,  3,  2,  0,  0), #  -3600     0 IST
        datetime(1941,  3,  2,  2,  0,  0), #      0  3600 ISST
        datetime(1941, 11,  2,  2,  0,  0), #  -3600     0 IST
        datetime(1942,  3,  8,  2,  0,  0), #      0  3600 ISST
        datetime(1942, 10, 25,  2,  0,  0), #  -3600     0 IST
        datetime(1943,  3,  7,  2,  0,  0), #      0  3600 ISST
        datetime(1943, 10, 24,  2,  0,  0), #  -3600     0 IST
        datetime(1944,  3,  5,  2,  0,  0), #      0  3600 ISST
        datetime(1944, 10, 22,  2,  0,  0), #  -3600     0 IST
        datetime(1945,  3,  4,  2,  0,  0), #      0  3600 ISST
        datetime(1945, 10, 28,  2,  0,  0), #  -3600     0 IST
        datetime(1946,  3,  3,  2,  0,  0), #      0  3600 ISST
        datetime(1946, 10, 27,  2,  0,  0), #  -3600     0 IST
        datetime(1947,  4,  6,  2,  0,  0), #      0  3600 ISST
        datetime(1947, 10, 26,  2,  0,  0), #  -3600     0 IST
        datetime(1948,  4,  4,  2,  0,  0), #      0  3600 ISST
        datetime(1948, 10, 24,  2,  0,  0), #  -3600     0 IST
        datetime(1949,  4,  3,  2,  0,  0), #      0  3600 ISST
        datetime(1949, 10, 30,  2,  0,  0), #  -3600     0 IST
        datetime(1950,  4,  2,  2,  0,  0), #      0  3600 ISST
        datetime(1950, 10, 22,  2,  0,  0), #  -3600     0 IST
        datetime(1951,  4,  1,  2,  0,  0), #      0  3600 ISST
        datetime(1951, 10, 28,  2,  0,  0), #  -3600     0 IST
        datetime(1952,  4,  6,  2,  0,  0), #      0  3600 ISST
        datetime(1952, 10, 26,  2,  0,  0), #  -3600     0 IST
        datetime(1953,  4,  5,  2,  0,  0), #      0  3600 ISST
        datetime(1953, 10, 25,  2,  0,  0), #  -3600     0 IST
        datetime(1954,  4,  4,  2,  0,  0), #      0  3600 ISST
        datetime(1954, 10, 24,  2,  0,  0), #  -3600     0 IST
        datetime(1955,  4,  3,  2,  0,  0), #      0  3600 ISST
        datetime(1955, 10, 23,  2,  0,  0), #  -3600     0 IST
        datetime(1956,  4,  1,  2,  0,  0), #      0  3600 ISST
        datetime(1956, 10, 28,  2,  0,  0), #  -3600     0 IST
        datetime(1957,  4,  7,  2,  0,  0), #      0  3600 ISST
        datetime(1957, 10, 27,  2,  0,  0), #  -3600     0 IST
        datetime(1958,  4,  6,  2,  0,  0), #      0  3600 ISST
        datetime(1958, 10, 26,  2,  0,  0), #  -3600     0 IST
        datetime(1959,  4,  5,  2,  0,  0), #      0  3600 ISST
        datetime(1959, 10, 25,  2,  0,  0), #  -3600     0 IST
        datetime(1960,  4,  3,  2,  0,  0), #      0  3600 ISST
        datetime(1960, 10, 23,  2,  0,  0), #  -3600     0 IST
        datetime(1961,  4,  2,  2,  0,  0), #      0  3600 ISST
        datetime(1961, 10, 22,  2,  0,  0), #  -3600     0 IST
        datetime(1962,  4,  1,  2,  0,  0), #      0  3600 ISST
        datetime(1962, 10, 28,  2,  0,  0), #  -3600     0 IST
        datetime(1963,  4,  7,  2,  0,  0), #      0  3600 ISST
        datetime(1963, 10, 27,  2,  0,  0), #  -3600     0 IST
        datetime(1964,  4,  5,  2,  0,  0), #      0  3600 ISST
        datetime(1964, 10, 25,  2,  0,  0), #  -3600     0 IST
        datetime(1965,  4,  4,  2,  0,  0), #      0  3600 ISST
        datetime(1965, 10, 24,  2,  0,  0), #  -3600     0 IST
        datetime(1966,  4,  3,  2,  0,  0), #      0  3600 ISST
        datetime(1966, 10, 23,  2,  0,  0), #  -3600     0 IST
        datetime(1967,  4,  2,  2,  0,  0), #      0  3600 ISST
        datetime(1967, 10, 29,  2,  0,  0), #  -3600     0 IST
        datetime(1968,  4,  7,  2,  0,  0), #      0     0 GMT
        ]

    _transition_info = [
        ttinfo( -5268,      0,  'RMT'),
        ttinfo( -3600,      0,  'IST'),
        ttinfo(     0,   3600, 'ISST'),
        ttinfo( -3600,      0,  'IST'),
        ttinfo(     0,   3600, 'ISST'),
        ttinfo( -3600,      0,  'IST'),
        ttinfo(     0,   3600, 'ISST'),
        ttinfo( -3600,      0,  'IST'),
        ttinfo(     0,   3600, 'ISST'),
        ttinfo( -3600,      0,  'IST'),
        ttinfo(     0,   3600, 'ISST'),
        ttinfo( -3600,      0,  'IST'),
        ttinfo(     0,   3600, 'ISST'),
        ttinfo( -3600,      0,  'IST'),
        ttinfo(     0,   3600, 'ISST'),
        ttinfo( -3600,      0,  'IST'),
        ttinfo(     0,   3600, 'ISST'),
        ttinfo( -3600,      0,  'IST'),
        ttinfo(     0,   3600, 'ISST'),
        ttinfo( -3600,      0,  'IST'),
        ttinfo(     0,   3600, 'ISST'),
        ttinfo( -3600,      0,  'IST'),
        ttinfo(     0,   3600, 'ISST'),
        ttinfo( -3600,      0,  'IST'),
        ttinfo(     0,   3600, 'ISST'),
        ttinfo( -3600,      0,  'IST'),
        ttinfo(     0,   3600, 'ISST'),
        ttinfo( -3600,      0,  'IST'),
        ttinfo(     0,   3600, 'ISST'),
        ttinfo( -3600,      0,  'IST'),
        ttinfo(     0,   3600, 'ISST'),
        ttinfo( -3600,      0,  'IST'),
        ttinfo(     0,   3600, 'ISST'),
        ttinfo( -3600,      0,  'IST'),
        ttinfo(     0,   3600, 'ISST'),
        ttinfo( -3600,      0,  'IST'),
        ttinfo(     0,   3600, 'ISST'),
        ttinfo( -3600,      0,  'IST'),
        ttinfo(     0,   3600, 'ISST'),
        ttinfo( -3600,      0,  'IST'),
        ttinfo(     0,   3600, 'ISST'),
        ttinfo( -3600,      0,  'IST'),
        ttinfo(     0,   3600, 'ISST'),
        ttinfo( -3600,      0,  'IST'),
        ttinfo(     0,   3600, 'ISST'),
        ttinfo( -3600,      0,  'IST'),
        ttinfo(     0,   3600, 'ISST'),
        ttinfo( -3600,      0,  'IST'),
        ttinfo(     0,   3600, 'ISST'),
        ttinfo( -3600,      0,  'IST'),
        ttinfo(     0,   3600, 'ISST'),
        ttinfo( -3600,      0,  'IST'),
        ttinfo(     0,   3600, 'ISST'),
        ttinfo( -3600,      0,  'IST'),
        ttinfo(     0,   3600, 'ISST'),
        ttinfo( -3600,      0,  'IST'),
        ttinfo(     0,   3600, 'ISST'),
        ttinfo( -3600,      0,  'IST'),
        ttinfo(     0,   3600, 'ISST'),
        ttinfo( -3600,      0,  'IST'),
        ttinfo(     0,   3600, 'ISST'),
        ttinfo( -3600,      0,  'IST'),
        ttinfo(     0,   3600, 'ISST'),
        ttinfo( -3600,      0,  'IST'),
        ttinfo(     0,      0,  'GMT'),
        ]

Reykjavik = Reykjavik() # Singleton

