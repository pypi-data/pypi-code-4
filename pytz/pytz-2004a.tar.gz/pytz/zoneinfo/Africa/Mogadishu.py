'''
tzinfo timezone information for Africa/Mogadishu.

Generated from the Olson timezone database:
    ftp://elsie.nci.nih.gov/pub/tz*.tar.gz
'''

from pytz.tzinfo import DstTzInfo
from pytz.tzinfo import memorized_datetime as datetime
from pytz.tzinfo import memorized_ttinfo as ttinfo

class Mogadishu(DstTzInfo):
    '''Africa/Mogadishu timezone definition. See datetime.tzinfo for details'''

    _zone = 'Africa/Mogadishu'

    _utc_transition_times = [
        datetime(   1,  1,  1,  0,  0,  0), #  10800     0 EAT
        datetime(1930, 12, 31, 21,  0,  0), #   9000     0 BEAT
        datetime(1956, 12, 31, 21, 30,  0), #  10800     0 EAT
        ]

    _transition_info = [
        ttinfo( 10800,      0,  'EAT'),
        ttinfo(  9000,      0, 'BEAT'),
        ttinfo( 10800,      0,  'EAT'),
        ]

Mogadishu = Mogadishu() # Singleton

