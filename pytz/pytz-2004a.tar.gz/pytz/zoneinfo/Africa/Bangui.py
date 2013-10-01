'''
tzinfo timezone information for Africa/Bangui.

Generated from the Olson timezone database:
    ftp://elsie.nci.nih.gov/pub/tz*.tar.gz
'''

from pytz.tzinfo import DstTzInfo
from pytz.tzinfo import memorized_datetime as datetime
from pytz.tzinfo import memorized_ttinfo as ttinfo

class Bangui(DstTzInfo):
    '''Africa/Bangui timezone definition. See datetime.tzinfo for details'''

    _zone = 'Africa/Bangui'

    _utc_transition_times = [
        datetime(   1,  1,  1,  0,  0,  0), #   4460     0 LMT
        datetime(1911, 12, 31, 22, 45, 40), #   3600     0 WAT
        ]

    _transition_info = [
        ttinfo(  4460,      0,  'LMT'),
        ttinfo(  3600,      0,  'WAT'),
        ]

Bangui = Bangui() # Singleton

