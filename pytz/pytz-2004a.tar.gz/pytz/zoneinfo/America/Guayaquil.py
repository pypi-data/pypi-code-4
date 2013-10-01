'''
tzinfo timezone information for America/Guayaquil.

Generated from the Olson timezone database:
    ftp://elsie.nci.nih.gov/pub/tz*.tar.gz
'''

from pytz.tzinfo import DstTzInfo
from pytz.tzinfo import memorized_datetime as datetime
from pytz.tzinfo import memorized_ttinfo as ttinfo

class Guayaquil(DstTzInfo):
    '''America/Guayaquil timezone definition. See datetime.tzinfo for details'''

    _zone = 'America/Guayaquil'

    _utc_transition_times = [
        datetime(   1,  1,  1,  0,  0,  0), # -18840     0 QMT
        datetime(1931,  1,  1,  5, 14,  0), # -18000     0 ECT
        ]

    _transition_info = [
        ttinfo(-18840,      0,  'QMT'),
        ttinfo(-18000,      0,  'ECT'),
        ]

Guayaquil = Guayaquil() # Singleton

