'''
tzinfo timezone information for Asia/Macao.

Generated from the Olson timezone database:
    ftp://elsie.nci.nih.gov/pub/tz*.tar.gz
'''

from pytz.tzinfo import DstTzInfo
from pytz.tzinfo import memorized_datetime as datetime
from pytz.tzinfo import memorized_ttinfo as ttinfo

class Macao(DstTzInfo):
    '''Asia/Macao timezone definition. See datetime.tzinfo for details'''

    _zone = 'Asia/Macao'

    _utc_transition_times = [
        datetime(   1,  1,  1,  0,  0,  0), #  27260     0 LMT
        datetime(1911, 12, 31, 16, 25, 40), #  28800     0 MOT
        datetime(1961,  3, 18, 19, 30,  0), #  32400  3600 MOST
        datetime(1961, 11,  4, 18, 30,  0), #  28800     0 MOT
        datetime(1962,  3, 17, 19, 30,  0), #  32400  3600 MOST
        datetime(1962, 11,  3, 18, 30,  0), #  28800     0 MOT
        datetime(1963,  3, 16, 16,  0,  0), #  32400  3600 MOST
        datetime(1963, 11,  2, 18, 30,  0), #  28800     0 MOT
        datetime(1964,  3, 21, 19, 30,  0), #  32400  3600 MOST
        datetime(1964, 10, 31, 18, 30,  0), #  28800     0 MOT
        datetime(1965,  3, 20, 16,  0,  0), #  32400  3600 MOST
        datetime(1965, 10, 30, 15,  0,  0), #  28800     0 MOT
        datetime(1966,  4, 16, 19, 30,  0), #  32400  3600 MOST
        datetime(1966, 10, 15, 18, 30,  0), #  28800     0 MOT
        datetime(1967,  4, 15, 19, 30,  0), #  32400  3600 MOST
        datetime(1967, 10, 21, 18, 30,  0), #  28800     0 MOT
        datetime(1968,  4, 20, 19, 30,  0), #  32400  3600 MOST
        datetime(1968, 10, 19, 18, 30,  0), #  28800     0 MOT
        datetime(1969,  4, 19, 19, 30,  0), #  32400  3600 MOST
        datetime(1969, 10, 18, 18, 30,  0), #  28800     0 MOT
        datetime(1970,  4, 18, 19, 30,  0), #  32400  3600 MOST
        datetime(1970, 10, 17, 18, 30,  0), #  28800     0 MOT
        datetime(1971,  4, 17, 19, 30,  0), #  32400  3600 MOST
        datetime(1971, 10, 16, 18, 30,  0), #  28800     0 MOT
        datetime(1972,  4, 15, 16,  0,  0), #  32400  3600 MOST
        datetime(1972, 10, 14, 15,  0,  0), #  28800     0 MOT
        datetime(1973,  4, 14, 16,  0,  0), #  32400  3600 MOST
        datetime(1973, 10, 20, 15,  0,  0), #  28800     0 MOT
        datetime(1974,  4, 20, 16,  0,  0), #  32400  3600 MOST
        datetime(1974, 10, 19, 18, 30,  0), #  28800     0 MOT
        datetime(1975,  4, 19, 19, 30,  0), #  32400  3600 MOST
        datetime(1975, 10, 18, 18, 30,  0), #  28800     0 MOT
        datetime(1976,  4, 17, 19, 30,  0), #  32400  3600 MOST
        datetime(1976, 10, 16, 18, 30,  0), #  28800     0 MOT
        datetime(1977,  4, 16, 19, 30,  0), #  32400  3600 MOST
        datetime(1977, 10, 15, 18, 30,  0), #  28800     0 MOT
        datetime(1978,  4, 15, 16,  0,  0), #  32400  3600 MOST
        datetime(1978, 10, 14, 15,  0,  0), #  28800     0 MOT
        datetime(1979,  4, 14, 16,  0,  0), #  32400  3600 MOST
        datetime(1979, 10, 20, 15,  0,  0), #  28800     0 MOT
        datetime(1980,  4, 19, 16,  0,  0), #  32400  3600 MOST
        datetime(1980, 10, 18, 15,  0,  0), #  28800     0 MOT
        datetime(1999, 12, 19, 16,  0,  0), #  28800     0 CST
        ]

    _transition_info = [
        ttinfo( 27260,      0,  'LMT'),
        ttinfo( 28800,      0,  'MOT'),
        ttinfo( 32400,   3600, 'MOST'),
        ttinfo( 28800,      0,  'MOT'),
        ttinfo( 32400,   3600, 'MOST'),
        ttinfo( 28800,      0,  'MOT'),
        ttinfo( 32400,   3600, 'MOST'),
        ttinfo( 28800,      0,  'MOT'),
        ttinfo( 32400,   3600, 'MOST'),
        ttinfo( 28800,      0,  'MOT'),
        ttinfo( 32400,   3600, 'MOST'),
        ttinfo( 28800,      0,  'MOT'),
        ttinfo( 32400,   3600, 'MOST'),
        ttinfo( 28800,      0,  'MOT'),
        ttinfo( 32400,   3600, 'MOST'),
        ttinfo( 28800,      0,  'MOT'),
        ttinfo( 32400,   3600, 'MOST'),
        ttinfo( 28800,      0,  'MOT'),
        ttinfo( 32400,   3600, 'MOST'),
        ttinfo( 28800,      0,  'MOT'),
        ttinfo( 32400,   3600, 'MOST'),
        ttinfo( 28800,      0,  'MOT'),
        ttinfo( 32400,   3600, 'MOST'),
        ttinfo( 28800,      0,  'MOT'),
        ttinfo( 32400,   3600, 'MOST'),
        ttinfo( 28800,      0,  'MOT'),
        ttinfo( 32400,   3600, 'MOST'),
        ttinfo( 28800,      0,  'MOT'),
        ttinfo( 32400,   3600, 'MOST'),
        ttinfo( 28800,      0,  'MOT'),
        ttinfo( 32400,   3600, 'MOST'),
        ttinfo( 28800,      0,  'MOT'),
        ttinfo( 32400,   3600, 'MOST'),
        ttinfo( 28800,      0,  'MOT'),
        ttinfo( 32400,   3600, 'MOST'),
        ttinfo( 28800,      0,  'MOT'),
        ttinfo( 32400,   3600, 'MOST'),
        ttinfo( 28800,      0,  'MOT'),
        ttinfo( 32400,   3600, 'MOST'),
        ttinfo( 28800,      0,  'MOT'),
        ttinfo( 32400,   3600, 'MOST'),
        ttinfo( 28800,      0,  'MOT'),
        ttinfo( 28800,      0,  'CST'),
        ]

Macao = Macao() # Singleton

