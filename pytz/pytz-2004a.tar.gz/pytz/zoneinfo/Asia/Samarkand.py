'''
tzinfo timezone information for Asia/Samarkand.

Generated from the Olson timezone database:
    ftp://elsie.nci.nih.gov/pub/tz*.tar.gz
'''

from pytz.tzinfo import DstTzInfo
from pytz.tzinfo import memorized_datetime as datetime
from pytz.tzinfo import memorized_ttinfo as ttinfo

class Samarkand(DstTzInfo):
    '''Asia/Samarkand timezone definition. See datetime.tzinfo for details'''

    _zone = 'Asia/Samarkand'

    _utc_transition_times = [
        datetime(   1,  1,  1,  0,  0,  0), #  16032     0 LMT
        datetime(1924,  5,  1, 19, 32, 48), #  14400     0 SAMT
        datetime(1930,  6, 20, 20,  0,  0), #  18000     0 SAMT
        datetime(1981,  3, 31, 19,  0,  0), #  21600  3600 SAMST
        datetime(1981,  9, 30, 18,  0,  0), #  21600     0 TAST
        datetime(1982,  3, 31, 18,  0,  0), #  25200  3600 TASST
        datetime(1982,  9, 30, 17,  0,  0), #  21600     0 TAST
        datetime(1983,  3, 31, 18,  0,  0), #  25200  3600 TASST
        datetime(1983,  9, 30, 17,  0,  0), #  21600     0 TAST
        datetime(1984,  3, 31, 18,  0,  0), #  25200  3600 TASST
        datetime(1984,  9, 29, 20,  0,  0), #  21600     0 TAST
        datetime(1985,  3, 30, 20,  0,  0), #  25200  3600 TASST
        datetime(1985,  9, 28, 20,  0,  0), #  21600     0 TAST
        datetime(1986,  3, 29, 20,  0,  0), #  25200  3600 TASST
        datetime(1986,  9, 27, 20,  0,  0), #  21600     0 TAST
        datetime(1987,  3, 28, 20,  0,  0), #  25200  3600 TASST
        datetime(1987,  9, 26, 20,  0,  0), #  21600     0 TAST
        datetime(1988,  3, 26, 20,  0,  0), #  25200  3600 TASST
        datetime(1988,  9, 24, 20,  0,  0), #  21600     0 TAST
        datetime(1989,  3, 25, 20,  0,  0), #  25200  3600 TASST
        datetime(1989,  9, 23, 20,  0,  0), #  21600     0 TAST
        datetime(1990,  3, 24, 20,  0,  0), #  25200  3600 TASST
        datetime(1990,  9, 29, 20,  0,  0), #  21600     0 TAST
        datetime(1991,  3, 30, 20,  0,  0), #  21600     0 TASST
        datetime(1991,  8, 31, 18,  0,  0), #  21600     0 UZST
        datetime(1991,  9, 28, 21,  0,  0), #  18000     0 UZT
        datetime(1991, 12, 31, 19,  0,  0), #  18000     0 UZT
        datetime(1992,  3, 28, 18,  0,  0), #  21600  3600 UZST
        datetime(1992,  9, 26, 17,  0,  0), #  18000     0 UZT
        ]

    _transition_info = [
        ttinfo( 16032,      0,  'LMT'),
        ttinfo( 14400,      0, 'SAMT'),
        ttinfo( 18000,      0, 'SAMT'),
        ttinfo( 21600,   3600, 'SAMST'),
        ttinfo( 21600,      0, 'TAST'),
        ttinfo( 25200,   3600, 'TASST'),
        ttinfo( 21600,      0, 'TAST'),
        ttinfo( 25200,   3600, 'TASST'),
        ttinfo( 21600,      0, 'TAST'),
        ttinfo( 25200,   3600, 'TASST'),
        ttinfo( 21600,      0, 'TAST'),
        ttinfo( 25200,   3600, 'TASST'),
        ttinfo( 21600,      0, 'TAST'),
        ttinfo( 25200,   3600, 'TASST'),
        ttinfo( 21600,      0, 'TAST'),
        ttinfo( 25200,   3600, 'TASST'),
        ttinfo( 21600,      0, 'TAST'),
        ttinfo( 25200,   3600, 'TASST'),
        ttinfo( 21600,      0, 'TAST'),
        ttinfo( 25200,   3600, 'TASST'),
        ttinfo( 21600,      0, 'TAST'),
        ttinfo( 25200,   3600, 'TASST'),
        ttinfo( 21600,      0, 'TAST'),
        ttinfo( 21600,      0, 'TASST'),
        ttinfo( 21600,      0, 'UZST'),
        ttinfo( 18000,      0,  'UZT'),
        ttinfo( 18000,      0,  'UZT'),
        ttinfo( 21600,   3600, 'UZST'),
        ttinfo( 18000,      0,  'UZT'),
        ]

Samarkand = Samarkand() # Singleton

