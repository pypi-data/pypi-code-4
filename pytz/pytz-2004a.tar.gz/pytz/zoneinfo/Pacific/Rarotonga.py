'''
tzinfo timezone information for Pacific/Rarotonga.

Generated from the Olson timezone database:
    ftp://elsie.nci.nih.gov/pub/tz*.tar.gz
'''

from pytz.tzinfo import DstTzInfo
from pytz.tzinfo import memorized_datetime as datetime
from pytz.tzinfo import memorized_ttinfo as ttinfo

class Rarotonga(DstTzInfo):
    '''Pacific/Rarotonga timezone definition. See datetime.tzinfo for details'''

    _zone = 'Pacific/Rarotonga'

    _utc_transition_times = [
        datetime(   1,  1,  1,  0,  0,  0), # -37800     0 CKT
        datetime(1978, 11, 12, 10, 30,  0), # -34200  3600 CKHST
        datetime(1979,  3,  4,  9, 30,  0), # -36000     0 CKT
        datetime(1979, 10, 28, 10,  0,  0), # -34200  1800 CKHST
        datetime(1980,  3,  2,  9, 30,  0), # -36000     0 CKT
        datetime(1980, 10, 26, 10,  0,  0), # -34200  1800 CKHST
        datetime(1981,  3,  1,  9, 30,  0), # -36000     0 CKT
        datetime(1981, 10, 25, 10,  0,  0), # -34200  1800 CKHST
        datetime(1982,  3,  7,  9, 30,  0), # -36000     0 CKT
        datetime(1982, 10, 31, 10,  0,  0), # -34200  1800 CKHST
        datetime(1983,  3,  6,  9, 30,  0), # -36000     0 CKT
        datetime(1983, 10, 30, 10,  0,  0), # -34200  1800 CKHST
        datetime(1984,  3,  4,  9, 30,  0), # -36000     0 CKT
        datetime(1984, 10, 28, 10,  0,  0), # -34200  1800 CKHST
        datetime(1985,  3,  3,  9, 30,  0), # -36000     0 CKT
        datetime(1985, 10, 27, 10,  0,  0), # -34200  1800 CKHST
        datetime(1986,  3,  2,  9, 30,  0), # -36000     0 CKT
        datetime(1986, 10, 26, 10,  0,  0), # -34200  1800 CKHST
        datetime(1987,  3,  1,  9, 30,  0), # -36000     0 CKT
        datetime(1987, 10, 25, 10,  0,  0), # -34200  1800 CKHST
        datetime(1988,  3,  6,  9, 30,  0), # -36000     0 CKT
        datetime(1988, 10, 30, 10,  0,  0), # -34200  1800 CKHST
        datetime(1989,  3,  5,  9, 30,  0), # -36000     0 CKT
        datetime(1989, 10, 29, 10,  0,  0), # -34200  1800 CKHST
        datetime(1990,  3,  4,  9, 30,  0), # -36000     0 CKT
        datetime(1990, 10, 28, 10,  0,  0), # -34200  1800 CKHST
        datetime(1991,  3,  3,  9, 30,  0), # -36000     0 CKT
        ]

    _transition_info = [
        ttinfo(-37800,      0,  'CKT'),
        ttinfo(-34200,   3600, 'CKHST'),
        ttinfo(-36000,      0,  'CKT'),
        ttinfo(-34200,   1800, 'CKHST'),
        ttinfo(-36000,      0,  'CKT'),
        ttinfo(-34200,   1800, 'CKHST'),
        ttinfo(-36000,      0,  'CKT'),
        ttinfo(-34200,   1800, 'CKHST'),
        ttinfo(-36000,      0,  'CKT'),
        ttinfo(-34200,   1800, 'CKHST'),
        ttinfo(-36000,      0,  'CKT'),
        ttinfo(-34200,   1800, 'CKHST'),
        ttinfo(-36000,      0,  'CKT'),
        ttinfo(-34200,   1800, 'CKHST'),
        ttinfo(-36000,      0,  'CKT'),
        ttinfo(-34200,   1800, 'CKHST'),
        ttinfo(-36000,      0,  'CKT'),
        ttinfo(-34200,   1800, 'CKHST'),
        ttinfo(-36000,      0,  'CKT'),
        ttinfo(-34200,   1800, 'CKHST'),
        ttinfo(-36000,      0,  'CKT'),
        ttinfo(-34200,   1800, 'CKHST'),
        ttinfo(-36000,      0,  'CKT'),
        ttinfo(-34200,   1800, 'CKHST'),
        ttinfo(-36000,      0,  'CKT'),
        ttinfo(-34200,   1800, 'CKHST'),
        ttinfo(-36000,      0,  'CKT'),
        ]

Rarotonga = Rarotonga() # Singleton

