'''
tzinfo timezone information for Atlantic/Cape_Verde.

Generated from the Olson timezone database:
    ftp://elsie.nci.nih.gov/pub/tz*.tar.gz
'''

from pytz.tzinfo import DstTzInfo
from pytz.tzinfo import memorized_datetime as datetime
from pytz.tzinfo import memorized_ttinfo as ttinfo

class Cape_Verde(DstTzInfo):
    '''Atlantic/Cape_Verde timezone definition. See datetime.tzinfo for details'''

    _zone = 'Atlantic/Cape_Verde'

    _utc_transition_times = [
        datetime(   1,  1,  1,  0,  0,  0), #  -5644     0 LMT
        datetime(1907,  1,  1,  1, 34,  4), #  -7200     0 CVT
        datetime(1942,  9,  1,  2,  0,  0), #  -3600  3600 CVST
        datetime(1945, 10, 15,  1,  0,  0), #  -7200     0 CVT
        datetime(1975, 11, 25,  4,  0,  0), #  -3600     0 CVT
        ]

    _transition_info = [
        ttinfo( -5644,      0,  'LMT'),
        ttinfo( -7200,      0,  'CVT'),
        ttinfo( -3600,   3600, 'CVST'),
        ttinfo( -7200,      0,  'CVT'),
        ttinfo( -3600,      0,  'CVT'),
        ]

Cape_Verde = Cape_Verde() # Singleton

