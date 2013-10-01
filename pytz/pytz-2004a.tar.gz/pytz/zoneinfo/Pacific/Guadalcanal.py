'''
tzinfo timezone information for Pacific/Guadalcanal.

Generated from the Olson timezone database:
    ftp://elsie.nci.nih.gov/pub/tz*.tar.gz
'''

from pytz.tzinfo import DstTzInfo
from pytz.tzinfo import memorized_datetime as datetime
from pytz.tzinfo import memorized_ttinfo as ttinfo

class Guadalcanal(DstTzInfo):
    '''Pacific/Guadalcanal timezone definition. See datetime.tzinfo for details'''

    _zone = 'Pacific/Guadalcanal'

    _utc_transition_times = [
        datetime(   1,  1,  1,  0,  0,  0), #  38388     0 LMT
        datetime(1912,  9, 30, 13, 20, 12), #  39600     0 SBT
        ]

    _transition_info = [
        ttinfo( 38388,      0,  'LMT'),
        ttinfo( 39600,      0,  'SBT'),
        ]

Guadalcanal = Guadalcanal() # Singleton

