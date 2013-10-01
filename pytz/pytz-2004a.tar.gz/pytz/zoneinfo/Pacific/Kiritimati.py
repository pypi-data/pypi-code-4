'''
tzinfo timezone information for Pacific/Kiritimati.

Generated from the Olson timezone database:
    ftp://elsie.nci.nih.gov/pub/tz*.tar.gz
'''

from pytz.tzinfo import DstTzInfo
from pytz.tzinfo import memorized_datetime as datetime
from pytz.tzinfo import memorized_ttinfo as ttinfo

class Kiritimati(DstTzInfo):
    '''Pacific/Kiritimati timezone definition. See datetime.tzinfo for details'''

    _zone = 'Pacific/Kiritimati'

    _utc_transition_times = [
        datetime(   1,  1,  1,  0,  0,  0), # -38400     0 LINT
        datetime(1979, 10,  1, 10, 40,  0), # -36000     0 LINT
        datetime(1995,  1,  1, 10,  0,  0), #  50400     0 LINT
        ]

    _transition_info = [
        ttinfo(-38400,      0, 'LINT'),
        ttinfo(-36000,      0, 'LINT'),
        ttinfo( 50400,      0, 'LINT'),
        ]

Kiritimati = Kiritimati() # Singleton

