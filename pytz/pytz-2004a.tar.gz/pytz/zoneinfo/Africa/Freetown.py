'''
tzinfo timezone information for Africa/Freetown.

Generated from the Olson timezone database:
    ftp://elsie.nci.nih.gov/pub/tz*.tar.gz
'''

from pytz.tzinfo import DstTzInfo
from pytz.tzinfo import memorized_datetime as datetime
from pytz.tzinfo import memorized_ttinfo as ttinfo

class Freetown(DstTzInfo):
    '''Africa/Freetown timezone definition. See datetime.tzinfo for details'''

    _zone = 'Africa/Freetown'

    _utc_transition_times = [
        datetime(   1,  1,  1,  0,  0,  0), #  -3180     0 FMT
        datetime(1913,  6,  1,  0, 53,  0), #  -3600     0 WAT
        datetime(1935,  6,  1,  1,  0,  0), #  -1200  2400 SLST
        datetime(1935, 10,  1,  0, 20,  0), #  -3600     0 WAT
        datetime(1936,  6,  1,  1,  0,  0), #  -1200  2400 SLST
        datetime(1936, 10,  1,  0, 20,  0), #  -3600     0 WAT
        datetime(1937,  6,  1,  1,  0,  0), #  -1200  2400 SLST
        datetime(1937, 10,  1,  0, 20,  0), #  -3600     0 WAT
        datetime(1938,  6,  1,  1,  0,  0), #  -1200  2400 SLST
        datetime(1938, 10,  1,  0, 20,  0), #  -3600     0 WAT
        datetime(1939,  6,  1,  1,  0,  0), #  -1200  2400 SLST
        datetime(1939, 10,  1,  0, 20,  0), #  -3600     0 WAT
        datetime(1940,  6,  1,  1,  0,  0), #  -1200  2400 SLST
        datetime(1940, 10,  1,  0, 20,  0), #  -3600     0 WAT
        datetime(1941,  6,  1,  1,  0,  0), #  -1200  2400 SLST
        datetime(1941, 10,  1,  0, 20,  0), #  -3600     0 WAT
        datetime(1942,  6,  1,  1,  0,  0), #  -1200  2400 SLST
        datetime(1942, 10,  1,  0, 20,  0), #  -3600     0 WAT
        datetime(1957,  1,  1,  1,  0,  0), #      0     0 WAT
        datetime(1957,  6,  1,  0,  0,  0), #   3600  3600 SLST
        datetime(1957,  8, 31, 23,  0,  0), #      0     0 GMT
        datetime(1958,  6,  1,  0,  0,  0), #   3600  3600 SLST
        datetime(1958,  8, 31, 23,  0,  0), #      0     0 GMT
        datetime(1959,  6,  1,  0,  0,  0), #   3600  3600 SLST
        datetime(1959,  8, 31, 23,  0,  0), #      0     0 GMT
        datetime(1960,  6,  1,  0,  0,  0), #   3600  3600 SLST
        datetime(1960,  8, 31, 23,  0,  0), #      0     0 GMT
        datetime(1961,  6,  1,  0,  0,  0), #   3600  3600 SLST
        datetime(1961,  8, 31, 23,  0,  0), #      0     0 GMT
        datetime(1962,  6,  1,  0,  0,  0), #   3600  3600 SLST
        datetime(1962,  8, 31, 23,  0,  0), #      0     0 GMT
        ]

    _transition_info = [
        ttinfo( -3180,      0,  'FMT'),
        ttinfo( -3600,      0,  'WAT'),
        ttinfo( -1200,   2400, 'SLST'),
        ttinfo( -3600,      0,  'WAT'),
        ttinfo( -1200,   2400, 'SLST'),
        ttinfo( -3600,      0,  'WAT'),
        ttinfo( -1200,   2400, 'SLST'),
        ttinfo( -3600,      0,  'WAT'),
        ttinfo( -1200,   2400, 'SLST'),
        ttinfo( -3600,      0,  'WAT'),
        ttinfo( -1200,   2400, 'SLST'),
        ttinfo( -3600,      0,  'WAT'),
        ttinfo( -1200,   2400, 'SLST'),
        ttinfo( -3600,      0,  'WAT'),
        ttinfo( -1200,   2400, 'SLST'),
        ttinfo( -3600,      0,  'WAT'),
        ttinfo( -1200,   2400, 'SLST'),
        ttinfo( -3600,      0,  'WAT'),
        ttinfo(     0,      0,  'WAT'),
        ttinfo(  3600,   3600, 'SLST'),
        ttinfo(     0,      0,  'GMT'),
        ttinfo(  3600,   3600, 'SLST'),
        ttinfo(     0,      0,  'GMT'),
        ttinfo(  3600,   3600, 'SLST'),
        ttinfo(     0,      0,  'GMT'),
        ttinfo(  3600,   3600, 'SLST'),
        ttinfo(     0,      0,  'GMT'),
        ttinfo(  3600,   3600, 'SLST'),
        ttinfo(     0,      0,  'GMT'),
        ttinfo(  3600,   3600, 'SLST'),
        ttinfo(     0,      0,  'GMT'),
        ]

Freetown = Freetown() # Singleton

