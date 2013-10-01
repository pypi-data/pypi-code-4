'''
tzinfo timezone information for Asia/Dili.

Generated from the Olson timezone database:
    ftp://elsie.nci.nih.gov/pub/tz*.tar.gz
'''

from pytz.tzinfo import DstTzInfo
from pytz.tzinfo import memorized_datetime as datetime
from pytz.tzinfo import memorized_ttinfo as ttinfo

class Dili(DstTzInfo):
    '''Asia/Dili timezone definition. See datetime.tzinfo for details'''

    _zone = 'Asia/Dili'

    _utc_transition_times = [
        datetime(   1,  1,  1,  0,  0,  0), #  30140     0 LMT
        datetime(1911, 12, 31, 15, 37, 40), #  28800     0 TPT
        datetime(1942,  2, 21, 15,  0,  0), #  32400     0 JST
        datetime(1945,  7, 31, 15,  0,  0), #  32400     0 TPT
        datetime(1976,  5,  2, 15,  0,  0), #  28800     0 CIT
        datetime(2000,  9, 16, 16,  0,  0), #  32400     0 TPT
        ]

    _transition_info = [
        ttinfo( 30140,      0,  'LMT'),
        ttinfo( 28800,      0,  'TPT'),
        ttinfo( 32400,      0,  'JST'),
        ttinfo( 32400,      0,  'TPT'),
        ttinfo( 28800,      0,  'CIT'),
        ttinfo( 32400,      0,  'TPT'),
        ]

Dili = Dili() # Singleton

