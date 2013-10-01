'''
tzinfo timezone information for Asia/Jakarta.

Generated from the Olson timezone database:
    ftp://elsie.nci.nih.gov/pub/tz*.tar.gz
'''

from pytz.tzinfo import DstTzInfo
from pytz.tzinfo import memorized_datetime as datetime
from pytz.tzinfo import memorized_ttinfo as ttinfo

class Jakarta(DstTzInfo):
    '''Asia/Jakarta timezone definition. See datetime.tzinfo for details'''

    _zone = 'Asia/Jakarta'

    _utc_transition_times = [
        datetime(   1,  1,  1,  0,  0,  0), #  25632     0 JMT
        datetime(1923, 12, 31, 16, 40,  0), #  26400     0 JAVT
        datetime(1932, 10, 31, 16, 40,  0), #  27000     0 WIT
        datetime(1942,  3, 22, 16, 30,  0), #  32400     0 JST
        datetime(1945,  7, 31, 15,  0,  0), #  27000     0 WIT
        datetime(1948,  4, 30, 16, 30,  0), #  28800     0 WIT
        datetime(1950,  4, 30, 16,  0,  0), #  27000     0 WIT
        datetime(1963, 12, 31, 16, 30,  0), #  25200     0 WIT
        ]

    _transition_info = [
        ttinfo( 25632,      0,  'JMT'),
        ttinfo( 26400,      0, 'JAVT'),
        ttinfo( 27000,      0,  'WIT'),
        ttinfo( 32400,      0,  'JST'),
        ttinfo( 27000,      0,  'WIT'),
        ttinfo( 28800,      0,  'WIT'),
        ttinfo( 27000,      0,  'WIT'),
        ttinfo( 25200,      0,  'WIT'),
        ]

Jakarta = Jakarta() # Singleton

