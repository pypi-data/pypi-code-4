'''
tzinfo timezone information for Asia/Ujung_Pandang.

Generated from the Olson timezone database:
    ftp://elsie.nci.nih.gov/pub/tz*.tar.gz
'''

from pytz.tzinfo import DstTzInfo
from pytz.tzinfo import memorized_datetime as datetime
from pytz.tzinfo import memorized_ttinfo as ttinfo

class Ujung_Pandang(DstTzInfo):
    '''Asia/Ujung_Pandang timezone definition. See datetime.tzinfo for details'''

    _zone = 'Asia/Ujung_Pandang'

    _utc_transition_times = [
        datetime(   1,  1,  1,  0,  0,  0), #  28656     0 LMT
        datetime(1919, 12, 31, 16,  2, 24), #  28656     0 MMT
        datetime(1932, 10, 31, 16,  2, 24), #  28800     0 CIT
        datetime(1942,  2,  8, 16,  0,  0), #  32400     0 JST
        datetime(1945,  7, 31, 15,  0,  0), #  28800     0 CIT
        ]

    _transition_info = [
        ttinfo( 28656,      0,  'LMT'),
        ttinfo( 28656,      0,  'MMT'),
        ttinfo( 28800,      0,  'CIT'),
        ttinfo( 32400,      0,  'JST'),
        ttinfo( 28800,      0,  'CIT'),
        ]

Ujung_Pandang = Ujung_Pandang() # Singleton

