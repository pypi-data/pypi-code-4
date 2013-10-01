'''
tzinfo timezone information for Africa/Kigali.

Generated from the Olson timezone database:
    ftp://elsie.nci.nih.gov/pub/tz*.tar.gz
'''

from pytz.tzinfo import DstTzInfo
from pytz.tzinfo import memorized_datetime as datetime
from pytz.tzinfo import memorized_ttinfo as ttinfo

class Kigali(DstTzInfo):
    '''Africa/Kigali timezone definition. See datetime.tzinfo for details'''

    _zone = 'Africa/Kigali'

    _utc_transition_times = [
        datetime(   1,  1,  1,  0,  0,  0), #   7216     0 LMT
        datetime(1935,  5, 31, 21, 59, 44), #   7200     0 CAT
        ]

    _transition_info = [
        ttinfo(  7216,      0,  'LMT'),
        ttinfo(  7200,      0,  'CAT'),
        ]

Kigali = Kigali() # Singleton

