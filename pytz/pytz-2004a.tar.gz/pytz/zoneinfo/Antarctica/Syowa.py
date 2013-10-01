'''
tzinfo timezone information for Antarctica/Syowa.

Generated from the Olson timezone database:
    ftp://elsie.nci.nih.gov/pub/tz*.tar.gz
'''

from pytz.tzinfo import DstTzInfo
from pytz.tzinfo import memorized_datetime as datetime
from pytz.tzinfo import memorized_ttinfo as ttinfo

class Syowa(DstTzInfo):
    '''Antarctica/Syowa timezone definition. See datetime.tzinfo for details'''

    _zone = 'Antarctica/Syowa'

    _utc_transition_times = [
        datetime(   1,  1,  1,  0,  0,  0), #      0     0 zzz
        datetime(1957,  1, 29,  0,  0,  0), #  10800     0 SYOT
        ]

    _transition_info = [
        ttinfo(     0,      0,  'zzz'),
        ttinfo( 10800,      0, 'SYOT'),
        ]

Syowa = Syowa() # Singleton

