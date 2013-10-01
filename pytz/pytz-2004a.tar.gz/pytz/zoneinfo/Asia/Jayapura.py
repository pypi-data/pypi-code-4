'''
tzinfo timezone information for Asia/Jayapura.

Generated from the Olson timezone database:
    ftp://elsie.nci.nih.gov/pub/tz*.tar.gz
'''

from pytz.tzinfo import DstTzInfo
from pytz.tzinfo import memorized_datetime as datetime
from pytz.tzinfo import memorized_ttinfo as ttinfo

class Jayapura(DstTzInfo):
    '''Asia/Jayapura timezone definition. See datetime.tzinfo for details'''

    _zone = 'Asia/Jayapura'

    _utc_transition_times = [
        datetime(   1,  1,  1,  0,  0,  0), #  33768     0 LMT
        datetime(1932, 10, 31, 14, 37, 12), #  32400     0 EIT
        datetime(1943, 12, 31, 15,  0,  0), #  34200     0 CST
        datetime(1963, 12, 31, 14, 30,  0), #  32400     0 EIT
        ]

    _transition_info = [
        ttinfo( 33768,      0,  'LMT'),
        ttinfo( 32400,      0,  'EIT'),
        ttinfo( 34200,      0,  'CST'),
        ttinfo( 32400,      0,  'EIT'),
        ]

Jayapura = Jayapura() # Singleton

