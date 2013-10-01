'''
tzinfo timezone information for America/Mendoza.

Generated from the Olson timezone database:
    ftp://elsie.nci.nih.gov/pub/tz*.tar.gz
'''

from pytz.tzinfo import DstTzInfo
from pytz.tzinfo import memorized_datetime as datetime
from pytz.tzinfo import memorized_ttinfo as ttinfo

class Mendoza(DstTzInfo):
    '''America/Mendoza timezone definition. See datetime.tzinfo for details'''

    _zone = 'America/Mendoza'

    _utc_transition_times = [
        datetime(   1,  1,  1,  0,  0,  0), # -15408     0 CMT
        datetime(1920,  5,  1,  4, 16, 48), # -14400     0 ART
        datetime(1930, 12,  1,  4,  0,  0), # -10800  3600 ARST
        datetime(1931,  4,  1,  3,  0,  0), # -14400     0 ART
        datetime(1931, 10, 15,  4,  0,  0), # -10800  3600 ARST
        datetime(1932,  3,  1,  3,  0,  0), # -14400     0 ART
        datetime(1932, 11,  1,  4,  0,  0), # -10800  3600 ARST
        datetime(1933,  3,  1,  3,  0,  0), # -14400     0 ART
        datetime(1933, 11,  1,  4,  0,  0), # -10800  3600 ARST
        datetime(1934,  3,  1,  3,  0,  0), # -14400     0 ART
        datetime(1934, 11,  1,  4,  0,  0), # -10800  3600 ARST
        datetime(1935,  3,  1,  3,  0,  0), # -14400     0 ART
        datetime(1935, 11,  1,  4,  0,  0), # -10800  3600 ARST
        datetime(1936,  3,  1,  3,  0,  0), # -14400     0 ART
        datetime(1936, 11,  1,  4,  0,  0), # -10800  3600 ARST
        datetime(1937,  3,  1,  3,  0,  0), # -14400     0 ART
        datetime(1937, 11,  1,  4,  0,  0), # -10800  3600 ARST
        datetime(1938,  3,  1,  3,  0,  0), # -14400     0 ART
        datetime(1938, 11,  1,  4,  0,  0), # -10800  3600 ARST
        datetime(1939,  3,  1,  3,  0,  0), # -14400     0 ART
        datetime(1939, 11,  1,  4,  0,  0), # -10800  3600 ARST
        datetime(1940,  3,  1,  3,  0,  0), # -14400     0 ART
        datetime(1940,  7,  1,  4,  0,  0), # -10800  3600 ARST
        datetime(1941,  6, 15,  3,  0,  0), # -14400     0 ART
        datetime(1941, 10, 15,  4,  0,  0), # -10800  3600 ARST
        datetime(1943,  8,  1,  3,  0,  0), # -14400     0 ART
        datetime(1943, 10, 15,  4,  0,  0), # -10800  3600 ARST
        datetime(1946,  3,  1,  3,  0,  0), # -14400     0 ART
        datetime(1946, 10,  1,  4,  0,  0), # -10800  3600 ARST
        datetime(1963, 10,  1,  3,  0,  0), # -14400     0 ART
        datetime(1963, 12, 15,  4,  0,  0), # -10800  3600 ARST
        datetime(1964,  3,  1,  3,  0,  0), # -14400     0 ART
        datetime(1964, 10, 15,  4,  0,  0), # -10800  3600 ARST
        datetime(1965,  3,  1,  3,  0,  0), # -14400     0 ART
        datetime(1965, 10, 15,  4,  0,  0), # -10800  3600 ARST
        datetime(1966,  3,  1,  3,  0,  0), # -14400     0 ART
        datetime(1966, 10, 15,  4,  0,  0), # -10800  3600 ARST
        datetime(1967,  4,  2,  3,  0,  0), # -14400     0 ART
        datetime(1967, 10,  1,  4,  0,  0), # -10800  3600 ARST
        datetime(1968,  4,  7,  3,  0,  0), # -14400     0 ART
        datetime(1968, 10,  6,  4,  0,  0), # -10800  3600 ARST
        datetime(1969,  4,  6,  3,  0,  0), # -14400     0 ART
        datetime(1969, 10,  5,  4,  0,  0), # -10800     0 ART
        datetime(1974,  1, 23,  3,  0,  0), #  -7200  3600 ARST
        datetime(1974,  5,  1,  2,  0,  0), # -10800     0 ART
        datetime(1988, 12,  1,  3,  0,  0), #  -7200  3600 ARST
        datetime(1989,  3,  5,  2,  0,  0), # -10800     0 ART
        datetime(1989, 10, 15,  3,  0,  0), #  -7200  3600 ARST
        datetime(1990,  3,  4,  2,  0,  0), # -14400     0 WART
        datetime(1990, 10, 15,  4,  0,  0), # -10800  3600 WARST
        datetime(1991,  3,  1,  3,  0,  0), # -14400     0 WART
        datetime(1991, 10, 15,  4,  0,  0), # -10800  3600 WARST
        datetime(1992,  3,  1,  3,  0,  0), # -14400     0 WART
        datetime(1992, 10, 18,  4,  0,  0), #  -7200  7200 ARST
        datetime(1993,  3,  7,  2,  0,  0), # -10800     0 ART
        datetime(1999, 10,  3,  3,  0,  0), # -10800     0 ARST
        datetime(2000,  3,  3,  3,  0,  0), # -10800     0 ART
        datetime(2004,  5, 23,  3,  0,  0), # -14400     0 WART
        datetime(2004, 10, 17,  4,  0,  0), # -10800     0 ART
        ]

    _transition_info = [
        ttinfo(-15408,      0,  'CMT'),
        ttinfo(-14400,      0,  'ART'),
        ttinfo(-10800,   3600, 'ARST'),
        ttinfo(-14400,      0,  'ART'),
        ttinfo(-10800,   3600, 'ARST'),
        ttinfo(-14400,      0,  'ART'),
        ttinfo(-10800,   3600, 'ARST'),
        ttinfo(-14400,      0,  'ART'),
        ttinfo(-10800,   3600, 'ARST'),
        ttinfo(-14400,      0,  'ART'),
        ttinfo(-10800,   3600, 'ARST'),
        ttinfo(-14400,      0,  'ART'),
        ttinfo(-10800,   3600, 'ARST'),
        ttinfo(-14400,      0,  'ART'),
        ttinfo(-10800,   3600, 'ARST'),
        ttinfo(-14400,      0,  'ART'),
        ttinfo(-10800,   3600, 'ARST'),
        ttinfo(-14400,      0,  'ART'),
        ttinfo(-10800,   3600, 'ARST'),
        ttinfo(-14400,      0,  'ART'),
        ttinfo(-10800,   3600, 'ARST'),
        ttinfo(-14400,      0,  'ART'),
        ttinfo(-10800,   3600, 'ARST'),
        ttinfo(-14400,      0,  'ART'),
        ttinfo(-10800,   3600, 'ARST'),
        ttinfo(-14400,      0,  'ART'),
        ttinfo(-10800,   3600, 'ARST'),
        ttinfo(-14400,      0,  'ART'),
        ttinfo(-10800,   3600, 'ARST'),
        ttinfo(-14400,      0,  'ART'),
        ttinfo(-10800,   3600, 'ARST'),
        ttinfo(-14400,      0,  'ART'),
        ttinfo(-10800,   3600, 'ARST'),
        ttinfo(-14400,      0,  'ART'),
        ttinfo(-10800,   3600, 'ARST'),
        ttinfo(-14400,      0,  'ART'),
        ttinfo(-10800,   3600, 'ARST'),
        ttinfo(-14400,      0,  'ART'),
        ttinfo(-10800,   3600, 'ARST'),
        ttinfo(-14400,      0,  'ART'),
        ttinfo(-10800,   3600, 'ARST'),
        ttinfo(-14400,      0,  'ART'),
        ttinfo(-10800,      0,  'ART'),
        ttinfo( -7200,   3600, 'ARST'),
        ttinfo(-10800,      0,  'ART'),
        ttinfo( -7200,   3600, 'ARST'),
        ttinfo(-10800,      0,  'ART'),
        ttinfo( -7200,   3600, 'ARST'),
        ttinfo(-14400,      0, 'WART'),
        ttinfo(-10800,   3600, 'WARST'),
        ttinfo(-14400,      0, 'WART'),
        ttinfo(-10800,   3600, 'WARST'),
        ttinfo(-14400,      0, 'WART'),
        ttinfo( -7200,   7200, 'ARST'),
        ttinfo(-10800,      0,  'ART'),
        ttinfo(-10800,      0, 'ARST'),
        ttinfo(-10800,      0,  'ART'),
        ttinfo(-14400,      0, 'WART'),
        ttinfo(-10800,      0,  'ART'),
        ]

Mendoza = Mendoza() # Singleton

