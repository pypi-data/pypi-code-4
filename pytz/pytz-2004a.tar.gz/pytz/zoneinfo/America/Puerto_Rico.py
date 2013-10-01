'''
tzinfo timezone information for America/Puerto_Rico.

Generated from the Olson timezone database:
    ftp://elsie.nci.nih.gov/pub/tz*.tar.gz
'''

from pytz.tzinfo import DstTzInfo
from pytz.tzinfo import memorized_datetime as datetime
from pytz.tzinfo import memorized_ttinfo as ttinfo

class Puerto_Rico(DstTzInfo):
    '''America/Puerto_Rico timezone definition. See datetime.tzinfo for details'''

    _zone = 'America/Puerto_Rico'

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

Puerto_Rico = Puerto_Rico() # Singleton

