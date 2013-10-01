'''
tzinfo timezone information for Indian/Chagos.

Generated from the Olson timezone database:
    ftp://elsie.nci.nih.gov/pub/tz*.tar.gz
'''

from pytz.tzinfo import DstTzInfo
from pytz.tzinfo import memorized_datetime as datetime
from pytz.tzinfo import memorized_ttinfo as ttinfo

class Chagos(DstTzInfo):
    '''Indian/Chagos timezone definition. See datetime.tzinfo for details'''

    _zone = 'Indian/Chagos'

    _utc_transition_times = [
        datetime(   1,  1,  1,  0,  0,  0), #  18000     0 IOT
        datetime(1995, 12, 31, 19,  0,  0), #  21600     0 IOT
        ]

    _transition_info = [
        ttinfo( 18000,      0,  'IOT'),
        ttinfo( 21600,      0,  'IOT'),
        ]

Chagos = Chagos() # Singleton

