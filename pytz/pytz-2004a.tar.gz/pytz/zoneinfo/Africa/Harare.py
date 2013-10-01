'''
tzinfo timezone information for Africa/Harare.

Generated from the Olson timezone database:
    ftp://elsie.nci.nih.gov/pub/tz*.tar.gz
'''

from pytz.tzinfo import DstTzInfo
from pytz.tzinfo import memorized_datetime as datetime
from pytz.tzinfo import memorized_ttinfo as ttinfo

class Harare(DstTzInfo):
    '''Africa/Harare timezone definition. See datetime.tzinfo for details'''

    _zone = 'Africa/Harare'

    _utc_transition_times = [
        datetime(   1,  1,  1,  0,  0,  0), #   7452     0 LMT
        datetime(1903,  2, 28, 21, 55, 48), #   7200     0 CAT
        ]

    _transition_info = [
        ttinfo(  7452,      0,  'LMT'),
        ttinfo(  7200,      0,  'CAT'),
        ]

Harare = Harare() # Singleton

