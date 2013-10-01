'''
tzinfo timezone information for Africa/Banjul.

Generated from the Olson timezone database:
    ftp://elsie.nci.nih.gov/pub/tz*.tar.gz
'''

from pytz.tzinfo import DstTzInfo
from pytz.tzinfo import memorized_datetime as datetime
from pytz.tzinfo import memorized_ttinfo as ttinfo

class Banjul(DstTzInfo):
    '''Africa/Banjul timezone definition. See datetime.tzinfo for details'''

    _zone = 'Africa/Banjul'

    _utc_transition_times = [
        datetime(   1,  1,  1,  0,  0,  0), #  -3996     0 LMT
        datetime(1912,  1,  1,  1,  6, 36), #  -3996     0 BMT
        datetime(1935,  1,  1,  1,  6, 36), #  -3600     0 WAT
        datetime(1964,  1,  1,  1,  0,  0), #      0     0 GMT
        ]

    _transition_info = [
        ttinfo( -3996,      0,  'LMT'),
        ttinfo( -3996,      0,  'BMT'),
        ttinfo( -3600,      0,  'WAT'),
        ttinfo(     0,      0,  'GMT'),
        ]

Banjul = Banjul() # Singleton

