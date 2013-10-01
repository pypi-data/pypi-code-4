'''
tzinfo timezone information for Indian/Comoro.

Generated from the Olson timezone database:
    ftp://elsie.nci.nih.gov/pub/tz*.tar.gz
'''

from pytz.tzinfo import DstTzInfo
from pytz.tzinfo import memorized_datetime as datetime
from pytz.tzinfo import memorized_ttinfo as ttinfo

class Comoro(DstTzInfo):
    '''Indian/Comoro timezone definition. See datetime.tzinfo for details'''

    _zone = 'Indian/Comoro'

    _utc_transition_times = [
        datetime(   1,  1,  1,  0,  0,  0), #  10384     0 LMT
        datetime(1911,  6, 30, 21,  6, 56), #  10800     0 EAT
        ]

    _transition_info = [
        ttinfo( 10384,      0,  'LMT'),
        ttinfo( 10800,      0,  'EAT'),
        ]

Comoro = Comoro() # Singleton

