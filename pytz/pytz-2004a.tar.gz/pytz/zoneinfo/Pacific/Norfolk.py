'''
tzinfo timezone information for Pacific/Norfolk.

Generated from the Olson timezone database:
    ftp://elsie.nci.nih.gov/pub/tz*.tar.gz
'''

from pytz.tzinfo import DstTzInfo
from pytz.tzinfo import memorized_datetime as datetime
from pytz.tzinfo import memorized_ttinfo as ttinfo

class Norfolk(DstTzInfo):
    '''Pacific/Norfolk timezone definition. See datetime.tzinfo for details'''

    _zone = 'Pacific/Norfolk'

    _utc_transition_times = [
        datetime(   1,  1,  1,  0,  0,  0), #  40320     0 NMT
        datetime(1950, 12, 31, 12, 48,  0), #  41400     0 NFT
        ]

    _transition_info = [
        ttinfo( 40320,      0,  'NMT'),
        ttinfo( 41400,      0,  'NFT'),
        ]

Norfolk = Norfolk() # Singleton

