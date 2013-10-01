'''
tzinfo timezone information for America/St_Vincent.

Generated from the Olson timezone database:
    ftp://elsie.nci.nih.gov/pub/tz*.tar.gz
'''

from pytz.tzinfo import DstTzInfo
from pytz.tzinfo import memorized_datetime as datetime
from pytz.tzinfo import memorized_ttinfo as ttinfo

class St_Vincent(DstTzInfo):
    '''America/St_Vincent timezone definition. See datetime.tzinfo for details'''

    _zone = 'America/St_Vincent'

    _utc_transition_times = [
        datetime(   1,  1,  1,  0,  0,  0), # -14696     0 KMT
        datetime(1912,  1,  1,  4,  4, 56), # -14400     0 AST
        ]

    _transition_info = [
        ttinfo(-14696,      0,  'KMT'),
        ttinfo(-14400,      0,  'AST'),
        ]

St_Vincent = St_Vincent() # Singleton

