'''
tzinfo timezone information for Africa/Casablanca.

Generated from the Olson timezone database:
    ftp://elsie.nci.nih.gov/pub/tz*.tar.gz
'''

from pytz.tzinfo import DstTzInfo
from pytz.tzinfo import memorized_datetime as datetime
from pytz.tzinfo import memorized_ttinfo as ttinfo

class Casablanca(DstTzInfo):
    '''Africa/Casablanca timezone definition. See datetime.tzinfo for details'''

    _zone = 'Africa/Casablanca'

    _utc_transition_times = [
        datetime(   1,  1,  1,  0,  0,  0), #  -1820     0 LMT
        datetime(1913, 10, 26,  0, 30, 20), #      0     0 WET
        datetime(1939,  9, 12,  0,  0,  0), #   3600  3600 WEST
        datetime(1939, 11, 18, 23,  0,  0), #      0     0 WET
        datetime(1940,  2, 25,  0,  0,  0), #   3600  3600 WEST
        datetime(1945, 11, 17, 23,  0,  0), #      0     0 WET
        datetime(1950,  6, 11,  0,  0,  0), #   3600  3600 WEST
        datetime(1950, 10, 28, 23,  0,  0), #      0     0 WET
        datetime(1967,  6,  3, 12,  0,  0), #   3600  3600 WEST
        datetime(1967,  9, 30, 23,  0,  0), #      0     0 WET
        datetime(1974,  6, 24,  0,  0,  0), #   3600  3600 WEST
        datetime(1974,  8, 31, 23,  0,  0), #      0     0 WET
        datetime(1976,  5,  1,  0,  0,  0), #   3600  3600 WEST
        datetime(1976,  7, 31, 23,  0,  0), #      0     0 WET
        datetime(1977,  5,  1,  0,  0,  0), #   3600  3600 WEST
        datetime(1977,  9, 27, 23,  0,  0), #      0     0 WET
        datetime(1978,  6,  1,  0,  0,  0), #   3600  3600 WEST
        datetime(1978,  8,  3, 23,  0,  0), #      0     0 WET
        datetime(1984,  3, 16,  0,  0,  0), #   3600     0 CET
        datetime(1985, 12, 31, 23,  0,  0), #      0     0 WET
        ]

    _transition_info = [
        ttinfo( -1820,      0,  'LMT'),
        ttinfo(     0,      0,  'WET'),
        ttinfo(  3600,   3600, 'WEST'),
        ttinfo(     0,      0,  'WET'),
        ttinfo(  3600,   3600, 'WEST'),
        ttinfo(     0,      0,  'WET'),
        ttinfo(  3600,   3600, 'WEST'),
        ttinfo(     0,      0,  'WET'),
        ttinfo(  3600,   3600, 'WEST'),
        ttinfo(     0,      0,  'WET'),
        ttinfo(  3600,   3600, 'WEST'),
        ttinfo(     0,      0,  'WET'),
        ttinfo(  3600,   3600, 'WEST'),
        ttinfo(     0,      0,  'WET'),
        ttinfo(  3600,   3600, 'WEST'),
        ttinfo(     0,      0,  'WET'),
        ttinfo(  3600,   3600, 'WEST'),
        ttinfo(     0,      0,  'WET'),
        ttinfo(  3600,      0,  'CET'),
        ttinfo(     0,      0,  'WET'),
        ]

Casablanca = Casablanca() # Singleton

