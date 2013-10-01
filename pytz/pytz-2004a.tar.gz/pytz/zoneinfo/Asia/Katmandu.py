'''
tzinfo timezone information for Asia/Katmandu.

Generated from the Olson timezone database:
    ftp://elsie.nci.nih.gov/pub/tz*.tar.gz
'''

from pytz.tzinfo import DstTzInfo
from pytz.tzinfo import memorized_datetime as datetime
from pytz.tzinfo import memorized_ttinfo as ttinfo

class Katmandu(DstTzInfo):
    '''Asia/Katmandu timezone definition. See datetime.tzinfo for details'''

    _zone = 'Asia/Katmandu'

    _utc_transition_times = [
        datetime(   1,  1,  1,  0,  0,  0), #  20476     0 LMT
        datetime(1919, 12, 31, 18, 18, 44), #  19800     0 IST
        datetime(1985, 12, 31, 18, 30,  0), #  20700     0 NPT
        ]

    _transition_info = [
        ttinfo( 20476,      0,  'LMT'),
        ttinfo( 19800,      0,  'IST'),
        ttinfo( 20700,      0,  'NPT'),
        ]

Katmandu = Katmandu() # Singleton

