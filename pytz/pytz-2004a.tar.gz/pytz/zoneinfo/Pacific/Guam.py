'''
tzinfo timezone information for Pacific/Guam.

Generated from the Olson timezone database:
    ftp://elsie.nci.nih.gov/pub/tz*.tar.gz
'''

from pytz.tzinfo import DstTzInfo
from pytz.tzinfo import memorized_datetime as datetime
from pytz.tzinfo import memorized_ttinfo as ttinfo

class Guam(DstTzInfo):
    '''Pacific/Guam timezone definition. See datetime.tzinfo for details'''

    _zone = 'Pacific/Guam'

    _utc_transition_times = [
        datetime(   1,  1,  1,  0,  0,  0), #  36000     0 GST
        datetime(2000, 12, 22, 14,  0,  0), #  36000     0 ChST
        ]

    _transition_info = [
        ttinfo( 36000,      0,  'GST'),
        ttinfo( 36000,      0, 'ChST'),
        ]

Guam = Guam() # Singleton

