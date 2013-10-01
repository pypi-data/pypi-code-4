'''
tzinfo timezone information for Pacific/Efate.

Generated from the Olson timezone database:
    ftp://elsie.nci.nih.gov/pub/tz*.tar.gz
'''

from pytz.tzinfo import DstTzInfo
from pytz.tzinfo import memorized_datetime as datetime
from pytz.tzinfo import memorized_ttinfo as ttinfo

class Efate(DstTzInfo):
    '''Pacific/Efate timezone definition. See datetime.tzinfo for details'''

    _zone = 'Pacific/Efate'

    _utc_transition_times = [
        datetime(   1,  1,  1,  0,  0,  0), #  40396     0 LMT
        datetime(1912,  1, 12, 12, 46, 44), #  39600     0 VUT
        datetime(1983,  9, 24, 13,  0,  0), #  43200  3600 VUST
        datetime(1984,  3, 24, 12,  0,  0), #  39600     0 VUT
        datetime(1984, 10, 22, 13,  0,  0), #  43200  3600 VUST
        datetime(1985,  3, 23, 12,  0,  0), #  39600     0 VUT
        datetime(1985,  9, 28, 13,  0,  0), #  43200  3600 VUST
        datetime(1986,  3, 22, 12,  0,  0), #  39600     0 VUT
        datetime(1986,  9, 27, 13,  0,  0), #  43200  3600 VUST
        datetime(1987,  3, 28, 12,  0,  0), #  39600     0 VUT
        datetime(1987,  9, 26, 13,  0,  0), #  43200  3600 VUST
        datetime(1988,  3, 26, 12,  0,  0), #  39600     0 VUT
        datetime(1988,  9, 24, 13,  0,  0), #  43200  3600 VUST
        datetime(1989,  3, 25, 12,  0,  0), #  39600     0 VUT
        datetime(1989,  9, 23, 13,  0,  0), #  43200  3600 VUST
        datetime(1990,  3, 24, 12,  0,  0), #  39600     0 VUT
        datetime(1990,  9, 22, 13,  0,  0), #  43200  3600 VUST
        datetime(1991,  3, 23, 12,  0,  0), #  39600     0 VUT
        datetime(1991,  9, 28, 13,  0,  0), #  43200  3600 VUST
        datetime(1992,  1, 25, 12,  0,  0), #  39600     0 VUT
        datetime(1992, 10, 24, 13,  0,  0), #  43200  3600 VUST
        datetime(1993,  1, 23, 12,  0,  0), #  39600     0 VUT
        ]

    _transition_info = [
        ttinfo( 40396,      0,  'LMT'),
        ttinfo( 39600,      0,  'VUT'),
        ttinfo( 43200,   3600, 'VUST'),
        ttinfo( 39600,      0,  'VUT'),
        ttinfo( 43200,   3600, 'VUST'),
        ttinfo( 39600,      0,  'VUT'),
        ttinfo( 43200,   3600, 'VUST'),
        ttinfo( 39600,      0,  'VUT'),
        ttinfo( 43200,   3600, 'VUST'),
        ttinfo( 39600,      0,  'VUT'),
        ttinfo( 43200,   3600, 'VUST'),
        ttinfo( 39600,      0,  'VUT'),
        ttinfo( 43200,   3600, 'VUST'),
        ttinfo( 39600,      0,  'VUT'),
        ttinfo( 43200,   3600, 'VUST'),
        ttinfo( 39600,      0,  'VUT'),
        ttinfo( 43200,   3600, 'VUST'),
        ttinfo( 39600,      0,  'VUT'),
        ttinfo( 43200,   3600, 'VUST'),
        ttinfo( 39600,      0,  'VUT'),
        ttinfo( 43200,   3600, 'VUST'),
        ttinfo( 39600,      0,  'VUT'),
        ]

Efate = Efate() # Singleton

