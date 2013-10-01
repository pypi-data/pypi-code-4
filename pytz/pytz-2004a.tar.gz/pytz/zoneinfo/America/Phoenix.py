'''
tzinfo timezone information for America/Phoenix.

Generated from the Olson timezone database:
    ftp://elsie.nci.nih.gov/pub/tz*.tar.gz
'''

from pytz.tzinfo import DstTzInfo
from pytz.tzinfo import memorized_datetime as datetime
from pytz.tzinfo import memorized_ttinfo as ttinfo

class Phoenix(DstTzInfo):
    '''America/Phoenix timezone definition. See datetime.tzinfo for details'''

    _zone = 'America/Phoenix'

    _utc_transition_times = [
        datetime(   1,  1,  1,  0,  0,  0), # -25200     0 MST
        datetime(1918,  3, 31,  9,  0,  0), # -21600  3600 MDT
        datetime(1918, 10, 27,  8,  0,  0), # -25200     0 MST
        datetime(1919,  3, 30,  9,  0,  0), # -21600  3600 MDT
        datetime(1919, 10, 26,  8,  0,  0), # -25200     0 MST
        datetime(1942,  2,  9,  9,  0,  0), # -21600  3600 MWT
        datetime(1944,  1,  1,  6,  1,  0), # -25200     0 MST
        datetime(1944,  4,  1,  7,  1,  0), # -21600  3600 MWT
        datetime(1944, 10,  1,  6,  1,  0), # -25200     0 MST
        datetime(1967,  4, 30,  9,  0,  0), # -21600  3600 MDT
        datetime(1967, 10, 29,  8,  0,  0), # -25200     0 MST
        ]

    _transition_info = [
        ttinfo(-25200,      0,  'MST'),
        ttinfo(-21600,   3600,  'MDT'),
        ttinfo(-25200,      0,  'MST'),
        ttinfo(-21600,   3600,  'MDT'),
        ttinfo(-25200,      0,  'MST'),
        ttinfo(-21600,   3600,  'MWT'),
        ttinfo(-25200,      0,  'MST'),
        ttinfo(-21600,   3600,  'MWT'),
        ttinfo(-25200,      0,  'MST'),
        ttinfo(-21600,   3600,  'MDT'),
        ttinfo(-25200,      0,  'MST'),
        ]

Phoenix = Phoenix() # Singleton

