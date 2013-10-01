'''
tzinfo timezone information for Africa/Brazzaville.

Generated from the Olson timezone database:
    ftp://elsie.nci.nih.gov/pub/tz*.tar.gz
'''

from pytz.tzinfo import DstTzInfo
from pytz.tzinfo import memorized_datetime as datetime
from pytz.tzinfo import memorized_ttinfo as ttinfo

class Brazzaville(DstTzInfo):
    '''Africa/Brazzaville timezone definition. See datetime.tzinfo for details'''

    _zone = 'Africa/Brazzaville'

    _utc_transition_times = [
        datetime(   1,  1,  1,  0,  0,  0), #   3668     0 LMT
        datetime(1911, 12, 31, 22, 58, 52), #   3600     0 WAT
        ]

    _transition_info = [
        ttinfo(  3668,      0,  'LMT'),
        ttinfo(  3600,      0,  'WAT'),
        ]

Brazzaville = Brazzaville() # Singleton

