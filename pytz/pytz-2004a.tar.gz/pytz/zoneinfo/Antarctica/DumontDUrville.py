'''
tzinfo timezone information for Antarctica/DumontDUrville.

Generated from the Olson timezone database:
    ftp://elsie.nci.nih.gov/pub/tz*.tar.gz
'''

from pytz.tzinfo import DstTzInfo
from pytz.tzinfo import memorized_datetime as datetime
from pytz.tzinfo import memorized_ttinfo as ttinfo

class DumontDUrville(DstTzInfo):
    '''Antarctica/DumontDUrville timezone definition. See datetime.tzinfo for details'''

    _zone = 'Antarctica/DumontDUrville'

    _utc_transition_times = [
        datetime(   1,  1,  1,  0,  0,  0), #      0     0 zzz
        datetime(1947,  1,  1,  0,  0,  0), #  36000     0 PMT
        datetime(1952,  1, 13, 14,  0,  0), #      0     0 zzz
        datetime(1956, 11,  1,  0,  0,  0), #  36000     0 DDUT
        ]

    _transition_info = [
        ttinfo(     0,      0,  'zzz'),
        ttinfo( 36000,      0,  'PMT'),
        ttinfo(     0,      0,  'zzz'),
        ttinfo( 36000,      0, 'DDUT'),
        ]

DumontDUrville = DumontDUrville() # Singleton

