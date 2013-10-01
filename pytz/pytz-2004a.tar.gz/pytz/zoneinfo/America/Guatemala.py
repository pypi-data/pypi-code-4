'''
tzinfo timezone information for America/Guatemala.

Generated from the Olson timezone database:
    ftp://elsie.nci.nih.gov/pub/tz*.tar.gz
'''

from pytz.tzinfo import DstTzInfo
from pytz.tzinfo import memorized_datetime as datetime
from pytz.tzinfo import memorized_ttinfo as ttinfo

class Guatemala(DstTzInfo):
    '''America/Guatemala timezone definition. See datetime.tzinfo for details'''

    _zone = 'America/Guatemala'

    _utc_transition_times = [
        datetime(   1,  1,  1,  0,  0,  0), # -21724     0 LMT
        datetime(1918, 10,  5,  6,  2,  4), # -21600     0 CST
        datetime(1973, 11, 25,  6,  0,  0), # -18000  3600 CDT
        datetime(1974,  2, 24,  5,  0,  0), # -21600     0 CST
        datetime(1983,  5, 21,  6,  0,  0), # -18000  3600 CDT
        datetime(1983,  9, 22,  5,  0,  0), # -21600     0 CST
        datetime(1991,  3, 23,  6,  0,  0), # -18000  3600 CDT
        datetime(1991,  9,  7,  5,  0,  0), # -21600     0 CST
        ]

    _transition_info = [
        ttinfo(-21724,      0,  'LMT'),
        ttinfo(-21600,      0,  'CST'),
        ttinfo(-18000,   3600,  'CDT'),
        ttinfo(-21600,      0,  'CST'),
        ttinfo(-18000,   3600,  'CDT'),
        ttinfo(-21600,      0,  'CST'),
        ttinfo(-18000,   3600,  'CDT'),
        ttinfo(-21600,      0,  'CST'),
        ]

Guatemala = Guatemala() # Singleton

