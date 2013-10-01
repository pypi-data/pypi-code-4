'''
tzinfo timezone information for Africa/Bissau.

Generated from the Olson timezone database:
    ftp://elsie.nci.nih.gov/pub/tz*.tar.gz
'''

from pytz.tzinfo import DstTzInfo
from pytz.tzinfo import memorized_datetime as datetime
from pytz.tzinfo import memorized_ttinfo as ttinfo

class Bissau(DstTzInfo):
    '''Africa/Bissau timezone definition. See datetime.tzinfo for details'''

    _zone = 'Africa/Bissau'

    _utc_transition_times = [
        datetime(   1,  1,  1,  0,  0,  0), #  -3740     0 LMT
        datetime(1911,  5, 26,  1,  2, 20), #  -3600     0 WAT
        datetime(1975,  1,  1,  1,  0,  0), #      0     0 GMT
        ]

    _transition_info = [
        ttinfo( -3740,      0,  'LMT'),
        ttinfo( -3600,      0,  'WAT'),
        ttinfo(     0,      0,  'GMT'),
        ]

Bissau = Bissau() # Singleton

