'''
tzinfo timezone information for Antarctica/Rothera.

Generated from the Olson timezone database:
    ftp://elsie.nci.nih.gov/pub/tz*.tar.gz
'''

from pytz.tzinfo import DstTzInfo
from pytz.tzinfo import memorized_datetime as datetime
from pytz.tzinfo import memorized_ttinfo as ttinfo

class Rothera(DstTzInfo):
    '''Antarctica/Rothera timezone definition. See datetime.tzinfo for details'''

    _zone = 'Antarctica/Rothera'

    _utc_transition_times = [
        datetime(   1,  1,  1,  0,  0,  0), #      0     0 zzz
        datetime(1976, 12,  1,  0,  0,  0), # -10800     0 ROTT
        ]

    _transition_info = [
        ttinfo(     0,      0,  'zzz'),
        ttinfo(-10800,      0, 'ROTT'),
        ]

Rothera = Rothera() # Singleton

