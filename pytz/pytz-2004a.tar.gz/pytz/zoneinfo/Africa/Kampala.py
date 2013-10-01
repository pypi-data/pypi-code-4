'''
tzinfo timezone information for Africa/Kampala.

Generated from the Olson timezone database:
    ftp://elsie.nci.nih.gov/pub/tz*.tar.gz
'''

from pytz.tzinfo import DstTzInfo
from pytz.tzinfo import memorized_datetime as datetime
from pytz.tzinfo import memorized_ttinfo as ttinfo

class Kampala(DstTzInfo):
    '''Africa/Kampala timezone definition. See datetime.tzinfo for details'''

    _zone = 'Africa/Kampala'

    _utc_transition_times = [
        datetime(   1,  1,  1,  0,  0,  0), #   7780     0 LMT
        datetime(1928,  6, 30, 21, 50, 20), #  10800     0 EAT
        datetime(1929, 12, 31, 21,  0,  0), #   9000     0 BEAT
        datetime(1947, 12, 31, 21, 30,  0), #   9885     0 BEAUT
        datetime(1956, 12, 31, 21, 15, 15), #  10800     0 EAT
        ]

    _transition_info = [
        ttinfo(  7780,      0,  'LMT'),
        ttinfo( 10800,      0,  'EAT'),
        ttinfo(  9000,      0, 'BEAT'),
        ttinfo(  9885,      0, 'BEAUT'),
        ttinfo( 10800,      0,  'EAT'),
        ]

Kampala = Kampala() # Singleton

