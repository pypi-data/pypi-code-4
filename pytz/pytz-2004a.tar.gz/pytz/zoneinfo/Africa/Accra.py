'''
tzinfo timezone information for Africa/Accra.

Generated from the Olson timezone database:
    ftp://elsie.nci.nih.gov/pub/tz*.tar.gz
'''

from pytz.tzinfo import DstTzInfo
from pytz.tzinfo import memorized_datetime as datetime
from pytz.tzinfo import memorized_ttinfo as ttinfo

class Accra(DstTzInfo):
    '''Africa/Accra timezone definition. See datetime.tzinfo for details'''

    _zone = 'Africa/Accra'

    _utc_transition_times = [
        datetime(   1,  1,  1,  0,  0,  0), #    -52     0 LMT
        datetime(1918,  1,  1,  0,  0, 52), #      0     0 GMT
        datetime(1936,  9,  1,  0,  0,  0), #   1200  1200 GHST
        datetime(1936, 12, 30, 23, 40,  0), #      0     0 GMT
        datetime(1937,  9,  1,  0,  0,  0), #   1200  1200 GHST
        datetime(1937, 12, 30, 23, 40,  0), #      0     0 GMT
        datetime(1938,  9,  1,  0,  0,  0), #   1200  1200 GHST
        datetime(1938, 12, 30, 23, 40,  0), #      0     0 GMT
        datetime(1939,  9,  1,  0,  0,  0), #   1200  1200 GHST
        datetime(1939, 12, 30, 23, 40,  0), #      0     0 GMT
        datetime(1940,  9,  1,  0,  0,  0), #   1200  1200 GHST
        datetime(1940, 12, 30, 23, 40,  0), #      0     0 GMT
        datetime(1941,  9,  1,  0,  0,  0), #   1200  1200 GHST
        datetime(1941, 12, 30, 23, 40,  0), #      0     0 GMT
        datetime(1942,  9,  1,  0,  0,  0), #   1200  1200 GHST
        datetime(1942, 12, 30, 23, 40,  0), #      0     0 GMT
        ]

    _transition_info = [
        ttinfo(   -52,      0,  'LMT'),
        ttinfo(     0,      0,  'GMT'),
        ttinfo(  1200,   1200, 'GHST'),
        ttinfo(     0,      0,  'GMT'),
        ttinfo(  1200,   1200, 'GHST'),
        ttinfo(     0,      0,  'GMT'),
        ttinfo(  1200,   1200, 'GHST'),
        ttinfo(     0,      0,  'GMT'),
        ttinfo(  1200,   1200, 'GHST'),
        ttinfo(     0,      0,  'GMT'),
        ttinfo(  1200,   1200, 'GHST'),
        ttinfo(     0,      0,  'GMT'),
        ttinfo(  1200,   1200, 'GHST'),
        ttinfo(     0,      0,  'GMT'),
        ttinfo(  1200,   1200, 'GHST'),
        ttinfo(     0,      0,  'GMT'),
        ]

Accra = Accra() # Singleton

