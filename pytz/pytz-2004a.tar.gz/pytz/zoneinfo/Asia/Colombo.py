'''
tzinfo timezone information for Asia/Colombo.

Generated from the Olson timezone database:
    ftp://elsie.nci.nih.gov/pub/tz*.tar.gz
'''

from pytz.tzinfo import DstTzInfo
from pytz.tzinfo import memorized_datetime as datetime
from pytz.tzinfo import memorized_ttinfo as ttinfo

class Colombo(DstTzInfo):
    '''Asia/Colombo timezone definition. See datetime.tzinfo for details'''

    _zone = 'Asia/Colombo'

    _utc_transition_times = [
        datetime(   1,  1,  1,  0,  0,  0), #  19172     0 MMT
        datetime(1905, 12, 31, 18, 40, 28), #  19800     0 IST
        datetime(1942,  1,  4, 18, 30,  0), #  21600  1800 IHST
        datetime(1942,  8, 31, 18,  0,  0), #  23400  1800 IST
        datetime(1945, 10, 15, 19, 30,  0), #  19800     0 IST
        datetime(1996,  5, 24, 18, 30,  0), #  23400     0 LKT
        datetime(1996, 10, 25, 18,  0,  0), #  21600     0 LKT
        ]

    _transition_info = [
        ttinfo( 19172,      0,  'MMT'),
        ttinfo( 19800,      0,  'IST'),
        ttinfo( 21600,   1800, 'IHST'),
        ttinfo( 23400,   1800,  'IST'),
        ttinfo( 19800,      0,  'IST'),
        ttinfo( 23400,      0,  'LKT'),
        ttinfo( 21600,      0,  'LKT'),
        ]

Colombo = Colombo() # Singleton

