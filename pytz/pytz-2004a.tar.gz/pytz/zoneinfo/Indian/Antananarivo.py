'''
tzinfo timezone information for Indian/Antananarivo.

Generated from the Olson timezone database:
    ftp://elsie.nci.nih.gov/pub/tz*.tar.gz
'''

from pytz.tzinfo import DstTzInfo
from pytz.tzinfo import memorized_datetime as datetime
from pytz.tzinfo import memorized_ttinfo as ttinfo

class Antananarivo(DstTzInfo):
    '''Indian/Antananarivo timezone definition. See datetime.tzinfo for details'''

    _zone = 'Indian/Antananarivo'

    _utc_transition_times = [
        datetime(   1,  1,  1,  0,  0,  0), #  11404     0 LMT
        datetime(1911,  6, 30, 20, 49, 56), #  10800     0 EAT
        datetime(1954,  2, 27, 20,  0,  0), #  14400  3600 EAST
        datetime(1954,  5, 29, 20,  0,  0), #  10800     0 EAT
        ]

    _transition_info = [
        ttinfo( 11404,      0,  'LMT'),
        ttinfo( 10800,      0,  'EAT'),
        ttinfo( 14400,   3600, 'EAST'),
        ttinfo( 10800,      0,  'EAT'),
        ]

Antananarivo = Antananarivo() # Singleton

