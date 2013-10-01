'''
tzinfo timezone information for America/Montevideo.

Generated from the Olson timezone database:
    ftp://elsie.nci.nih.gov/pub/tz*.tar.gz
'''

from pytz.tzinfo import DstTzInfo
from pytz.tzinfo import memorized_datetime as datetime
from pytz.tzinfo import memorized_ttinfo as ttinfo

class Montevideo(DstTzInfo):
    '''America/Montevideo timezone definition. See datetime.tzinfo for details'''

    _zone = 'America/Montevideo'

    _utc_transition_times = [
        datetime(   1,  1,  1,  0,  0,  0), # -13484     0 MMT
        datetime(1920,  5,  1,  3, 44, 44), # -12600     0 UYT
        datetime(1923, 10,  2,  3, 30,  0), # -10800  1800 UYHST
        datetime(1924,  4,  1,  3,  0,  0), # -12600     0 UYT
        datetime(1924, 10,  1,  3, 30,  0), # -10800  1800 UYHST
        datetime(1925,  4,  1,  3,  0,  0), # -12600     0 UYT
        datetime(1925, 10,  1,  3, 30,  0), # -10800  1800 UYHST
        datetime(1926,  4,  1,  3,  0,  0), # -12600     0 UYT
        datetime(1933, 10, 29,  3, 30,  0), # -10800  1800 UYHST
        datetime(1934,  4,  1,  3,  0,  0), # -12600     0 UYT
        datetime(1934, 10, 28,  3, 30,  0), # -10800  1800 UYHST
        datetime(1935,  3, 31,  3,  0,  0), # -12600     0 UYT
        datetime(1935, 10, 27,  3, 30,  0), # -10800  1800 UYHST
        datetime(1936,  3, 29,  3,  0,  0), # -12600     0 UYT
        datetime(1936, 11,  1,  3, 30,  0), # -10800  1800 UYHST
        datetime(1937,  3, 28,  3,  0,  0), # -12600     0 UYT
        datetime(1937, 10, 31,  3, 30,  0), # -10800  1800 UYHST
        datetime(1938,  3, 27,  3,  0,  0), # -12600     0 UYT
        datetime(1938, 10, 30,  3, 30,  0), # -10800  1800 UYHST
        datetime(1939,  3, 26,  3,  0,  0), # -12600     0 UYT
        datetime(1939, 10, 29,  3, 30,  0), # -10800  1800 UYHST
        datetime(1940,  3, 31,  3,  0,  0), # -12600     0 UYT
        datetime(1940, 10, 27,  3, 30,  0), # -10800  1800 UYHST
        datetime(1941,  3, 30,  3,  0,  0), # -12600     0 UYT
        datetime(1942,  1,  1,  3, 30,  0), # -10800  1800 UYHST
        datetime(1942, 12, 14,  3,  0,  0), #  -7200  3600 UYST
        datetime(1943,  3, 14,  2,  0,  0), # -10800     0 UYT
        datetime(1959,  5, 24,  3,  0,  0), #  -7200  3600 UYST
        datetime(1959, 11, 15,  2,  0,  0), # -10800     0 UYT
        datetime(1960,  1, 17,  3,  0,  0), #  -7200  3600 UYST
        datetime(1960,  3,  6,  2,  0,  0), # -10800     0 UYT
        datetime(1965,  4,  4,  3,  0,  0), #  -7200  3600 UYST
        datetime(1965,  9, 26,  2,  0,  0), # -10800     0 UYT
        datetime(1966,  4,  3,  3,  0,  0), #  -7200  3600 UYST
        datetime(1966, 10, 31,  2,  0,  0), # -10800     0 UYT
        datetime(1967,  4,  2,  3,  0,  0), #  -7200  3600 UYST
        datetime(1967, 10, 31,  2,  0,  0), # -10800     0 UYT
        datetime(1968,  5, 27,  3,  0,  0), #  -9000  1800 UYHST
        datetime(1968, 12,  2,  2, 30,  0), # -10800     0 UYT
        datetime(1969,  5, 27,  3,  0,  0), #  -9000  1800 UYHST
        datetime(1969, 12,  2,  2, 30,  0), # -10800     0 UYT
        datetime(1970,  5, 27,  3,  0,  0), #  -9000  1800 UYHST
        datetime(1970, 12,  2,  2, 30,  0), # -10800     0 UYT
        datetime(1972,  4, 24,  3,  0,  0), #  -7200  3600 UYST
        datetime(1972,  8, 15,  2,  0,  0), # -10800     0 UYT
        datetime(1974,  3, 10,  3,  0,  0), #  -9000  1800 UYHST
        datetime(1974, 12, 22,  2, 30,  0), #  -7200  1800 UYST
        datetime(1976, 10,  1,  2,  0,  0), # -10800     0 UYT
        datetime(1977, 12,  4,  3,  0,  0), #  -7200  3600 UYST
        datetime(1978,  4,  1,  2,  0,  0), # -10800     0 UYT
        datetime(1979, 10,  1,  3,  0,  0), #  -7200  3600 UYST
        datetime(1980,  5,  1,  2,  0,  0), # -10800     0 UYT
        datetime(1987, 12, 14,  3,  0,  0), #  -7200  3600 UYST
        datetime(1988,  3, 14,  2,  0,  0), # -10800     0 UYT
        datetime(1988, 12, 11,  3,  0,  0), #  -7200  3600 UYST
        datetime(1989,  3, 12,  2,  0,  0), # -10800     0 UYT
        datetime(1989, 10, 29,  3,  0,  0), #  -7200  3600 UYST
        datetime(1990,  3,  4,  2,  0,  0), # -10800     0 UYT
        datetime(1990, 10, 21,  3,  0,  0), #  -7200  3600 UYST
        datetime(1991,  3,  3,  2,  0,  0), # -10800     0 UYT
        datetime(1991, 10, 27,  3,  0,  0), #  -7200  3600 UYST
        datetime(1992,  3,  1,  2,  0,  0), # -10800     0 UYT
        datetime(1992, 10, 18,  3,  0,  0), #  -7200  3600 UYST
        datetime(1993,  2, 28,  2,  0,  0), # -10800     0 UYT
        ]

    _transition_info = [
        ttinfo(-13484,      0,  'MMT'),
        ttinfo(-12600,      0,  'UYT'),
        ttinfo(-10800,   1800, 'UYHST'),
        ttinfo(-12600,      0,  'UYT'),
        ttinfo(-10800,   1800, 'UYHST'),
        ttinfo(-12600,      0,  'UYT'),
        ttinfo(-10800,   1800, 'UYHST'),
        ttinfo(-12600,      0,  'UYT'),
        ttinfo(-10800,   1800, 'UYHST'),
        ttinfo(-12600,      0,  'UYT'),
        ttinfo(-10800,   1800, 'UYHST'),
        ttinfo(-12600,      0,  'UYT'),
        ttinfo(-10800,   1800, 'UYHST'),
        ttinfo(-12600,      0,  'UYT'),
        ttinfo(-10800,   1800, 'UYHST'),
        ttinfo(-12600,      0,  'UYT'),
        ttinfo(-10800,   1800, 'UYHST'),
        ttinfo(-12600,      0,  'UYT'),
        ttinfo(-10800,   1800, 'UYHST'),
        ttinfo(-12600,      0,  'UYT'),
        ttinfo(-10800,   1800, 'UYHST'),
        ttinfo(-12600,      0,  'UYT'),
        ttinfo(-10800,   1800, 'UYHST'),
        ttinfo(-12600,      0,  'UYT'),
        ttinfo(-10800,   1800, 'UYHST'),
        ttinfo( -7200,   3600, 'UYST'),
        ttinfo(-10800,      0,  'UYT'),
        ttinfo( -7200,   3600, 'UYST'),
        ttinfo(-10800,      0,  'UYT'),
        ttinfo( -7200,   3600, 'UYST'),
        ttinfo(-10800,      0,  'UYT'),
        ttinfo( -7200,   3600, 'UYST'),
        ttinfo(-10800,      0,  'UYT'),
        ttinfo( -7200,   3600, 'UYST'),
        ttinfo(-10800,      0,  'UYT'),
        ttinfo( -7200,   3600, 'UYST'),
        ttinfo(-10800,      0,  'UYT'),
        ttinfo( -9000,   1800, 'UYHST'),
        ttinfo(-10800,      0,  'UYT'),
        ttinfo( -9000,   1800, 'UYHST'),
        ttinfo(-10800,      0,  'UYT'),
        ttinfo( -9000,   1800, 'UYHST'),
        ttinfo(-10800,      0,  'UYT'),
        ttinfo( -7200,   3600, 'UYST'),
        ttinfo(-10800,      0,  'UYT'),
        ttinfo( -9000,   1800, 'UYHST'),
        ttinfo( -7200,   1800, 'UYST'),
        ttinfo(-10800,      0,  'UYT'),
        ttinfo( -7200,   3600, 'UYST'),
        ttinfo(-10800,      0,  'UYT'),
        ttinfo( -7200,   3600, 'UYST'),
        ttinfo(-10800,      0,  'UYT'),
        ttinfo( -7200,   3600, 'UYST'),
        ttinfo(-10800,      0,  'UYT'),
        ttinfo( -7200,   3600, 'UYST'),
        ttinfo(-10800,      0,  'UYT'),
        ttinfo( -7200,   3600, 'UYST'),
        ttinfo(-10800,      0,  'UYT'),
        ttinfo( -7200,   3600, 'UYST'),
        ttinfo(-10800,      0,  'UYT'),
        ttinfo( -7200,   3600, 'UYST'),
        ttinfo(-10800,      0,  'UYT'),
        ttinfo( -7200,   3600, 'UYST'),
        ttinfo(-10800,      0,  'UYT'),
        ]

Montevideo = Montevideo() # Singleton

