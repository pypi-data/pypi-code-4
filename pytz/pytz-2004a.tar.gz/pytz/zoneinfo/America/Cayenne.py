'''
tzinfo timezone information for America/Cayenne.

Generated from the Olson timezone database:
    ftp://elsie.nci.nih.gov/pub/tz*.tar.gz
'''

from pytz.tzinfo import DstTzInfo
from pytz.tzinfo import memorized_datetime as datetime
from pytz.tzinfo import memorized_ttinfo as ttinfo

class Cayenne(DstTzInfo):
    '''America/Cayenne timezone definition. See datetime.tzinfo for details'''

    _zone = 'America/Cayenne'

    _utc_transition_times = [
        datetime(   1,  1,  1,  0,  0,  0), # -12560     0 LMT
        datetime(1911,  7,  1,  3, 29, 20), # -14400     0 GFT
        datetime(1967, 10,  1,  4,  0,  0), # -10800     0 GFT
        ]

    _transition_info = [
        ttinfo(-12560,      0,  'LMT'),
        ttinfo(-14400,      0,  'GFT'),
        ttinfo(-10800,      0,  'GFT'),
        ]

Cayenne = Cayenne() # Singleton

