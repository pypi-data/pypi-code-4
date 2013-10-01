'''
tzinfo timezone information for Indian/Kerguelen.

Generated from the Olson timezone database:
    ftp://elsie.nci.nih.gov/pub/tz*.tar.gz
'''

from pytz.tzinfo import DstTzInfo
from pytz.tzinfo import memorized_datetime as datetime
from pytz.tzinfo import memorized_ttinfo as ttinfo

class Kerguelen(DstTzInfo):
    '''Indian/Kerguelen timezone definition. See datetime.tzinfo for details'''

    _zone = 'Indian/Kerguelen'

    _utc_transition_times = [
        datetime(   1,  1,  1,  0,  0,  0), #      0     0 zzz
        datetime(1950,  1,  1,  0,  0,  0), #  18000     0 TFT
        ]

    _transition_info = [
        ttinfo(     0,      0,  'zzz'),
        ttinfo( 18000,      0,  'TFT'),
        ]

Kerguelen = Kerguelen() # Singleton

