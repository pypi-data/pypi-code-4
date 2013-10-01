'''
tzinfo timezone information for Pacific/Galapagos.

Generated from the Olson timezone database:
    ftp://elsie.nci.nih.gov/pub/tz*.tar.gz
'''

from pytz.tzinfo import DstTzInfo
from pytz.tzinfo import memorized_datetime as datetime
from pytz.tzinfo import memorized_ttinfo as ttinfo

class Galapagos(DstTzInfo):
    '''Pacific/Galapagos timezone definition. See datetime.tzinfo for details'''

    _zone = 'Pacific/Galapagos'

    _utc_transition_times = [
        datetime(   1,  1,  1,  0,  0,  0), # -21504     0 LMT
        datetime(1931,  1,  1,  5, 58, 24), # -18000     0 ECT
        datetime(1986,  1,  1,  5,  0,  0), # -21600     0 GALT
        ]

    _transition_info = [
        ttinfo(-21504,      0,  'LMT'),
        ttinfo(-18000,      0,  'ECT'),
        ttinfo(-21600,      0, 'GALT'),
        ]

Galapagos = Galapagos() # Singleton

