'''
tzinfo timezone information for Africa/Dakar.

Generated from the Olson timezone database:
    ftp://elsie.nci.nih.gov/pub/tz*.tar.gz
'''

from pytz.tzinfo import DstTzInfo
from pytz.tzinfo import memorized_datetime as datetime
from pytz.tzinfo import memorized_ttinfo as ttinfo

class Dakar(DstTzInfo):
    '''Africa/Dakar timezone definition. See datetime.tzinfo for details'''

    _zone = 'Africa/Dakar'

    _utc_transition_times = [
        datetime(   1,  1,  1,  0,  0,  0), #  -4184     0 LMT
        datetime(1912,  1,  1,  1,  9, 44), #  -3600     0 WAT
        datetime(1941,  6,  1,  1,  0,  0), #      0     0 GMT
        ]

    _transition_info = [
        ttinfo( -4184,      0,  'LMT'),
        ttinfo( -3600,      0,  'WAT'),
        ttinfo(     0,      0,  'GMT'),
        ]

Dakar = Dakar() # Singleton

