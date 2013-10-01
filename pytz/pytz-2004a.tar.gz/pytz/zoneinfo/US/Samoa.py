'''
tzinfo timezone information for US/Samoa.

Generated from the Olson timezone database:
    ftp://elsie.nci.nih.gov/pub/tz*.tar.gz
'''

from pytz.tzinfo import DstTzInfo
from pytz.tzinfo import memorized_datetime as datetime
from pytz.tzinfo import memorized_ttinfo as ttinfo

class Samoa(DstTzInfo):
    '''US/Samoa timezone definition. See datetime.tzinfo for details'''

    _zone = 'US/Samoa'

    _utc_transition_times = [
        datetime(   1,  1,  1,  0,  0,  0), # -40968     0 LMT
        datetime(1911,  1,  1, 11, 22, 48), # -41400     0 SAMT
        datetime(1950,  1,  1, 11, 30,  0), # -39600     0 NST
        datetime(1967,  4,  1, 11,  0,  0), # -39600     0 BST
        datetime(1983, 11, 30, 11,  0,  0), # -39600     0 SST
        ]

    _transition_info = [
        ttinfo(-40968,      0,  'LMT'),
        ttinfo(-41400,      0, 'SAMT'),
        ttinfo(-39600,      0,  'NST'),
        ttinfo(-39600,      0,  'BST'),
        ttinfo(-39600,      0,  'SST'),
        ]

Samoa = Samoa() # Singleton

