'''
tzinfo timezone information for Africa/Addis_Ababa.

Generated from the Olson timezone database:
    ftp://elsie.nci.nih.gov/pub/tz*.tar.gz
'''

from pytz.tzinfo import DstTzInfo
from pytz.tzinfo import memorized_datetime as datetime
from pytz.tzinfo import memorized_ttinfo as ttinfo

class Addis_Ababa(DstTzInfo):
    '''Africa/Addis_Ababa timezone definition. See datetime.tzinfo for details'''

    _zone = 'Africa/Addis_Ababa'

    _utc_transition_times = [
        datetime(   1,  1,  1,  0,  0,  0), #   9320     0 ADMT
        datetime(1936,  5,  4, 21, 24, 40), #  10800     0 EAT
        ]

    _transition_info = [
        ttinfo(  9320,      0, 'ADMT'),
        ttinfo( 10800,      0,  'EAT'),
        ]

Addis_Ababa = Addis_Ababa() # Singleton

