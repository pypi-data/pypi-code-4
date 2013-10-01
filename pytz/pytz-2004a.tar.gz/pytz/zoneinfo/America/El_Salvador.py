'''
tzinfo timezone information for America/El_Salvador.

Generated from the Olson timezone database:
    ftp://elsie.nci.nih.gov/pub/tz*.tar.gz
'''

from pytz.tzinfo import DstTzInfo
from pytz.tzinfo import memorized_datetime as datetime
from pytz.tzinfo import memorized_ttinfo as ttinfo

class El_Salvador(DstTzInfo):
    '''America/El_Salvador timezone definition. See datetime.tzinfo for details'''

    _zone = 'America/El_Salvador'

    _utc_transition_times = [
        datetime(   1,  1,  1,  0,  0,  0), # -21408     0 LMT
        datetime(1921,  1,  1,  5, 56, 48), # -21600     0 CST
        datetime(1987,  5,  3,  6,  0,  0), # -18000  3600 CDT
        datetime(1987,  9, 27,  5,  0,  0), # -21600     0 CST
        datetime(1988,  5,  1,  6,  0,  0), # -18000  3600 CDT
        datetime(1988,  9, 25,  5,  0,  0), # -21600     0 CST
        ]

    _transition_info = [
        ttinfo(-21408,      0,  'LMT'),
        ttinfo(-21600,      0,  'CST'),
        ttinfo(-18000,   3600,  'CDT'),
        ttinfo(-21600,      0,  'CST'),
        ttinfo(-18000,   3600,  'CDT'),
        ttinfo(-21600,      0,  'CST'),
        ]

El_Salvador = El_Salvador() # Singleton

