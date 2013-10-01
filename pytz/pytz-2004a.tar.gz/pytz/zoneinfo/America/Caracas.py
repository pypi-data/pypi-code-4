'''
tzinfo timezone information for America/Caracas.

Generated from the Olson timezone database:
    ftp://elsie.nci.nih.gov/pub/tz*.tar.gz
'''

from pytz.tzinfo import DstTzInfo
from pytz.tzinfo import memorized_datetime as datetime
from pytz.tzinfo import memorized_ttinfo as ttinfo

class Caracas(DstTzInfo):
    '''America/Caracas timezone definition. See datetime.tzinfo for details'''

    _zone = 'America/Caracas'

    _utc_transition_times = [
        datetime(   1,  1,  1,  0,  0,  0), # -16060     0 CMT
        datetime(1912,  2, 12,  4, 27, 40), # -16200     0 VET
        datetime(1965,  1,  1,  4, 30,  0), # -14400     0 VET
        ]

    _transition_info = [
        ttinfo(-16060,      0,  'CMT'),
        ttinfo(-16200,      0,  'VET'),
        ttinfo(-14400,      0,  'VET'),
        ]

Caracas = Caracas() # Singleton

