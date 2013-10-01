'''
tzinfo timezone information for Australia/Darwin.

Generated from the Olson timezone database:
    ftp://elsie.nci.nih.gov/pub/tz*.tar.gz
'''

from pytz.tzinfo import DstTzInfo
from pytz.tzinfo import memorized_datetime as datetime
from pytz.tzinfo import memorized_ttinfo as ttinfo

class Darwin(DstTzInfo):
    '''Australia/Darwin timezone definition. See datetime.tzinfo for details'''

    _zone = 'Australia/Darwin'

    _utc_transition_times = [
        datetime(   1,  1,  1,  0,  0,  0), #  34200     0 CST
        datetime(1916, 12, 31, 14, 31,  0), #  37800  3600 CST
        datetime(1917,  3, 24, 15, 30,  0), #  34200     0 CST
        datetime(1941, 12, 31, 16, 30,  0), #  37800  3600 CST
        datetime(1942,  3, 28, 15, 30,  0), #  34200     0 CST
        datetime(1942,  9, 26, 16, 30,  0), #  37800  3600 CST
        datetime(1943,  3, 27, 15, 30,  0), #  34200     0 CST
        datetime(1943, 10,  2, 16, 30,  0), #  37800  3600 CST
        datetime(1944,  3, 25, 15, 30,  0), #  34200     0 CST
        ]

    _transition_info = [
        ttinfo( 34200,      0,  'CST'),
        ttinfo( 37800,   3600,  'CST'),
        ttinfo( 34200,      0,  'CST'),
        ttinfo( 37800,   3600,  'CST'),
        ttinfo( 34200,      0,  'CST'),
        ttinfo( 37800,   3600,  'CST'),
        ttinfo( 34200,      0,  'CST'),
        ttinfo( 37800,   3600,  'CST'),
        ttinfo( 34200,      0,  'CST'),
        ]

Darwin = Darwin() # Singleton

