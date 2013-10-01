'''
tzinfo timezone information for Africa/Niamey.

Generated from the Olson timezone database:
    ftp://elsie.nci.nih.gov/pub/tz*.tar.gz
'''

from pytz.tzinfo import DstTzInfo
from pytz.tzinfo import memorized_datetime as datetime
from pytz.tzinfo import memorized_ttinfo as ttinfo

class Niamey(DstTzInfo):
    '''Africa/Niamey timezone definition. See datetime.tzinfo for details'''

    _zone = 'Africa/Niamey'

    _utc_transition_times = [
        datetime(   1,  1,  1,  0,  0,  0), #    508     0 LMT
        datetime(1911, 12, 31, 23, 51, 32), #  -3600     0 WAT
        datetime(1934,  2, 26,  1,  0,  0), #      0     0 GMT
        datetime(1960,  1,  1,  0,  0,  0), #   3600     0 WAT
        ]

    _transition_info = [
        ttinfo(   508,      0,  'LMT'),
        ttinfo( -3600,      0,  'WAT'),
        ttinfo(     0,      0,  'GMT'),
        ttinfo(  3600,      0,  'WAT'),
        ]

Niamey = Niamey() # Singleton

