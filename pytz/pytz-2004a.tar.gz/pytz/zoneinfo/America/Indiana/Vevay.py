'''
tzinfo timezone information for America/Indiana/Vevay.

Generated from the Olson timezone database:
    ftp://elsie.nci.nih.gov/pub/tz*.tar.gz
'''

from pytz.tzinfo import DstTzInfo
from pytz.tzinfo import memorized_datetime as datetime
from pytz.tzinfo import memorized_ttinfo as ttinfo

class Vevay(DstTzInfo):
    '''America/Indiana/Vevay timezone definition. See datetime.tzinfo for details'''

    _zone = 'America/Indiana/Vevay'

    _utc_transition_times = [
        datetime(   1,  1,  1,  0,  0,  0), # -21600     0 CST
        datetime(1918,  3, 31,  8,  0,  0), # -18000  3600 CDT
        datetime(1918, 10, 27,  7,  0,  0), # -21600     0 CST
        datetime(1919,  3, 30,  8,  0,  0), # -18000  3600 CDT
        datetime(1919, 10, 26,  7,  0,  0), # -21600     0 CST
        datetime(1942,  2,  9,  8,  0,  0), # -18000  3600 CWT
        datetime(1945,  8, 14, 23,  0,  0), # -18000     0 CPT
        datetime(1945,  9, 30,  7,  0,  0), # -21600     0 CST
        datetime(1954,  4, 25,  8,  0,  0), # -18000     0 EST
        datetime(1969,  4, 27,  7,  0,  0), # -14400  3600 EDT
        datetime(1969, 10, 26,  6,  0,  0), # -18000     0 EST
        datetime(1970,  4, 26,  7,  0,  0), # -14400  3600 EDT
        datetime(1970, 10, 25,  6,  0,  0), # -18000     0 EST
        datetime(1971,  4, 25,  7,  0,  0), # -14400  3600 EDT
        datetime(1971, 10, 31,  6,  0,  0), # -18000     0 EST
        datetime(1972,  4, 30,  7,  0,  0), # -14400  3600 EDT
        datetime(1972, 10, 29,  6,  0,  0), # -18000     0 EST
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

Vevay = Vevay() # Singleton

