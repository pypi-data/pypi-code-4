'''
tzinfo timezone information for Africa/Mbabane.

Generated from the Olson timezone database:
    ftp://elsie.nci.nih.gov/pub/tz*.tar.gz
'''

from pytz.tzinfo import DstTzInfo
from pytz.tzinfo import memorized_datetime as datetime
from pytz.tzinfo import memorized_ttinfo as ttinfo

class Mbabane(DstTzInfo):
    '''Africa/Mbabane timezone definition. See datetime.tzinfo for details'''

    _zone = 'Africa/Mbabane'

    _utc_transition_times = [
        datetime(   1,  1,  1,  0,  0,  0), #   7464     0 LMT
        datetime(1903,  2, 28, 21, 55, 36), #   7200     0 SAST
        ]

    _transition_info = [
        ttinfo(  7464,      0,  'LMT'),
        ttinfo(  7200,      0, 'SAST'),
        ]

Mbabane = Mbabane() # Singleton

