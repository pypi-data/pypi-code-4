'''
tzinfo timezone information for Pacific/Tongatapu.

Generated from the Olson timezone database:
    ftp://elsie.nci.nih.gov/pub/tz*.tar.gz
'''

from pytz.tzinfo import DstTzInfo
from pytz.tzinfo import memorized_datetime as datetime
from pytz.tzinfo import memorized_ttinfo as ttinfo

class Tongatapu(DstTzInfo):
    '''Pacific/Tongatapu timezone definition. See datetime.tzinfo for details'''

    _zone = 'Pacific/Tongatapu'

    _utc_transition_times = [
        datetime(   1,  1,  1,  0,  0,  0), #  44400     0 TOT
        datetime(1940, 12, 31, 11, 40,  0), #  46800     0 TOT
        datetime(1999, 10,  6, 13,  0,  0), #  50400  3600 TOST
        datetime(2000,  3, 18, 13,  0,  0), #  46800     0 TOT
        datetime(2000, 11,  4, 13,  0,  0), #  50400  3600 TOST
        datetime(2001,  1, 27, 12,  0,  0), #  46800     0 TOT
        datetime(2001, 11,  3, 13,  0,  0), #  50400  3600 TOST
        datetime(2002,  1, 26, 12,  0,  0), #  46800     0 TOT
        ]

    _transition_info = [
        ttinfo( 44400,      0,  'TOT'),
        ttinfo( 46800,      0,  'TOT'),
        ttinfo( 50400,   3600, 'TOST'),
        ttinfo( 46800,      0,  'TOT'),
        ttinfo( 50400,   3600, 'TOST'),
        ttinfo( 46800,      0,  'TOT'),
        ttinfo( 50400,   3600, 'TOST'),
        ttinfo( 46800,      0,  'TOT'),
        ]

Tongatapu = Tongatapu() # Singleton

