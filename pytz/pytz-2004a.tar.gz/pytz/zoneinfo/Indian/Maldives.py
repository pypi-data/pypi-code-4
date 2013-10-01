'''
tzinfo timezone information for Indian/Maldives.

Generated from the Olson timezone database:
    ftp://elsie.nci.nih.gov/pub/tz*.tar.gz
'''

from pytz.tzinfo import DstTzInfo
from pytz.tzinfo import memorized_datetime as datetime
from pytz.tzinfo import memorized_ttinfo as ttinfo

class Maldives(DstTzInfo):
    '''Indian/Maldives timezone definition. See datetime.tzinfo for details'''

    _zone = 'Indian/Maldives'

    _utc_transition_times = [
        datetime(   1,  1,  1,  0,  0,  0), #  17640     0 MMT
        datetime(1959, 12, 31, 19,  6,  0), #  18000     0 MVT
        ]

    _transition_info = [
        ttinfo( 17640,      0,  'MMT'),
        ttinfo( 18000,      0,  'MVT'),
        ]

Maldives = Maldives() # Singleton

