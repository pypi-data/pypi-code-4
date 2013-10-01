'''
tzinfo timezone information for SystemV/AST4.

Generated from the Olson timezone database:
    ftp://elsie.nci.nih.gov/pub/tz*.tar.gz
'''

from pytz.tzinfo import DstTzInfo
from pytz.tzinfo import memorized_datetime as datetime
from pytz.tzinfo import memorized_ttinfo as ttinfo

class AST4(DstTzInfo):
    '''SystemV/AST4 timezone definition. See datetime.tzinfo for details'''

    _zone = 'SystemV/AST4'

    _utc_transition_times = [
        datetime(   1,  1,  1,  0,  0,  0), # -14400     0 AST
        datetime(1942,  5,  3,  4,  0,  0), # -10800  3600 AWT
        datetime(1945,  9, 30,  5,  0,  0), # -14400     0 AST
        ]

    _transition_info = [
        ttinfo(-14400,      0,  'AST'),
        ttinfo(-10800,   3600,  'AWT'),
        ttinfo(-14400,      0,  'AST'),
        ]

AST4 = AST4() # Singleton

