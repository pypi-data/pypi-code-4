'''
tzinfo timezone information for America/Guadeloupe.

Generated from the Olson timezone database:
    ftp://elsie.nci.nih.gov/pub/tz*.tar.gz
'''

from pytz.tzinfo import DstTzInfo
from pytz.tzinfo import memorized_datetime as datetime
from pytz.tzinfo import memorized_ttinfo as ttinfo

class Guadeloupe(DstTzInfo):
    '''America/Guadeloupe timezone definition. See datetime.tzinfo for details'''

    _zone = 'America/Guadeloupe'

    _utc_transition_times = [
        datetime(   1,  1,  1,  0,  0,  0), # -14768     0 LMT
        datetime(1911,  6,  8,  4,  6,  8), # -14400     0 AST
        ]

    _transition_info = [
        ttinfo(-14768,      0,  'LMT'),
        ttinfo(-14400,      0,  'AST'),
        ]

Guadeloupe = Guadeloupe() # Singleton

