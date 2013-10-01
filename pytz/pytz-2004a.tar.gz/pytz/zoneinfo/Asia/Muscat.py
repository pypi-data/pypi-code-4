'''
tzinfo timezone information for Asia/Muscat.

Generated from the Olson timezone database:
    ftp://elsie.nci.nih.gov/pub/tz*.tar.gz
'''

from pytz.tzinfo import DstTzInfo
from pytz.tzinfo import memorized_datetime as datetime
from pytz.tzinfo import memorized_ttinfo as ttinfo

class Muscat(DstTzInfo):
    '''Asia/Muscat timezone definition. See datetime.tzinfo for details'''

    _zone = 'Asia/Muscat'

    _utc_transition_times = [
        datetime(   1,  1,  1,  0,  0,  0), #  14060     0 LMT
        datetime(1919, 12, 31, 20,  5, 40), #  14400     0 GST
        ]

    _transition_info = [
        ttinfo( 14060,      0,  'LMT'),
        ttinfo( 14400,      0,  'GST'),
        ]

Muscat = Muscat() # Singleton

