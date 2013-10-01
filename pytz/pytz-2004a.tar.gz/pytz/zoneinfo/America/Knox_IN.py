'''
tzinfo timezone information for America/Knox_IN.

Generated from the Olson timezone database:
    ftp://elsie.nci.nih.gov/pub/tz*.tar.gz
'''

from pytz.tzinfo import DstTzInfo
from pytz.tzinfo import memorized_datetime as datetime
from pytz.tzinfo import memorized_ttinfo as ttinfo

class Knox_IN(DstTzInfo):
    '''America/Knox_IN timezone definition. See datetime.tzinfo for details'''

    _zone = 'America/Knox_IN'

    _utc_transition_times = [
        datetime(   1,  1,  1,  0,  0,  0), # -21600     0 CST
        datetime(1918,  3, 31,  8,  0,  0), # -18000  3600 CDT
        datetime(1918, 10, 27,  7,  0,  0), # -21600     0 CST
        datetime(1919,  3, 30,  8,  0,  0), # -18000  3600 CDT
        datetime(1919, 10, 26,  7,  0,  0), # -21600     0 CST
        datetime(1942,  2,  9,  8,  0,  0), # -18000  3600 CWT
        datetime(1945,  8, 14, 23,  0,  0), # -18000     0 CPT
        datetime(1945,  9, 30,  7,  0,  0), # -21600     0 CST
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
        datetime(1955,  4, 24,  8,  0,  0), # -18000  3600 CDT
        datetime(1955, 10, 30,  7,  0,  0), # -21600     0 CST
        datetime(1956,  4, 29,  8,  0,  0), # -18000  3600 CDT
        datetime(1956, 10, 28,  7,  0,  0), # -21600     0 CST
        datetime(1957,  4, 28,  8,  0,  0), # -18000  3600 CDT
        datetime(1957,  9, 29,  7,  0,  0), # -21600     0 CST
        datetime(1958,  4, 27,  8,  0,  0), # -18000  3600 CDT
        datetime(1958,  9, 28,  7,  0,  0), # -21600     0 CST
        datetime(1959,  4, 26,  8,  0,  0), # -18000  3600 CDT
        datetime(1959, 10, 25,  7,  0,  0), # -21600     0 CST
        datetime(1960,  4, 24,  8,  0,  0), # -18000  3600 CDT
        datetime(1960, 10, 30,  7,  0,  0), # -21600     0 CST
        datetime(1961,  4, 30,  8,  0,  0), # -18000  3600 CDT
        datetime(1961, 10, 29,  7,  0,  0), # -21600     0 CST
        datetime(1962,  4, 29,  8,  0,  0), # -18000     0 EST
        datetime(1963, 10, 27,  7,  0,  0), # -21600     0 CST
        datetime(1967,  4, 30,  8,  0,  0), # -18000  3600 CDT
        datetime(1967, 10, 29,  7,  0,  0), # -21600     0 CST
        datetime(1968,  4, 28,  8,  0,  0), # -18000  3600 CDT
        datetime(1968, 10, 27,  7,  0,  0), # -21600     0 CST
        datetime(1969,  4, 27,  8,  0,  0), # -18000  3600 CDT
        datetime(1969, 10, 26,  7,  0,  0), # -21600     0 CST
        datetime(1970,  4, 26,  8,  0,  0), # -18000  3600 CDT
        datetime(1970, 10, 25,  7,  0,  0), # -21600     0 CST
        datetime(1971,  4, 25,  8,  0,  0), # -18000  3600 CDT
        datetime(1971, 10, 31,  7,  0,  0), # -21600     0 CST
        datetime(1972,  4, 30,  8,  0,  0), # -18000  3600 CDT
        datetime(1972, 10, 29,  7,  0,  0), # -21600     0 CST
        datetime(1973,  4, 29,  8,  0,  0), # -18000  3600 CDT
        datetime(1973, 10, 28,  7,  0,  0), # -21600     0 CST
        datetime(1974,  1,  6,  8,  0,  0), # -18000  3600 CDT
        datetime(1974, 10, 27,  7,  0,  0), # -21600     0 CST
        datetime(1975,  2, 23,  8,  0,  0), # -18000  3600 CDT
        datetime(1975, 10, 26,  7,  0,  0), # -21600     0 CST
        datetime(1976,  4, 25,  8,  0,  0), # -18000  3600 CDT
        datetime(1976, 10, 31,  7,  0,  0), # -21600     0 CST
        datetime(1977,  4, 24,  8,  0,  0), # -18000  3600 CDT
        datetime(1977, 10, 30,  7,  0,  0), # -21600     0 CST
        datetime(1978,  4, 30,  8,  0,  0), # -18000  3600 CDT
        datetime(1978, 10, 29,  7,  0,  0), # -21600     0 CST
        datetime(1979,  4, 29,  8,  0,  0), # -18000  3600 CDT
        datetime(1979, 10, 28,  7,  0,  0), # -21600     0 CST
        datetime(1980,  4, 27,  8,  0,  0), # -18000  3600 CDT
        datetime(1980, 10, 26,  7,  0,  0), # -21600     0 CST
        datetime(1981,  4, 26,  8,  0,  0), # -18000  3600 CDT
        datetime(1981, 10, 25,  7,  0,  0), # -21600     0 CST
        datetime(1982,  4, 25,  8,  0,  0), # -18000  3600 CDT
        datetime(1982, 10, 31,  7,  0,  0), # -21600     0 CST
        datetime(1983,  4, 24,  8,  0,  0), # -18000  3600 CDT
        datetime(1983, 10, 30,  7,  0,  0), # -21600     0 CST
        datetime(1984,  4, 29,  8,  0,  0), # -18000  3600 CDT
        datetime(1984, 10, 28,  7,  0,  0), # -21600     0 CST
        datetime(1985,  4, 28,  8,  0,  0), # -18000  3600 CDT
        datetime(1985, 10, 27,  7,  0,  0), # -21600     0 CST
        datetime(1986,  4, 27,  8,  0,  0), # -18000  3600 CDT
        datetime(1986, 10, 26,  7,  0,  0), # -21600     0 CST
        datetime(1987,  4,  5,  8,  0,  0), # -18000  3600 CDT
        datetime(1987, 10, 25,  7,  0,  0), # -21600     0 CST
        datetime(1988,  4,  3,  8,  0,  0), # -18000  3600 CDT
        datetime(1988, 10, 30,  7,  0,  0), # -21600     0 CST
        datetime(1989,  4,  2,  8,  0,  0), # -18000  3600 CDT
        datetime(1989, 10, 29,  7,  0,  0), # -21600     0 CST
        datetime(1990,  4,  1,  8,  0,  0), # -18000  3600 CDT
        datetime(1990, 10, 28,  7,  0,  0), # -21600     0 CST
        datetime(1991,  4,  7,  8,  0,  0), # -18000  3600 CDT
        datetime(1991, 10, 27,  7,  0,  0), # -18000     0 EST
        ]

    _transition_info = [
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
        ttinfo(-18000,      0,  'EST'),
        ]

Knox_IN = Knox_IN() # Singleton

