'''
tzinfo timezone information for Pacific/Apia.

Generated from the Olson timezone database:
    ftp://elsie.nci.nih.gov/pub/tz*.tar.gz
'''

from pytz.tzinfo import DstTzInfo
from pytz.tzinfo import memorized_datetime as datetime
from pytz.tzinfo import memorized_ttinfo as ttinfo

class Apia(DstTzInfo):
    '''Pacific/Apia timezone definition. See datetime.tzinfo for details'''

    _zone = 'Pacific/Apia'

    _utc_transition_times = [
        datetime(   1,  1,  1,  0,  0,  0), # -41216     0 LMT
        datetime(1911,  1,  1, 11, 26, 56), # -41400     0 SAMT
        datetime(1950,  1,  1, 11, 30,  0), # -39600     0 WST
        ]

    _transition_info = [
        ttinfo(-41216,      0,  'LMT'),
        ttinfo(-41400,      0, 'SAMT'),
        ttinfo(-39600,      0,  'WST'),
        ]

Apia = Apia() # Singleton

