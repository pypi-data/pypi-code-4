'''
tzinfo timezone information for America/Antigua.

Generated from the Olson timezone database:
    ftp://elsie.nci.nih.gov/pub/tz*.tar.gz
'''

from pytz.tzinfo import DstTzInfo
from pytz.tzinfo import memorized_datetime as datetime
from pytz.tzinfo import memorized_ttinfo as ttinfo

class Antigua(DstTzInfo):
    '''America/Antigua timezone definition. See datetime.tzinfo for details'''

    _zone = 'America/Antigua'

    _utc_transition_times = [
        datetime(   1,  1,  1,  0,  0,  0), # -14832     0 LMT
        datetime(1912,  3,  2,  4,  7, 12), # -18000     0 EST
        datetime(1951,  1,  1,  5,  0,  0), # -14400     0 AST
        ]

    _transition_info = [
        ttinfo(-14832,      0,  'LMT'),
        ttinfo(-18000,      0,  'EST'),
        ttinfo(-14400,      0,  'AST'),
        ]

Antigua = Antigua() # Singleton

