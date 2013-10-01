'''
tzinfo timezone information for America/Aruba.

Generated from the Olson timezone database:
    ftp://elsie.nci.nih.gov/pub/tz*.tar.gz
'''

from pytz.tzinfo import DstTzInfo
from pytz.tzinfo import memorized_datetime as datetime
from pytz.tzinfo import memorized_ttinfo as ttinfo

class Aruba(DstTzInfo):
    '''America/Aruba timezone definition. See datetime.tzinfo for details'''

    _zone = 'America/Aruba'

    _utc_transition_times = [
        datetime(   1,  1,  1,  0,  0,  0), # -16824     0 LMT
        datetime(1912,  2, 12,  4, 40, 24), # -16200     0 ANT
        datetime(1965,  1,  1,  4, 30,  0), # -14400     0 AST
        ]

    _transition_info = [
        ttinfo(-16824,      0,  'LMT'),
        ttinfo(-16200,      0,  'ANT'),
        ttinfo(-14400,      0,  'AST'),
        ]

Aruba = Aruba() # Singleton

