'''
tzinfo timezone information for Africa/Gaborone.

Generated from the Olson timezone database:
    ftp://elsie.nci.nih.gov/pub/tz*.tar.gz
'''

from pytz.tzinfo import DstTzInfo
from pytz.tzinfo import memorized_datetime as datetime
from pytz.tzinfo import memorized_ttinfo as ttinfo

class Gaborone(DstTzInfo):
    '''Africa/Gaborone timezone definition. See datetime.tzinfo for details'''

    _zone = 'Africa/Gaborone'

    _utc_transition_times = [
        datetime(   1,  1,  1,  0,  0,  0), #   7200     0 CAT
        datetime(1943,  9, 19,  0,  0,  0), #  10800  3600 CAST
        datetime(1944,  3, 18, 23,  0,  0), #   7200     0 CAT
        ]

    _transition_info = [
        ttinfo(  7200,      0,  'CAT'),
        ttinfo( 10800,   3600, 'CAST'),
        ttinfo(  7200,      0,  'CAT'),
        ]

Gaborone = Gaborone() # Singleton

