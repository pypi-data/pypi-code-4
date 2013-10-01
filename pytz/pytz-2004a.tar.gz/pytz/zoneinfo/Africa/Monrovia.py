'''
tzinfo timezone information for Africa/Monrovia.

Generated from the Olson timezone database:
    ftp://elsie.nci.nih.gov/pub/tz*.tar.gz
'''

from pytz.tzinfo import DstTzInfo
from pytz.tzinfo import memorized_datetime as datetime
from pytz.tzinfo import memorized_ttinfo as ttinfo

class Monrovia(DstTzInfo):
    '''Africa/Monrovia timezone definition. See datetime.tzinfo for details'''

    _zone = 'Africa/Monrovia'

    _utc_transition_times = [
        datetime(   1,  1,  1,  0,  0,  0), #  -2588     0 MMT
        datetime(1919,  3,  1,  0, 43,  8), #  -2670     0 LRT
        datetime(1972,  5,  1,  0, 44, 30), #      0     0 GMT
        ]

    _transition_info = [
        ttinfo( -2588,      0,  'MMT'),
        ttinfo( -2670,      0,  'LRT'),
        ttinfo(     0,      0,  'GMT'),
        ]

Monrovia = Monrovia() # Singleton

