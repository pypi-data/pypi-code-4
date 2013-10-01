'''
tzinfo timezone information for Pacific/Yap.

Generated from the Olson timezone database:
    ftp://elsie.nci.nih.gov/pub/tz*.tar.gz
'''

from pytz.tzinfo import DstTzInfo
from pytz.tzinfo import memorized_datetime as datetime
from pytz.tzinfo import memorized_ttinfo as ttinfo

class Yap(DstTzInfo):
    '''Pacific/Yap timezone definition. See datetime.tzinfo for details'''

    _zone = 'Pacific/Yap'

    _utc_transition_times = [
        datetime(   1,  1,  1,  0,  0,  0), #  32400     0 YAPT
        datetime(1969,  9, 30, 15,  0,  0), #  36000     0 YAPT
        ]

    _transition_info = [
        ttinfo( 32400,      0, 'YAPT'),
        ttinfo( 36000,      0, 'YAPT'),
        ]

Yap = Yap() # Singleton

