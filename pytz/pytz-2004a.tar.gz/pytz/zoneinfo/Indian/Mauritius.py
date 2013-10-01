'''
tzinfo timezone information for Indian/Mauritius.

Generated from the Olson timezone database:
    ftp://elsie.nci.nih.gov/pub/tz*.tar.gz
'''

from pytz.tzinfo import DstTzInfo
from pytz.tzinfo import memorized_datetime as datetime
from pytz.tzinfo import memorized_ttinfo as ttinfo

class Mauritius(DstTzInfo):
    '''Indian/Mauritius timezone definition. See datetime.tzinfo for details'''

    _zone = 'Indian/Mauritius'

    _utc_transition_times = [
        datetime(   1,  1,  1,  0,  0,  0), #  13800     0 LMT
        datetime(1906, 12, 31, 20, 10,  0), #  14400     0 MUT
        ]

    _transition_info = [
        ttinfo( 13800,      0,  'LMT'),
        ttinfo( 14400,      0,  'MUT'),
        ]

Mauritius = Mauritius() # Singleton

