'''
tzinfo timezone information for America/Montserrat.

Generated from the Olson timezone database:
    ftp://elsie.nci.nih.gov/pub/tz*.tar.gz
'''

from pytz.tzinfo import DstTzInfo
from pytz.tzinfo import memorized_datetime as datetime
from pytz.tzinfo import memorized_ttinfo as ttinfo

class Montserrat(DstTzInfo):
    '''America/Montserrat timezone definition. See datetime.tzinfo for details'''

    _zone = 'America/Montserrat'

    _utc_transition_times = [
        datetime(   1,  1,  1,  0,  0,  0), # -14932     0 LMT
        datetime(1911,  7,  1,  4,  9, 52), # -14400     0 AST
        ]

    _transition_info = [
        ttinfo(-14932,      0,  'LMT'),
        ttinfo(-14400,      0,  'AST'),
        ]

Montserrat = Montserrat() # Singleton

