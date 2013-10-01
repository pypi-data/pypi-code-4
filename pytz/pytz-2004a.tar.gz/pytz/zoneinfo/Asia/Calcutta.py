'''
tzinfo timezone information for Asia/Calcutta.

Generated from the Olson timezone database:
    ftp://elsie.nci.nih.gov/pub/tz*.tar.gz
'''

from pytz.tzinfo import DstTzInfo
from pytz.tzinfo import memorized_datetime as datetime
from pytz.tzinfo import memorized_ttinfo as ttinfo

class Calcutta(DstTzInfo):
    '''Asia/Calcutta timezone definition. See datetime.tzinfo for details'''

    _zone = 'Asia/Calcutta'

    _utc_transition_times = [
        datetime(   1,  1,  1,  0,  0,  0), #  21200     0 HMT
        datetime(1941,  9, 30, 18,  6, 40), #  23400     0 BURT
        datetime(1942,  5, 14, 17, 30,  0), #  19800     0 IST
        datetime(1942,  8, 31, 18, 30,  0), #  23400  3600 IST
        datetime(1945, 10, 14, 17, 30,  0), #  19800     0 IST
        ]

    _transition_info = [
        ttinfo( 21200,      0,  'HMT'),
        ttinfo( 23400,      0, 'BURT'),
        ttinfo( 19800,      0,  'IST'),
        ttinfo( 23400,   3600,  'IST'),
        ttinfo( 19800,      0,  'IST'),
        ]

Calcutta = Calcutta() # Singleton

