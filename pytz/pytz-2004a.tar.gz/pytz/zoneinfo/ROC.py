'''
tzinfo timezone information for ROC.

Generated from the Olson timezone database:
    ftp://elsie.nci.nih.gov/pub/tz*.tar.gz
'''

from pytz.tzinfo import DstTzInfo
from pytz.tzinfo import memorized_datetime as datetime
from pytz.tzinfo import memorized_ttinfo as ttinfo

class ROC(DstTzInfo):
    '''ROC timezone definition. See datetime.tzinfo for details'''

    _zone = 'ROC'

    _utc_transition_times = [
        datetime(   1,  1,  1,  0,  0,  0), #  28800     0 CST
        datetime(1945,  4, 30, 16,  0,  0), #  32400  3600 CDT
        datetime(1945,  9, 30, 15,  0,  0), #  28800     0 CST
        datetime(1946,  4, 30, 16,  0,  0), #  32400  3600 CDT
        datetime(1946,  9, 30, 15,  0,  0), #  28800     0 CST
        datetime(1947,  4, 30, 16,  0,  0), #  32400  3600 CDT
        datetime(1947,  9, 30, 15,  0,  0), #  28800     0 CST
        datetime(1948,  4, 30, 16,  0,  0), #  32400  3600 CDT
        datetime(1948,  9, 30, 15,  0,  0), #  28800     0 CST
        datetime(1949,  4, 30, 16,  0,  0), #  32400  3600 CDT
        datetime(1949,  9, 30, 15,  0,  0), #  28800     0 CST
        datetime(1950,  4, 30, 16,  0,  0), #  32400  3600 CDT
        datetime(1950,  9, 30, 15,  0,  0), #  28800     0 CST
        datetime(1951,  4, 30, 16,  0,  0), #  32400  3600 CDT
        datetime(1951,  9, 30, 15,  0,  0), #  28800     0 CST
        datetime(1952,  2, 29, 16,  0,  0), #  32400  3600 CDT
        datetime(1952, 10, 31, 15,  0,  0), #  28800     0 CST
        datetime(1953,  3, 31, 16,  0,  0), #  32400  3600 CDT
        datetime(1953, 10, 31, 15,  0,  0), #  28800     0 CST
        datetime(1954,  3, 31, 16,  0,  0), #  32400  3600 CDT
        datetime(1954, 10, 31, 15,  0,  0), #  28800     0 CST
        datetime(1955,  3, 31, 16,  0,  0), #  32400  3600 CDT
        datetime(1955,  9, 30, 15,  0,  0), #  28800     0 CST
        datetime(1956,  3, 31, 16,  0,  0), #  32400  3600 CDT
        datetime(1956,  9, 30, 15,  0,  0), #  28800     0 CST
        datetime(1957,  3, 31, 16,  0,  0), #  32400  3600 CDT
        datetime(1957,  9, 30, 15,  0,  0), #  28800     0 CST
        datetime(1958,  3, 31, 16,  0,  0), #  32400  3600 CDT
        datetime(1958,  9, 30, 15,  0,  0), #  28800     0 CST
        datetime(1959,  3, 31, 16,  0,  0), #  32400  3600 CDT
        datetime(1959,  9, 30, 15,  0,  0), #  28800     0 CST
        datetime(1960,  5, 31, 16,  0,  0), #  32400  3600 CDT
        datetime(1960,  9, 30, 15,  0,  0), #  28800     0 CST
        datetime(1961,  5, 31, 16,  0,  0), #  32400  3600 CDT
        datetime(1961,  9, 30, 15,  0,  0), #  28800     0 CST
        datetime(1974,  3, 31, 16,  0,  0), #  32400  3600 CDT
        datetime(1974,  9, 30, 15,  0,  0), #  28800     0 CST
        datetime(1975,  3, 31, 16,  0,  0), #  32400  3600 CDT
        datetime(1975,  9, 30, 15,  0,  0), #  28800     0 CST
        datetime(1980,  6, 29, 16,  0,  0), #  32400  3600 CDT
        datetime(1980,  9, 29, 15,  0,  0), #  28800     0 CST
        ]

    _transition_info = [
        ttinfo( 28800,      0,  'CST'),
        ttinfo( 32400,   3600,  'CDT'),
        ttinfo( 28800,      0,  'CST'),
        ttinfo( 32400,   3600,  'CDT'),
        ttinfo( 28800,      0,  'CST'),
        ttinfo( 32400,   3600,  'CDT'),
        ttinfo( 28800,      0,  'CST'),
        ttinfo( 32400,   3600,  'CDT'),
        ttinfo( 28800,      0,  'CST'),
        ttinfo( 32400,   3600,  'CDT'),
        ttinfo( 28800,      0,  'CST'),
        ttinfo( 32400,   3600,  'CDT'),
        ttinfo( 28800,      0,  'CST'),
        ttinfo( 32400,   3600,  'CDT'),
        ttinfo( 28800,      0,  'CST'),
        ttinfo( 32400,   3600,  'CDT'),
        ttinfo( 28800,      0,  'CST'),
        ttinfo( 32400,   3600,  'CDT'),
        ttinfo( 28800,      0,  'CST'),
        ttinfo( 32400,   3600,  'CDT'),
        ttinfo( 28800,      0,  'CST'),
        ttinfo( 32400,   3600,  'CDT'),
        ttinfo( 28800,      0,  'CST'),
        ttinfo( 32400,   3600,  'CDT'),
        ttinfo( 28800,      0,  'CST'),
        ttinfo( 32400,   3600,  'CDT'),
        ttinfo( 28800,      0,  'CST'),
        ttinfo( 32400,   3600,  'CDT'),
        ttinfo( 28800,      0,  'CST'),
        ttinfo( 32400,   3600,  'CDT'),
        ttinfo( 28800,      0,  'CST'),
        ttinfo( 32400,   3600,  'CDT'),
        ttinfo( 28800,      0,  'CST'),
        ttinfo( 32400,   3600,  'CDT'),
        ttinfo( 28800,      0,  'CST'),
        ttinfo( 32400,   3600,  'CDT'),
        ttinfo( 28800,      0,  'CST'),
        ttinfo( 32400,   3600,  'CDT'),
        ttinfo( 28800,      0,  'CST'),
        ttinfo( 32400,   3600,  'CDT'),
        ttinfo( 28800,      0,  'CST'),
        ]

ROC = ROC() # Singleton

