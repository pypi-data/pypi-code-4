'''
tzinfo timezone information for America/St_Kitts.

Generated from the Olson timezone database:
    ftp://elsie.nci.nih.gov/pub/tz*.tar.gz
'''

from pytz.tzinfo import DstTzInfo
from pytz.tzinfo import memorized_datetime as datetime
from pytz.tzinfo import memorized_ttinfo as ttinfo

class St_Kitts(DstTzInfo):
    '''America/St_Kitts timezone definition. See datetime.tzinfo for details'''

    _zone = 'America/St_Kitts'

    _utc_transition_times = [
        datetime(   1,  1,  1,  0,  0,  0), # -15052     0 LMT
        datetime(1912,  3,  2,  4, 10, 52), # -14400     0 AST
        ]

    _transition_info = [
        ttinfo(-15052,      0,  'LMT'),
        ttinfo(-14400,      0,  'AST'),
        ]

St_Kitts = St_Kitts() # Singleton

