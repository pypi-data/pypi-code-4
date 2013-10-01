'''
tzinfo timezone information for America/Managua.

Generated from the Olson timezone database:
    ftp://elsie.nci.nih.gov/pub/tz*.tar.gz
'''

from pytz.tzinfo import DstTzInfo
from pytz.tzinfo import memorized_datetime as datetime
from pytz.tzinfo import memorized_ttinfo as ttinfo

class Managua(DstTzInfo):
    '''America/Managua timezone definition. See datetime.tzinfo for details'''

    _zone = 'America/Managua'

    _utc_transition_times = [
        datetime(   1,  1,  1,  0,  0,  0), # -20712     0 MMT
        datetime(1934,  6, 23,  5, 45, 12), # -21600     0 CST
        datetime(1973,  5,  1,  6,  0,  0), # -18000     0 EST
        datetime(1975,  2, 16,  5,  0,  0), # -21600     0 CST
        datetime(1979,  3, 18,  6,  0,  0), # -18000  3600 CDT
        datetime(1979,  6, 25,  5,  0,  0), # -21600     0 CST
        datetime(1980,  3, 16,  6,  0,  0), # -18000  3600 CDT
        datetime(1980,  6, 23,  5,  0,  0), # -21600     0 CST
        datetime(1992,  1,  1, 10,  0,  0), # -18000  3600 CDT
        datetime(1992,  9, 24,  5,  0,  0), # -21600     0 CST
        datetime(1993,  1,  1, 10,  0,  0), # -18000     0 EST
        datetime(1998, 12,  1,  5,  0,  0), # -21600     0 CST
        ]

    _transition_info = [
        ttinfo(-20712,      0,  'MMT'),
        ttinfo(-21600,      0,  'CST'),
        ttinfo(-18000,      0,  'EST'),
        ttinfo(-21600,      0,  'CST'),
        ttinfo(-18000,   3600,  'CDT'),
        ttinfo(-21600,      0,  'CST'),
        ttinfo(-18000,   3600,  'CDT'),
        ttinfo(-21600,      0,  'CST'),
        ttinfo(-18000,   3600,  'CDT'),
        ttinfo(-21600,      0,  'CST'),
        ttinfo(-18000,      0,  'EST'),
        ttinfo(-21600,      0,  'CST'),
        ]

Managua = Managua() # Singleton

