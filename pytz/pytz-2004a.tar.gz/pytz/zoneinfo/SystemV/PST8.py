'''
tzinfo timezone information for SystemV/PST8.

Generated from the Olson timezone database:
    ftp://elsie.nci.nih.gov/pub/tz*.tar.gz
'''

from pytz.tzinfo import DstTzInfo
from pytz.tzinfo import memorized_datetime as datetime
from pytz.tzinfo import memorized_ttinfo as ttinfo

class PST8(DstTzInfo):
    '''SystemV/PST8 timezone definition. See datetime.tzinfo for details'''

    _zone = 'SystemV/PST8'

    _utc_transition_times = [
        datetime(   1,  1,  1,  0,  0,  0), # -30600     0 PNT
        datetime(1998,  4, 27,  8, 30,  0), # -28800     0 PST
        ]

    _transition_info = [
        ttinfo(-30600,      0,  'PNT'),
        ttinfo(-28800,      0,  'PST'),
        ]

PST8 = PST8() # Singleton

