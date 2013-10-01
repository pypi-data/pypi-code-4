'''
tzinfo timezone information for Africa/Abidjan.

Generated from the Olson timezone database:
    ftp://elsie.nci.nih.gov/pub/tz*.tar.gz
'''

from pytz.tzinfo import DstTzInfo
from pytz.tzinfo import memorized_datetime as datetime
from pytz.tzinfo import memorized_ttinfo as ttinfo

class Abidjan(DstTzInfo):
    '''Africa/Abidjan timezone definition. See datetime.tzinfo for details'''

    _zone = 'Africa/Abidjan'

    _utc_transition_times = [
        datetime(   1,  1,  1,  0,  0,  0), #   -968     0 LMT
        datetime(1912,  1,  1,  0, 16,  8), #      0     0 GMT
        ]

    _transition_info = [
        ttinfo(  -968,      0,  'LMT'),
        ttinfo(     0,      0,  'GMT'),
        ]

Abidjan = Abidjan() # Singleton

