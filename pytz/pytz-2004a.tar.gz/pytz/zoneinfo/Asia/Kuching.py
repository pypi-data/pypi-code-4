'''
tzinfo timezone information for Asia/Kuching.

Generated from the Olson timezone database:
    ftp://elsie.nci.nih.gov/pub/tz*.tar.gz
'''

from pytz.tzinfo import DstTzInfo
from pytz.tzinfo import memorized_datetime as datetime
from pytz.tzinfo import memorized_ttinfo as ttinfo

class Kuching(DstTzInfo):
    '''Asia/Kuching timezone definition. See datetime.tzinfo for details'''

    _zone = 'Asia/Kuching'

    _utc_transition_times = [
        datetime(   1,  1,  1,  0,  0,  0), #  26480     0 LMT
        datetime(1926,  2, 28, 16, 38, 40), #  27000     0 BORT
        datetime(1932, 12, 31, 16, 30,  0), #  28800     0 BORT
        datetime(1935,  9, 13, 16,  0,  0), #  30000  1200 BORTST
        datetime(1935, 12, 13, 15, 40,  0), #  28800     0 BORT
        datetime(1936,  9, 13, 16,  0,  0), #  30000  1200 BORTST
        datetime(1936, 12, 13, 15, 40,  0), #  28800     0 BORT
        datetime(1937,  9, 13, 16,  0,  0), #  30000  1200 BORTST
        datetime(1937, 12, 13, 15, 40,  0), #  28800     0 BORT
        datetime(1938,  9, 13, 16,  0,  0), #  30000  1200 BORTST
        datetime(1938, 12, 13, 15, 40,  0), #  28800     0 BORT
        datetime(1939,  9, 13, 16,  0,  0), #  30000  1200 BORTST
        datetime(1939, 12, 13, 15, 40,  0), #  28800     0 BORT
        datetime(1940,  9, 13, 16,  0,  0), #  30000  1200 BORTST
        datetime(1940, 12, 13, 15, 40,  0), #  28800     0 BORT
        datetime(1941,  9, 13, 16,  0,  0), #  30000  1200 BORTST
        datetime(1941, 12, 13, 15, 40,  0), #  28800     0 BORT
        datetime(1942,  2, 15, 16,  0,  0), #  32400     0 JST
        datetime(1945,  9, 11, 15,  0,  0), #  28800     0 BORT
        datetime(1981, 12, 31, 16,  0,  0), #  28800     0 MYT
        ]

    _transition_info = [
        ttinfo( 26480,      0,  'LMT'),
        ttinfo( 27000,      0, 'BORT'),
        ttinfo( 28800,      0, 'BORT'),
        ttinfo( 30000,   1200, 'BORTST'),
        ttinfo( 28800,      0, 'BORT'),
        ttinfo( 30000,   1200, 'BORTST'),
        ttinfo( 28800,      0, 'BORT'),
        ttinfo( 30000,   1200, 'BORTST'),
        ttinfo( 28800,      0, 'BORT'),
        ttinfo( 30000,   1200, 'BORTST'),
        ttinfo( 28800,      0, 'BORT'),
        ttinfo( 30000,   1200, 'BORTST'),
        ttinfo( 28800,      0, 'BORT'),
        ttinfo( 30000,   1200, 'BORTST'),
        ttinfo( 28800,      0, 'BORT'),
        ttinfo( 30000,   1200, 'BORTST'),
        ttinfo( 28800,      0, 'BORT'),
        ttinfo( 32400,      0,  'JST'),
        ttinfo( 28800,      0, 'BORT'),
        ttinfo( 28800,      0,  'MYT'),
        ]

Kuching = Kuching() # Singleton

