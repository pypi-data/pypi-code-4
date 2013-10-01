'''
tzinfo timezone information for Africa/Porto_minus_Novo.

Generated from the Olson timezone database:
    ftp://elsie.nci.nih.gov/pub/tz*.tar.gz
'''

from pytz.tzinfo import DstTzInfo
from pytz.tzinfo import memorized_datetime as datetime
from pytz.tzinfo import memorized_ttinfo as ttinfo

class Porto_minus_Novo(DstTzInfo):
    '''Africa/Porto_minus_Novo timezone definition. See datetime.tzinfo for details'''

    _zone = 'Africa/Porto_minus_Novo'

    _utc_transition_times = [
        datetime(   1,  1,  1,  0,  0,  0), #    628     0 LMT
        datetime(1911, 12, 31, 23, 49, 32), #      0     0 GMT
        datetime(1934,  2, 26,  0,  0,  0), #   3600     0 WAT
        ]

    _transition_info = [
        ttinfo(   628,      0,  'LMT'),
        ttinfo(     0,      0,  'GMT'),
        ttinfo(  3600,      0,  'WAT'),
        ]

Porto_minus_Novo = Porto_minus_Novo() # Singleton

