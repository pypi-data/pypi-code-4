'''
tzinfo timezone information for Asia/Kabul.

Generated from the Olson timezone database:
    ftp://elsie.nci.nih.gov/pub/tz*.tar.gz
'''

from pytz.tzinfo import DstTzInfo
from pytz.tzinfo import memorized_datetime as datetime
from pytz.tzinfo import memorized_ttinfo as ttinfo

class Kabul(DstTzInfo):
    '''Asia/Kabul timezone definition. See datetime.tzinfo for details'''

    _zone = 'Asia/Kabul'

    _utc_transition_times = [
        datetime(   1,  1,  1,  0,  0,  0), #  14400     0 AFT
        datetime(1944, 12, 31, 20,  0,  0), #  16200     0 AFT
        ]

    _transition_info = [
        ttinfo( 14400,      0,  'AFT'),
        ttinfo( 16200,      0,  'AFT'),
        ]

Kabul = Kabul() # Singleton

