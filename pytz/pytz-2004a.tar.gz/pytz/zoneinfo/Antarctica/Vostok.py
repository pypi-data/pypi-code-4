'''
tzinfo timezone information for Antarctica/Vostok.

Generated from the Olson timezone database:
    ftp://elsie.nci.nih.gov/pub/tz*.tar.gz
'''

from pytz.tzinfo import DstTzInfo
from pytz.tzinfo import memorized_datetime as datetime
from pytz.tzinfo import memorized_ttinfo as ttinfo

class Vostok(DstTzInfo):
    '''Antarctica/Vostok timezone definition. See datetime.tzinfo for details'''

    _zone = 'Antarctica/Vostok'

    _utc_transition_times = [
        datetime(   1,  1,  1,  0,  0,  0), #      0     0 zzz
        datetime(1957, 12, 16,  0,  0,  0), #  21600     0 VOST
        ]

    _transition_info = [
        ttinfo(     0,      0,  'zzz'),
        ttinfo( 21600,      0, 'VOST'),
        ]

Vostok = Vostok() # Singleton

