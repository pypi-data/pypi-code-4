'''
tzinfo timezone information for Asia/Riyadh.

Generated from the Olson timezone database:
    ftp://elsie.nci.nih.gov/pub/tz*.tar.gz
'''

from pytz.tzinfo import DstTzInfo
from pytz.tzinfo import memorized_datetime as datetime
from pytz.tzinfo import memorized_ttinfo as ttinfo

class Riyadh(DstTzInfo):
    '''Asia/Riyadh timezone definition. See datetime.tzinfo for details'''

    _zone = 'Asia/Riyadh'

    _utc_transition_times = [
        datetime(   1,  1,  1,  0,  0,  0), #  11212     0 LMT
        datetime(1949, 12, 31, 20, 53,  8), #  10800     0 AST
        ]

    _transition_info = [
        ttinfo( 11212,      0,  'LMT'),
        ttinfo( 10800,      0,  'AST'),
        ]

Riyadh = Riyadh() # Singleton

