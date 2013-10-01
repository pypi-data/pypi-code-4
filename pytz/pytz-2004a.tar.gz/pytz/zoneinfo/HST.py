'''
tzinfo timezone information for HST.

Generated from the Olson timezone database:
    ftp://elsie.nci.nih.gov/pub/tz*.tar.gz
'''

from pytz.tzinfo import DstTzInfo
from pytz.tzinfo import memorized_datetime as datetime
from pytz.tzinfo import memorized_ttinfo as ttinfo

class HST(DstTzInfo):
    '''HST timezone definition. See datetime.tzinfo for details'''

    _zone = 'HST'

    _utc_transition_times = [
        datetime(   1,  1,  1,  0,  0,  0), # -37800     0 HST
        datetime(1933,  4, 30, 12, 30,  0), # -34200  3600 HDT
        datetime(1933,  5, 21, 11, 30,  0), # -37800     0 HST
        datetime(1942,  2,  9, 12, 30,  0), # -34200  3600 HWT
        datetime(1945,  8, 14, 23,  0,  0), # -34200     0 HPT
        datetime(1945,  9, 30, 11, 30,  0), # -37800     0 HST
        datetime(1947,  6,  8, 12, 30,  0), # -36000     0 HST
        ]

    _transition_info = [
        ttinfo(-37800,      0,  'HST'),
        ttinfo(-34200,   3600,  'HDT'),
        ttinfo(-37800,      0,  'HST'),
        ttinfo(-34200,   3600,  'HWT'),
        ttinfo(-34200,      0,  'HPT'),
        ttinfo(-37800,      0,  'HST'),
        ttinfo(-36000,      0,  'HST'),
        ]

HST = HST() # Singleton

