'''
tzinfo timezone information for Africa/Blantyre.

Generated from the Olson timezone database:
    ftp://elsie.nci.nih.gov/pub/tz*.tar.gz
'''

from pytz.tzinfo import DstTzInfo
from pytz.tzinfo import memorized_datetime as datetime
from pytz.tzinfo import memorized_ttinfo as ttinfo

class Blantyre(DstTzInfo):
    '''Africa/Blantyre timezone definition. See datetime.tzinfo for details'''

    _zone = 'Africa/Blantyre'

    _utc_transition_times = [
        datetime(   1,  1,  1,  0,  0,  0), #   8400     0 LMT
        datetime(1903,  2, 28, 21, 40,  0), #   7200     0 CAT
        ]

    _transition_info = [
        ttinfo(  8400,      0,  'LMT'),
        ttinfo(  7200,      0,  'CAT'),
        ]

Blantyre = Blantyre() # Singleton

