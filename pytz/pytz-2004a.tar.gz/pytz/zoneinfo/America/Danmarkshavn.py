'''
tzinfo timezone information for America/Danmarkshavn.

Generated from the Olson timezone database:
    ftp://elsie.nci.nih.gov/pub/tz*.tar.gz
'''

from pytz.tzinfo import DstTzInfo
from pytz.tzinfo import memorized_datetime as datetime
from pytz.tzinfo import memorized_ttinfo as ttinfo

class Danmarkshavn(DstTzInfo):
    '''America/Danmarkshavn timezone definition. See datetime.tzinfo for details'''

    _zone = 'America/Danmarkshavn'

    _utc_transition_times = [
        datetime(   1,  1,  1,  0,  0,  0), #  -4480     0 LMT
        datetime(1916,  7, 28,  1, 14, 40), # -10800     0 WGT
        datetime(1980,  4,  6,  5,  0,  0), #  -7200  3600 WGST
        datetime(1980,  9, 28,  1,  0,  0), # -10800     0 WGT
        datetime(1981,  3, 29,  1,  0,  0), #  -7200  3600 WGST
        datetime(1981,  9, 27,  1,  0,  0), # -10800     0 WGT
        datetime(1982,  3, 28,  1,  0,  0), #  -7200  3600 WGST
        datetime(1982,  9, 26,  1,  0,  0), # -10800     0 WGT
        datetime(1983,  3, 27,  1,  0,  0), #  -7200  3600 WGST
        datetime(1983,  9, 25,  1,  0,  0), # -10800     0 WGT
        datetime(1984,  3, 25,  1,  0,  0), #  -7200  3600 WGST
        datetime(1984,  9, 30,  1,  0,  0), # -10800     0 WGT
        datetime(1985,  3, 31,  1,  0,  0), #  -7200  3600 WGST
        datetime(1985,  9, 29,  1,  0,  0), # -10800     0 WGT
        datetime(1986,  3, 30,  1,  0,  0), #  -7200  3600 WGST
        datetime(1986,  9, 28,  1,  0,  0), # -10800     0 WGT
        datetime(1987,  3, 29,  1,  0,  0), #  -7200  3600 WGST
        datetime(1987,  9, 27,  1,  0,  0), # -10800     0 WGT
        datetime(1988,  3, 27,  1,  0,  0), #  -7200  3600 WGST
        datetime(1988,  9, 25,  1,  0,  0), # -10800     0 WGT
        datetime(1989,  3, 26,  1,  0,  0), #  -7200  3600 WGST
        datetime(1989,  9, 24,  1,  0,  0), # -10800     0 WGT
        datetime(1990,  3, 25,  1,  0,  0), #  -7200  3600 WGST
        datetime(1990,  9, 30,  1,  0,  0), # -10800     0 WGT
        datetime(1991,  3, 31,  1,  0,  0), #  -7200  3600 WGST
        datetime(1991,  9, 29,  1,  0,  0), # -10800     0 WGT
        datetime(1992,  3, 29,  1,  0,  0), #  -7200  3600 WGST
        datetime(1992,  9, 27,  1,  0,  0), # -10800     0 WGT
        datetime(1993,  3, 28,  1,  0,  0), #  -7200  3600 WGST
        datetime(1993,  9, 26,  1,  0,  0), # -10800     0 WGT
        datetime(1994,  3, 27,  1,  0,  0), #  -7200  3600 WGST
        datetime(1994,  9, 25,  1,  0,  0), # -10800     0 WGT
        datetime(1995,  3, 26,  1,  0,  0), #  -7200  3600 WGST
        datetime(1995,  9, 24,  1,  0,  0), # -10800     0 WGT
        datetime(1996,  1,  1,  3,  0,  0), #      0     0 GMT
        ]

    _transition_info = [
        ttinfo( -4480,      0,  'LMT'),
        ttinfo(-10800,      0,  'WGT'),
        ttinfo( -7200,   3600, 'WGST'),
        ttinfo(-10800,      0,  'WGT'),
        ttinfo( -7200,   3600, 'WGST'),
        ttinfo(-10800,      0,  'WGT'),
        ttinfo( -7200,   3600, 'WGST'),
        ttinfo(-10800,      0,  'WGT'),
        ttinfo( -7200,   3600, 'WGST'),
        ttinfo(-10800,      0,  'WGT'),
        ttinfo( -7200,   3600, 'WGST'),
        ttinfo(-10800,      0,  'WGT'),
        ttinfo( -7200,   3600, 'WGST'),
        ttinfo(-10800,      0,  'WGT'),
        ttinfo( -7200,   3600, 'WGST'),
        ttinfo(-10800,      0,  'WGT'),
        ttinfo( -7200,   3600, 'WGST'),
        ttinfo(-10800,      0,  'WGT'),
        ttinfo( -7200,   3600, 'WGST'),
        ttinfo(-10800,      0,  'WGT'),
        ttinfo( -7200,   3600, 'WGST'),
        ttinfo(-10800,      0,  'WGT'),
        ttinfo( -7200,   3600, 'WGST'),
        ttinfo(-10800,      0,  'WGT'),
        ttinfo( -7200,   3600, 'WGST'),
        ttinfo(-10800,      0,  'WGT'),
        ttinfo( -7200,   3600, 'WGST'),
        ttinfo(-10800,      0,  'WGT'),
        ttinfo( -7200,   3600, 'WGST'),
        ttinfo(-10800,      0,  'WGT'),
        ttinfo( -7200,   3600, 'WGST'),
        ttinfo(-10800,      0,  'WGT'),
        ttinfo( -7200,   3600, 'WGST'),
        ttinfo(-10800,      0,  'WGT'),
        ttinfo(     0,      0,  'GMT'),
        ]

Danmarkshavn = Danmarkshavn() # Singleton

