'''
tzinfo timezone information for Pacific/Niue.

Generated from the Olson timezone database:
    ftp://elsie.nci.nih.gov/pub/tz*.tar.gz
'''

from pytz.tzinfo import DstTzInfo
from pytz.tzinfo import memorized_datetime as datetime
from pytz.tzinfo import memorized_ttinfo as ttinfo

class Niue(DstTzInfo):
    '''Pacific/Niue timezone definition. See datetime.tzinfo for details'''

    _zone = 'Pacific/Niue'

    _utc_transition_times = [
        datetime(   1,  1,  1,  0,  0,  0), # -40800     0 NUT
        datetime(1951,  1,  1, 11, 20,  0), # -41400     0 NUT
        datetime(1978, 10,  1, 11, 30,  0), # -39600     0 NUT
        ]

    _transition_info = [
        ttinfo(-40800,      0,  'NUT'),
        ttinfo(-41400,      0,  'NUT'),
        ttinfo(-39600,      0,  'NUT'),
        ]

Niue = Niue() # Singleton

