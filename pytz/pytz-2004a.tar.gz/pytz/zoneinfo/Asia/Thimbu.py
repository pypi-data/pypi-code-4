'''
tzinfo timezone information for Asia/Thimbu.

Generated from the Olson timezone database:
    ftp://elsie.nci.nih.gov/pub/tz*.tar.gz
'''

from pytz.tzinfo import DstTzInfo
from pytz.tzinfo import memorized_datetime as datetime
from pytz.tzinfo import memorized_ttinfo as ttinfo

class Thimbu(DstTzInfo):
    '''Asia/Thimbu timezone definition. See datetime.tzinfo for details'''

    _zone = 'Asia/Thimbu'

    _utc_transition_times = [
        datetime(   1,  1,  1,  0,  0,  0), #  21516     0 LMT
        datetime(1947,  8, 14, 18,  1, 24), #  19800     0 IST
        datetime(1987,  9, 30, 18, 30,  0), #  21600     0 BTT
        ]

    _transition_info = [
        ttinfo( 21516,      0,  'LMT'),
        ttinfo( 19800,      0,  'IST'),
        ttinfo( 21600,      0,  'BTT'),
        ]

Thimbu = Thimbu() # Singleton

