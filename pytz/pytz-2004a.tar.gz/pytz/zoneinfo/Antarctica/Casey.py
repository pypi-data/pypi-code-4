'''
tzinfo timezone information for Antarctica/Casey.

Generated from the Olson timezone database:
    ftp://elsie.nci.nih.gov/pub/tz*.tar.gz
'''

from pytz.tzinfo import DstTzInfo
from pytz.tzinfo import memorized_datetime as datetime
from pytz.tzinfo import memorized_ttinfo as ttinfo

class Casey(DstTzInfo):
    '''Antarctica/Casey timezone definition. See datetime.tzinfo for details'''

    _zone = 'Antarctica/Casey'

    _utc_transition_times = [
        datetime(   1,  1,  1,  0,  0,  0), #      0     0 zzz
        datetime(1969,  1,  1,  0,  0,  0), #  28800     0 WST
        ]

    _transition_info = [
        ttinfo(     0,      0,  'zzz'),
        ttinfo( 28800,      0,  'WST'),
        ]

Casey = Casey() # Singleton

