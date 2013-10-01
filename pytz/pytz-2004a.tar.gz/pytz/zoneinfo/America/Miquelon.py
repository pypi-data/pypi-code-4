'''
tzinfo timezone information for America/Miquelon.

Generated from the Olson timezone database:
    ftp://elsie.nci.nih.gov/pub/tz*.tar.gz
'''

from pytz.tzinfo import DstTzInfo
from pytz.tzinfo import memorized_datetime as datetime
from pytz.tzinfo import memorized_ttinfo as ttinfo

class Miquelon(DstTzInfo):
    '''America/Miquelon timezone definition. See datetime.tzinfo for details'''

    _zone = 'America/Miquelon'

    _utc_transition_times = [
        datetime(   1,  1,  1,  0,  0,  0), # -13480     0 LMT
        datetime(1911,  5, 15,  3, 44, 40), # -14400     0 AST
        datetime(1980,  5,  1,  4,  0,  0), # -10800     0 PMST
        datetime(1987,  4,  5,  5,  0,  0), #  -7200  3600 PMDT
        datetime(1987, 10, 25,  4,  0,  0), # -10800     0 PMST
        datetime(1988,  4,  3,  5,  0,  0), #  -7200  3600 PMDT
        datetime(1988, 10, 30,  4,  0,  0), # -10800     0 PMST
        datetime(1989,  4,  2,  5,  0,  0), #  -7200  3600 PMDT
        datetime(1989, 10, 29,  4,  0,  0), # -10800     0 PMST
        datetime(1990,  4,  1,  5,  0,  0), #  -7200  3600 PMDT
        datetime(1990, 10, 28,  4,  0,  0), # -10800     0 PMST
        datetime(1991,  4,  7,  5,  0,  0), #  -7200  3600 PMDT
        datetime(1991, 10, 27,  4,  0,  0), # -10800     0 PMST
        datetime(1992,  4,  5,  5,  0,  0), #  -7200  3600 PMDT
        datetime(1992, 10, 25,  4,  0,  0), # -10800     0 PMST
        datetime(1993,  4,  4,  5,  0,  0), #  -7200  3600 PMDT
        datetime(1993, 10, 31,  4,  0,  0), # -10800     0 PMST
        datetime(1994,  4,  3,  5,  0,  0), #  -7200  3600 PMDT
        datetime(1994, 10, 30,  4,  0,  0), # -10800     0 PMST
        datetime(1995,  4,  2,  5,  0,  0), #  -7200  3600 PMDT
        datetime(1995, 10, 29,  4,  0,  0), # -10800     0 PMST
        datetime(1996,  4,  7,  5,  0,  0), #  -7200  3600 PMDT
        datetime(1996, 10, 27,  4,  0,  0), # -10800     0 PMST
        datetime(1997,  4,  6,  5,  0,  0), #  -7200  3600 PMDT
        datetime(1997, 10, 26,  4,  0,  0), # -10800     0 PMST
        datetime(1998,  4,  5,  5,  0,  0), #  -7200  3600 PMDT
        datetime(1998, 10, 25,  4,  0,  0), # -10800     0 PMST
        datetime(1999,  4,  4,  5,  0,  0), #  -7200  3600 PMDT
        datetime(1999, 10, 31,  4,  0,  0), # -10800     0 PMST
        datetime(2000,  4,  2,  5,  0,  0), #  -7200  3600 PMDT
        datetime(2000, 10, 29,  4,  0,  0), # -10800     0 PMST
        datetime(2001,  4,  1,  5,  0,  0), #  -7200  3600 PMDT
        datetime(2001, 10, 28,  4,  0,  0), # -10800     0 PMST
        datetime(2002,  4,  7,  5,  0,  0), #  -7200  3600 PMDT
        datetime(2002, 10, 27,  4,  0,  0), # -10800     0 PMST
        datetime(2003,  4,  6,  5,  0,  0), #  -7200  3600 PMDT
        datetime(2003, 10, 26,  4,  0,  0), # -10800     0 PMST
        datetime(2004,  4,  4,  5,  0,  0), #  -7200  3600 PMDT
        datetime(2004, 10, 31,  4,  0,  0), # -10800     0 PMST
        datetime(2005,  4,  3,  5,  0,  0), #  -7200  3600 PMDT
        datetime(2005, 10, 30,  4,  0,  0), # -10800     0 PMST
        datetime(2006,  4,  2,  5,  0,  0), #  -7200  3600 PMDT
        datetime(2006, 10, 29,  4,  0,  0), # -10800     0 PMST
        datetime(2007,  4,  1,  5,  0,  0), #  -7200  3600 PMDT
        datetime(2007, 10, 28,  4,  0,  0), # -10800     0 PMST
        datetime(2008,  4,  6,  5,  0,  0), #  -7200  3600 PMDT
        datetime(2008, 10, 26,  4,  0,  0), # -10800     0 PMST
        datetime(2009,  4,  5,  5,  0,  0), #  -7200  3600 PMDT
        datetime(2009, 10, 25,  4,  0,  0), # -10800     0 PMST
        datetime(2010,  4,  4,  5,  0,  0), #  -7200  3600 PMDT
        datetime(2010, 10, 31,  4,  0,  0), # -10800     0 PMST
        datetime(2011,  4,  3,  5,  0,  0), #  -7200  3600 PMDT
        datetime(2011, 10, 30,  4,  0,  0), # -10800     0 PMST
        datetime(2012,  4,  1,  5,  0,  0), #  -7200  3600 PMDT
        datetime(2012, 10, 28,  4,  0,  0), # -10800     0 PMST
        datetime(2013,  4,  7,  5,  0,  0), #  -7200  3600 PMDT
        datetime(2013, 10, 27,  4,  0,  0), # -10800     0 PMST
        datetime(2014,  4,  6,  5,  0,  0), #  -7200  3600 PMDT
        datetime(2014, 10, 26,  4,  0,  0), # -10800     0 PMST
        datetime(2015,  4,  5,  5,  0,  0), #  -7200  3600 PMDT
        datetime(2015, 10, 25,  4,  0,  0), # -10800     0 PMST
        datetime(2016,  4,  3,  5,  0,  0), #  -7200  3600 PMDT
        datetime(2016, 10, 30,  4,  0,  0), # -10800     0 PMST
        datetime(2017,  4,  2,  5,  0,  0), #  -7200  3600 PMDT
        datetime(2017, 10, 29,  4,  0,  0), # -10800     0 PMST
        datetime(2018,  4,  1,  5,  0,  0), #  -7200  3600 PMDT
        datetime(2018, 10, 28,  4,  0,  0), # -10800     0 PMST
        datetime(2019,  4,  7,  5,  0,  0), #  -7200  3600 PMDT
        datetime(2019, 10, 27,  4,  0,  0), # -10800     0 PMST
        datetime(2020,  4,  5,  5,  0,  0), #  -7200  3600 PMDT
        datetime(2020, 10, 25,  4,  0,  0), # -10800     0 PMST
        datetime(2021,  4,  4,  5,  0,  0), #  -7200  3600 PMDT
        datetime(2021, 10, 31,  4,  0,  0), # -10800     0 PMST
        datetime(2022,  4,  3,  5,  0,  0), #  -7200  3600 PMDT
        datetime(2022, 10, 30,  4,  0,  0), # -10800     0 PMST
        datetime(2023,  4,  2,  5,  0,  0), #  -7200  3600 PMDT
        datetime(2023, 10, 29,  4,  0,  0), # -10800     0 PMST
        datetime(2024,  4,  7,  5,  0,  0), #  -7200  3600 PMDT
        datetime(2024, 10, 27,  4,  0,  0), # -10800     0 PMST
        datetime(2025,  4,  6,  5,  0,  0), #  -7200  3600 PMDT
        datetime(2025, 10, 26,  4,  0,  0), # -10800     0 PMST
        datetime(2026,  4,  5,  5,  0,  0), #  -7200  3600 PMDT
        datetime(2026, 10, 25,  4,  0,  0), # -10800     0 PMST
        datetime(2027,  4,  4,  5,  0,  0), #  -7200  3600 PMDT
        datetime(2027, 10, 31,  4,  0,  0), # -10800     0 PMST
        datetime(2028,  4,  2,  5,  0,  0), #  -7200  3600 PMDT
        datetime(2028, 10, 29,  4,  0,  0), # -10800     0 PMST
        datetime(2029,  4,  1,  5,  0,  0), #  -7200  3600 PMDT
        datetime(2029, 10, 28,  4,  0,  0), # -10800     0 PMST
        datetime(2030,  4,  7,  5,  0,  0), #  -7200  3600 PMDT
        datetime(2030, 10, 27,  4,  0,  0), # -10800     0 PMST
        datetime(2031,  4,  6,  5,  0,  0), #  -7200  3600 PMDT
        datetime(2031, 10, 26,  4,  0,  0), # -10800     0 PMST
        datetime(2032,  4,  4,  5,  0,  0), #  -7200  3600 PMDT
        datetime(2032, 10, 31,  4,  0,  0), # -10800     0 PMST
        datetime(2033,  4,  3,  5,  0,  0), #  -7200  3600 PMDT
        datetime(2033, 10, 30,  4,  0,  0), # -10800     0 PMST
        datetime(2034,  4,  2,  5,  0,  0), #  -7200  3600 PMDT
        datetime(2034, 10, 29,  4,  0,  0), # -10800     0 PMST
        datetime(2035,  4,  1,  5,  0,  0), #  -7200  3600 PMDT
        datetime(2035, 10, 28,  4,  0,  0), # -10800     0 PMST
        datetime(2036,  4,  6,  5,  0,  0), #  -7200  3600 PMDT
        datetime(2036, 10, 26,  4,  0,  0), # -10800     0 PMST
        datetime(2037,  4,  5,  5,  0,  0), #  -7200  3600 PMDT
        datetime(2037, 10, 25,  4,  0,  0), # -10800     0 PMST
        ]

    _transition_info = [
        ttinfo(-13480,      0,  'LMT'),
        ttinfo(-14400,      0,  'AST'),
        ttinfo(-10800,      0, 'PMST'),
        ttinfo( -7200,   3600, 'PMDT'),
        ttinfo(-10800,      0, 'PMST'),
        ttinfo( -7200,   3600, 'PMDT'),
        ttinfo(-10800,      0, 'PMST'),
        ttinfo( -7200,   3600, 'PMDT'),
        ttinfo(-10800,      0, 'PMST'),
        ttinfo( -7200,   3600, 'PMDT'),
        ttinfo(-10800,      0, 'PMST'),
        ttinfo( -7200,   3600, 'PMDT'),
        ttinfo(-10800,      0, 'PMST'),
        ttinfo( -7200,   3600, 'PMDT'),
        ttinfo(-10800,      0, 'PMST'),
        ttinfo( -7200,   3600, 'PMDT'),
        ttinfo(-10800,      0, 'PMST'),
        ttinfo( -7200,   3600, 'PMDT'),
        ttinfo(-10800,      0, 'PMST'),
        ttinfo( -7200,   3600, 'PMDT'),
        ttinfo(-10800,      0, 'PMST'),
        ttinfo( -7200,   3600, 'PMDT'),
        ttinfo(-10800,      0, 'PMST'),
        ttinfo( -7200,   3600, 'PMDT'),
        ttinfo(-10800,      0, 'PMST'),
        ttinfo( -7200,   3600, 'PMDT'),
        ttinfo(-10800,      0, 'PMST'),
        ttinfo( -7200,   3600, 'PMDT'),
        ttinfo(-10800,      0, 'PMST'),
        ttinfo( -7200,   3600, 'PMDT'),
        ttinfo(-10800,      0, 'PMST'),
        ttinfo( -7200,   3600, 'PMDT'),
        ttinfo(-10800,      0, 'PMST'),
        ttinfo( -7200,   3600, 'PMDT'),
        ttinfo(-10800,      0, 'PMST'),
        ttinfo( -7200,   3600, 'PMDT'),
        ttinfo(-10800,      0, 'PMST'),
        ttinfo( -7200,   3600, 'PMDT'),
        ttinfo(-10800,      0, 'PMST'),
        ttinfo( -7200,   3600, 'PMDT'),
        ttinfo(-10800,      0, 'PMST'),
        ttinfo( -7200,   3600, 'PMDT'),
        ttinfo(-10800,      0, 'PMST'),
        ttinfo( -7200,   3600, 'PMDT'),
        ttinfo(-10800,      0, 'PMST'),
        ttinfo( -7200,   3600, 'PMDT'),
        ttinfo(-10800,      0, 'PMST'),
        ttinfo( -7200,   3600, 'PMDT'),
        ttinfo(-10800,      0, 'PMST'),
        ttinfo( -7200,   3600, 'PMDT'),
        ttinfo(-10800,      0, 'PMST'),
        ttinfo( -7200,   3600, 'PMDT'),
        ttinfo(-10800,      0, 'PMST'),
        ttinfo( -7200,   3600, 'PMDT'),
        ttinfo(-10800,      0, 'PMST'),
        ttinfo( -7200,   3600, 'PMDT'),
        ttinfo(-10800,      0, 'PMST'),
        ttinfo( -7200,   3600, 'PMDT'),
        ttinfo(-10800,      0, 'PMST'),
        ttinfo( -7200,   3600, 'PMDT'),
        ttinfo(-10800,      0, 'PMST'),
        ttinfo( -7200,   3600, 'PMDT'),
        ttinfo(-10800,      0, 'PMST'),
        ttinfo( -7200,   3600, 'PMDT'),
        ttinfo(-10800,      0, 'PMST'),
        ttinfo( -7200,   3600, 'PMDT'),
        ttinfo(-10800,      0, 'PMST'),
        ttinfo( -7200,   3600, 'PMDT'),
        ttinfo(-10800,      0, 'PMST'),
        ttinfo( -7200,   3600, 'PMDT'),
        ttinfo(-10800,      0, 'PMST'),
        ttinfo( -7200,   3600, 'PMDT'),
        ttinfo(-10800,      0, 'PMST'),
        ttinfo( -7200,   3600, 'PMDT'),
        ttinfo(-10800,      0, 'PMST'),
        ttinfo( -7200,   3600, 'PMDT'),
        ttinfo(-10800,      0, 'PMST'),
        ttinfo( -7200,   3600, 'PMDT'),
        ttinfo(-10800,      0, 'PMST'),
        ttinfo( -7200,   3600, 'PMDT'),
        ttinfo(-10800,      0, 'PMST'),
        ttinfo( -7200,   3600, 'PMDT'),
        ttinfo(-10800,      0, 'PMST'),
        ttinfo( -7200,   3600, 'PMDT'),
        ttinfo(-10800,      0, 'PMST'),
        ttinfo( -7200,   3600, 'PMDT'),
        ttinfo(-10800,      0, 'PMST'),
        ttinfo( -7200,   3600, 'PMDT'),
        ttinfo(-10800,      0, 'PMST'),
        ttinfo( -7200,   3600, 'PMDT'),
        ttinfo(-10800,      0, 'PMST'),
        ttinfo( -7200,   3600, 'PMDT'),
        ttinfo(-10800,      0, 'PMST'),
        ttinfo( -7200,   3600, 'PMDT'),
        ttinfo(-10800,      0, 'PMST'),
        ttinfo( -7200,   3600, 'PMDT'),
        ttinfo(-10800,      0, 'PMST'),
        ttinfo( -7200,   3600, 'PMDT'),
        ttinfo(-10800,      0, 'PMST'),
        ttinfo( -7200,   3600, 'PMDT'),
        ttinfo(-10800,      0, 'PMST'),
        ttinfo( -7200,   3600, 'PMDT'),
        ttinfo(-10800,      0, 'PMST'),
        ttinfo( -7200,   3600, 'PMDT'),
        ttinfo(-10800,      0, 'PMST'),
        ]

Miquelon = Miquelon() # Singleton

