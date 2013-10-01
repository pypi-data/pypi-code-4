'''
tzinfo timezone information for Asia/Karachi.

Generated from the Olson timezone database:
    ftp://elsie.nci.nih.gov/pub/tz*.tar.gz
'''

from pytz.tzinfo import DstTzInfo
from pytz.tzinfo import memorized_datetime as datetime
from pytz.tzinfo import memorized_ttinfo as ttinfo

class Karachi(DstTzInfo):
    '''Asia/Karachi timezone definition. See datetime.tzinfo for details'''

    _zone = 'Asia/Karachi'

    _utc_transition_times = [
        datetime(   1,  1,  1,  0,  0,  0), #  16092     0 LMT
        datetime(1906, 12, 31, 19, 31, 48), #  19800     0 IST
        datetime(1942,  8, 31, 18, 30,  0), #  23400  3600 IST
        datetime(1945, 10, 14, 17, 30,  0), #  19800     0 IST
        datetime(1951,  9, 29, 18, 30,  0), #  18000     0 KART
        datetime(1971,  3, 25, 19,  0,  0), #  18000     0 PKT
        datetime(2002,  4,  6, 19,  1,  0), #  21600  3600 PKST
        datetime(2002, 10,  5, 18,  1,  0), #  18000     0 PKT
        ]

    _transition_info = [
        ttinfo( 16092,      0,  'LMT'),
        ttinfo( 19800,      0,  'IST'),
        ttinfo( 23400,   3600,  'IST'),
        ttinfo( 19800,      0,  'IST'),
        ttinfo( 18000,      0, 'KART'),
        ttinfo( 18000,      0,  'PKT'),
        ttinfo( 21600,   3600, 'PKST'),
        ttinfo( 18000,      0,  'PKT'),
        ]

Karachi = Karachi() # Singleton

