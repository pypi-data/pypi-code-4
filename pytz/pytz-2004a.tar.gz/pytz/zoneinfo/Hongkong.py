'''
tzinfo timezone information for Hongkong.

Generated from the Olson timezone database:
    ftp://elsie.nci.nih.gov/pub/tz*.tar.gz
'''

from pytz.tzinfo import DstTzInfo
from pytz.tzinfo import memorized_datetime as datetime
from pytz.tzinfo import memorized_ttinfo as ttinfo

class Hongkong(DstTzInfo):
    '''Hongkong timezone definition. See datetime.tzinfo for details'''

    _zone = 'Hongkong'

    _utc_transition_times = [
        datetime(   1,  1,  1,  0,  0,  0), #  27396     0 LMT
        datetime(1904, 10, 29, 16, 23, 24), #  28800     0 HKT
        datetime(1946,  4, 19, 19, 30,  0), #  32400  3600 HKST
        datetime(1946, 11, 30, 18, 30,  0), #  28800     0 HKT
        datetime(1947,  4, 12, 19, 30,  0), #  32400  3600 HKST
        datetime(1947, 12, 29, 18, 30,  0), #  28800     0 HKT
        datetime(1948,  5,  1, 19, 30,  0), #  32400  3600 HKST
        datetime(1948, 10, 30, 18, 30,  0), #  28800     0 HKT
        datetime(1949,  4,  2, 19, 30,  0), #  32400  3600 HKST
        datetime(1949, 10, 29, 18, 30,  0), #  28800     0 HKT
        datetime(1950,  4,  1, 19, 30,  0), #  32400  3600 HKST
        datetime(1950, 10, 28, 18, 30,  0), #  28800     0 HKT
        datetime(1951,  3, 31, 19, 30,  0), #  32400  3600 HKST
        datetime(1951, 10, 27, 18, 30,  0), #  28800     0 HKT
        datetime(1952,  4,  5, 19, 30,  0), #  32400  3600 HKST
        datetime(1952, 10, 25, 18, 30,  0), #  28800     0 HKT
        datetime(1953,  4,  4, 19, 30,  0), #  32400  3600 HKST
        datetime(1953, 10, 31, 18, 30,  0), #  28800     0 HKT
        datetime(1954,  3, 20, 19, 30,  0), #  32400  3600 HKST
        datetime(1954, 10, 30, 18, 30,  0), #  28800     0 HKT
        datetime(1955,  3, 19, 19, 30,  0), #  32400  3600 HKST
        datetime(1955, 11,  5, 18, 30,  0), #  28800     0 HKT
        datetime(1956,  3, 17, 19, 30,  0), #  32400  3600 HKST
        datetime(1956, 11,  3, 18, 30,  0), #  28800     0 HKT
        datetime(1957,  3, 23, 19, 30,  0), #  32400  3600 HKST
        datetime(1957, 11,  2, 18, 30,  0), #  28800     0 HKT
        datetime(1958,  3, 22, 19, 30,  0), #  32400  3600 HKST
        datetime(1958, 11,  1, 18, 30,  0), #  28800     0 HKT
        datetime(1959,  3, 21, 19, 30,  0), #  32400  3600 HKST
        datetime(1959, 10, 31, 18, 30,  0), #  28800     0 HKT
        datetime(1960,  3, 19, 19, 30,  0), #  32400  3600 HKST
        datetime(1960, 11,  5, 18, 30,  0), #  28800     0 HKT
        datetime(1961,  3, 18, 19, 30,  0), #  32400  3600 HKST
        datetime(1961, 11,  4, 18, 30,  0), #  28800     0 HKT
        datetime(1962,  3, 17, 19, 30,  0), #  32400  3600 HKST
        datetime(1962, 11,  3, 18, 30,  0), #  28800     0 HKT
        datetime(1963,  3, 23, 19, 30,  0), #  32400  3600 HKST
        datetime(1963, 11,  2, 18, 30,  0), #  28800     0 HKT
        datetime(1964,  3, 21, 19, 30,  0), #  32400  3600 HKST
        datetime(1964, 10, 31, 18, 30,  0), #  28800     0 HKT
        datetime(1965,  4, 17, 19, 30,  0), #  32400  3600 HKST
        datetime(1965, 10, 16, 18, 30,  0), #  28800     0 HKT
        datetime(1966,  4, 16, 19, 30,  0), #  32400  3600 HKST
        datetime(1966, 10, 15, 18, 30,  0), #  28800     0 HKT
        datetime(1967,  4, 15, 19, 30,  0), #  32400  3600 HKST
        datetime(1967, 10, 21, 18, 30,  0), #  28800     0 HKT
        datetime(1968,  4, 20, 19, 30,  0), #  32400  3600 HKST
        datetime(1968, 10, 19, 18, 30,  0), #  28800     0 HKT
        datetime(1969,  4, 19, 19, 30,  0), #  32400  3600 HKST
        datetime(1969, 10, 18, 18, 30,  0), #  28800     0 HKT
        datetime(1970,  4, 18, 19, 30,  0), #  32400  3600 HKST
        datetime(1970, 10, 17, 18, 30,  0), #  28800     0 HKT
        datetime(1971,  4, 17, 19, 30,  0), #  32400  3600 HKST
        datetime(1971, 10, 16, 18, 30,  0), #  28800     0 HKT
        datetime(1972,  4, 15, 19, 30,  0), #  32400  3600 HKST
        datetime(1972, 10, 21, 18, 30,  0), #  28800     0 HKT
        datetime(1973,  4, 21, 19, 30,  0), #  32400  3600 HKST
        datetime(1973, 10, 20, 18, 30,  0), #  28800     0 HKT
        datetime(1974,  4, 20, 19, 30,  0), #  32400  3600 HKST
        datetime(1974, 10, 19, 18, 30,  0), #  28800     0 HKT
        datetime(1975,  4, 19, 19, 30,  0), #  32400  3600 HKST
        datetime(1975, 10, 18, 18, 30,  0), #  28800     0 HKT
        datetime(1976,  4, 17, 19, 30,  0), #  32400  3600 HKST
        datetime(1976, 10, 16, 18, 30,  0), #  28800     0 HKT
        datetime(1977,  4, 16, 19, 30,  0), #  32400  3600 HKST
        datetime(1977, 10, 15, 18, 30,  0), #  28800     0 HKT
        datetime(1979,  5, 12, 19, 30,  0), #  32400  3600 HKST
        datetime(1979, 10, 20, 18, 30,  0), #  28800     0 HKT
        datetime(1980,  5, 10, 19, 30,  0), #  32400  3600 HKST
        datetime(1980, 10, 18, 18, 30,  0), #  28800     0 HKT
        ]

    _transition_info = [
        ttinfo( 27396,      0,  'LMT'),
        ttinfo( 28800,      0,  'HKT'),
        ttinfo( 32400,   3600, 'HKST'),
        ttinfo( 28800,      0,  'HKT'),
        ttinfo( 32400,   3600, 'HKST'),
        ttinfo( 28800,      0,  'HKT'),
        ttinfo( 32400,   3600, 'HKST'),
        ttinfo( 28800,      0,  'HKT'),
        ttinfo( 32400,   3600, 'HKST'),
        ttinfo( 28800,      0,  'HKT'),
        ttinfo( 32400,   3600, 'HKST'),
        ttinfo( 28800,      0,  'HKT'),
        ttinfo( 32400,   3600, 'HKST'),
        ttinfo( 28800,      0,  'HKT'),
        ttinfo( 32400,   3600, 'HKST'),
        ttinfo( 28800,      0,  'HKT'),
        ttinfo( 32400,   3600, 'HKST'),
        ttinfo( 28800,      0,  'HKT'),
        ttinfo( 32400,   3600, 'HKST'),
        ttinfo( 28800,      0,  'HKT'),
        ttinfo( 32400,   3600, 'HKST'),
        ttinfo( 28800,      0,  'HKT'),
        ttinfo( 32400,   3600, 'HKST'),
        ttinfo( 28800,      0,  'HKT'),
        ttinfo( 32400,   3600, 'HKST'),
        ttinfo( 28800,      0,  'HKT'),
        ttinfo( 32400,   3600, 'HKST'),
        ttinfo( 28800,      0,  'HKT'),
        ttinfo( 32400,   3600, 'HKST'),
        ttinfo( 28800,      0,  'HKT'),
        ttinfo( 32400,   3600, 'HKST'),
        ttinfo( 28800,      0,  'HKT'),
        ttinfo( 32400,   3600, 'HKST'),
        ttinfo( 28800,      0,  'HKT'),
        ttinfo( 32400,   3600, 'HKST'),
        ttinfo( 28800,      0,  'HKT'),
        ttinfo( 32400,   3600, 'HKST'),
        ttinfo( 28800,      0,  'HKT'),
        ttinfo( 32400,   3600, 'HKST'),
        ttinfo( 28800,      0,  'HKT'),
        ttinfo( 32400,   3600, 'HKST'),
        ttinfo( 28800,      0,  'HKT'),
        ttinfo( 32400,   3600, 'HKST'),
        ttinfo( 28800,      0,  'HKT'),
        ttinfo( 32400,   3600, 'HKST'),
        ttinfo( 28800,      0,  'HKT'),
        ttinfo( 32400,   3600, 'HKST'),
        ttinfo( 28800,      0,  'HKT'),
        ttinfo( 32400,   3600, 'HKST'),
        ttinfo( 28800,      0,  'HKT'),
        ttinfo( 32400,   3600, 'HKST'),
        ttinfo( 28800,      0,  'HKT'),
        ttinfo( 32400,   3600, 'HKST'),
        ttinfo( 28800,      0,  'HKT'),
        ttinfo( 32400,   3600, 'HKST'),
        ttinfo( 28800,      0,  'HKT'),
        ttinfo( 32400,   3600, 'HKST'),
        ttinfo( 28800,      0,  'HKT'),
        ttinfo( 32400,   3600, 'HKST'),
        ttinfo( 28800,      0,  'HKT'),
        ttinfo( 32400,   3600, 'HKST'),
        ttinfo( 28800,      0,  'HKT'),
        ttinfo( 32400,   3600, 'HKST'),
        ttinfo( 28800,      0,  'HKT'),
        ttinfo( 32400,   3600, 'HKST'),
        ttinfo( 28800,      0,  'HKT'),
        ttinfo( 32400,   3600, 'HKST'),
        ttinfo( 28800,      0,  'HKT'),
        ttinfo( 32400,   3600, 'HKST'),
        ttinfo( 28800,      0,  'HKT'),
        ]

Hongkong = Hongkong() # Singleton

