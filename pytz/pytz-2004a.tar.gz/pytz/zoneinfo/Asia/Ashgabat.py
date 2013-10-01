'''
tzinfo timezone information for Asia/Ashgabat.

Generated from the Olson timezone database:
    ftp://elsie.nci.nih.gov/pub/tz*.tar.gz
'''

from pytz.tzinfo import DstTzInfo
from pytz.tzinfo import memorized_datetime as datetime
from pytz.tzinfo import memorized_ttinfo as ttinfo

class Ashgabat(DstTzInfo):
    '''Asia/Ashgabat timezone definition. See datetime.tzinfo for details'''

    _zone = 'Asia/Ashgabat'

    _utc_transition_times = [
        datetime(   1,  1,  1,  0,  0,  0), #  14012     0 LMT
        datetime(1924,  5,  1, 20,  6, 28), #  14400     0 ASHT
        datetime(1930,  6, 20, 20,  0,  0), #  18000     0 ASHT
        datetime(1981,  3, 31, 19,  0,  0), #  21600  3600 ASHST
        datetime(1981,  9, 30, 18,  0,  0), #  18000     0 ASHT
        datetime(1982,  3, 31, 19,  0,  0), #  21600  3600 ASHST
        datetime(1982,  9, 30, 18,  0,  0), #  18000     0 ASHT
        datetime(1983,  3, 31, 19,  0,  0), #  21600  3600 ASHST
        datetime(1983,  9, 30, 18,  0,  0), #  18000     0 ASHT
        datetime(1984,  3, 31, 19,  0,  0), #  21600  3600 ASHST
        datetime(1984,  9, 29, 21,  0,  0), #  18000     0 ASHT
        datetime(1985,  3, 30, 21,  0,  0), #  21600  3600 ASHST
        datetime(1985,  9, 28, 21,  0,  0), #  18000     0 ASHT
        datetime(1986,  3, 29, 21,  0,  0), #  21600  3600 ASHST
        datetime(1986,  9, 27, 21,  0,  0), #  18000     0 ASHT
        datetime(1987,  3, 28, 21,  0,  0), #  21600  3600 ASHST
        datetime(1987,  9, 26, 21,  0,  0), #  18000     0 ASHT
        datetime(1988,  3, 26, 21,  0,  0), #  21600  3600 ASHST
        datetime(1988,  9, 24, 21,  0,  0), #  18000     0 ASHT
        datetime(1989,  3, 25, 21,  0,  0), #  21600  3600 ASHST
        datetime(1989,  9, 23, 21,  0,  0), #  18000     0 ASHT
        datetime(1990,  3, 24, 21,  0,  0), #  21600  3600 ASHST
        datetime(1990,  9, 29, 21,  0,  0), #  18000     0 ASHT
        datetime(1991,  3, 30, 21,  0,  0), #  18000     0 ASHST
        datetime(1991,  9, 28, 22,  0,  0), #  14400     0 ASHT
        datetime(1991, 10, 26, 20,  0,  0), #  14400     0 TMT
        datetime(1992,  1, 18, 22,  0,  0), #  18000     0 TMT
        ]

    _transition_info = [
        ttinfo( 14012,      0,  'LMT'),
        ttinfo( 14400,      0, 'ASHT'),
        ttinfo( 18000,      0, 'ASHT'),
        ttinfo( 21600,   3600, 'ASHST'),
        ttinfo( 18000,      0, 'ASHT'),
        ttinfo( 21600,   3600, 'ASHST'),
        ttinfo( 18000,      0, 'ASHT'),
        ttinfo( 21600,   3600, 'ASHST'),
        ttinfo( 18000,      0, 'ASHT'),
        ttinfo( 21600,   3600, 'ASHST'),
        ttinfo( 18000,      0, 'ASHT'),
        ttinfo( 21600,   3600, 'ASHST'),
        ttinfo( 18000,      0, 'ASHT'),
        ttinfo( 21600,   3600, 'ASHST'),
        ttinfo( 18000,      0, 'ASHT'),
        ttinfo( 21600,   3600, 'ASHST'),
        ttinfo( 18000,      0, 'ASHT'),
        ttinfo( 21600,   3600, 'ASHST'),
        ttinfo( 18000,      0, 'ASHT'),
        ttinfo( 21600,   3600, 'ASHST'),
        ttinfo( 18000,      0, 'ASHT'),
        ttinfo( 21600,   3600, 'ASHST'),
        ttinfo( 18000,      0, 'ASHT'),
        ttinfo( 18000,      0, 'ASHST'),
        ttinfo( 14400,      0, 'ASHT'),
        ttinfo( 14400,      0,  'TMT'),
        ttinfo( 18000,      0,  'TMT'),
        ]

Ashgabat = Ashgabat() # Singleton

