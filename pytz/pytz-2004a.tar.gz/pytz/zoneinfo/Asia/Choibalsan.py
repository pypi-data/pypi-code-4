'''
tzinfo timezone information for Asia/Choibalsan.

Generated from the Olson timezone database:
    ftp://elsie.nci.nih.gov/pub/tz*.tar.gz
'''

from pytz.tzinfo import DstTzInfo
from pytz.tzinfo import memorized_datetime as datetime
from pytz.tzinfo import memorized_ttinfo as ttinfo

class Choibalsan(DstTzInfo):
    '''Asia/Choibalsan timezone definition. See datetime.tzinfo for details'''

    _zone = 'Asia/Choibalsan'

    _utc_transition_times = [
        datetime(   1,  1,  1,  0,  0,  0), #  27480     0 LMT
        datetime(1905,  7, 31, 16, 22,  0), #  25200     0 ULAT
        datetime(1977, 12, 31, 17,  0,  0), #  28800     0 ULAT
        datetime(1983,  3, 31, 16,  0,  0), #  36000  7200 CHOST
        datetime(1983,  9, 30, 14,  0,  0), #  32400     0 CHOT
        datetime(1984,  3, 31, 15,  0,  0), #  36000  3600 CHOST
        datetime(1984,  9, 29, 17,  0,  0), #  32400     0 CHOT
        datetime(1985,  3, 30, 17,  0,  0), #  36000  3600 CHOST
        datetime(1985,  9, 28, 17,  0,  0), #  32400     0 CHOT
        datetime(1986,  3, 29, 17,  0,  0), #  36000  3600 CHOST
        datetime(1986,  9, 27, 17,  0,  0), #  32400     0 CHOT
        datetime(1987,  3, 28, 17,  0,  0), #  36000  3600 CHOST
        datetime(1987,  9, 26, 17,  0,  0), #  32400     0 CHOT
        datetime(1988,  3, 26, 17,  0,  0), #  36000  3600 CHOST
        datetime(1988,  9, 24, 17,  0,  0), #  32400     0 CHOT
        datetime(1989,  3, 25, 17,  0,  0), #  36000  3600 CHOST
        datetime(1989,  9, 23, 17,  0,  0), #  32400     0 CHOT
        datetime(1990,  3, 24, 17,  0,  0), #  36000  3600 CHOST
        datetime(1990,  9, 29, 17,  0,  0), #  32400     0 CHOT
        datetime(1991,  3, 30, 17,  0,  0), #  36000  3600 CHOST
        datetime(1991,  9, 28, 17,  0,  0), #  32400     0 CHOT
        datetime(1992,  3, 28, 17,  0,  0), #  36000  3600 CHOST
        datetime(1992,  9, 26, 17,  0,  0), #  32400     0 CHOT
        datetime(1993,  3, 27, 17,  0,  0), #  36000  3600 CHOST
        datetime(1993,  9, 25, 17,  0,  0), #  32400     0 CHOT
        datetime(1994,  3, 26, 17,  0,  0), #  36000  3600 CHOST
        datetime(1994,  9, 24, 17,  0,  0), #  32400     0 CHOT
        datetime(1995,  3, 25, 17,  0,  0), #  36000  3600 CHOST
        datetime(1995,  9, 23, 17,  0,  0), #  32400     0 CHOT
        datetime(1996,  3, 30, 17,  0,  0), #  36000  3600 CHOST
        datetime(1996,  9, 28, 17,  0,  0), #  32400     0 CHOT
        datetime(1997,  3, 29, 17,  0,  0), #  36000  3600 CHOST
        datetime(1997,  9, 27, 17,  0,  0), #  32400     0 CHOT
        datetime(1998,  3, 28, 17,  0,  0), #  36000  3600 CHOST
        datetime(1998,  9, 26, 17,  0,  0), #  32400     0 CHOT
        datetime(2001,  4, 27, 17,  0,  0), #  36000  3600 CHOST
        datetime(2001,  9, 28, 16,  0,  0), #  32400     0 CHOT
        datetime(2002,  3, 29, 17,  0,  0), #  36000  3600 CHOST
        datetime(2002,  9, 27, 16,  0,  0), #  32400     0 CHOT
        datetime(2003,  3, 28, 17,  0,  0), #  36000  3600 CHOST
        datetime(2003,  9, 26, 16,  0,  0), #  32400     0 CHOT
        datetime(2004,  3, 26, 17,  0,  0), #  36000  3600 CHOST
        datetime(2004,  9, 24, 16,  0,  0), #  32400     0 CHOT
        datetime(2005,  3, 25, 17,  0,  0), #  36000  3600 CHOST
        datetime(2005,  9, 23, 16,  0,  0), #  32400     0 CHOT
        datetime(2006,  3, 24, 17,  0,  0), #  36000  3600 CHOST
        datetime(2006,  9, 29, 16,  0,  0), #  32400     0 CHOT
        datetime(2007,  3, 30, 17,  0,  0), #  36000  3600 CHOST
        datetime(2007,  9, 28, 16,  0,  0), #  32400     0 CHOT
        datetime(2008,  3, 28, 17,  0,  0), #  36000  3600 CHOST
        datetime(2008,  9, 26, 16,  0,  0), #  32400     0 CHOT
        datetime(2009,  3, 27, 17,  0,  0), #  36000  3600 CHOST
        datetime(2009,  9, 25, 16,  0,  0), #  32400     0 CHOT
        datetime(2010,  3, 26, 17,  0,  0), #  36000  3600 CHOST
        datetime(2010,  9, 24, 16,  0,  0), #  32400     0 CHOT
        datetime(2011,  3, 25, 17,  0,  0), #  36000  3600 CHOST
        datetime(2011,  9, 23, 16,  0,  0), #  32400     0 CHOT
        datetime(2012,  3, 30, 17,  0,  0), #  36000  3600 CHOST
        datetime(2012,  9, 28, 16,  0,  0), #  32400     0 CHOT
        datetime(2013,  3, 29, 17,  0,  0), #  36000  3600 CHOST
        datetime(2013,  9, 27, 16,  0,  0), #  32400     0 CHOT
        datetime(2014,  3, 28, 17,  0,  0), #  36000  3600 CHOST
        datetime(2014,  9, 26, 16,  0,  0), #  32400     0 CHOT
        datetime(2015,  3, 27, 17,  0,  0), #  36000  3600 CHOST
        datetime(2015,  9, 25, 16,  0,  0), #  32400     0 CHOT
        datetime(2016,  3, 25, 17,  0,  0), #  36000  3600 CHOST
        datetime(2016,  9, 23, 16,  0,  0), #  32400     0 CHOT
        datetime(2017,  3, 24, 17,  0,  0), #  36000  3600 CHOST
        datetime(2017,  9, 29, 16,  0,  0), #  32400     0 CHOT
        datetime(2018,  3, 30, 17,  0,  0), #  36000  3600 CHOST
        datetime(2018,  9, 28, 16,  0,  0), #  32400     0 CHOT
        datetime(2019,  3, 29, 17,  0,  0), #  36000  3600 CHOST
        datetime(2019,  9, 27, 16,  0,  0), #  32400     0 CHOT
        datetime(2020,  3, 27, 17,  0,  0), #  36000  3600 CHOST
        datetime(2020,  9, 25, 16,  0,  0), #  32400     0 CHOT
        datetime(2021,  3, 26, 17,  0,  0), #  36000  3600 CHOST
        datetime(2021,  9, 24, 16,  0,  0), #  32400     0 CHOT
        datetime(2022,  3, 25, 17,  0,  0), #  36000  3600 CHOST
        datetime(2022,  9, 23, 16,  0,  0), #  32400     0 CHOT
        datetime(2023,  3, 24, 17,  0,  0), #  36000  3600 CHOST
        datetime(2023,  9, 29, 16,  0,  0), #  32400     0 CHOT
        datetime(2024,  3, 29, 17,  0,  0), #  36000  3600 CHOST
        datetime(2024,  9, 27, 16,  0,  0), #  32400     0 CHOT
        datetime(2025,  3, 28, 17,  0,  0), #  36000  3600 CHOST
        datetime(2025,  9, 26, 16,  0,  0), #  32400     0 CHOT
        datetime(2026,  3, 27, 17,  0,  0), #  36000  3600 CHOST
        datetime(2026,  9, 25, 16,  0,  0), #  32400     0 CHOT
        datetime(2027,  3, 26, 17,  0,  0), #  36000  3600 CHOST
        datetime(2027,  9, 24, 16,  0,  0), #  32400     0 CHOT
        datetime(2028,  3, 24, 17,  0,  0), #  36000  3600 CHOST
        datetime(2028,  9, 29, 16,  0,  0), #  32400     0 CHOT
        datetime(2029,  3, 30, 17,  0,  0), #  36000  3600 CHOST
        datetime(2029,  9, 28, 16,  0,  0), #  32400     0 CHOT
        datetime(2030,  3, 29, 17,  0,  0), #  36000  3600 CHOST
        datetime(2030,  9, 27, 16,  0,  0), #  32400     0 CHOT
        datetime(2031,  3, 28, 17,  0,  0), #  36000  3600 CHOST
        datetime(2031,  9, 26, 16,  0,  0), #  32400     0 CHOT
        datetime(2032,  3, 26, 17,  0,  0), #  36000  3600 CHOST
        datetime(2032,  9, 24, 16,  0,  0), #  32400     0 CHOT
        datetime(2033,  3, 25, 17,  0,  0), #  36000  3600 CHOST
        datetime(2033,  9, 23, 16,  0,  0), #  32400     0 CHOT
        datetime(2034,  3, 24, 17,  0,  0), #  36000  3600 CHOST
        datetime(2034,  9, 29, 16,  0,  0), #  32400     0 CHOT
        datetime(2035,  3, 30, 17,  0,  0), #  36000  3600 CHOST
        datetime(2035,  9, 28, 16,  0,  0), #  32400     0 CHOT
        datetime(2036,  3, 28, 17,  0,  0), #  36000  3600 CHOST
        datetime(2036,  9, 26, 16,  0,  0), #  32400     0 CHOT
        datetime(2037,  3, 27, 17,  0,  0), #  36000  3600 CHOST
        datetime(2037,  9, 25, 16,  0,  0), #  32400     0 CHOT
        ]

    _transition_info = [
        ttinfo( 27480,      0,  'LMT'),
        ttinfo( 25200,      0, 'ULAT'),
        ttinfo( 28800,      0, 'ULAT'),
        ttinfo( 36000,   7200, 'CHOST'),
        ttinfo( 32400,      0, 'CHOT'),
        ttinfo( 36000,   3600, 'CHOST'),
        ttinfo( 32400,      0, 'CHOT'),
        ttinfo( 36000,   3600, 'CHOST'),
        ttinfo( 32400,      0, 'CHOT'),
        ttinfo( 36000,   3600, 'CHOST'),
        ttinfo( 32400,      0, 'CHOT'),
        ttinfo( 36000,   3600, 'CHOST'),
        ttinfo( 32400,      0, 'CHOT'),
        ttinfo( 36000,   3600, 'CHOST'),
        ttinfo( 32400,      0, 'CHOT'),
        ttinfo( 36000,   3600, 'CHOST'),
        ttinfo( 32400,      0, 'CHOT'),
        ttinfo( 36000,   3600, 'CHOST'),
        ttinfo( 32400,      0, 'CHOT'),
        ttinfo( 36000,   3600, 'CHOST'),
        ttinfo( 32400,      0, 'CHOT'),
        ttinfo( 36000,   3600, 'CHOST'),
        ttinfo( 32400,      0, 'CHOT'),
        ttinfo( 36000,   3600, 'CHOST'),
        ttinfo( 32400,      0, 'CHOT'),
        ttinfo( 36000,   3600, 'CHOST'),
        ttinfo( 32400,      0, 'CHOT'),
        ttinfo( 36000,   3600, 'CHOST'),
        ttinfo( 32400,      0, 'CHOT'),
        ttinfo( 36000,   3600, 'CHOST'),
        ttinfo( 32400,      0, 'CHOT'),
        ttinfo( 36000,   3600, 'CHOST'),
        ttinfo( 32400,      0, 'CHOT'),
        ttinfo( 36000,   3600, 'CHOST'),
        ttinfo( 32400,      0, 'CHOT'),
        ttinfo( 36000,   3600, 'CHOST'),
        ttinfo( 32400,      0, 'CHOT'),
        ttinfo( 36000,   3600, 'CHOST'),
        ttinfo( 32400,      0, 'CHOT'),
        ttinfo( 36000,   3600, 'CHOST'),
        ttinfo( 32400,      0, 'CHOT'),
        ttinfo( 36000,   3600, 'CHOST'),
        ttinfo( 32400,      0, 'CHOT'),
        ttinfo( 36000,   3600, 'CHOST'),
        ttinfo( 32400,      0, 'CHOT'),
        ttinfo( 36000,   3600, 'CHOST'),
        ttinfo( 32400,      0, 'CHOT'),
        ttinfo( 36000,   3600, 'CHOST'),
        ttinfo( 32400,      0, 'CHOT'),
        ttinfo( 36000,   3600, 'CHOST'),
        ttinfo( 32400,      0, 'CHOT'),
        ttinfo( 36000,   3600, 'CHOST'),
        ttinfo( 32400,      0, 'CHOT'),
        ttinfo( 36000,   3600, 'CHOST'),
        ttinfo( 32400,      0, 'CHOT'),
        ttinfo( 36000,   3600, 'CHOST'),
        ttinfo( 32400,      0, 'CHOT'),
        ttinfo( 36000,   3600, 'CHOST'),
        ttinfo( 32400,      0, 'CHOT'),
        ttinfo( 36000,   3600, 'CHOST'),
        ttinfo( 32400,      0, 'CHOT'),
        ttinfo( 36000,   3600, 'CHOST'),
        ttinfo( 32400,      0, 'CHOT'),
        ttinfo( 36000,   3600, 'CHOST'),
        ttinfo( 32400,      0, 'CHOT'),
        ttinfo( 36000,   3600, 'CHOST'),
        ttinfo( 32400,      0, 'CHOT'),
        ttinfo( 36000,   3600, 'CHOST'),
        ttinfo( 32400,      0, 'CHOT'),
        ttinfo( 36000,   3600, 'CHOST'),
        ttinfo( 32400,      0, 'CHOT'),
        ttinfo( 36000,   3600, 'CHOST'),
        ttinfo( 32400,      0, 'CHOT'),
        ttinfo( 36000,   3600, 'CHOST'),
        ttinfo( 32400,      0, 'CHOT'),
        ttinfo( 36000,   3600, 'CHOST'),
        ttinfo( 32400,      0, 'CHOT'),
        ttinfo( 36000,   3600, 'CHOST'),
        ttinfo( 32400,      0, 'CHOT'),
        ttinfo( 36000,   3600, 'CHOST'),
        ttinfo( 32400,      0, 'CHOT'),
        ttinfo( 36000,   3600, 'CHOST'),
        ttinfo( 32400,      0, 'CHOT'),
        ttinfo( 36000,   3600, 'CHOST'),
        ttinfo( 32400,      0, 'CHOT'),
        ttinfo( 36000,   3600, 'CHOST'),
        ttinfo( 32400,      0, 'CHOT'),
        ttinfo( 36000,   3600, 'CHOST'),
        ttinfo( 32400,      0, 'CHOT'),
        ttinfo( 36000,   3600, 'CHOST'),
        ttinfo( 32400,      0, 'CHOT'),
        ttinfo( 36000,   3600, 'CHOST'),
        ttinfo( 32400,      0, 'CHOT'),
        ttinfo( 36000,   3600, 'CHOST'),
        ttinfo( 32400,      0, 'CHOT'),
        ttinfo( 36000,   3600, 'CHOST'),
        ttinfo( 32400,      0, 'CHOT'),
        ttinfo( 36000,   3600, 'CHOST'),
        ttinfo( 32400,      0, 'CHOT'),
        ttinfo( 36000,   3600, 'CHOST'),
        ttinfo( 32400,      0, 'CHOT'),
        ttinfo( 36000,   3600, 'CHOST'),
        ttinfo( 32400,      0, 'CHOT'),
        ttinfo( 36000,   3600, 'CHOST'),
        ttinfo( 32400,      0, 'CHOT'),
        ttinfo( 36000,   3600, 'CHOST'),
        ttinfo( 32400,      0, 'CHOT'),
        ttinfo( 36000,   3600, 'CHOST'),
        ttinfo( 32400,      0, 'CHOT'),
        ]

Choibalsan = Choibalsan() # Singleton

