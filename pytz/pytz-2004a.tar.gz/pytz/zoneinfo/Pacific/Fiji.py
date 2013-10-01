'''
tzinfo timezone information for Pacific/Fiji.

Generated from the Olson timezone database:
    ftp://elsie.nci.nih.gov/pub/tz*.tar.gz
'''

from pytz.tzinfo import DstTzInfo
from pytz.tzinfo import memorized_datetime as datetime
from pytz.tzinfo import memorized_ttinfo as ttinfo

class Fiji(DstTzInfo):
    '''Pacific/Fiji timezone definition. See datetime.tzinfo for details'''

    _zone = 'Pacific/Fiji'

    _utc_transition_times = [
        datetime(   1,  1,  1,  0,  0,  0), #  42820     0 LMT
        datetime(1915, 10, 25, 12,  6, 20), #  43200     0 FJT
        datetime(1998, 10, 31, 14,  0,  0), #  46800  3600 FJST
        datetime(1999,  2, 27, 14,  0,  0), #  43200     0 FJT
        datetime(1999, 11,  6, 14,  0,  0), #  46800  3600 FJST
        datetime(2000,  2, 26, 14,  0,  0), #  43200     0 FJT
        ]

    _transition_info = [
        ttinfo( 42820,      0,  'LMT'),
        ttinfo( 43200,      0,  'FJT'),
        ttinfo( 46800,   3600, 'FJST'),
        ttinfo( 43200,      0,  'FJT'),
        ttinfo( 46800,   3600, 'FJST'),
        ttinfo( 43200,      0,  'FJT'),
        ]

Fiji = Fiji() # Singleton

