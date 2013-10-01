'''
tzinfo timezone information for Japan.

Generated from the Olson timezone database:
    ftp://elsie.nci.nih.gov/pub/tz*.tar.gz
'''

from pytz.tzinfo import DstTzInfo
from pytz.tzinfo import memorized_datetime as datetime
from pytz.tzinfo import memorized_ttinfo as ttinfo

class Japan(DstTzInfo):
    '''Japan timezone definition. See datetime.tzinfo for details'''

    _zone = 'Japan'

    _utc_transition_times = [
        datetime(   1,  1,  1,  0,  0,  0), #  32400     0 CJT
        datetime(1937, 12, 31, 15,  0,  0), #  32400     0 JST
        ]

    _transition_info = [
        ttinfo( 32400,      0,  'CJT'),
        ttinfo( 32400,      0,  'JST'),
        ]

Japan = Japan() # Singleton

