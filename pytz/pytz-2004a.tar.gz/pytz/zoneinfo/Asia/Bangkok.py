'''
tzinfo timezone information for Asia/Bangkok.

Generated from the Olson timezone database:
    ftp://elsie.nci.nih.gov/pub/tz*.tar.gz
'''

from pytz.tzinfo import DstTzInfo
from pytz.tzinfo import memorized_datetime as datetime
from pytz.tzinfo import memorized_ttinfo as ttinfo

class Bangkok(DstTzInfo):
    '''Asia/Bangkok timezone definition. See datetime.tzinfo for details'''

    _zone = 'Asia/Bangkok'

    _utc_transition_times = [
        datetime(   1,  1,  1,  0,  0,  0), #  24124     0 BMT
        datetime(1920,  3, 31, 17, 17, 56), #  25200     0 ICT
        ]

    _transition_info = [
        ttinfo( 24124,      0,  'BMT'),
        ttinfo( 25200,      0,  'ICT'),
        ]

Bangkok = Bangkok() # Singleton

