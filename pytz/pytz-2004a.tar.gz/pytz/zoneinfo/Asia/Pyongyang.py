'''
tzinfo timezone information for Asia/Pyongyang.

Generated from the Olson timezone database:
    ftp://elsie.nci.nih.gov/pub/tz*.tar.gz
'''

from pytz.tzinfo import DstTzInfo
from pytz.tzinfo import memorized_datetime as datetime
from pytz.tzinfo import memorized_ttinfo as ttinfo

class Pyongyang(DstTzInfo):
    '''Asia/Pyongyang timezone definition. See datetime.tzinfo for details'''

    _zone = 'Asia/Pyongyang'

    _utc_transition_times = [
        datetime(   1,  1,  1,  0,  0,  0), #  30600     0 KST
        datetime(1904, 11, 30, 15, 30,  0), #  32400     0 KST
        datetime(1927, 12, 31, 15,  0,  0), #  30600     0 KST
        datetime(1931, 12, 31, 15, 30,  0), #  32400     0 KST
        datetime(1954,  3, 20, 15,  0,  0), #  28800     0 KST
        datetime(1961,  8,  9, 16,  0,  0), #  32400     0 KST
        ]

    _transition_info = [
        ttinfo( 30600,      0,  'KST'),
        ttinfo( 32400,      0,  'KST'),
        ttinfo( 30600,      0,  'KST'),
        ttinfo( 32400,      0,  'KST'),
        ttinfo( 28800,      0,  'KST'),
        ttinfo( 32400,      0,  'KST'),
        ]

Pyongyang = Pyongyang() # Singleton

