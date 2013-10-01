'''
tzinfo timezone information for Africa/Djibouti.

Generated from the Olson timezone database:
    ftp://elsie.nci.nih.gov/pub/tz*.tar.gz
'''

from pytz.tzinfo import DstTzInfo
from pytz.tzinfo import memorized_datetime as datetime
from pytz.tzinfo import memorized_ttinfo as ttinfo

class Djibouti(DstTzInfo):
    '''Africa/Djibouti timezone definition. See datetime.tzinfo for details'''

    _zone = 'Africa/Djibouti'

    _utc_transition_times = [
        datetime(   1,  1,  1,  0,  0,  0), #  10356     0 LMT
        datetime(1911,  6, 30, 21,  7, 24), #  10800     0 EAT
        ]

    _transition_info = [
        ttinfo( 10356,      0,  'LMT'),
        ttinfo( 10800,      0,  'EAT'),
        ]

Djibouti = Djibouti() # Singleton

