'''
tzinfo timezone information for Africa/Luanda.

Generated from the Olson timezone database:
    ftp://elsie.nci.nih.gov/pub/tz*.tar.gz
'''

from pytz.tzinfo import DstTzInfo
from pytz.tzinfo import memorized_datetime as datetime
from pytz.tzinfo import memorized_ttinfo as ttinfo

class Luanda(DstTzInfo):
    '''Africa/Luanda timezone definition. See datetime.tzinfo for details'''

    _zone = 'Africa/Luanda'

    _utc_transition_times = [
        datetime(   1,  1,  1,  0,  0,  0), #   3124     0 AOT
        datetime(1911,  5, 25, 23,  7, 56), #   3600     0 WAT
        ]

    _transition_info = [
        ttinfo(  3124,      0,  'AOT'),
        ttinfo(  3600,      0,  'WAT'),
        ]

Luanda = Luanda() # Singleton

