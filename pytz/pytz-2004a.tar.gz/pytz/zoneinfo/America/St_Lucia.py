'''
tzinfo timezone information for America/St_Lucia.

Generated from the Olson timezone database:
    ftp://elsie.nci.nih.gov/pub/tz*.tar.gz
'''

from pytz.tzinfo import DstTzInfo
from pytz.tzinfo import memorized_datetime as datetime
from pytz.tzinfo import memorized_ttinfo as ttinfo

class St_Lucia(DstTzInfo):
    '''America/St_Lucia timezone definition. See datetime.tzinfo for details'''

    _zone = 'America/St_Lucia'

    _utc_transition_times = [
        datetime(   1,  1,  1,  0,  0,  0), # -14640     0 CMT
        datetime(1912,  1,  1,  4,  4,  0), # -14400     0 AST
        ]

    _transition_info = [
        ttinfo(-14640,      0,  'CMT'),
        ttinfo(-14400,      0,  'AST'),
        ]

St_Lucia = St_Lucia() # Singleton

