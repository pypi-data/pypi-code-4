'''
tzinfo timezone information for Pacific/Kosrae.

Generated from the Olson timezone database:
    ftp://elsie.nci.nih.gov/pub/tz*.tar.gz
'''

from pytz.tzinfo import DstTzInfo
from pytz.tzinfo import memorized_datetime as datetime
from pytz.tzinfo import memorized_ttinfo as ttinfo

class Kosrae(DstTzInfo):
    '''Pacific/Kosrae timezone definition. See datetime.tzinfo for details'''

    _zone = 'Pacific/Kosrae'

    _utc_transition_times = [
        datetime(   1,  1,  1,  0,  0,  0), #  39600     0 KOST
        datetime(1969,  9, 30, 13,  0,  0), #  43200     0 KOST
        datetime(1998, 12, 31, 12,  0,  0), #  39600     0 KOST
        ]

    _transition_info = [
        ttinfo( 39600,      0, 'KOST'),
        ttinfo( 43200,      0, 'KOST'),
        ttinfo( 39600,      0, 'KOST'),
        ]

Kosrae = Kosrae() # Singleton

