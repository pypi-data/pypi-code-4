'''
tzinfo timezone information for Africa/Sao_Tome.

Generated from the Olson timezone database:
    ftp://elsie.nci.nih.gov/pub/tz*.tar.gz
'''

from pytz.tzinfo import DstTzInfo
from pytz.tzinfo import memorized_datetime as datetime
from pytz.tzinfo import memorized_ttinfo as ttinfo

class Sao_Tome(DstTzInfo):
    '''Africa/Sao_Tome timezone definition. See datetime.tzinfo for details'''

    _zone = 'Africa/Sao_Tome'

    _utc_transition_times = [
        datetime(   1,  1,  1,  0,  0,  0), #  -2192     0 LMT
        datetime(1912,  1,  1,  0, 36, 32), #      0     0 GMT
        ]

    _transition_info = [
        ttinfo( -2192,      0,  'LMT'),
        ttinfo(     0,      0,  'GMT'),
        ]

Sao_Tome = Sao_Tome() # Singleton

