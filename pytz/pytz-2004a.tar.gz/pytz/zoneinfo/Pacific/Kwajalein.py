'''
tzinfo timezone information for Pacific/Kwajalein.

Generated from the Olson timezone database:
    ftp://elsie.nci.nih.gov/pub/tz*.tar.gz
'''

from pytz.tzinfo import DstTzInfo
from pytz.tzinfo import memorized_datetime as datetime
from pytz.tzinfo import memorized_ttinfo as ttinfo

class Kwajalein(DstTzInfo):
    '''Pacific/Kwajalein timezone definition. See datetime.tzinfo for details'''

    _zone = 'Pacific/Kwajalein'

    _utc_transition_times = [
        datetime(   1,  1,  1,  0,  0,  0), #  39600     0 MHT
        datetime(1969,  9, 30, 13,  0,  0), # -43200     0 KWAT
        datetime(1993,  8, 20, 12,  0,  0), #  43200     0 MHT
        ]

    _transition_info = [
        ttinfo( 39600,      0,  'MHT'),
        ttinfo(-43200,      0, 'KWAT'),
        ttinfo( 43200,      0,  'MHT'),
        ]

Kwajalein = Kwajalein() # Singleton

