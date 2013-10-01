'''
tzinfo timezone information for Australia/Brisbane.

Generated from the Olson timezone database:
    ftp://elsie.nci.nih.gov/pub/tz*.tar.gz
'''

from pytz.tzinfo import DstTzInfo
from pytz.tzinfo import memorized_datetime as datetime
from pytz.tzinfo import memorized_ttinfo as ttinfo

class Brisbane(DstTzInfo):
    '''Australia/Brisbane timezone definition. See datetime.tzinfo for details'''

    _zone = 'Australia/Brisbane'

    _utc_transition_times = [
        datetime(   1,  1,  1,  0,  0,  0), #  36000     0 EST
        datetime(1916, 12, 31, 14,  1,  0), #  39600  3600 EST
        datetime(1917,  3, 24, 15,  0,  0), #  36000     0 EST
        datetime(1941, 12, 31, 16,  0,  0), #  39600  3600 EST
        datetime(1942,  3, 28, 15,  0,  0), #  36000     0 EST
        datetime(1942,  9, 26, 16,  0,  0), #  39600  3600 EST
        datetime(1943,  3, 27, 15,  0,  0), #  36000     0 EST
        datetime(1943, 10,  2, 16,  0,  0), #  39600  3600 EST
        datetime(1944,  3, 25, 15,  0,  0), #  36000     0 EST
        datetime(1971, 10, 30, 16,  0,  0), #  39600  3600 EST
        datetime(1972,  2, 26, 16,  0,  0), #  36000     0 EST
        datetime(1989, 10, 28, 16,  0,  0), #  39600  3600 EST
        datetime(1990,  3,  3, 16,  0,  0), #  36000     0 EST
        datetime(1990, 10, 27, 16,  0,  0), #  39600  3600 EST
        datetime(1991,  3,  2, 16,  0,  0), #  36000     0 EST
        datetime(1991, 10, 26, 16,  0,  0), #  39600  3600 EST
        datetime(1992,  2, 29, 16,  0,  0), #  36000     0 EST
        ]

    _transition_info = [
        ttinfo( 36000,      0,  'EST'),
        ttinfo( 39600,   3600,  'EST'),
        ttinfo( 36000,      0,  'EST'),
        ttinfo( 39600,   3600,  'EST'),
        ttinfo( 36000,      0,  'EST'),
        ttinfo( 39600,   3600,  'EST'),
        ttinfo( 36000,      0,  'EST'),
        ttinfo( 39600,   3600,  'EST'),
        ttinfo( 36000,      0,  'EST'),
        ttinfo( 39600,   3600,  'EST'),
        ttinfo( 36000,      0,  'EST'),
        ttinfo( 39600,   3600,  'EST'),
        ttinfo( 36000,      0,  'EST'),
        ttinfo( 39600,   3600,  'EST'),
        ttinfo( 36000,      0,  'EST'),
        ttinfo( 39600,   3600,  'EST'),
        ttinfo( 36000,      0,  'EST'),
        ]

Brisbane = Brisbane() # Singleton

