'''
tzinfo timezone information for Africa/Ouagadougou.

Generated from the Olson timezone database:
    ftp://elsie.nci.nih.gov/pub/tz*.tar.gz
'''

from pytz.tzinfo import DstTzInfo
from pytz.tzinfo import memorized_datetime as datetime
from pytz.tzinfo import memorized_ttinfo as ttinfo

class Ouagadougou(DstTzInfo):
    '''Africa/Ouagadougou timezone definition. See datetime.tzinfo for details'''

    _zone = 'Africa/Ouagadougou'

    _utc_transition_times = [
        datetime(   1,  1,  1,  0,  0,  0), #   -364     0 LMT
        datetime(1912,  1,  1,  0,  6,  4), #      0     0 GMT
        ]

    _transition_info = [
        ttinfo(  -364,      0,  'LMT'),
        ttinfo(     0,      0,  'GMT'),
        ]

Ouagadougou = Ouagadougou() # Singleton

