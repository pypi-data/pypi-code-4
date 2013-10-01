'''
tzinfo timezone information for Asia/Aden.

Generated from the Olson timezone database:
    ftp://elsie.nci.nih.gov/pub/tz*.tar.gz
'''

from pytz.tzinfo import DstTzInfo
from pytz.tzinfo import memorized_datetime as datetime
from pytz.tzinfo import memorized_ttinfo as ttinfo

class Aden(DstTzInfo):
    '''Asia/Aden timezone definition. See datetime.tzinfo for details'''

    _zone = 'Asia/Aden'

    _utc_transition_times = [
        datetime(   1,  1,  1,  0,  0,  0), #  10848     0 LMT
        datetime(1949, 12, 31, 20, 59, 12), #  10800     0 AST
        ]

    _transition_info = [
        ttinfo( 10848,      0,  'LMT'),
        ttinfo( 10800,      0,  'AST'),
        ]

Aden = Aden() # Singleton

