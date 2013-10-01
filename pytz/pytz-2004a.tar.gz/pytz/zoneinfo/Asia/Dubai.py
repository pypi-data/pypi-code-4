'''
tzinfo timezone information for Asia/Dubai.

Generated from the Olson timezone database:
    ftp://elsie.nci.nih.gov/pub/tz*.tar.gz
'''

from pytz.tzinfo import DstTzInfo
from pytz.tzinfo import memorized_datetime as datetime
from pytz.tzinfo import memorized_ttinfo as ttinfo

class Dubai(DstTzInfo):
    '''Asia/Dubai timezone definition. See datetime.tzinfo for details'''

    _zone = 'Asia/Dubai'

    _utc_transition_times = [
        datetime(   1,  1,  1,  0,  0,  0), #  13272     0 LMT
        datetime(1919, 12, 31, 20, 18, 48), #  14400     0 GST
        ]

    _transition_info = [
        ttinfo( 13272,      0,  'LMT'),
        ttinfo( 14400,      0,  'GST'),
        ]

Dubai = Dubai() # Singleton

