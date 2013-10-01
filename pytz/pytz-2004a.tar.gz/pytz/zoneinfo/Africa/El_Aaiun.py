'''
tzinfo timezone information for Africa/El_Aaiun.

Generated from the Olson timezone database:
    ftp://elsie.nci.nih.gov/pub/tz*.tar.gz
'''

from pytz.tzinfo import DstTzInfo
from pytz.tzinfo import memorized_datetime as datetime
from pytz.tzinfo import memorized_ttinfo as ttinfo

class El_Aaiun(DstTzInfo):
    '''Africa/El_Aaiun timezone definition. See datetime.tzinfo for details'''

    _zone = 'Africa/El_Aaiun'

    _utc_transition_times = [
        datetime(   1,  1,  1,  0,  0,  0), #  -3168     0 LMT
        datetime(1934,  1,  1,  0, 52, 48), #  -3600     0 WAT
        datetime(1976,  4, 14,  1,  0,  0), #      0     0 WET
        ]

    _transition_info = [
        ttinfo( -3168,      0,  'LMT'),
        ttinfo( -3600,      0,  'WAT'),
        ttinfo(     0,      0,  'WET'),
        ]

El_Aaiun = El_Aaiun() # Singleton

