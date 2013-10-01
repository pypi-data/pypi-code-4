'''
tzinfo timezone information for Indian/Reunion.

Generated from the Olson timezone database:
    ftp://elsie.nci.nih.gov/pub/tz*.tar.gz
'''

from pytz.tzinfo import DstTzInfo
from pytz.tzinfo import memorized_datetime as datetime
from pytz.tzinfo import memorized_ttinfo as ttinfo

class Reunion(DstTzInfo):
    '''Indian/Reunion timezone definition. See datetime.tzinfo for details'''

    _zone = 'Indian/Reunion'

    _utc_transition_times = [
        datetime(   1,  1,  1,  0,  0,  0), #  13312     0 LMT
        datetime(1911,  5, 31, 20, 18,  8), #  14400     0 RET
        ]

    _transition_info = [
        ttinfo( 13312,      0,  'LMT'),
        ttinfo( 14400,      0,  'RET'),
        ]

Reunion = Reunion() # Singleton

