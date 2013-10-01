'''
tzinfo timezone information for America/Indiana/Marengo.

Generated from the Olson timezone database:
    ftp://elsie.nci.nih.gov/pub/tz*.tar.gz
'''

from pytz.tzinfo import DstTzInfo
from pytz.tzinfo import memorized_datetime as datetime
from pytz.tzinfo import memorized_ttinfo as ttinfo

class Marengo(DstTzInfo):
    '''America/Indiana/Marengo timezone definition. See datetime.tzinfo for details'''

    _zone = 'America/Indiana/Marengo'

    _utc_transition_times = [
        datetime(   1,  1,  1,  0,  0,  0), # -21600     0 CST
        datetime(1918,  3, 31,  8,  0,  0), # -18000  3600 CDT
        datetime(1918, 10, 27,  7,  0,  0), # -21600     0 CST
        datetime(1919,  3, 30,  8,  0,  0), # -18000  3600 CDT
        datetime(1919, 10, 26,  7,  0,  0), # -21600     0 CST
        datetime(1942,  2,  9,  8,  0,  0), # -18000  3600 CWT
        datetime(1945,  8, 14, 23,  0,  0), # -18000     0 CPT
        datetime(1945,  9, 30,  7,  0,  0), # -21600     0 CST
        datetime(1951,  4, 29,  8,  0,  0), # -18000  3600 CDT
        datetime(1951,  9, 30,  7,  0,  0), # -21600     0 CST
        datetime(1954,  4, 25,  8,  0,  0), # -18000  3600 CDT
        datetime(1954,  9, 26,  7,  0,  0), # -21600     0 CST
        datetime(1955,  4, 24,  8,  0,  0), # -18000  3600 CDT
        datetime(1955,  9, 25,  7,  0,  0), # -21600     0 CST
        datetime(1956,  4, 29,  8,  0,  0), # -18000  3600 CDT
        datetime(1956,  9, 30,  7,  0,  0), # -21600     0 CST
        datetime(1957,  4, 28,  8,  0,  0), # -18000  3600 CDT
        datetime(1957,  9, 29,  7,  0,  0), # -21600     0 CST
        datetime(1958,  4, 27,  8,  0,  0), # -18000  3600 CDT
        datetime(1958,  9, 28,  7,  0,  0), # -21600     0 CST
        datetime(1959,  4, 26,  8,  0,  0), # -18000  3600 CDT
        datetime(1959,  9, 27,  7,  0,  0), # -21600     0 CST
        datetime(1960,  4, 24,  8,  0,  0), # -18000  3600 CDT
        datetime(1960,  9, 25,  7,  0,  0), # -21600     0 CST
        datetime(1961,  4, 30,  8,  0,  0), # -18000     0 EST
        datetime(1969,  4, 27,  7,  0,  0), # -14400  3600 EDT
        datetime(1969, 10, 26,  6,  0,  0), # -18000     0 EST
        datetime(1970,  4, 26,  7,  0,  0), # -14400  3600 EDT
        datetime(1970, 10, 25,  6,  0,  0), # -18000     0 EST
        datetime(1971,  4, 25,  7,  0,  0), # -14400  3600 EDT
        datetime(1971, 10, 31,  6,  0,  0), # -18000     0 EST
        datetime(1972,  4, 30,  7,  0,  0), # -14400  3600 EDT
        datetime(1972, 10, 29,  6,  0,  0), # -18000     0 EST
        datetime(1973,  4, 29,  7,  0,  0), # -14400  3600 EDT
        datetime(1973, 10, 28,  6,  0,  0), # -18000     0 EST
        datetime(1974,  1,  6,  7,  0,  0), # -18000     0 CDT
        datetime(1974, 10, 27,  7,  0,  0), # -18000     0 EST
        datetime(1975,  2, 23,  7,  0,  0), # -14400  3600 EDT
        datetime(1975, 10, 26,  6,  0,  0), # -18000     0 EST
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
        ttinfo(-18000,      0,  'CDT'),
        ttinfo(-18000,      0,  'EST'),
        ttinfo(-14400,   3600,  'EDT'),
        ttinfo(-18000,      0,  'EST'),
        ]

Marengo = Marengo() # Singleton

