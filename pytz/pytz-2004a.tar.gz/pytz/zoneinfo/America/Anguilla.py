'''
tzinfo timezone information for America/Anguilla.

Generated from the Olson timezone database:
    ftp://elsie.nci.nih.gov/pub/tz*.tar.gz
'''

from pytz.tzinfo import DstTzInfo
from pytz.tzinfo import memorized_datetime as datetime
from pytz.tzinfo import memorized_ttinfo as ttinfo

class Anguilla(DstTzInfo):
    '''America/Anguilla timezone definition. See datetime.tzinfo for details'''

    _zone = 'America/Anguilla'

    _utc_transition_times = [
        datetime(   1,  1,  1,  0,  0,  0), # -15136     0 LMT
        datetime(1912,  3,  2,  4, 12, 16), # -14400     0 AST
        ]

    _transition_info = [
        ttinfo(-15136,      0,  'LMT'),
        ttinfo(-14400,      0,  'AST'),
        ]

Anguilla = Anguilla() # Singleton

