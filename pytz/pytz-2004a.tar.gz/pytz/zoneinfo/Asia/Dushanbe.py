'''
tzinfo timezone information for Asia/Dushanbe.

Generated from the Olson timezone database:
    ftp://elsie.nci.nih.gov/pub/tz*.tar.gz
'''

from pytz.tzinfo import DstTzInfo
from pytz.tzinfo import memorized_datetime as datetime
from pytz.tzinfo import memorized_ttinfo as ttinfo

class Dushanbe(DstTzInfo):
    '''Asia/Dushanbe timezone definition. See datetime.tzinfo for details'''

    _zone = 'Asia/Dushanbe'

    _utc_transition_times = [
        datetime(   1,  1,  1,  0,  0,  0), #  16512     0 LMT
        datetime(1924,  5,  1, 19, 24, 48), #  18000     0 DUST
        datetime(1930,  6, 20, 19,  0,  0), #  21600     0 DUST
        datetime(1981,  3, 31, 18,  0,  0), #  25200  3600 DUSST
        datetime(1981,  9, 30, 17,  0,  0), #  21600     0 DUST
        datetime(1982,  3, 31, 18,  0,  0), #  25200  3600 DUSST
        datetime(1982,  9, 30, 17,  0,  0), #  21600     0 DUST
        datetime(1983,  3, 31, 18,  0,  0), #  25200  3600 DUSST
        datetime(1983,  9, 30, 17,  0,  0), #  21600     0 DUST
        datetime(1984,  3, 31, 18,  0,  0), #  25200  3600 DUSST
        datetime(1984,  9, 29, 20,  0,  0), #  21600     0 DUST
        datetime(1985,  3, 30, 20,  0,  0), #  25200  3600 DUSST
        datetime(1985,  9, 28, 20,  0,  0), #  21600     0 DUST
        datetime(1986,  3, 29, 20,  0,  0), #  25200  3600 DUSST
        datetime(1986,  9, 27, 20,  0,  0), #  21600     0 DUST
        datetime(1987,  3, 28, 20,  0,  0), #  25200  3600 DUSST
        datetime(1987,  9, 26, 20,  0,  0), #  21600     0 DUST
        datetime(1988,  3, 26, 20,  0,  0), #  25200  3600 DUSST
        datetime(1988,  9, 24, 20,  0,  0), #  21600     0 DUST
        datetime(1989,  3, 25, 20,  0,  0), #  25200  3600 DUSST
        datetime(1989,  9, 23, 20,  0,  0), #  21600     0 DUST
        datetime(1990,  3, 24, 20,  0,  0), #  25200  3600 DUSST
        datetime(1990,  9, 29, 20,  0,  0), #  21600     0 DUST
        datetime(1991,  3, 30, 20,  0,  0), #  21600     0 DUSST
        datetime(1991,  9,  8, 21,  0,  0), #  18000     0 TJT
        ]

    _transition_info = [
        ttinfo( 16512,      0,  'LMT'),
        ttinfo( 18000,      0, 'DUST'),
        ttinfo( 21600,      0, 'DUST'),
        ttinfo( 25200,   3600, 'DUSST'),
        ttinfo( 21600,      0, 'DUST'),
        ttinfo( 25200,   3600, 'DUSST'),
        ttinfo( 21600,      0, 'DUST'),
        ttinfo( 25200,   3600, 'DUSST'),
        ttinfo( 21600,      0, 'DUST'),
        ttinfo( 25200,   3600, 'DUSST'),
        ttinfo( 21600,      0, 'DUST'),
        ttinfo( 25200,   3600, 'DUSST'),
        ttinfo( 21600,      0, 'DUST'),
        ttinfo( 25200,   3600, 'DUSST'),
        ttinfo( 21600,      0, 'DUST'),
        ttinfo( 25200,   3600, 'DUSST'),
        ttinfo( 21600,      0, 'DUST'),
        ttinfo( 25200,   3600, 'DUSST'),
        ttinfo( 21600,      0, 'DUST'),
        ttinfo( 25200,   3600, 'DUSST'),
        ttinfo( 21600,      0, 'DUST'),
        ttinfo( 25200,   3600, 'DUSST'),
        ttinfo( 21600,      0, 'DUST'),
        ttinfo( 21600,      0, 'DUSST'),
        ttinfo( 18000,      0,  'TJT'),
        ]

Dushanbe = Dushanbe() # Singleton

