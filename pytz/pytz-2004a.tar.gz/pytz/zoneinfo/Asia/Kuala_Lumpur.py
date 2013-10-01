'''
tzinfo timezone information for Asia/Kuala_Lumpur.

Generated from the Olson timezone database:
    ftp://elsie.nci.nih.gov/pub/tz*.tar.gz
'''

from pytz.tzinfo import DstTzInfo
from pytz.tzinfo import memorized_datetime as datetime
from pytz.tzinfo import memorized_ttinfo as ttinfo

class Kuala_Lumpur(DstTzInfo):
    '''Asia/Kuala_Lumpur timezone definition. See datetime.tzinfo for details'''

    _zone = 'Asia/Kuala_Lumpur'

    _utc_transition_times = [
        datetime(   1,  1,  1,  0,  0,  0), #  24925     0 SMT
        datetime(1905,  5, 31, 17,  4, 35), #  25200     0 MALT
        datetime(1932, 12, 31, 17,  0,  0), #  26400  1200 MALST
        datetime(1935, 12, 31, 16, 40,  0), #  26400     0 MALT
        datetime(1941,  8, 31, 16, 40,  0), #  27000     0 MALT
        datetime(1942,  2, 15, 16, 30,  0), #  32400     0 JST
        datetime(1945,  9, 11, 15,  0,  0), #  27000     0 MALT
        datetime(1981, 12, 31, 16, 30,  0), #  28800     0 MYT
        ]

    _transition_info = [
        ttinfo( 24925,      0,  'SMT'),
        ttinfo( 25200,      0, 'MALT'),
        ttinfo( 26400,   1200, 'MALST'),
        ttinfo( 26400,      0, 'MALT'),
        ttinfo( 27000,      0, 'MALT'),
        ttinfo( 32400,      0,  'JST'),
        ttinfo( 27000,      0, 'MALT'),
        ttinfo( 28800,      0,  'MYT'),
        ]

Kuala_Lumpur = Kuala_Lumpur() # Singleton

