'''
tzinfo timezone information for Antarctica/Davis.

Generated from the Olson timezone database:
    ftp://elsie.nci.nih.gov/pub/tz*.tar.gz
'''

from pytz.tzinfo import DstTzInfo
from pytz.tzinfo import memorized_datetime as datetime
from pytz.tzinfo import memorized_ttinfo as ttinfo

class Davis(DstTzInfo):
    '''Antarctica/Davis timezone definition. See datetime.tzinfo for details'''

    _zone = 'Antarctica/Davis'

    _utc_transition_times = [
        datetime(   1,  1,  1,  0,  0,  0), #      0     0 zzz
        datetime(1957,  1, 13,  0,  0,  0), #  25200     0 DAVT
        datetime(1964, 10, 31, 17,  0,  0), #      0     0 zzz
        datetime(1969,  2,  1,  0,  0,  0), #  25200     0 DAVT
        ]

    _transition_info = [
        ttinfo(     0,      0,  'zzz'),
        ttinfo( 25200,      0, 'DAVT'),
        ttinfo(     0,      0,  'zzz'),
        ttinfo( 25200,      0, 'DAVT'),
        ]

Davis = Davis() # Singleton

