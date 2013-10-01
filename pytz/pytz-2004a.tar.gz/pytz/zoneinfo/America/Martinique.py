'''
tzinfo timezone information for America/Martinique.

Generated from the Olson timezone database:
    ftp://elsie.nci.nih.gov/pub/tz*.tar.gz
'''

from pytz.tzinfo import DstTzInfo
from pytz.tzinfo import memorized_datetime as datetime
from pytz.tzinfo import memorized_ttinfo as ttinfo

class Martinique(DstTzInfo):
    '''America/Martinique timezone definition. See datetime.tzinfo for details'''

    _zone = 'America/Martinique'

    _utc_transition_times = [
        datetime(   1,  1,  1,  0,  0,  0), # -14660     0 FFMT
        datetime(1911,  5,  1,  4,  4, 20), # -14400     0 AST
        datetime(1980,  4,  6,  4,  0,  0), # -10800  3600 ADT
        datetime(1980,  9, 28,  3,  0,  0), # -14400     0 AST
        ]

    _transition_info = [
        ttinfo(-14660,      0, 'FFMT'),
        ttinfo(-14400,      0,  'AST'),
        ttinfo(-10800,   3600,  'ADT'),
        ttinfo(-14400,      0,  'AST'),
        ]

Martinique = Martinique() # Singleton

