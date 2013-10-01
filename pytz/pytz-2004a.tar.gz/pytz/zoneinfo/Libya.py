'''
tzinfo timezone information for Libya.

Generated from the Olson timezone database:
    ftp://elsie.nci.nih.gov/pub/tz*.tar.gz
'''

from pytz.tzinfo import DstTzInfo
from pytz.tzinfo import memorized_datetime as datetime
from pytz.tzinfo import memorized_ttinfo as ttinfo

class Libya(DstTzInfo):
    '''Libya timezone definition. See datetime.tzinfo for details'''

    _zone = 'Libya'

    _utc_transition_times = [
        datetime(   1,  1,  1,  0,  0,  0), #   3164     0 LMT
        datetime(1919, 12, 31, 23,  7, 16), #   3600     0 CET
        datetime(1951, 10, 14,  1,  0,  0), #   7200  3600 CEST
        datetime(1951, 12, 31, 22,  0,  0), #   3600     0 CET
        datetime(1953, 10,  9,  1,  0,  0), #   7200  3600 CEST
        datetime(1953, 12, 31, 22,  0,  0), #   3600     0 CET
        datetime(1955,  9, 29, 23,  0,  0), #   7200  3600 CEST
        datetime(1955, 12, 31, 22,  0,  0), #   3600     0 CET
        datetime(1958, 12, 31, 23,  0,  0), #   7200     0 EET
        datetime(1981, 12, 31, 22,  0,  0), #   3600     0 CET
        datetime(1982,  3, 31, 23,  0,  0), #   7200  3600 CEST
        datetime(1982,  9, 30, 22,  0,  0), #   3600     0 CET
        datetime(1983,  3, 31, 23,  0,  0), #   7200  3600 CEST
        datetime(1983,  9, 30, 22,  0,  0), #   3600     0 CET
        datetime(1984,  3, 31, 23,  0,  0), #   7200  3600 CEST
        datetime(1984,  9, 30, 22,  0,  0), #   3600     0 CET
        datetime(1985,  4,  5, 23,  0,  0), #   7200  3600 CEST
        datetime(1985,  9, 30, 22,  0,  0), #   3600     0 CET
        datetime(1986,  4,  3, 23,  0,  0), #   7200  3600 CEST
        datetime(1986, 10,  2, 22,  0,  0), #   3600     0 CET
        datetime(1987,  3, 31, 23,  0,  0), #   7200  3600 CEST
        datetime(1987,  9, 30, 22,  0,  0), #   3600     0 CET
        datetime(1988,  3, 31, 23,  0,  0), #   7200  3600 CEST
        datetime(1988,  9, 30, 22,  0,  0), #   3600     0 CET
        datetime(1989,  3, 31, 23,  0,  0), #   7200  3600 CEST
        datetime(1989,  9, 30, 22,  0,  0), #   3600     0 CET
        datetime(1990,  5,  3, 23,  0,  0), #   7200     0 EET
        datetime(1996,  9, 29, 22,  0,  0), #   3600     0 CET
        datetime(1997,  4,  3, 23,  0,  0), #   7200  3600 CEST
        datetime(1997, 10,  3, 22,  0,  0), #   7200     0 EET
        ]

    _transition_info = [
        ttinfo(  3164,      0,  'LMT'),
        ttinfo(  3600,      0,  'CET'),
        ttinfo(  7200,   3600, 'CEST'),
        ttinfo(  3600,      0,  'CET'),
        ttinfo(  7200,   3600, 'CEST'),
        ttinfo(  3600,      0,  'CET'),
        ttinfo(  7200,   3600, 'CEST'),
        ttinfo(  3600,      0,  'CET'),
        ttinfo(  7200,      0,  'EET'),
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
        ttinfo(  7200,      0,  'EET'),
        ttinfo(  3600,      0,  'CET'),
        ttinfo(  7200,   3600, 'CEST'),
        ttinfo(  7200,      0,  'EET'),
        ]

Libya = Libya() # Singleton

