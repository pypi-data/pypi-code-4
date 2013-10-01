'''
tzinfo timezone information for Asia/Ulaanbaatar.

Generated from the Olson timezone database:
    ftp://elsie.nci.nih.gov/pub/tz*.tar.gz
'''

from pytz.tzinfo import DstTzInfo
from pytz.tzinfo import memorized_datetime as datetime
from pytz.tzinfo import memorized_ttinfo as ttinfo

class Ulaanbaatar(DstTzInfo):
    '''Asia/Ulaanbaatar timezone definition. See datetime.tzinfo for details'''

    _zone = 'Asia/Ulaanbaatar'

    _utc_transition_times = [
        datetime(   1,  1,  1,  0,  0,  0), #  25652     0 LMT
        datetime(1905,  7, 31, 16, 52, 28), #  25200     0 ULAT
        datetime(1977, 12, 31, 17,  0,  0), #  28800     0 ULAT
        datetime(1983,  3, 31, 16,  0,  0), #  32400  3600 ULAST
        datetime(1983,  9, 30, 15,  0,  0), #  28800     0 ULAT
        datetime(1984,  3, 31, 16,  0,  0), #  32400  3600 ULAST
        datetime(1984,  9, 29, 18,  0,  0), #  28800     0 ULAT
        datetime(1985,  3, 30, 18,  0,  0), #  32400  3600 ULAST
        datetime(1985,  9, 28, 18,  0,  0), #  28800     0 ULAT
        datetime(1986,  3, 29, 18,  0,  0), #  32400  3600 ULAST
        datetime(1986,  9, 27, 18,  0,  0), #  28800     0 ULAT
        datetime(1987,  3, 28, 18,  0,  0), #  32400  3600 ULAST
        datetime(1987,  9, 26, 18,  0,  0), #  28800     0 ULAT
        datetime(1988,  3, 26, 18,  0,  0), #  32400  3600 ULAST
        datetime(1988,  9, 24, 18,  0,  0), #  28800     0 ULAT
        datetime(1989,  3, 25, 18,  0,  0), #  32400  3600 ULAST
        datetime(1989,  9, 23, 18,  0,  0), #  28800     0 ULAT
        datetime(1990,  3, 24, 18,  0,  0), #  32400  3600 ULAST
        datetime(1990,  9, 29, 18,  0,  0), #  28800     0 ULAT
        datetime(1991,  3, 30, 18,  0,  0), #  32400  3600 ULAST
        datetime(1991,  9, 28, 18,  0,  0), #  28800     0 ULAT
        datetime(1992,  3, 28, 18,  0,  0), #  32400  3600 ULAST
        datetime(1992,  9, 26, 18,  0,  0), #  28800     0 ULAT
        datetime(1993,  3, 27, 18,  0,  0), #  32400  3600 ULAST
        datetime(1993,  9, 25, 18,  0,  0), #  28800     0 ULAT
        datetime(1994,  3, 26, 18,  0,  0), #  32400  3600 ULAST
        datetime(1994,  9, 24, 18,  0,  0), #  28800     0 ULAT
        datetime(1995,  3, 25, 18,  0,  0), #  32400  3600 ULAST
        datetime(1995,  9, 23, 18,  0,  0), #  28800     0 ULAT
        datetime(1996,  3, 30, 18,  0,  0), #  32400  3600 ULAST
        datetime(1996,  9, 28, 18,  0,  0), #  28800     0 ULAT
        datetime(1997,  3, 29, 18,  0,  0), #  32400  3600 ULAST
        datetime(1997,  9, 27, 18,  0,  0), #  28800     0 ULAT
        datetime(1998,  3, 28, 18,  0,  0), #  32400  3600 ULAST
        datetime(1998,  9, 26, 18,  0,  0), #  28800     0 ULAT
        datetime(2001,  4, 27, 18,  0,  0), #  32400  3600 ULAST
        datetime(2001,  9, 28, 17,  0,  0), #  28800     0 ULAT
        datetime(2002,  3, 29, 18,  0,  0), #  32400  3600 ULAST
        datetime(2002,  9, 27, 17,  0,  0), #  28800     0 ULAT
        datetime(2003,  3, 28, 18,  0,  0), #  32400  3600 ULAST
        datetime(2003,  9, 26, 17,  0,  0), #  28800     0 ULAT
        datetime(2004,  3, 26, 18,  0,  0), #  32400  3600 ULAST
        datetime(2004,  9, 24, 17,  0,  0), #  28800     0 ULAT
        datetime(2005,  3, 25, 18,  0,  0), #  32400  3600 ULAST
        datetime(2005,  9, 23, 17,  0,  0), #  28800     0 ULAT
        datetime(2006,  3, 24, 18,  0,  0), #  32400  3600 ULAST
        datetime(2006,  9, 29, 17,  0,  0), #  28800     0 ULAT
        datetime(2007,  3, 30, 18,  0,  0), #  32400  3600 ULAST
        datetime(2007,  9, 28, 17,  0,  0), #  28800     0 ULAT
        datetime(2008,  3, 28, 18,  0,  0), #  32400  3600 ULAST
        datetime(2008,  9, 26, 17,  0,  0), #  28800     0 ULAT
        datetime(2009,  3, 27, 18,  0,  0), #  32400  3600 ULAST
        datetime(2009,  9, 25, 17,  0,  0), #  28800     0 ULAT
        datetime(2010,  3, 26, 18,  0,  0), #  32400  3600 ULAST
        datetime(2010,  9, 24, 17,  0,  0), #  28800     0 ULAT
        datetime(2011,  3, 25, 18,  0,  0), #  32400  3600 ULAST
        datetime(2011,  9, 23, 17,  0,  0), #  28800     0 ULAT
        datetime(2012,  3, 30, 18,  0,  0), #  32400  3600 ULAST
        datetime(2012,  9, 28, 17,  0,  0), #  28800     0 ULAT
        datetime(2013,  3, 29, 18,  0,  0), #  32400  3600 ULAST
        datetime(2013,  9, 27, 17,  0,  0), #  28800     0 ULAT
        datetime(2014,  3, 28, 18,  0,  0), #  32400  3600 ULAST
        datetime(2014,  9, 26, 17,  0,  0), #  28800     0 ULAT
        datetime(2015,  3, 27, 18,  0,  0), #  32400  3600 ULAST
        datetime(2015,  9, 25, 17,  0,  0), #  28800     0 ULAT
        datetime(2016,  3, 25, 18,  0,  0), #  32400  3600 ULAST
        datetime(2016,  9, 23, 17,  0,  0), #  28800     0 ULAT
        datetime(2017,  3, 24, 18,  0,  0), #  32400  3600 ULAST
        datetime(2017,  9, 29, 17,  0,  0), #  28800     0 ULAT
        datetime(2018,  3, 30, 18,  0,  0), #  32400  3600 ULAST
        datetime(2018,  9, 28, 17,  0,  0), #  28800     0 ULAT
        datetime(2019,  3, 29, 18,  0,  0), #  32400  3600 ULAST
        datetime(2019,  9, 27, 17,  0,  0), #  28800     0 ULAT
        datetime(2020,  3, 27, 18,  0,  0), #  32400  3600 ULAST
        datetime(2020,  9, 25, 17,  0,  0), #  28800     0 ULAT
        datetime(2021,  3, 26, 18,  0,  0), #  32400  3600 ULAST
        datetime(2021,  9, 24, 17,  0,  0), #  28800     0 ULAT
        datetime(2022,  3, 25, 18,  0,  0), #  32400  3600 ULAST
        datetime(2022,  9, 23, 17,  0,  0), #  28800     0 ULAT
        datetime(2023,  3, 24, 18,  0,  0), #  32400  3600 ULAST
        datetime(2023,  9, 29, 17,  0,  0), #  28800     0 ULAT
        datetime(2024,  3, 29, 18,  0,  0), #  32400  3600 ULAST
        datetime(2024,  9, 27, 17,  0,  0), #  28800     0 ULAT
        datetime(2025,  3, 28, 18,  0,  0), #  32400  3600 ULAST
        datetime(2025,  9, 26, 17,  0,  0), #  28800     0 ULAT
        datetime(2026,  3, 27, 18,  0,  0), #  32400  3600 ULAST
        datetime(2026,  9, 25, 17,  0,  0), #  28800     0 ULAT
        datetime(2027,  3, 26, 18,  0,  0), #  32400  3600 ULAST
        datetime(2027,  9, 24, 17,  0,  0), #  28800     0 ULAT
        datetime(2028,  3, 24, 18,  0,  0), #  32400  3600 ULAST
        datetime(2028,  9, 29, 17,  0,  0), #  28800     0 ULAT
        datetime(2029,  3, 30, 18,  0,  0), #  32400  3600 ULAST
        datetime(2029,  9, 28, 17,  0,  0), #  28800     0 ULAT
        datetime(2030,  3, 29, 18,  0,  0), #  32400  3600 ULAST
        datetime(2030,  9, 27, 17,  0,  0), #  28800     0 ULAT
        datetime(2031,  3, 28, 18,  0,  0), #  32400  3600 ULAST
        datetime(2031,  9, 26, 17,  0,  0), #  28800     0 ULAT
        datetime(2032,  3, 26, 18,  0,  0), #  32400  3600 ULAST
        datetime(2032,  9, 24, 17,  0,  0), #  28800     0 ULAT
        datetime(2033,  3, 25, 18,  0,  0), #  32400  3600 ULAST
        datetime(2033,  9, 23, 17,  0,  0), #  28800     0 ULAT
        datetime(2034,  3, 24, 18,  0,  0), #  32400  3600 ULAST
        datetime(2034,  9, 29, 17,  0,  0), #  28800     0 ULAT
        datetime(2035,  3, 30, 18,  0,  0), #  32400  3600 ULAST
        datetime(2035,  9, 28, 17,  0,  0), #  28800     0 ULAT
        datetime(2036,  3, 28, 18,  0,  0), #  32400  3600 ULAST
        datetime(2036,  9, 26, 17,  0,  0), #  28800     0 ULAT
        datetime(2037,  3, 27, 18,  0,  0), #  32400  3600 ULAST
        datetime(2037,  9, 25, 17,  0,  0), #  28800     0 ULAT
        ]

    _transition_info = [
        ttinfo( 25652,      0,  'LMT'),
        ttinfo( 25200,      0, 'ULAT'),
        ttinfo( 28800,      0, 'ULAT'),
        ttinfo( 32400,   3600, 'ULAST'),
        ttinfo( 28800,      0, 'ULAT'),
        ttinfo( 32400,   3600, 'ULAST'),
        ttinfo( 28800,      0, 'ULAT'),
        ttinfo( 32400,   3600, 'ULAST'),
        ttinfo( 28800,      0, 'ULAT'),
        ttinfo( 32400,   3600, 'ULAST'),
        ttinfo( 28800,      0, 'ULAT'),
        ttinfo( 32400,   3600, 'ULAST'),
        ttinfo( 28800,      0, 'ULAT'),
        ttinfo( 32400,   3600, 'ULAST'),
        ttinfo( 28800,      0, 'ULAT'),
        ttinfo( 32400,   3600, 'ULAST'),
        ttinfo( 28800,      0, 'ULAT'),
        ttinfo( 32400,   3600, 'ULAST'),
        ttinfo( 28800,      0, 'ULAT'),
        ttinfo( 32400,   3600, 'ULAST'),
        ttinfo( 28800,      0, 'ULAT'),
        ttinfo( 32400,   3600, 'ULAST'),
        ttinfo( 28800,      0, 'ULAT'),
        ttinfo( 32400,   3600, 'ULAST'),
        ttinfo( 28800,      0, 'ULAT'),
        ttinfo( 32400,   3600, 'ULAST'),
        ttinfo( 28800,      0, 'ULAT'),
        ttinfo( 32400,   3600, 'ULAST'),
        ttinfo( 28800,      0, 'ULAT'),
        ttinfo( 32400,   3600, 'ULAST'),
        ttinfo( 28800,      0, 'ULAT'),
        ttinfo( 32400,   3600, 'ULAST'),
        ttinfo( 28800,      0, 'ULAT'),
        ttinfo( 32400,   3600, 'ULAST'),
        ttinfo( 28800,      0, 'ULAT'),
        ttinfo( 32400,   3600, 'ULAST'),
        ttinfo( 28800,      0, 'ULAT'),
        ttinfo( 32400,   3600, 'ULAST'),
        ttinfo( 28800,      0, 'ULAT'),
        ttinfo( 32400,   3600, 'ULAST'),
        ttinfo( 28800,      0, 'ULAT'),
        ttinfo( 32400,   3600, 'ULAST'),
        ttinfo( 28800,      0, 'ULAT'),
        ttinfo( 32400,   3600, 'ULAST'),
        ttinfo( 28800,      0, 'ULAT'),
        ttinfo( 32400,   3600, 'ULAST'),
        ttinfo( 28800,      0, 'ULAT'),
        ttinfo( 32400,   3600, 'ULAST'),
        ttinfo( 28800,      0, 'ULAT'),
        ttinfo( 32400,   3600, 'ULAST'),
        ttinfo( 28800,      0, 'ULAT'),
        ttinfo( 32400,   3600, 'ULAST'),
        ttinfo( 28800,      0, 'ULAT'),
        ttinfo( 32400,   3600, 'ULAST'),
        ttinfo( 28800,      0, 'ULAT'),
        ttinfo( 32400,   3600, 'ULAST'),
        ttinfo( 28800,      0, 'ULAT'),
        ttinfo( 32400,   3600, 'ULAST'),
        ttinfo( 28800,      0, 'ULAT'),
        ttinfo( 32400,   3600, 'ULAST'),
        ttinfo( 28800,      0, 'ULAT'),
        ttinfo( 32400,   3600, 'ULAST'),
        ttinfo( 28800,      0, 'ULAT'),
        ttinfo( 32400,   3600, 'ULAST'),
        ttinfo( 28800,      0, 'ULAT'),
        ttinfo( 32400,   3600, 'ULAST'),
        ttinfo( 28800,      0, 'ULAT'),
        ttinfo( 32400,   3600, 'ULAST'),
        ttinfo( 28800,      0, 'ULAT'),
        ttinfo( 32400,   3600, 'ULAST'),
        ttinfo( 28800,      0, 'ULAT'),
        ttinfo( 32400,   3600, 'ULAST'),
        ttinfo( 28800,      0, 'ULAT'),
        ttinfo( 32400,   3600, 'ULAST'),
        ttinfo( 28800,      0, 'ULAT'),
        ttinfo( 32400,   3600, 'ULAST'),
        ttinfo( 28800,      0, 'ULAT'),
        ttinfo( 32400,   3600, 'ULAST'),
        ttinfo( 28800,      0, 'ULAT'),
        ttinfo( 32400,   3600, 'ULAST'),
        ttinfo( 28800,      0, 'ULAT'),
        ttinfo( 32400,   3600, 'ULAST'),
        ttinfo( 28800,      0, 'ULAT'),
        ttinfo( 32400,   3600, 'ULAST'),
        ttinfo( 28800,      0, 'ULAT'),
        ttinfo( 32400,   3600, 'ULAST'),
        ttinfo( 28800,      0, 'ULAT'),
        ttinfo( 32400,   3600, 'ULAST'),
        ttinfo( 28800,      0, 'ULAT'),
        ttinfo( 32400,   3600, 'ULAST'),
        ttinfo( 28800,      0, 'ULAT'),
        ttinfo( 32400,   3600, 'ULAST'),
        ttinfo( 28800,      0, 'ULAT'),
        ttinfo( 32400,   3600, 'ULAST'),
        ttinfo( 28800,      0, 'ULAT'),
        ttinfo( 32400,   3600, 'ULAST'),
        ttinfo( 28800,      0, 'ULAT'),
        ttinfo( 32400,   3600, 'ULAST'),
        ttinfo( 28800,      0, 'ULAT'),
        ttinfo( 32400,   3600, 'ULAST'),
        ttinfo( 28800,      0, 'ULAT'),
        ttinfo( 32400,   3600, 'ULAST'),
        ttinfo( 28800,      0, 'ULAT'),
        ttinfo( 32400,   3600, 'ULAST'),
        ttinfo( 28800,      0, 'ULAT'),
        ttinfo( 32400,   3600, 'ULAST'),
        ttinfo( 28800,      0, 'ULAT'),
        ttinfo( 32400,   3600, 'ULAST'),
        ttinfo( 28800,      0, 'ULAT'),
        ]

Ulaanbaatar = Ulaanbaatar() # Singleton

