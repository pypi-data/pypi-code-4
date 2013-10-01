'''
tzinfo timezone information for Asia/Manila.

Generated from the Olson timezone database:
    ftp://elsie.nci.nih.gov/pub/tz*.tar.gz
'''

from pytz.tzinfo import DstTzInfo
from pytz.tzinfo import memorized_datetime as datetime
from pytz.tzinfo import memorized_ttinfo as ttinfo

class Manila(DstTzInfo):
    '''Asia/Manila timezone definition. See datetime.tzinfo for details'''

    _zone = 'Asia/Manila'

    _utc_transition_times = [
        datetime(   1,  1,  1,  0,  0,  0), #  28800     0 PHT
        datetime(1936, 10, 31, 16,  0,  0), #  32400  3600 PHST
        datetime(1937,  1, 31, 15,  0,  0), #  28800     0 PHT
        datetime(1942,  4, 30, 16,  0,  0), #  32400     0 JST
        datetime(1944, 10, 31, 15,  0,  0), #  28800     0 PHT
        datetime(1954,  4, 11, 16,  0,  0), #  32400  3600 PHST
        datetime(1954,  6, 30, 15,  0,  0), #  28800     0 PHT
        datetime(1978,  3, 21, 16,  0,  0), #  32400  3600 PHST
        datetime(1978,  9, 20, 15,  0,  0), #  28800     0 PHT
        ]

    _transition_info = [
        ttinfo( 28800,      0,  'PHT'),
        ttinfo( 32400,   3600, 'PHST'),
        ttinfo( 28800,      0,  'PHT'),
        ttinfo( 32400,      0,  'JST'),
        ttinfo( 28800,      0,  'PHT'),
        ttinfo( 32400,   3600, 'PHST'),
        ttinfo( 28800,      0,  'PHT'),
        ttinfo( 32400,   3600, 'PHST'),
        ttinfo( 28800,      0,  'PHT'),
        ]

Manila = Manila() # Singleton

