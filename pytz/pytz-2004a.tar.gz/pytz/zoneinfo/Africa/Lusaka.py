'''
tzinfo timezone information for Africa/Lusaka.

Generated from the Olson timezone database:
    ftp://elsie.nci.nih.gov/pub/tz*.tar.gz
'''

from pytz.tzinfo import DstTzInfo
from pytz.tzinfo import memorized_datetime as datetime
from pytz.tzinfo import memorized_ttinfo as ttinfo

class Lusaka(DstTzInfo):
    '''Africa/Lusaka timezone definition. See datetime.tzinfo for details'''

    _zone = 'Africa/Lusaka'

    _utc_transition_times = [
        datetime(   1,  1,  1,  0,  0,  0), #   6788     0 LMT
        datetime(1903,  2, 28, 22,  6, 52), #   7200     0 CAT
        ]

    _transition_info = [
        ttinfo(  6788,      0,  'LMT'),
        ttinfo(  7200,      0,  'CAT'),
        ]

Lusaka = Lusaka() # Singleton

