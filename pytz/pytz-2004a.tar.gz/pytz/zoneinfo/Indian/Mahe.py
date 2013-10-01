'''
tzinfo timezone information for Indian/Mahe.

Generated from the Olson timezone database:
    ftp://elsie.nci.nih.gov/pub/tz*.tar.gz
'''

from pytz.tzinfo import DstTzInfo
from pytz.tzinfo import memorized_datetime as datetime
from pytz.tzinfo import memorized_ttinfo as ttinfo

class Mahe(DstTzInfo):
    '''Indian/Mahe timezone definition. See datetime.tzinfo for details'''

    _zone = 'Indian/Mahe'

    _utc_transition_times = [
        datetime(   1,  1,  1,  0,  0,  0), #  13308     0 LMT
        datetime(1906,  5, 31, 20, 18, 12), #  14400     0 SCT
        ]

    _transition_info = [
        ttinfo( 13308,      0,  'LMT'),
        ttinfo( 14400,      0,  'SCT'),
        ]

Mahe = Mahe() # Singleton

