'''
tzinfo timezone information for Asia/Rangoon.

Generated from the Olson timezone database:
    ftp://elsie.nci.nih.gov/pub/tz*.tar.gz
'''

from pytz.tzinfo import DstTzInfo
from pytz.tzinfo import memorized_datetime as datetime
from pytz.tzinfo import memorized_ttinfo as ttinfo

class Rangoon(DstTzInfo):
    '''Asia/Rangoon timezone definition. See datetime.tzinfo for details'''

    _zone = 'Asia/Rangoon'

    _utc_transition_times = [
        datetime(   1,  1,  1,  0,  0,  0), #  23076     0 RMT
        datetime(1919, 12, 31, 17, 35, 24), #  23400     0 BURT
        datetime(1942,  4, 30, 17, 30,  0), #  32400     0 JST
        datetime(1945,  5,  2, 15,  0,  0), #  23400     0 MMT
        ]

    _transition_info = [
        ttinfo( 23076,      0,  'RMT'),
        ttinfo( 23400,      0, 'BURT'),
        ttinfo( 32400,      0,  'JST'),
        ttinfo( 23400,      0,  'MMT'),
        ]

Rangoon = Rangoon() # Singleton

