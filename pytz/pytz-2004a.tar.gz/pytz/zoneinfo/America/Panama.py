'''
tzinfo timezone information for America/Panama.

Generated from the Olson timezone database:
    ftp://elsie.nci.nih.gov/pub/tz*.tar.gz
'''

from pytz.tzinfo import DstTzInfo
from pytz.tzinfo import memorized_datetime as datetime
from pytz.tzinfo import memorized_ttinfo as ttinfo

class Panama(DstTzInfo):
    '''America/Panama timezone definition. See datetime.tzinfo for details'''

    _zone = 'America/Panama'

    _utc_transition_times = [
        datetime(   1,  1,  1,  0,  0,  0), # -19176     0 CMT
        datetime(1908,  4, 22,  5, 19, 36), # -18000     0 EST
        ]

    _transition_info = [
        ttinfo(-19176,      0,  'CMT'),
        ttinfo(-18000,      0,  'EST'),
        ]

Panama = Panama() # Singleton

