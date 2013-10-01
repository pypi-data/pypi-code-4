'''
tzinfo timezone information for America/Santo_Domingo.

Generated from the Olson timezone database:
    ftp://elsie.nci.nih.gov/pub/tz*.tar.gz
'''

from pytz.tzinfo import DstTzInfo
from pytz.tzinfo import memorized_datetime as datetime
from pytz.tzinfo import memorized_ttinfo as ttinfo

class Santo_Domingo(DstTzInfo):
    '''America/Santo_Domingo timezone definition. See datetime.tzinfo for details'''

    _zone = 'America/Santo_Domingo'

    _utc_transition_times = [
        datetime(   1,  1,  1,  0,  0,  0), # -16800     0 SDMT
        datetime(1933,  4,  1, 16, 40,  0), # -18000     0 EST
        datetime(1966, 10, 30,  5,  0,  0), # -14400  3600 EDT
        datetime(1967,  2, 28,  4,  0,  0), # -18000     0 EST
        datetime(1969, 10, 26,  5,  0,  0), # -16200  1800 EHDT
        datetime(1970,  2, 21,  4, 30,  0), # -18000     0 EST
        datetime(1970, 10, 25,  5,  0,  0), # -16200  1800 EHDT
        datetime(1971,  1, 20,  4, 30,  0), # -18000     0 EST
        datetime(1971, 10, 31,  5,  0,  0), # -16200  1800 EHDT
        datetime(1972,  1, 21,  4, 30,  0), # -18000     0 EST
        datetime(1972, 10, 29,  5,  0,  0), # -16200  1800 EHDT
        datetime(1973,  1, 21,  4, 30,  0), # -18000     0 EST
        datetime(1973, 10, 28,  5,  0,  0), # -16200  1800 EHDT
        datetime(1974,  1, 21,  4, 30,  0), # -18000     0 EST
        datetime(1974, 10, 27,  5,  0,  0), # -14400     0 AST
        datetime(2000, 10, 29,  6,  0,  0), # -18000     0 EST
        datetime(2000, 12,  3,  6,  0,  0), # -14400     0 AST
        ]

    _transition_info = [
        ttinfo(-16800,      0, 'SDMT'),
        ttinfo(-18000,      0,  'EST'),
        ttinfo(-14400,   3600,  'EDT'),
        ttinfo(-18000,      0,  'EST'),
        ttinfo(-16200,   1800, 'EHDT'),
        ttinfo(-18000,      0,  'EST'),
        ttinfo(-16200,   1800, 'EHDT'),
        ttinfo(-18000,      0,  'EST'),
        ttinfo(-16200,   1800, 'EHDT'),
        ttinfo(-18000,      0,  'EST'),
        ttinfo(-16200,   1800, 'EHDT'),
        ttinfo(-18000,      0,  'EST'),
        ttinfo(-16200,   1800, 'EHDT'),
        ttinfo(-18000,      0,  'EST'),
        ttinfo(-14400,      0,  'AST'),
        ttinfo(-18000,      0,  'EST'),
        ttinfo(-14400,      0,  'AST'),
        ]

Santo_Domingo = Santo_Domingo() # Singleton

