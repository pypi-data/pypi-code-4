'''
tzinfo timezone information for Asia/Yakutsk.

Generated from the Olson timezone database:
    ftp://elsie.nci.nih.gov/pub/tz*.tar.gz
'''

from pytz.tzinfo import DstTzInfo
from pytz.tzinfo import memorized_datetime as datetime
from pytz.tzinfo import memorized_ttinfo as ttinfo

class Yakutsk(DstTzInfo):
    '''Asia/Yakutsk timezone definition. See datetime.tzinfo for details'''

    _zone = 'Asia/Yakutsk'

    _utc_transition_times = [
        datetime(   1,  1,  1,  0,  0,  0), #  31120     0 LMT
        datetime(1919, 12, 14, 15, 21, 20), #  28800     0 YAKT
        datetime(1930,  6, 20, 16,  0,  0), #  32400     0 YAKT
        datetime(1981,  3, 31, 15,  0,  0), #  36000  3600 YAKST
        datetime(1981,  9, 30, 14,  0,  0), #  32400     0 YAKT
        datetime(1982,  3, 31, 15,  0,  0), #  36000  3600 YAKST
        datetime(1982,  9, 30, 14,  0,  0), #  32400     0 YAKT
        datetime(1983,  3, 31, 15,  0,  0), #  36000  3600 YAKST
        datetime(1983,  9, 30, 14,  0,  0), #  32400     0 YAKT
        datetime(1984,  3, 31, 15,  0,  0), #  36000  3600 YAKST
        datetime(1984,  9, 29, 17,  0,  0), #  32400     0 YAKT
        datetime(1985,  3, 30, 17,  0,  0), #  36000  3600 YAKST
        datetime(1985,  9, 28, 17,  0,  0), #  32400     0 YAKT
        datetime(1986,  3, 29, 17,  0,  0), #  36000  3600 YAKST
        datetime(1986,  9, 27, 17,  0,  0), #  32400     0 YAKT
        datetime(1987,  3, 28, 17,  0,  0), #  36000  3600 YAKST
        datetime(1987,  9, 26, 17,  0,  0), #  32400     0 YAKT
        datetime(1988,  3, 26, 17,  0,  0), #  36000  3600 YAKST
        datetime(1988,  9, 24, 17,  0,  0), #  32400     0 YAKT
        datetime(1989,  3, 25, 17,  0,  0), #  36000  3600 YAKST
        datetime(1989,  9, 23, 17,  0,  0), #  32400     0 YAKT
        datetime(1990,  3, 24, 17,  0,  0), #  36000  3600 YAKST
        datetime(1990,  9, 29, 17,  0,  0), #  32400     0 YAKT
        datetime(1991,  3, 30, 17,  0,  0), #  32400     0 YAKST
        datetime(1991,  9, 28, 18,  0,  0), #  28800     0 YAKT
        datetime(1992,  1, 18, 18,  0,  0), #  32400     0 YAKT
        datetime(1992,  3, 28, 14,  0,  0), #  36000  3600 YAKST
        datetime(1992,  9, 26, 13,  0,  0), #  32400     0 YAKT
        datetime(1993,  3, 27, 17,  0,  0), #  36000  3600 YAKST
        datetime(1993,  9, 25, 17,  0,  0), #  32400     0 YAKT
        datetime(1994,  3, 26, 17,  0,  0), #  36000  3600 YAKST
        datetime(1994,  9, 24, 17,  0,  0), #  32400     0 YAKT
        datetime(1995,  3, 25, 17,  0,  0), #  36000  3600 YAKST
        datetime(1995,  9, 23, 17,  0,  0), #  32400     0 YAKT
        datetime(1996,  3, 30, 17,  0,  0), #  36000  3600 YAKST
        datetime(1996, 10, 26, 17,  0,  0), #  32400     0 YAKT
        datetime(1997,  3, 29, 17,  0,  0), #  36000  3600 YAKST
        datetime(1997, 10, 25, 17,  0,  0), #  32400     0 YAKT
        datetime(1998,  3, 28, 17,  0,  0), #  36000  3600 YAKST
        datetime(1998, 10, 24, 17,  0,  0), #  32400     0 YAKT
        datetime(1999,  3, 27, 17,  0,  0), #  36000  3600 YAKST
        datetime(1999, 10, 30, 17,  0,  0), #  32400     0 YAKT
        datetime(2000,  3, 25, 17,  0,  0), #  36000  3600 YAKST
        datetime(2000, 10, 28, 17,  0,  0), #  32400     0 YAKT
        datetime(2001,  3, 24, 17,  0,  0), #  36000  3600 YAKST
        datetime(2001, 10, 27, 17,  0,  0), #  32400     0 YAKT
        datetime(2002,  3, 30, 17,  0,  0), #  36000  3600 YAKST
        datetime(2002, 10, 26, 17,  0,  0), #  32400     0 YAKT
        datetime(2003,  3, 29, 17,  0,  0), #  36000  3600 YAKST
        datetime(2003, 10, 25, 17,  0,  0), #  32400     0 YAKT
        datetime(2004,  3, 27, 17,  0,  0), #  36000  3600 YAKST
        datetime(2004, 10, 30, 17,  0,  0), #  32400     0 YAKT
        datetime(2005,  3, 26, 17,  0,  0), #  36000  3600 YAKST
        datetime(2005, 10, 29, 17,  0,  0), #  32400     0 YAKT
        datetime(2006,  3, 25, 17,  0,  0), #  36000  3600 YAKST
        datetime(2006, 10, 28, 17,  0,  0), #  32400     0 YAKT
        datetime(2007,  3, 24, 17,  0,  0), #  36000  3600 YAKST
        datetime(2007, 10, 27, 17,  0,  0), #  32400     0 YAKT
        datetime(2008,  3, 29, 17,  0,  0), #  36000  3600 YAKST
        datetime(2008, 10, 25, 17,  0,  0), #  32400     0 YAKT
        datetime(2009,  3, 28, 17,  0,  0), #  36000  3600 YAKST
        datetime(2009, 10, 24, 17,  0,  0), #  32400     0 YAKT
        datetime(2010,  3, 27, 17,  0,  0), #  36000  3600 YAKST
        datetime(2010, 10, 30, 17,  0,  0), #  32400     0 YAKT
        datetime(2011,  3, 26, 17,  0,  0), #  36000  3600 YAKST
        datetime(2011, 10, 29, 17,  0,  0), #  32400     0 YAKT
        datetime(2012,  3, 24, 17,  0,  0), #  36000  3600 YAKST
        datetime(2012, 10, 27, 17,  0,  0), #  32400     0 YAKT
        datetime(2013,  3, 30, 17,  0,  0), #  36000  3600 YAKST
        datetime(2013, 10, 26, 17,  0,  0), #  32400     0 YAKT
        datetime(2014,  3, 29, 17,  0,  0), #  36000  3600 YAKST
        datetime(2014, 10, 25, 17,  0,  0), #  32400     0 YAKT
        datetime(2015,  3, 28, 17,  0,  0), #  36000  3600 YAKST
        datetime(2015, 10, 24, 17,  0,  0), #  32400     0 YAKT
        datetime(2016,  3, 26, 17,  0,  0), #  36000  3600 YAKST
        datetime(2016, 10, 29, 17,  0,  0), #  32400     0 YAKT
        datetime(2017,  3, 25, 17,  0,  0), #  36000  3600 YAKST
        datetime(2017, 10, 28, 17,  0,  0), #  32400     0 YAKT
        datetime(2018,  3, 24, 17,  0,  0), #  36000  3600 YAKST
        datetime(2018, 10, 27, 17,  0,  0), #  32400     0 YAKT
        datetime(2019,  3, 30, 17,  0,  0), #  36000  3600 YAKST
        datetime(2019, 10, 26, 17,  0,  0), #  32400     0 YAKT
        datetime(2020,  3, 28, 17,  0,  0), #  36000  3600 YAKST
        datetime(2020, 10, 24, 17,  0,  0), #  32400     0 YAKT
        datetime(2021,  3, 27, 17,  0,  0), #  36000  3600 YAKST
        datetime(2021, 10, 30, 17,  0,  0), #  32400     0 YAKT
        datetime(2022,  3, 26, 17,  0,  0), #  36000  3600 YAKST
        datetime(2022, 10, 29, 17,  0,  0), #  32400     0 YAKT
        datetime(2023,  3, 25, 17,  0,  0), #  36000  3600 YAKST
        datetime(2023, 10, 28, 17,  0,  0), #  32400     0 YAKT
        datetime(2024,  3, 30, 17,  0,  0), #  36000  3600 YAKST
        datetime(2024, 10, 26, 17,  0,  0), #  32400     0 YAKT
        datetime(2025,  3, 29, 17,  0,  0), #  36000  3600 YAKST
        datetime(2025, 10, 25, 17,  0,  0), #  32400     0 YAKT
        datetime(2026,  3, 28, 17,  0,  0), #  36000  3600 YAKST
        datetime(2026, 10, 24, 17,  0,  0), #  32400     0 YAKT
        datetime(2027,  3, 27, 17,  0,  0), #  36000  3600 YAKST
        datetime(2027, 10, 30, 17,  0,  0), #  32400     0 YAKT
        datetime(2028,  3, 25, 17,  0,  0), #  36000  3600 YAKST
        datetime(2028, 10, 28, 17,  0,  0), #  32400     0 YAKT
        datetime(2029,  3, 24, 17,  0,  0), #  36000  3600 YAKST
        datetime(2029, 10, 27, 17,  0,  0), #  32400     0 YAKT
        datetime(2030,  3, 30, 17,  0,  0), #  36000  3600 YAKST
        datetime(2030, 10, 26, 17,  0,  0), #  32400     0 YAKT
        datetime(2031,  3, 29, 17,  0,  0), #  36000  3600 YAKST
        datetime(2031, 10, 25, 17,  0,  0), #  32400     0 YAKT
        datetime(2032,  3, 27, 17,  0,  0), #  36000  3600 YAKST
        datetime(2032, 10, 30, 17,  0,  0), #  32400     0 YAKT
        datetime(2033,  3, 26, 17,  0,  0), #  36000  3600 YAKST
        datetime(2033, 10, 29, 17,  0,  0), #  32400     0 YAKT
        datetime(2034,  3, 25, 17,  0,  0), #  36000  3600 YAKST
        datetime(2034, 10, 28, 17,  0,  0), #  32400     0 YAKT
        datetime(2035,  3, 24, 17,  0,  0), #  36000  3600 YAKST
        datetime(2035, 10, 27, 17,  0,  0), #  32400     0 YAKT
        datetime(2036,  3, 29, 17,  0,  0), #  36000  3600 YAKST
        datetime(2036, 10, 25, 17,  0,  0), #  32400     0 YAKT
        datetime(2037,  3, 28, 17,  0,  0), #  36000  3600 YAKST
        datetime(2037, 10, 24, 17,  0,  0), #  32400     0 YAKT
        ]

    _transition_info = [
        ttinfo( 31120,      0,  'LMT'),
        ttinfo( 28800,      0, 'YAKT'),
        ttinfo( 32400,      0, 'YAKT'),
        ttinfo( 36000,   3600, 'YAKST'),
        ttinfo( 32400,      0, 'YAKT'),
        ttinfo( 36000,   3600, 'YAKST'),
        ttinfo( 32400,      0, 'YAKT'),
        ttinfo( 36000,   3600, 'YAKST'),
        ttinfo( 32400,      0, 'YAKT'),
        ttinfo( 36000,   3600, 'YAKST'),
        ttinfo( 32400,      0, 'YAKT'),
        ttinfo( 36000,   3600, 'YAKST'),
        ttinfo( 32400,      0, 'YAKT'),
        ttinfo( 36000,   3600, 'YAKST'),
        ttinfo( 32400,      0, 'YAKT'),
        ttinfo( 36000,   3600, 'YAKST'),
        ttinfo( 32400,      0, 'YAKT'),
        ttinfo( 36000,   3600, 'YAKST'),
        ttinfo( 32400,      0, 'YAKT'),
        ttinfo( 36000,   3600, 'YAKST'),
        ttinfo( 32400,      0, 'YAKT'),
        ttinfo( 36000,   3600, 'YAKST'),
        ttinfo( 32400,      0, 'YAKT'),
        ttinfo( 32400,      0, 'YAKST'),
        ttinfo( 28800,      0, 'YAKT'),
        ttinfo( 32400,      0, 'YAKT'),
        ttinfo( 36000,   3600, 'YAKST'),
        ttinfo( 32400,      0, 'YAKT'),
        ttinfo( 36000,   3600, 'YAKST'),
        ttinfo( 32400,      0, 'YAKT'),
        ttinfo( 36000,   3600, 'YAKST'),
        ttinfo( 32400,      0, 'YAKT'),
        ttinfo( 36000,   3600, 'YAKST'),
        ttinfo( 32400,      0, 'YAKT'),
        ttinfo( 36000,   3600, 'YAKST'),
        ttinfo( 32400,      0, 'YAKT'),
        ttinfo( 36000,   3600, 'YAKST'),
        ttinfo( 32400,      0, 'YAKT'),
        ttinfo( 36000,   3600, 'YAKST'),
        ttinfo( 32400,      0, 'YAKT'),
        ttinfo( 36000,   3600, 'YAKST'),
        ttinfo( 32400,      0, 'YAKT'),
        ttinfo( 36000,   3600, 'YAKST'),
        ttinfo( 32400,      0, 'YAKT'),
        ttinfo( 36000,   3600, 'YAKST'),
        ttinfo( 32400,      0, 'YAKT'),
        ttinfo( 36000,   3600, 'YAKST'),
        ttinfo( 32400,      0, 'YAKT'),
        ttinfo( 36000,   3600, 'YAKST'),
        ttinfo( 32400,      0, 'YAKT'),
        ttinfo( 36000,   3600, 'YAKST'),
        ttinfo( 32400,      0, 'YAKT'),
        ttinfo( 36000,   3600, 'YAKST'),
        ttinfo( 32400,      0, 'YAKT'),
        ttinfo( 36000,   3600, 'YAKST'),
        ttinfo( 32400,      0, 'YAKT'),
        ttinfo( 36000,   3600, 'YAKST'),
        ttinfo( 32400,      0, 'YAKT'),
        ttinfo( 36000,   3600, 'YAKST'),
        ttinfo( 32400,      0, 'YAKT'),
        ttinfo( 36000,   3600, 'YAKST'),
        ttinfo( 32400,      0, 'YAKT'),
        ttinfo( 36000,   3600, 'YAKST'),
        ttinfo( 32400,      0, 'YAKT'),
        ttinfo( 36000,   3600, 'YAKST'),
        ttinfo( 32400,      0, 'YAKT'),
        ttinfo( 36000,   3600, 'YAKST'),
        ttinfo( 32400,      0, 'YAKT'),
        ttinfo( 36000,   3600, 'YAKST'),
        ttinfo( 32400,      0, 'YAKT'),
        ttinfo( 36000,   3600, 'YAKST'),
        ttinfo( 32400,      0, 'YAKT'),
        ttinfo( 36000,   3600, 'YAKST'),
        ttinfo( 32400,      0, 'YAKT'),
        ttinfo( 36000,   3600, 'YAKST'),
        ttinfo( 32400,      0, 'YAKT'),
        ttinfo( 36000,   3600, 'YAKST'),
        ttinfo( 32400,      0, 'YAKT'),
        ttinfo( 36000,   3600, 'YAKST'),
        ttinfo( 32400,      0, 'YAKT'),
        ttinfo( 36000,   3600, 'YAKST'),
        ttinfo( 32400,      0, 'YAKT'),
        ttinfo( 36000,   3600, 'YAKST'),
        ttinfo( 32400,      0, 'YAKT'),
        ttinfo( 36000,   3600, 'YAKST'),
        ttinfo( 32400,      0, 'YAKT'),
        ttinfo( 36000,   3600, 'YAKST'),
        ttinfo( 32400,      0, 'YAKT'),
        ttinfo( 36000,   3600, 'YAKST'),
        ttinfo( 32400,      0, 'YAKT'),
        ttinfo( 36000,   3600, 'YAKST'),
        ttinfo( 32400,      0, 'YAKT'),
        ttinfo( 36000,   3600, 'YAKST'),
        ttinfo( 32400,      0, 'YAKT'),
        ttinfo( 36000,   3600, 'YAKST'),
        ttinfo( 32400,      0, 'YAKT'),
        ttinfo( 36000,   3600, 'YAKST'),
        ttinfo( 32400,      0, 'YAKT'),
        ttinfo( 36000,   3600, 'YAKST'),
        ttinfo( 32400,      0, 'YAKT'),
        ttinfo( 36000,   3600, 'YAKST'),
        ttinfo( 32400,      0, 'YAKT'),
        ttinfo( 36000,   3600, 'YAKST'),
        ttinfo( 32400,      0, 'YAKT'),
        ttinfo( 36000,   3600, 'YAKST'),
        ttinfo( 32400,      0, 'YAKT'),
        ttinfo( 36000,   3600, 'YAKST'),
        ttinfo( 32400,      0, 'YAKT'),
        ttinfo( 36000,   3600, 'YAKST'),
        ttinfo( 32400,      0, 'YAKT'),
        ttinfo( 36000,   3600, 'YAKST'),
        ttinfo( 32400,      0, 'YAKT'),
        ttinfo( 36000,   3600, 'YAKST'),
        ttinfo( 32400,      0, 'YAKT'),
        ttinfo( 36000,   3600, 'YAKST'),
        ttinfo( 32400,      0, 'YAKT'),
        ttinfo( 36000,   3600, 'YAKST'),
        ttinfo( 32400,      0, 'YAKT'),
        ]

Yakutsk = Yakutsk() # Singleton

