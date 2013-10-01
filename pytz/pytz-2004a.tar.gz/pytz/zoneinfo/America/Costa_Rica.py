'''
tzinfo timezone information for America/Costa_Rica.

Generated from the Olson timezone database:
    ftp://elsie.nci.nih.gov/pub/tz*.tar.gz
'''

from pytz.tzinfo import DstTzInfo
from pytz.tzinfo import memorized_datetime as datetime
from pytz.tzinfo import memorized_ttinfo as ttinfo

class Costa_Rica(DstTzInfo):
    '''America/Costa_Rica timezone definition. See datetime.tzinfo for details'''

    _zone = 'America/Costa_Rica'

    _utc_transition_times = [
        datetime(   1,  1,  1,  0,  0,  0), # -20180     0 SJMT
        datetime(1921,  1, 15,  5, 36, 20), # -21600     0 CST
        datetime(1979,  2, 25,  6,  0,  0), # -18000  3600 CDT
        datetime(1979,  6,  3,  5,  0,  0), # -21600     0 CST
        datetime(1980,  2, 24,  6,  0,  0), # -18000  3600 CDT
        datetime(1980,  6,  1,  5,  0,  0), # -21600     0 CST
        datetime(1991,  1, 19,  6,  0,  0), # -18000  3600 CDT
        datetime(1991,  7,  1,  5,  0,  0), # -21600     0 CST
        datetime(1992,  1, 18,  6,  0,  0), # -18000  3600 CDT
        datetime(1992,  3, 15,  5,  0,  0), # -21600     0 CST
        ]

    _transition_info = [
        ttinfo(-20180,      0, 'SJMT'),
        ttinfo(-21600,      0,  'CST'),
        ttinfo(-18000,   3600,  'CDT'),
        ttinfo(-21600,      0,  'CST'),
        ttinfo(-18000,   3600,  'CDT'),
        ttinfo(-21600,      0,  'CST'),
        ttinfo(-18000,   3600,  'CDT'),
        ttinfo(-21600,      0,  'CST'),
        ttinfo(-18000,   3600,  'CDT'),
        ttinfo(-21600,      0,  'CST'),
        ]

Costa_Rica = Costa_Rica() # Singleton

