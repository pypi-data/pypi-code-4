'''
tzinfo timezone information for America/Noronha.

Generated from the Olson timezone database:
    ftp://elsie.nci.nih.gov/pub/tz*.tar.gz
'''

from pytz.tzinfo import DstTzInfo
from pytz.tzinfo import memorized_datetime as datetime
from pytz.tzinfo import memorized_ttinfo as ttinfo

class Noronha(DstTzInfo):
    '''America/Noronha timezone definition. See datetime.tzinfo for details'''

    _zone = 'America/Noronha'

    _utc_transition_times = [
        datetime(   1,  1,  1,  0,  0,  0), #  -7780     0 LMT
        datetime(1914,  1,  1,  2,  9, 40), #  -7200     0 FNT
        datetime(1931, 10,  3, 13,  0,  0), #  -3600  3600 FNST
        datetime(1932,  4,  1,  1,  0,  0), #  -7200     0 FNT
        datetime(1932, 10,  3,  2,  0,  0), #  -3600  3600 FNST
        datetime(1933,  4,  1,  1,  0,  0), #  -7200     0 FNT
        datetime(1949, 12,  1,  2,  0,  0), #  -3600  3600 FNST
        datetime(1950,  4, 16,  2,  0,  0), #  -7200     0 FNT
        datetime(1950, 12,  1,  2,  0,  0), #  -3600  3600 FNST
        datetime(1951,  4,  1,  1,  0,  0), #  -7200     0 FNT
        datetime(1951, 12,  1,  2,  0,  0), #  -3600  3600 FNST
        datetime(1952,  4,  1,  1,  0,  0), #  -7200     0 FNT
        datetime(1952, 12,  1,  2,  0,  0), #  -3600  3600 FNST
        datetime(1953,  3,  1,  1,  0,  0), #  -7200     0 FNT
        datetime(1963, 12,  9,  2,  0,  0), #  -3600  3600 FNST
        datetime(1964,  3,  1,  1,  0,  0), #  -7200     0 FNT
        datetime(1965,  1, 31,  2,  0,  0), #  -3600  3600 FNST
        datetime(1965,  3, 31,  1,  0,  0), #  -7200     0 FNT
        datetime(1965, 12,  1,  2,  0,  0), #  -3600  3600 FNST
        datetime(1966,  3,  1,  1,  0,  0), #  -7200     0 FNT
        datetime(1966, 11,  1,  2,  0,  0), #  -3600  3600 FNST
        datetime(1967,  3,  1,  1,  0,  0), #  -7200     0 FNT
        datetime(1967, 11,  1,  2,  0,  0), #  -3600  3600 FNST
        datetime(1968,  3,  1,  1,  0,  0), #  -7200     0 FNT
        datetime(1985, 11,  2,  2,  0,  0), #  -3600  3600 FNST
        datetime(1986,  3, 15,  1,  0,  0), #  -7200     0 FNT
        datetime(1986, 10, 25,  2,  0,  0), #  -3600  3600 FNST
        datetime(1987,  2, 14,  1,  0,  0), #  -7200     0 FNT
        datetime(1987, 10, 25,  2,  0,  0), #  -3600  3600 FNST
        datetime(1988,  2,  7,  1,  0,  0), #  -7200     0 FNT
        datetime(1988, 10, 16,  2,  0,  0), #  -3600  3600 FNST
        datetime(1989,  1, 29,  1,  0,  0), #  -7200     0 FNT
        datetime(1989, 10, 15,  2,  0,  0), #  -3600  3600 FNST
        datetime(1990,  2, 11,  1,  0,  0), #  -7200     0 FNT
        datetime(1999, 10,  3,  2,  0,  0), #  -3600  3600 FNST
        datetime(2000,  2, 27,  1,  0,  0), #  -7200     0 FNT
        datetime(2000, 10,  8,  2,  0,  0), #  -3600  3600 FNST
        datetime(2000, 10, 15,  1,  0,  0), #  -7200     0 FNT
        datetime(2001, 10, 14,  2,  0,  0), #  -3600  3600 FNST
        datetime(2002,  2, 17,  1,  0,  0), #  -7200     0 FNT
        ]

    _transition_info = [
        ttinfo( -7780,      0,  'LMT'),
        ttinfo( -7200,      0,  'FNT'),
        ttinfo( -3600,   3600, 'FNST'),
        ttinfo( -7200,      0,  'FNT'),
        ttinfo( -3600,   3600, 'FNST'),
        ttinfo( -7200,      0,  'FNT'),
        ttinfo( -3600,   3600, 'FNST'),
        ttinfo( -7200,      0,  'FNT'),
        ttinfo( -3600,   3600, 'FNST'),
        ttinfo( -7200,      0,  'FNT'),
        ttinfo( -3600,   3600, 'FNST'),
        ttinfo( -7200,      0,  'FNT'),
        ttinfo( -3600,   3600, 'FNST'),
        ttinfo( -7200,      0,  'FNT'),
        ttinfo( -3600,   3600, 'FNST'),
        ttinfo( -7200,      0,  'FNT'),
        ttinfo( -3600,   3600, 'FNST'),
        ttinfo( -7200,      0,  'FNT'),
        ttinfo( -3600,   3600, 'FNST'),
        ttinfo( -7200,      0,  'FNT'),
        ttinfo( -3600,   3600, 'FNST'),
        ttinfo( -7200,      0,  'FNT'),
        ttinfo( -3600,   3600, 'FNST'),
        ttinfo( -7200,      0,  'FNT'),
        ttinfo( -3600,   3600, 'FNST'),
        ttinfo( -7200,      0,  'FNT'),
        ttinfo( -3600,   3600, 'FNST'),
        ttinfo( -7200,      0,  'FNT'),
        ttinfo( -3600,   3600, 'FNST'),
        ttinfo( -7200,      0,  'FNT'),
        ttinfo( -3600,   3600, 'FNST'),
        ttinfo( -7200,      0,  'FNT'),
        ttinfo( -3600,   3600, 'FNST'),
        ttinfo( -7200,      0,  'FNT'),
        ttinfo( -3600,   3600, 'FNST'),
        ttinfo( -7200,      0,  'FNT'),
        ttinfo( -3600,   3600, 'FNST'),
        ttinfo( -7200,      0,  'FNT'),
        ttinfo( -3600,   3600, 'FNST'),
        ttinfo( -7200,      0,  'FNT'),
        ]

Noronha = Noronha() # Singleton

