'''
tzinfo timezone information for Africa/Timbuktu.

Generated from the Olson timezone database:
    ftp://elsie.nci.nih.gov/pub/tz*.tar.gz
'''

from pytz.tzinfo import DstTzInfo
from pytz.tzinfo import memorized_datetime as datetime
from pytz.tzinfo import memorized_ttinfo as ttinfo

class Timbuktu(DstTzInfo):
    '''Africa/Timbuktu timezone definition. See datetime.tzinfo for details'''

    _zone = 'Africa/Timbuktu'

    _utc_transition_times = [
        datetime(   1,  1,  1,  0,  0,  0), #   -724     0 LMT
        datetime(1912,  1,  1,  0, 12,  4), #      0     0 GMT
        ]

    _transition_info = [
        ttinfo(  -724,      0,  'LMT'),
        ttinfo(     0,      0,  'GMT'),
        ]

Timbuktu = Timbuktu() # Singleton

