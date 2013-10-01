'''
tzinfo timezone information for America/Tegucigalpa.

Generated from the Olson timezone database:
    ftp://elsie.nci.nih.gov/pub/tz*.tar.gz
'''

from pytz.tzinfo import DstTzInfo
from pytz.tzinfo import memorized_datetime as datetime
from pytz.tzinfo import memorized_ttinfo as ttinfo

class Tegucigalpa(DstTzInfo):
    '''America/Tegucigalpa timezone definition. See datetime.tzinfo for details'''

    _zone = 'America/Tegucigalpa'

    _utc_transition_times = [
        datetime(   1,  1,  1,  0,  0,  0), # -20932     0 LMT
        datetime(1921,  4,  1,  5, 48, 52), # -21600     0 CST
        datetime(1987,  5,  3,  6,  0,  0), # -18000  3600 CDT
        datetime(1987,  9, 27,  5,  0,  0), # -21600     0 CST
        datetime(1988,  5,  1,  6,  0,  0), # -18000  3600 CDT
        datetime(1988,  9, 25,  5,  0,  0), # -21600     0 CST
        ]

    _transition_info = [
        ttinfo(-20932,      0,  'LMT'),
        ttinfo(-21600,      0,  'CST'),
        ttinfo(-18000,   3600,  'CDT'),
        ttinfo(-21600,      0,  'CST'),
        ttinfo(-18000,   3600,  'CDT'),
        ttinfo(-21600,      0,  'CST'),
        ]

Tegucigalpa = Tegucigalpa() # Singleton

