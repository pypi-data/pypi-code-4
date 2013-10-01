'''
tzinfo timezone information for America/Cayman.

Generated from the Olson timezone database:
    ftp://elsie.nci.nih.gov/pub/tz*.tar.gz
'''

from pytz.tzinfo import DstTzInfo
from pytz.tzinfo import memorized_datetime as datetime
from pytz.tzinfo import memorized_ttinfo as ttinfo

class Cayman(DstTzInfo):
    '''America/Cayman timezone definition. See datetime.tzinfo for details'''

    _zone = 'America/Cayman'

    _utc_transition_times = [
        datetime(   1,  1,  1,  0,  0,  0), # -18432     0 KMT
        datetime(1912,  2,  1,  5,  7, 12), # -18000     0 EST
        ]

    _transition_info = [
        ttinfo(-18432,      0,  'KMT'),
        ttinfo(-18000,      0,  'EST'),
        ]

Cayman = Cayman() # Singleton

