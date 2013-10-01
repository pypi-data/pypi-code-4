'''
tzinfo timezone information for America/Virgin.

Generated from the Olson timezone database:
    ftp://elsie.nci.nih.gov/pub/tz*.tar.gz
'''

from pytz.tzinfo import DstTzInfo
from pytz.tzinfo import memorized_datetime as datetime
from pytz.tzinfo import memorized_ttinfo as ttinfo

class Virgin(DstTzInfo):
    '''America/Virgin timezone definition. See datetime.tzinfo for details'''

    _zone = 'America/Virgin'

    _utc_transition_times = [
        datetime(   1,  1,  1,  0,  0,  0), # -15584     0 LMT
        datetime(1911,  7,  1,  4, 19, 44), # -14400     0 AST
        ]

    _transition_info = [
        ttinfo(-15584,      0,  'LMT'),
        ttinfo(-14400,      0,  'AST'),
        ]

Virgin = Virgin() # Singleton

