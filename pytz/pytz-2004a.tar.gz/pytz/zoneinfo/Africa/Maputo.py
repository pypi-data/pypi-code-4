'''
tzinfo timezone information for Africa/Maputo.

Generated from the Olson timezone database:
    ftp://elsie.nci.nih.gov/pub/tz*.tar.gz
'''

from pytz.tzinfo import DstTzInfo
from pytz.tzinfo import memorized_datetime as datetime
from pytz.tzinfo import memorized_ttinfo as ttinfo

class Maputo(DstTzInfo):
    '''Africa/Maputo timezone definition. See datetime.tzinfo for details'''

    _zone = 'Africa/Maputo'

    _utc_transition_times = [
        datetime(   1,  1,  1,  0,  0,  0), #   7820     0 LMT
        datetime(1903,  2, 28, 21, 49, 40), #   7200     0 CAT
        ]

    _transition_info = [
        ttinfo(  7820,      0,  'LMT'),
        ttinfo(  7200,      0,  'CAT'),
        ]

Maputo = Maputo() # Singleton

