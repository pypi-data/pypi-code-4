'''
tzinfo timezone information for Africa/Dar_es_Salaam.

Generated from the Olson timezone database:
    ftp://elsie.nci.nih.gov/pub/tz*.tar.gz
'''

from pytz.tzinfo import DstTzInfo
from pytz.tzinfo import memorized_datetime as datetime
from pytz.tzinfo import memorized_ttinfo as ttinfo

class Dar_es_Salaam(DstTzInfo):
    '''Africa/Dar_es_Salaam timezone definition. See datetime.tzinfo for details'''

    _zone = 'Africa/Dar_es_Salaam'

    _utc_transition_times = [
        datetime(   1,  1,  1,  0,  0,  0), #   9428     0 LMT
        datetime(1930, 12, 31, 21, 22, 52), #  10800     0 EAT
        datetime(1947, 12, 31, 21,  0,  0), #   9885     0 BEAUT
        datetime(1960, 12, 31, 21, 15, 15), #  10800     0 EAT
        ]

    _transition_info = [
        ttinfo(  9428,      0,  'LMT'),
        ttinfo( 10800,      0,  'EAT'),
        ttinfo(  9885,      0, 'BEAUT'),
        ttinfo( 10800,      0,  'EAT'),
        ]

Dar_es_Salaam = Dar_es_Salaam() # Singleton

