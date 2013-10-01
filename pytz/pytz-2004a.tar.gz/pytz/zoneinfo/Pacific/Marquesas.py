'''
tzinfo timezone information for Pacific/Marquesas.

Generated from the Olson timezone database:
    ftp://elsie.nci.nih.gov/pub/tz*.tar.gz
'''

from pytz.tzinfo import DstTzInfo
from pytz.tzinfo import memorized_datetime as datetime
from pytz.tzinfo import memorized_ttinfo as ttinfo

class Marquesas(DstTzInfo):
    '''Pacific/Marquesas timezone definition. See datetime.tzinfo for details'''

    _zone = 'Pacific/Marquesas'

    _utc_transition_times = [
        datetime(   1,  1,  1,  0,  0,  0), # -33480     0 LMT
        datetime(1912, 10,  1,  9, 18,  0), # -34200     0 MART
        ]

    _transition_info = [
        ttinfo(-33480,      0,  'LMT'),
        ttinfo(-34200,      0, 'MART'),
        ]

Marquesas = Marquesas() # Singleton

