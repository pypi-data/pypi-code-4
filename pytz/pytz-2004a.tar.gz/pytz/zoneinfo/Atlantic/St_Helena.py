'''
tzinfo timezone information for Atlantic/St_Helena.

Generated from the Olson timezone database:
    ftp://elsie.nci.nih.gov/pub/tz*.tar.gz
'''

from pytz.tzinfo import DstTzInfo
from pytz.tzinfo import memorized_datetime as datetime
from pytz.tzinfo import memorized_ttinfo as ttinfo

class St_Helena(DstTzInfo):
    '''Atlantic/St_Helena timezone definition. See datetime.tzinfo for details'''

    _zone = 'Atlantic/St_Helena'

    _utc_transition_times = [
        datetime(   1,  1,  1,  0,  0,  0), #  -1368     0 JMT
        datetime(1951,  1,  1,  0, 22, 48), #      0     0 GMT
        ]

    _transition_info = [
        ttinfo( -1368,      0,  'JMT'),
        ttinfo(     0,      0,  'GMT'),
        ]

St_Helena = St_Helena() # Singleton

