'''
tzinfo timezone information for Antarctica/Mawson.

Generated from the Olson timezone database:
    ftp://elsie.nci.nih.gov/pub/tz*.tar.gz
'''

from pytz.tzinfo import DstTzInfo
from pytz.tzinfo import memorized_datetime as datetime
from pytz.tzinfo import memorized_ttinfo as ttinfo

class Mawson(DstTzInfo):
    '''Antarctica/Mawson timezone definition. See datetime.tzinfo for details'''

    _zone = 'Antarctica/Mawson'

    _utc_transition_times = [
        datetime(   1,  1,  1,  0,  0,  0), #      0     0 zzz
        datetime(1954,  2, 13,  0,  0,  0), #  21600     0 MAWT
        ]

    _transition_info = [
        ttinfo(     0,      0,  'zzz'),
        ttinfo( 21600,      0, 'MAWT'),
        ]

Mawson = Mawson() # Singleton

