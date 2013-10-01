'''
tzinfo timezone information for Africa/Khartoum.

Generated from the Olson timezone database:
    ftp://elsie.nci.nih.gov/pub/tz*.tar.gz
'''

from pytz.tzinfo import DstTzInfo
from pytz.tzinfo import memorized_datetime as datetime
from pytz.tzinfo import memorized_ttinfo as ttinfo

class Khartoum(DstTzInfo):
    '''Africa/Khartoum timezone definition. See datetime.tzinfo for details'''

    _zone = 'Africa/Khartoum'

    _utc_transition_times = [
        datetime(   1,  1,  1,  0,  0,  0), #   7808     0 LMT
        datetime(1930, 12, 31, 21, 49, 52), #   7200     0 CAT
        datetime(1970,  4, 30, 22,  0,  0), #  10800  3600 CAST
        datetime(1970, 10, 14, 21,  0,  0), #   7200     0 CAT
        datetime(1971,  4, 29, 22,  0,  0), #  10800  3600 CAST
        datetime(1971, 10, 14, 21,  0,  0), #   7200     0 CAT
        datetime(1972,  4, 29, 22,  0,  0), #  10800  3600 CAST
        datetime(1972, 10, 14, 21,  0,  0), #   7200     0 CAT
        datetime(1973,  4, 28, 22,  0,  0), #  10800  3600 CAST
        datetime(1973, 10, 14, 21,  0,  0), #   7200     0 CAT
        datetime(1974,  4, 27, 22,  0,  0), #  10800  3600 CAST
        datetime(1974, 10, 14, 21,  0,  0), #   7200     0 CAT
        datetime(1975,  4, 26, 22,  0,  0), #  10800  3600 CAST
        datetime(1975, 10, 14, 21,  0,  0), #   7200     0 CAT
        datetime(1976,  4, 24, 22,  0,  0), #  10800  3600 CAST
        datetime(1976, 10, 14, 21,  0,  0), #   7200     0 CAT
        datetime(1977,  4, 23, 22,  0,  0), #  10800  3600 CAST
        datetime(1977, 10, 14, 21,  0,  0), #   7200     0 CAT
        datetime(1978,  4, 29, 22,  0,  0), #  10800  3600 CAST
        datetime(1978, 10, 14, 21,  0,  0), #   7200     0 CAT
        datetime(1979,  4, 28, 22,  0,  0), #  10800  3600 CAST
        datetime(1979, 10, 14, 21,  0,  0), #   7200     0 CAT
        datetime(1980,  4, 26, 22,  0,  0), #  10800  3600 CAST
        datetime(1980, 10, 14, 21,  0,  0), #   7200     0 CAT
        datetime(1981,  4, 25, 22,  0,  0), #  10800  3600 CAST
        datetime(1981, 10, 14, 21,  0,  0), #   7200     0 CAT
        datetime(1982,  4, 24, 22,  0,  0), #  10800  3600 CAST
        datetime(1982, 10, 14, 21,  0,  0), #   7200     0 CAT
        datetime(1983,  4, 23, 22,  0,  0), #  10800  3600 CAST
        datetime(1983, 10, 14, 21,  0,  0), #   7200     0 CAT
        datetime(1984,  4, 28, 22,  0,  0), #  10800  3600 CAST
        datetime(1984, 10, 14, 21,  0,  0), #   7200     0 CAT
        datetime(1985,  4, 27, 22,  0,  0), #  10800  3600 CAST
        datetime(1985, 10, 14, 21,  0,  0), #   7200     0 CAT
        datetime(2000,  1, 15, 10,  0,  0), #  10800     0 EAT
        ]

    _transition_info = [
        ttinfo(  7808,      0,  'LMT'),
        ttinfo(  7200,      0,  'CAT'),
        ttinfo( 10800,   3600, 'CAST'),
        ttinfo(  7200,      0,  'CAT'),
        ttinfo( 10800,   3600, 'CAST'),
        ttinfo(  7200,      0,  'CAT'),
        ttinfo( 10800,   3600, 'CAST'),
        ttinfo(  7200,      0,  'CAT'),
        ttinfo( 10800,   3600, 'CAST'),
        ttinfo(  7200,      0,  'CAT'),
        ttinfo( 10800,   3600, 'CAST'),
        ttinfo(  7200,      0,  'CAT'),
        ttinfo( 10800,   3600, 'CAST'),
        ttinfo(  7200,      0,  'CAT'),
        ttinfo( 10800,   3600, 'CAST'),
        ttinfo(  7200,      0,  'CAT'),
        ttinfo( 10800,   3600, 'CAST'),
        ttinfo(  7200,      0,  'CAT'),
        ttinfo( 10800,   3600, 'CAST'),
        ttinfo(  7200,      0,  'CAT'),
        ttinfo( 10800,   3600, 'CAST'),
        ttinfo(  7200,      0,  'CAT'),
        ttinfo( 10800,   3600, 'CAST'),
        ttinfo(  7200,      0,  'CAT'),
        ttinfo( 10800,   3600, 'CAST'),
        ttinfo(  7200,      0,  'CAT'),
        ttinfo( 10800,   3600, 'CAST'),
        ttinfo(  7200,      0,  'CAT'),
        ttinfo( 10800,   3600, 'CAST'),
        ttinfo(  7200,      0,  'CAT'),
        ttinfo( 10800,   3600, 'CAST'),
        ttinfo(  7200,      0,  'CAT'),
        ttinfo( 10800,   3600, 'CAST'),
        ttinfo(  7200,      0,  'CAT'),
        ttinfo( 10800,      0,  'EAT'),
        ]

Khartoum = Khartoum() # Singleton

