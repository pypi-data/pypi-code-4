'''
tzinfo timezone information for Pacific/Tahiti.

Generated from the Olson timezone database:
    ftp://elsie.nci.nih.gov/pub/tz*.tar.gz
'''

from pytz.tzinfo import DstTzInfo
from pytz.tzinfo import memorized_datetime as datetime
from pytz.tzinfo import memorized_ttinfo as ttinfo

class Tahiti(DstTzInfo):
    '''Pacific/Tahiti timezone definition. See datetime.tzinfo for details'''

    _zone = 'Pacific/Tahiti'

    _utc_transition_times = [
        datetime(   1,  1,  1,  0,  0,  0), # -35896     0 LMT
        datetime(1912, 10,  1,  9, 58, 16), # -36000     0 TAHT
        ]

    _transition_info = [
        ttinfo(-35896,      0,  'LMT'),
        ttinfo(-36000,      0, 'TAHT'),
        ]

Tahiti = Tahiti() # Singleton

