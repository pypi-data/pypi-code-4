'''
tzinfo timezone information for America/La_Paz.

Generated from the Olson timezone database:
    ftp://elsie.nci.nih.gov/pub/tz*.tar.gz
'''

from pytz.tzinfo import DstTzInfo
from pytz.tzinfo import memorized_datetime as datetime
from pytz.tzinfo import memorized_ttinfo as ttinfo

class La_Paz(DstTzInfo):
    '''America/La_Paz timezone definition. See datetime.tzinfo for details'''

    _zone = 'America/La_Paz'

    _utc_transition_times = [
        datetime(   1,  1,  1,  0,  0,  0), # -16356     0 CMT
        datetime(1931, 10, 15,  4, 32, 36), # -12756  3600 BOST
        datetime(1932,  3, 21,  3, 32, 36), # -14400     0 BOT
        ]

    _transition_info = [
        ttinfo(-16356,      0,  'CMT'),
        ttinfo(-12756,   3600, 'BOST'),
        ttinfo(-14400,      0,  'BOT'),
        ]

La_Paz = La_Paz() # Singleton

