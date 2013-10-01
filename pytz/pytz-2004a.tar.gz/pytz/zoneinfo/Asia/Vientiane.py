'''
tzinfo timezone information for Asia/Vientiane.

Generated from the Olson timezone database:
    ftp://elsie.nci.nih.gov/pub/tz*.tar.gz
'''

from pytz.tzinfo import DstTzInfo
from pytz.tzinfo import memorized_datetime as datetime
from pytz.tzinfo import memorized_ttinfo as ttinfo

class Vientiane(DstTzInfo):
    '''Asia/Vientiane timezone definition. See datetime.tzinfo for details'''

    _zone = 'Asia/Vientiane'

    _utc_transition_times = [
        datetime(   1,  1,  1,  0,  0,  0), #  24624     0 LMT
        datetime(1906,  6,  8, 17,  9, 36), #  25580     0 SMT
        datetime(1911,  3, 10, 16, 54, 40), #  25200     0 ICT
        datetime(1912,  4, 30, 17,  0,  0), #  28800     0 ICT
        datetime(1931,  4, 30, 16,  0,  0), #  25200     0 ICT
        ]

    _transition_info = [
        ttinfo( 24624,      0,  'LMT'),
        ttinfo( 25580,      0,  'SMT'),
        ttinfo( 25200,      0,  'ICT'),
        ttinfo( 28800,      0,  'ICT'),
        ttinfo( 25200,      0,  'ICT'),
        ]

Vientiane = Vientiane() # Singleton

