'''
tzinfo timezone information for America/Bogota.

Generated from the Olson timezone database:
    ftp://elsie.nci.nih.gov/pub/tz*.tar.gz
'''

from pytz.tzinfo import DstTzInfo
from pytz.tzinfo import memorized_datetime as datetime
from pytz.tzinfo import memorized_ttinfo as ttinfo

class Bogota(DstTzInfo):
    '''America/Bogota timezone definition. See datetime.tzinfo for details'''

    _zone = 'America/Bogota'

    _utc_transition_times = [
        datetime(   1,  1,  1,  0,  0,  0), # -17780     0 BMT
        datetime(1914, 11, 23,  4, 56, 20), # -18000     0 COT
        datetime(1992,  5,  2,  5,  0,  0), # -14400  3600 COST
        datetime(1992, 12, 31,  4,  0,  0), # -18000     0 COT
        ]

    _transition_info = [
        ttinfo(-17780,      0,  'BMT'),
        ttinfo(-18000,      0,  'COT'),
        ttinfo(-14400,   3600, 'COST'),
        ttinfo(-18000,      0,  'COT'),
        ]

Bogota = Bogota() # Singleton

