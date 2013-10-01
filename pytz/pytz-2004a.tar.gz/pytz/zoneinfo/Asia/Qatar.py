'''
tzinfo timezone information for Asia/Qatar.

Generated from the Olson timezone database:
    ftp://elsie.nci.nih.gov/pub/tz*.tar.gz
'''

from pytz.tzinfo import DstTzInfo
from pytz.tzinfo import memorized_datetime as datetime
from pytz.tzinfo import memorized_ttinfo as ttinfo

class Qatar(DstTzInfo):
    '''Asia/Qatar timezone definition. See datetime.tzinfo for details'''

    _zone = 'Asia/Qatar'

    _utc_transition_times = [
        datetime(   1,  1,  1,  0,  0,  0), #  12368     0 LMT
        datetime(1919, 12, 31, 20, 33, 52), #  14400     0 GST
        datetime(1972,  5, 31, 20,  0,  0), #  10800     0 AST
        ]

    _transition_info = [
        ttinfo( 12368,      0,  'LMT'),
        ttinfo( 14400,      0,  'GST'),
        ttinfo( 10800,      0,  'AST'),
        ]

Qatar = Qatar() # Singleton

