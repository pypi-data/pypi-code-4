'''
tzinfo timezone information for Africa/Tunis.

Generated from the Olson timezone database:
    ftp://elsie.nci.nih.gov/pub/tz*.tar.gz
'''

from pytz.tzinfo import DstTzInfo
from pytz.tzinfo import memorized_datetime as datetime
from pytz.tzinfo import memorized_ttinfo as ttinfo

class Tunis(DstTzInfo):
    '''Africa/Tunis timezone definition. See datetime.tzinfo for details'''

    _zone = 'Africa/Tunis'

    _utc_transition_times = [
        datetime(   1,  1,  1,  0,  0,  0), #    561     0 PMT
        datetime(1911,  3, 10, 23, 50, 39), #   3600     0 CET
        datetime(1939,  4, 15, 22,  0,  0), #   7200  3600 CEST
        datetime(1939, 11, 18, 22,  0,  0), #   3600     0 CET
        datetime(1940,  2, 25, 22,  0,  0), #   7200  3600 CEST
        datetime(1941, 10,  5, 22,  0,  0), #   3600     0 CET
        datetime(1942,  3,  8, 23,  0,  0), #   7200  3600 CEST
        datetime(1942, 11,  2,  1,  0,  0), #   3600     0 CET
        datetime(1943,  3, 29,  1,  0,  0), #   7200  3600 CEST
        datetime(1943,  4, 17,  0,  0,  0), #   3600     0 CET
        datetime(1943,  4, 25,  1,  0,  0), #   7200  3600 CEST
        datetime(1943, 10,  4,  0,  0,  0), #   3600     0 CET
        datetime(1944,  4,  3,  1,  0,  0), #   7200  3600 CEST
        datetime(1944, 10,  7, 22,  0,  0), #   3600     0 CET
        datetime(1945,  4,  2,  1,  0,  0), #   7200  3600 CEST
        datetime(1945,  9, 15, 22,  0,  0), #   3600     0 CET
        datetime(1977,  4, 29, 23,  0,  0), #   7200  3600 CEST
        datetime(1977,  9, 23, 23,  0,  0), #   3600     0 CET
        datetime(1978,  4, 30, 23,  0,  0), #   7200  3600 CEST
        datetime(1978,  9, 30, 23,  0,  0), #   3600     0 CET
        datetime(1988,  5, 31, 23,  0,  0), #   7200  3600 CEST
        datetime(1988,  9, 24, 23,  0,  0), #   3600     0 CET
        datetime(1989,  3, 25, 23,  0,  0), #   7200  3600 CEST
        datetime(1989,  9, 23, 23,  0,  0), #   3600     0 CET
        datetime(1990,  4, 30, 23,  0,  0), #   7200  3600 CEST
        datetime(1990,  9, 29, 23,  0,  0), #   3600     0 CET
        ]

    _transition_info = [
        ttinfo(   561,      0,  'PMT'),
        ttinfo(  3600,      0,  'CET'),
        ttinfo(  7200,   3600, 'CEST'),
        ttinfo(  3600,      0,  'CET'),
        ttinfo(  7200,   3600, 'CEST'),
        ttinfo(  3600,      0,  'CET'),
        ttinfo(  7200,   3600, 'CEST'),
        ttinfo(  3600,      0,  'CET'),
        ttinfo(  7200,   3600, 'CEST'),
        ttinfo(  3600,      0,  'CET'),
        ttinfo(  7200,   3600, 'CEST'),
        ttinfo(  3600,      0,  'CET'),
        ttinfo(  7200,   3600, 'CEST'),
        ttinfo(  3600,      0,  'CET'),
        ttinfo(  7200,   3600, 'CEST'),
        ttinfo(  3600,      0,  'CET'),
        ttinfo(  7200,   3600, 'CEST'),
        ttinfo(  3600,      0,  'CET'),
        ttinfo(  7200,   3600, 'CEST'),
        ttinfo(  3600,      0,  'CET'),
        ttinfo(  7200,   3600, 'CEST'),
        ttinfo(  3600,      0,  'CET'),
        ttinfo(  7200,   3600, 'CEST'),
        ttinfo(  3600,      0,  'CET'),
        ttinfo(  7200,   3600, 'CEST'),
        ttinfo(  3600,      0,  'CET'),
        ]

Tunis = Tunis() # Singleton

