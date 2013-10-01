'''
tzinfo timezone information for Pacific/Saipan.

Generated from the Olson timezone database:
    ftp://elsie.nci.nih.gov/pub/tz*.tar.gz
'''

from pytz.tzinfo import DstTzInfo
from pytz.tzinfo import memorized_datetime as datetime
from pytz.tzinfo import memorized_ttinfo as ttinfo

class Saipan(DstTzInfo):
    '''Pacific/Saipan timezone definition. See datetime.tzinfo for details'''

    _zone = 'Pacific/Saipan'

    _utc_transition_times = [
        datetime(   1,  1,  1,  0,  0,  0), #  32400     0 MPT
        datetime(1969,  9, 30, 15,  0,  0), #  36000     0 MPT
        datetime(2000, 12, 22, 14,  0,  0), #  36000     0 ChST
        ]

    _transition_info = [
        ttinfo( 32400,      0,  'MPT'),
        ttinfo( 36000,      0,  'MPT'),
        ttinfo( 36000,      0, 'ChST'),
        ]

Saipan = Saipan() # Singleton

