'''
tzinfo timezone information for Pacific/Noumea.

Generated from the Olson timezone database:
    ftp://elsie.nci.nih.gov/pub/tz*.tar.gz
'''

from pytz.tzinfo import DstTzInfo
from pytz.tzinfo import memorized_datetime as datetime
from pytz.tzinfo import memorized_ttinfo as ttinfo

class Noumea(DstTzInfo):
    '''Pacific/Noumea timezone definition. See datetime.tzinfo for details'''

    _zone = 'Pacific/Noumea'

    _utc_transition_times = [
        datetime(   1,  1,  1,  0,  0,  0), #  39948     0 LMT
        datetime(1912,  1, 12, 12, 54, 12), #  39600     0 NCT
        datetime(1977, 12,  3, 13,  0,  0), #  43200  3600 NCST
        datetime(1978,  2, 26, 12,  0,  0), #  39600     0 NCT
        datetime(1978, 12,  2, 13,  0,  0), #  43200  3600 NCST
        datetime(1979,  2, 26, 12,  0,  0), #  39600     0 NCT
        datetime(1996, 11, 30, 15,  0,  0), #  43200  3600 NCST
        datetime(1997,  3,  1, 15,  0,  0), #  39600     0 NCT
        ]

    _transition_info = [
        ttinfo( 39948,      0,  'LMT'),
        ttinfo( 39600,      0,  'NCT'),
        ttinfo( 43200,   3600, 'NCST'),
        ttinfo( 39600,      0,  'NCT'),
        ttinfo( 43200,   3600, 'NCST'),
        ttinfo( 39600,      0,  'NCT'),
        ttinfo( 43200,   3600, 'NCST'),
        ttinfo( 39600,      0,  'NCT'),
        ]

Noumea = Noumea() # Singleton

