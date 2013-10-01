'''
tzinfo timezone information for Asia/Brunei.

Generated from the Olson timezone database:
    ftp://elsie.nci.nih.gov/pub/tz*.tar.gz
'''

from pytz.tzinfo import DstTzInfo
from pytz.tzinfo import memorized_datetime as datetime
from pytz.tzinfo import memorized_ttinfo as ttinfo

class Brunei(DstTzInfo):
    '''Asia/Brunei timezone definition. See datetime.tzinfo for details'''

    _zone = 'Asia/Brunei'

    _utc_transition_times = [
        datetime(   1,  1,  1,  0,  0,  0), #  27580     0 LMT
        datetime(1926,  2, 28, 16, 20, 20), #  27000     0 BNT
        datetime(1932, 12, 31, 16, 30,  0), #  28800     0 BNT
        ]

    _transition_info = [
        ttinfo( 27580,      0,  'LMT'),
        ttinfo( 27000,      0,  'BNT'),
        ttinfo( 28800,      0,  'BNT'),
        ]

Brunei = Brunei() # Singleton

