'''
tzinfo timezone information for Pacific/Gambier.

Generated from the Olson timezone database:
    ftp://elsie.nci.nih.gov/pub/tz*.tar.gz
'''

from pytz.tzinfo import DstTzInfo
from pytz.tzinfo import memorized_datetime as datetime
from pytz.tzinfo import memorized_ttinfo as ttinfo

class Gambier(DstTzInfo):
    '''Pacific/Gambier timezone definition. See datetime.tzinfo for details'''

    _zone = 'Pacific/Gambier'

    _utc_transition_times = [
        datetime(   1,  1,  1,  0,  0,  0), # -32388     0 LMT
        datetime(1912, 10,  1,  8, 59, 48), # -32400     0 GAMT
        ]

    _transition_info = [
        ttinfo(-32388,      0,  'LMT'),
        ttinfo(-32400,      0, 'GAMT'),
        ]

Gambier = Gambier() # Singleton

