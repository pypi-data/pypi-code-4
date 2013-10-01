'''
tzinfo timezone information for Pacific/Nauru.

Generated from the Olson timezone database:
    ftp://elsie.nci.nih.gov/pub/tz*.tar.gz
'''

from pytz.tzinfo import DstTzInfo
from pytz.tzinfo import memorized_datetime as datetime
from pytz.tzinfo import memorized_ttinfo as ttinfo

class Nauru(DstTzInfo):
    '''Pacific/Nauru timezone definition. See datetime.tzinfo for details'''

    _zone = 'Pacific/Nauru'

    _utc_transition_times = [
        datetime(   1,  1,  1,  0,  0,  0), #  40060     0 LMT
        datetime(1921,  1, 14, 12, 52, 20), #  41400     0 NRT
        datetime(1942,  3, 14, 12, 30,  0), #  32400     0 JST
        datetime(1944,  8, 14, 15,  0,  0), #  41400     0 NRT
        datetime(1979,  4, 30, 12, 30,  0), #  43200     0 NRT
        ]

    _transition_info = [
        ttinfo( 40060,      0,  'LMT'),
        ttinfo( 41400,      0,  'NRT'),
        ttinfo( 32400,      0,  'JST'),
        ttinfo( 41400,      0,  'NRT'),
        ttinfo( 43200,      0,  'NRT'),
        ]

Nauru = Nauru() # Singleton

