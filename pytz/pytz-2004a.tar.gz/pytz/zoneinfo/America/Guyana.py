'''
tzinfo timezone information for America/Guyana.

Generated from the Olson timezone database:
    ftp://elsie.nci.nih.gov/pub/tz*.tar.gz
'''

from pytz.tzinfo import DstTzInfo
from pytz.tzinfo import memorized_datetime as datetime
from pytz.tzinfo import memorized_ttinfo as ttinfo

class Guyana(DstTzInfo):
    '''America/Guyana timezone definition. See datetime.tzinfo for details'''

    _zone = 'America/Guyana'

    _utc_transition_times = [
        datetime(   1,  1,  1,  0,  0,  0), # -13960     0 LMT
        datetime(1915,  3,  1,  3, 52, 40), # -13500     0 GBGT
        datetime(1966,  5, 26,  3, 45,  0), # -13500     0 GYT
        datetime(1975,  7, 31,  3, 45,  0), # -10800     0 GYT
        datetime(1991,  1,  1,  3,  0,  0), # -14400     0 GYT
        ]

    _transition_info = [
        ttinfo(-13960,      0,  'LMT'),
        ttinfo(-13500,      0, 'GBGT'),
        ttinfo(-13500,      0,  'GYT'),
        ttinfo(-10800,      0,  'GYT'),
        ttinfo(-14400,      0,  'GYT'),
        ]

Guyana = Guyana() # Singleton

