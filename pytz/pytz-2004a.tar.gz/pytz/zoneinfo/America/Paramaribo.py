'''
tzinfo timezone information for America/Paramaribo.

Generated from the Olson timezone database:
    ftp://elsie.nci.nih.gov/pub/tz*.tar.gz
'''

from pytz.tzinfo import DstTzInfo
from pytz.tzinfo import memorized_datetime as datetime
from pytz.tzinfo import memorized_ttinfo as ttinfo

class Paramaribo(DstTzInfo):
    '''America/Paramaribo timezone definition. See datetime.tzinfo for details'''

    _zone = 'America/Paramaribo'

    _utc_transition_times = [
        datetime(   1,  1,  1,  0,  0,  0), # -13240     0 LMT
        datetime(1911,  1,  1,  3, 40, 40), # -13252     0 PMT
        datetime(1935,  1,  1,  3, 40, 52), # -13236     0 PMT
        datetime(1945, 10,  1,  3, 40, 36), # -12600     0 NEGT
        datetime(1975, 11, 20,  3, 30,  0), # -12600     0 SRT
        datetime(1984, 10,  1,  3, 30,  0), # -10800     0 SRT
        ]

    _transition_info = [
        ttinfo(-13240,      0,  'LMT'),
        ttinfo(-13252,      0,  'PMT'),
        ttinfo(-13236,      0,  'PMT'),
        ttinfo(-12600,      0, 'NEGT'),
        ttinfo(-12600,      0,  'SRT'),
        ttinfo(-10800,      0,  'SRT'),
        ]

Paramaribo = Paramaribo() # Singleton

