'''
tzinfo timezone information for Africa/Bamako.

Generated from the Olson timezone database:
    ftp://elsie.nci.nih.gov/pub/tz*.tar.gz
'''

from pytz.tzinfo import DstTzInfo
from pytz.tzinfo import memorized_datetime as datetime
from pytz.tzinfo import memorized_ttinfo as ttinfo

class Bamako(DstTzInfo):
    '''Africa/Bamako timezone definition. See datetime.tzinfo for details'''

    _zone = 'Africa/Bamako'

    _utc_transition_times = [
        datetime(   1,  1,  1,  0,  0,  0), #  -1920     0 LMT
        datetime(1912,  1,  1,  0, 32,  0), #      0     0 GMT
        datetime(1934,  2, 26,  0,  0,  0), #  -3600     0 WAT
        datetime(1960,  6, 20,  1,  0,  0), #      0     0 GMT
        ]

    _transition_info = [
        ttinfo( -1920,      0,  'LMT'),
        ttinfo(     0,      0,  'GMT'),
        ttinfo( -3600,      0,  'WAT'),
        ttinfo(     0,      0,  'GMT'),
        ]

Bamako = Bamako() # Singleton

