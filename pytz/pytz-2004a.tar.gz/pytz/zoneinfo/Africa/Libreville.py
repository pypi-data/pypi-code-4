'''
tzinfo timezone information for Africa/Libreville.

Generated from the Olson timezone database:
    ftp://elsie.nci.nih.gov/pub/tz*.tar.gz
'''

from pytz.tzinfo import DstTzInfo
from pytz.tzinfo import memorized_datetime as datetime
from pytz.tzinfo import memorized_ttinfo as ttinfo

class Libreville(DstTzInfo):
    '''Africa/Libreville timezone definition. See datetime.tzinfo for details'''

    _zone = 'Africa/Libreville'

    _utc_transition_times = [
        datetime(   1,  1,  1,  0,  0,  0), #   2268     0 LMT
        datetime(1911, 12, 31, 23, 22, 12), #   3600     0 WAT
        ]

    _transition_info = [
        ttinfo(  2268,      0,  'LMT'),
        ttinfo(  3600,      0,  'WAT'),
        ]

Libreville = Libreville() # Singleton

