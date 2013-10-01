'''
tzinfo timezone information for Asia/Kuwait.

Generated from the Olson timezone database:
    ftp://elsie.nci.nih.gov/pub/tz*.tar.gz
'''

from pytz.tzinfo import DstTzInfo
from pytz.tzinfo import memorized_datetime as datetime
from pytz.tzinfo import memorized_ttinfo as ttinfo

class Kuwait(DstTzInfo):
    '''Asia/Kuwait timezone definition. See datetime.tzinfo for details'''

    _zone = 'Asia/Kuwait'

    _utc_transition_times = [
        datetime(   1,  1,  1,  0,  0,  0), #  11516     0 LMT
        datetime(1949, 12, 31, 20, 48,  4), #  10800     0 AST
        ]

    _transition_info = [
        ttinfo( 11516,      0,  'LMT'),
        ttinfo( 10800,      0,  'AST'),
        ]

Kuwait = Kuwait() # Singleton

