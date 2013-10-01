'''
tzinfo timezone information for Africa/Ndjamena.

Generated from the Olson timezone database:
    ftp://elsie.nci.nih.gov/pub/tz*.tar.gz
'''

from pytz.tzinfo import DstTzInfo
from pytz.tzinfo import memorized_datetime as datetime
from pytz.tzinfo import memorized_ttinfo as ttinfo

class Ndjamena(DstTzInfo):
    '''Africa/Ndjamena timezone definition. See datetime.tzinfo for details'''

    _zone = 'Africa/Ndjamena'

    _utc_transition_times = [
        datetime(   1,  1,  1,  0,  0,  0), #   3612     0 LMT
        datetime(1911, 12, 31, 22, 59, 48), #   3600     0 WAT
        datetime(1979, 10, 13, 23,  0,  0), #   7200  3600 WAST
        datetime(1980,  3,  7, 22,  0,  0), #   3600     0 WAT
        ]

    _transition_info = [
        ttinfo(  3612,      0,  'LMT'),
        ttinfo(  3600,      0,  'WAT'),
        ttinfo(  7200,   3600, 'WAST'),
        ttinfo(  3600,      0,  'WAT'),
        ]

Ndjamena = Ndjamena() # Singleton

