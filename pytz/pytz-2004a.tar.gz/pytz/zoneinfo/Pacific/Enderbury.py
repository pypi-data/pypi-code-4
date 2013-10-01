'''
tzinfo timezone information for Pacific/Enderbury.

Generated from the Olson timezone database:
    ftp://elsie.nci.nih.gov/pub/tz*.tar.gz
'''

from pytz.tzinfo import DstTzInfo
from pytz.tzinfo import memorized_datetime as datetime
from pytz.tzinfo import memorized_ttinfo as ttinfo

class Enderbury(DstTzInfo):
    '''Pacific/Enderbury timezone definition. See datetime.tzinfo for details'''

    _zone = 'Pacific/Enderbury'

    _utc_transition_times = [
        datetime(   1,  1,  1,  0,  0,  0), # -43200     0 PHOT
        datetime(1979, 10,  1, 12,  0,  0), # -39600     0 PHOT
        datetime(1995,  1,  1, 11,  0,  0), #  46800     0 PHOT
        ]

    _transition_info = [
        ttinfo(-43200,      0, 'PHOT'),
        ttinfo(-39600,      0, 'PHOT'),
        ttinfo( 46800,      0, 'PHOT'),
        ]

Enderbury = Enderbury() # Singleton

