'''
tzinfo timezone information for Africa/Lagos.

Generated from the Olson timezone database:
    ftp://elsie.nci.nih.gov/pub/tz*.tar.gz
'''

from pytz.tzinfo import DstTzInfo
from pytz.tzinfo import memorized_datetime as datetime
from pytz.tzinfo import memorized_ttinfo as ttinfo

class Lagos(DstTzInfo):
    '''Africa/Lagos timezone definition. See datetime.tzinfo for details'''

    _zone = 'Africa/Lagos'

    _utc_transition_times = [
        datetime(   1,  1,  1,  0,  0,  0), #    816     0 LMT
        datetime(1919,  8, 31, 23, 46, 24), #   3600     0 WAT
        ]

    _transition_info = [
        ttinfo(   816,      0,  'LMT'),
        ttinfo(  3600,      0,  'WAT'),
        ]

Lagos = Lagos() # Singleton

