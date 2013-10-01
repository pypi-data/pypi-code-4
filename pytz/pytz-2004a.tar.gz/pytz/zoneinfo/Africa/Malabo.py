'''
tzinfo timezone information for Africa/Malabo.

Generated from the Olson timezone database:
    ftp://elsie.nci.nih.gov/pub/tz*.tar.gz
'''

from pytz.tzinfo import DstTzInfo
from pytz.tzinfo import memorized_datetime as datetime
from pytz.tzinfo import memorized_ttinfo as ttinfo

class Malabo(DstTzInfo):
    '''Africa/Malabo timezone definition. See datetime.tzinfo for details'''

    _zone = 'Africa/Malabo'

    _utc_transition_times = [
        datetime(   1,  1,  1,  0,  0,  0), #   2108     0 LMT
        datetime(1911, 12, 31, 23, 24, 52), #      0     0 GMT
        datetime(1963, 12, 15,  0,  0,  0), #   3600     0 WAT
        ]

    _transition_info = [
        ttinfo(  2108,      0,  'LMT'),
        ttinfo(     0,      0,  'GMT'),
        ttinfo(  3600,      0,  'WAT'),
        ]

Malabo = Malabo() # Singleton

