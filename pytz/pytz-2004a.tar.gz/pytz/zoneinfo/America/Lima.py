'''
tzinfo timezone information for America/Lima.

Generated from the Olson timezone database:
    ftp://elsie.nci.nih.gov/pub/tz*.tar.gz
'''

from pytz.tzinfo import DstTzInfo
from pytz.tzinfo import memorized_datetime as datetime
from pytz.tzinfo import memorized_ttinfo as ttinfo

class Lima(DstTzInfo):
    '''America/Lima timezone definition. See datetime.tzinfo for details'''

    _zone = 'America/Lima'

    _utc_transition_times = [
        datetime(   1,  1,  1,  0,  0,  0), # -18516     0 LMT
        datetime(1908,  7, 28,  5,  8, 36), # -18000     0 PET
        datetime(1938,  1,  1,  5,  0,  0), # -14400  3600 PEST
        datetime(1938,  4,  1,  4,  0,  0), # -18000     0 PET
        datetime(1938,  9, 25,  5,  0,  0), # -14400  3600 PEST
        datetime(1939,  3, 26,  4,  0,  0), # -18000     0 PET
        datetime(1939,  9, 24,  5,  0,  0), # -14400  3600 PEST
        datetime(1940,  3, 24,  4,  0,  0), # -18000     0 PET
        datetime(1986,  1,  1,  5,  0,  0), # -14400  3600 PEST
        datetime(1986,  4,  1,  4,  0,  0), # -18000     0 PET
        datetime(1987,  1,  1,  5,  0,  0), # -14400  3600 PEST
        datetime(1987,  4,  1,  4,  0,  0), # -18000     0 PET
        datetime(1990,  1,  1,  5,  0,  0), # -14400  3600 PEST
        datetime(1990,  4,  1,  4,  0,  0), # -18000     0 PET
        datetime(1994,  1,  1,  5,  0,  0), # -14400  3600 PEST
        datetime(1994,  4,  1,  4,  0,  0), # -18000     0 PET
        ]

    _transition_info = [
        ttinfo(-18516,      0,  'LMT'),
        ttinfo(-18000,      0,  'PET'),
        ttinfo(-14400,   3600, 'PEST'),
        ttinfo(-18000,      0,  'PET'),
        ttinfo(-14400,   3600, 'PEST'),
        ttinfo(-18000,      0,  'PET'),
        ttinfo(-14400,   3600, 'PEST'),
        ttinfo(-18000,      0,  'PET'),
        ttinfo(-14400,   3600, 'PEST'),
        ttinfo(-18000,      0,  'PET'),
        ttinfo(-14400,   3600, 'PEST'),
        ttinfo(-18000,      0,  'PET'),
        ttinfo(-14400,   3600, 'PEST'),
        ttinfo(-18000,      0,  'PET'),
        ttinfo(-14400,   3600, 'PEST'),
        ttinfo(-18000,      0,  'PET'),
        ]

Lima = Lima() # Singleton

