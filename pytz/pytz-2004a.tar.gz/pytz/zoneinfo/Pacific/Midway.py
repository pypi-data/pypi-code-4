'''
tzinfo timezone information for Pacific/Midway.

Generated from the Olson timezone database:
    ftp://elsie.nci.nih.gov/pub/tz*.tar.gz
'''

from pytz.tzinfo import DstTzInfo
from pytz.tzinfo import memorized_datetime as datetime
from pytz.tzinfo import memorized_ttinfo as ttinfo

class Midway(DstTzInfo):
    '''Pacific/Midway timezone definition. See datetime.tzinfo for details'''

    _zone = 'Pacific/Midway'

    _utc_transition_times = [
        datetime(   1,  1,  1,  0,  0,  0), # -39600     0 NST
        datetime(1956,  6,  3, 11,  0,  0), # -36000  3600 NDT
        datetime(1956,  9,  2, 10,  0,  0), # -39600     0 NST
        datetime(1967,  4,  1, 11,  0,  0), # -39600     0 BST
        datetime(1983, 11, 30, 11,  0,  0), # -39600     0 SST
        ]

    _transition_info = [
        ttinfo(-39600,      0,  'NST'),
        ttinfo(-36000,   3600,  'NDT'),
        ttinfo(-39600,      0,  'NST'),
        ttinfo(-39600,      0,  'BST'),
        ttinfo(-39600,      0,  'SST'),
        ]

Midway = Midway() # Singleton

