'''
tzinfo timezone information for Africa/Asmera.

Generated from the Olson timezone database:
    ftp://elsie.nci.nih.gov/pub/tz*.tar.gz
'''

from pytz.tzinfo import DstTzInfo
from pytz.tzinfo import memorized_datetime as datetime
from pytz.tzinfo import memorized_ttinfo as ttinfo

class Asmera(DstTzInfo):
    '''Africa/Asmera timezone definition. See datetime.tzinfo for details'''

    _zone = 'Africa/Asmera'

    _utc_transition_times = [
        datetime(   1,  1,  1,  0,  0,  0), #   9320     0 ADMT
        datetime(1936,  5,  4, 21, 24, 40), #  10800     0 EAT
        ]

    _transition_info = [
        ttinfo(  9320,      0, 'ADMT'),
        ttinfo( 10800,      0,  'EAT'),
        ]

Asmera = Asmera() # Singleton

