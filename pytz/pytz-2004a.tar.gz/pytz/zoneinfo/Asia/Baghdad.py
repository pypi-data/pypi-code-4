'''
tzinfo timezone information for Asia/Baghdad.

Generated from the Olson timezone database:
    ftp://elsie.nci.nih.gov/pub/tz*.tar.gz
'''

from pytz.tzinfo import DstTzInfo
from pytz.tzinfo import memorized_datetime as datetime
from pytz.tzinfo import memorized_ttinfo as ttinfo

class Baghdad(DstTzInfo):
    '''Asia/Baghdad timezone definition. See datetime.tzinfo for details'''

    _zone = 'Asia/Baghdad'

    _utc_transition_times = [
        datetime(   1,  1,  1,  0,  0,  0), #  10656     0 BMT
        datetime(1917, 12, 31, 21,  2, 24), #  10800     0 AST
        datetime(1982,  4, 30, 21,  0,  0), #  14400  3600 ADT
        datetime(1982,  9, 30, 20,  0,  0), #  10800     0 AST
        datetime(1983,  3, 30, 21,  0,  0), #  14400  3600 ADT
        datetime(1983,  9, 30, 20,  0,  0), #  10800     0 AST
        datetime(1984,  3, 31, 21,  0,  0), #  14400  3600 ADT
        datetime(1984,  9, 30, 20,  0,  0), #  10800     0 AST
        datetime(1985,  3, 31, 21,  0,  0), #  14400  3600 ADT
        datetime(1985,  9, 28, 22,  0,  0), #  10800     0 AST
        datetime(1986,  3, 29, 22,  0,  0), #  14400  3600 ADT
        datetime(1986,  9, 27, 22,  0,  0), #  10800     0 AST
        datetime(1987,  3, 28, 22,  0,  0), #  14400  3600 ADT
        datetime(1987,  9, 26, 22,  0,  0), #  10800     0 AST
        datetime(1988,  3, 26, 22,  0,  0), #  14400  3600 ADT
        datetime(1988,  9, 24, 22,  0,  0), #  10800     0 AST
        datetime(1989,  3, 25, 22,  0,  0), #  14400  3600 ADT
        datetime(1989,  9, 23, 22,  0,  0), #  10800     0 AST
        datetime(1990,  3, 24, 22,  0,  0), #  14400  3600 ADT
        datetime(1990,  9, 29, 22,  0,  0), #  10800     0 AST
        datetime(1991,  4,  1,  0,  0,  0), #  14400  3600 ADT
        datetime(1991, 10,  1,  0,  0,  0), #  10800     0 AST
        datetime(1992,  4,  1,  0,  0,  0), #  14400  3600 ADT
        datetime(1992, 10,  1,  0,  0,  0), #  10800     0 AST
        datetime(1993,  4,  1,  0,  0,  0), #  14400  3600 ADT
        datetime(1993, 10,  1,  0,  0,  0), #  10800     0 AST
        datetime(1994,  4,  1,  0,  0,  0), #  14400  3600 ADT
        datetime(1994, 10,  1,  0,  0,  0), #  10800     0 AST
        datetime(1995,  4,  1,  0,  0,  0), #  14400  3600 ADT
        datetime(1995, 10,  1,  0,  0,  0), #  10800     0 AST
        datetime(1996,  4,  1,  0,  0,  0), #  14400  3600 ADT
        datetime(1996, 10,  1,  0,  0,  0), #  10800     0 AST
        datetime(1997,  4,  1,  0,  0,  0), #  14400  3600 ADT
        datetime(1997, 10,  1,  0,  0,  0), #  10800     0 AST
        datetime(1998,  4,  1,  0,  0,  0), #  14400  3600 ADT
        datetime(1998, 10,  1,  0,  0,  0), #  10800     0 AST
        datetime(1999,  4,  1,  0,  0,  0), #  14400  3600 ADT
        datetime(1999, 10,  1,  0,  0,  0), #  10800     0 AST
        datetime(2000,  4,  1,  0,  0,  0), #  14400  3600 ADT
        datetime(2000, 10,  1,  0,  0,  0), #  10800     0 AST
        datetime(2001,  4,  1,  0,  0,  0), #  14400  3600 ADT
        datetime(2001, 10,  1,  0,  0,  0), #  10800     0 AST
        datetime(2002,  4,  1,  0,  0,  0), #  14400  3600 ADT
        datetime(2002, 10,  1,  0,  0,  0), #  10800     0 AST
        datetime(2003,  4,  1,  0,  0,  0), #  14400  3600 ADT
        datetime(2003, 10,  1,  0,  0,  0), #  10800     0 AST
        datetime(2004,  4,  1,  0,  0,  0), #  14400  3600 ADT
        datetime(2004, 10,  1,  0,  0,  0), #  10800     0 AST
        datetime(2005,  4,  1,  0,  0,  0), #  14400  3600 ADT
        datetime(2005, 10,  1,  0,  0,  0), #  10800     0 AST
        datetime(2006,  4,  1,  0,  0,  0), #  14400  3600 ADT
        datetime(2006, 10,  1,  0,  0,  0), #  10800     0 AST
        datetime(2007,  4,  1,  0,  0,  0), #  14400  3600 ADT
        datetime(2007, 10,  1,  0,  0,  0), #  10800     0 AST
        datetime(2008,  4,  1,  0,  0,  0), #  14400  3600 ADT
        datetime(2008, 10,  1,  0,  0,  0), #  10800     0 AST
        datetime(2009,  4,  1,  0,  0,  0), #  14400  3600 ADT
        datetime(2009, 10,  1,  0,  0,  0), #  10800     0 AST
        datetime(2010,  4,  1,  0,  0,  0), #  14400  3600 ADT
        datetime(2010, 10,  1,  0,  0,  0), #  10800     0 AST
        datetime(2011,  4,  1,  0,  0,  0), #  14400  3600 ADT
        datetime(2011, 10,  1,  0,  0,  0), #  10800     0 AST
        datetime(2012,  4,  1,  0,  0,  0), #  14400  3600 ADT
        datetime(2012, 10,  1,  0,  0,  0), #  10800     0 AST
        datetime(2013,  4,  1,  0,  0,  0), #  14400  3600 ADT
        datetime(2013, 10,  1,  0,  0,  0), #  10800     0 AST
        datetime(2014,  4,  1,  0,  0,  0), #  14400  3600 ADT
        datetime(2014, 10,  1,  0,  0,  0), #  10800     0 AST
        datetime(2015,  4,  1,  0,  0,  0), #  14400  3600 ADT
        datetime(2015, 10,  1,  0,  0,  0), #  10800     0 AST
        datetime(2016,  4,  1,  0,  0,  0), #  14400  3600 ADT
        datetime(2016, 10,  1,  0,  0,  0), #  10800     0 AST
        datetime(2017,  4,  1,  0,  0,  0), #  14400  3600 ADT
        datetime(2017, 10,  1,  0,  0,  0), #  10800     0 AST
        datetime(2018,  4,  1,  0,  0,  0), #  14400  3600 ADT
        datetime(2018, 10,  1,  0,  0,  0), #  10800     0 AST
        datetime(2019,  4,  1,  0,  0,  0), #  14400  3600 ADT
        datetime(2019, 10,  1,  0,  0,  0), #  10800     0 AST
        datetime(2020,  4,  1,  0,  0,  0), #  14400  3600 ADT
        datetime(2020, 10,  1,  0,  0,  0), #  10800     0 AST
        datetime(2021,  4,  1,  0,  0,  0), #  14400  3600 ADT
        datetime(2021, 10,  1,  0,  0,  0), #  10800     0 AST
        datetime(2022,  4,  1,  0,  0,  0), #  14400  3600 ADT
        datetime(2022, 10,  1,  0,  0,  0), #  10800     0 AST
        datetime(2023,  4,  1,  0,  0,  0), #  14400  3600 ADT
        datetime(2023, 10,  1,  0,  0,  0), #  10800     0 AST
        datetime(2024,  4,  1,  0,  0,  0), #  14400  3600 ADT
        datetime(2024, 10,  1,  0,  0,  0), #  10800     0 AST
        datetime(2025,  4,  1,  0,  0,  0), #  14400  3600 ADT
        datetime(2025, 10,  1,  0,  0,  0), #  10800     0 AST
        datetime(2026,  4,  1,  0,  0,  0), #  14400  3600 ADT
        datetime(2026, 10,  1,  0,  0,  0), #  10800     0 AST
        datetime(2027,  4,  1,  0,  0,  0), #  14400  3600 ADT
        datetime(2027, 10,  1,  0,  0,  0), #  10800     0 AST
        datetime(2028,  4,  1,  0,  0,  0), #  14400  3600 ADT
        datetime(2028, 10,  1,  0,  0,  0), #  10800     0 AST
        datetime(2029,  4,  1,  0,  0,  0), #  14400  3600 ADT
        datetime(2029, 10,  1,  0,  0,  0), #  10800     0 AST
        datetime(2030,  4,  1,  0,  0,  0), #  14400  3600 ADT
        datetime(2030, 10,  1,  0,  0,  0), #  10800     0 AST
        datetime(2031,  4,  1,  0,  0,  0), #  14400  3600 ADT
        datetime(2031, 10,  1,  0,  0,  0), #  10800     0 AST
        datetime(2032,  4,  1,  0,  0,  0), #  14400  3600 ADT
        datetime(2032, 10,  1,  0,  0,  0), #  10800     0 AST
        datetime(2033,  4,  1,  0,  0,  0), #  14400  3600 ADT
        datetime(2033, 10,  1,  0,  0,  0), #  10800     0 AST
        datetime(2034,  4,  1,  0,  0,  0), #  14400  3600 ADT
        datetime(2034, 10,  1,  0,  0,  0), #  10800     0 AST
        datetime(2035,  4,  1,  0,  0,  0), #  14400  3600 ADT
        datetime(2035, 10,  1,  0,  0,  0), #  10800     0 AST
        datetime(2036,  4,  1,  0,  0,  0), #  14400  3600 ADT
        datetime(2036, 10,  1,  0,  0,  0), #  10800     0 AST
        datetime(2037,  4,  1,  0,  0,  0), #  14400  3600 ADT
        datetime(2037, 10,  1,  0,  0,  0), #  10800     0 AST
        ]

    _transition_info = [
        ttinfo( 10656,      0,  'BMT'),
        ttinfo( 10800,      0,  'AST'),
        ttinfo( 14400,   3600,  'ADT'),
        ttinfo( 10800,      0,  'AST'),
        ttinfo( 14400,   3600,  'ADT'),
        ttinfo( 10800,      0,  'AST'),
        ttinfo( 14400,   3600,  'ADT'),
        ttinfo( 10800,      0,  'AST'),
        ttinfo( 14400,   3600,  'ADT'),
        ttinfo( 10800,      0,  'AST'),
        ttinfo( 14400,   3600,  'ADT'),
        ttinfo( 10800,      0,  'AST'),
        ttinfo( 14400,   3600,  'ADT'),
        ttinfo( 10800,      0,  'AST'),
        ttinfo( 14400,   3600,  'ADT'),
        ttinfo( 10800,      0,  'AST'),
        ttinfo( 14400,   3600,  'ADT'),
        ttinfo( 10800,      0,  'AST'),
        ttinfo( 14400,   3600,  'ADT'),
        ttinfo( 10800,      0,  'AST'),
        ttinfo( 14400,   3600,  'ADT'),
        ttinfo( 10800,      0,  'AST'),
        ttinfo( 14400,   3600,  'ADT'),
        ttinfo( 10800,      0,  'AST'),
        ttinfo( 14400,   3600,  'ADT'),
        ttinfo( 10800,      0,  'AST'),
        ttinfo( 14400,   3600,  'ADT'),
        ttinfo( 10800,      0,  'AST'),
        ttinfo( 14400,   3600,  'ADT'),
        ttinfo( 10800,      0,  'AST'),
        ttinfo( 14400,   3600,  'ADT'),
        ttinfo( 10800,      0,  'AST'),
        ttinfo( 14400,   3600,  'ADT'),
        ttinfo( 10800,      0,  'AST'),
        ttinfo( 14400,   3600,  'ADT'),
        ttinfo( 10800,      0,  'AST'),
        ttinfo( 14400,   3600,  'ADT'),
        ttinfo( 10800,      0,  'AST'),
        ttinfo( 14400,   3600,  'ADT'),
        ttinfo( 10800,      0,  'AST'),
        ttinfo( 14400,   3600,  'ADT'),
        ttinfo( 10800,      0,  'AST'),
        ttinfo( 14400,   3600,  'ADT'),
        ttinfo( 10800,      0,  'AST'),
        ttinfo( 14400,   3600,  'ADT'),
        ttinfo( 10800,      0,  'AST'),
        ttinfo( 14400,   3600,  'ADT'),
        ttinfo( 10800,      0,  'AST'),
        ttinfo( 14400,   3600,  'ADT'),
        ttinfo( 10800,      0,  'AST'),
        ttinfo( 14400,   3600,  'ADT'),
        ttinfo( 10800,      0,  'AST'),
        ttinfo( 14400,   3600,  'ADT'),
        ttinfo( 10800,      0,  'AST'),
        ttinfo( 14400,   3600,  'ADT'),
        ttinfo( 10800,      0,  'AST'),
        ttinfo( 14400,   3600,  'ADT'),
        ttinfo( 10800,      0,  'AST'),
        ttinfo( 14400,   3600,  'ADT'),
        ttinfo( 10800,      0,  'AST'),
        ttinfo( 14400,   3600,  'ADT'),
        ttinfo( 10800,      0,  'AST'),
        ttinfo( 14400,   3600,  'ADT'),
        ttinfo( 10800,      0,  'AST'),
        ttinfo( 14400,   3600,  'ADT'),
        ttinfo( 10800,      0,  'AST'),
        ttinfo( 14400,   3600,  'ADT'),
        ttinfo( 10800,      0,  'AST'),
        ttinfo( 14400,   3600,  'ADT'),
        ttinfo( 10800,      0,  'AST'),
        ttinfo( 14400,   3600,  'ADT'),
        ttinfo( 10800,      0,  'AST'),
        ttinfo( 14400,   3600,  'ADT'),
        ttinfo( 10800,      0,  'AST'),
        ttinfo( 14400,   3600,  'ADT'),
        ttinfo( 10800,      0,  'AST'),
        ttinfo( 14400,   3600,  'ADT'),
        ttinfo( 10800,      0,  'AST'),
        ttinfo( 14400,   3600,  'ADT'),
        ttinfo( 10800,      0,  'AST'),
        ttinfo( 14400,   3600,  'ADT'),
        ttinfo( 10800,      0,  'AST'),
        ttinfo( 14400,   3600,  'ADT'),
        ttinfo( 10800,      0,  'AST'),
        ttinfo( 14400,   3600,  'ADT'),
        ttinfo( 10800,      0,  'AST'),
        ttinfo( 14400,   3600,  'ADT'),
        ttinfo( 10800,      0,  'AST'),
        ttinfo( 14400,   3600,  'ADT'),
        ttinfo( 10800,      0,  'AST'),
        ttinfo( 14400,   3600,  'ADT'),
        ttinfo( 10800,      0,  'AST'),
        ttinfo( 14400,   3600,  'ADT'),
        ttinfo( 10800,      0,  'AST'),
        ttinfo( 14400,   3600,  'ADT'),
        ttinfo( 10800,      0,  'AST'),
        ttinfo( 14400,   3600,  'ADT'),
        ttinfo( 10800,      0,  'AST'),
        ttinfo( 14400,   3600,  'ADT'),
        ttinfo( 10800,      0,  'AST'),
        ttinfo( 14400,   3600,  'ADT'),
        ttinfo( 10800,      0,  'AST'),
        ttinfo( 14400,   3600,  'ADT'),
        ttinfo( 10800,      0,  'AST'),
        ttinfo( 14400,   3600,  'ADT'),
        ttinfo( 10800,      0,  'AST'),
        ttinfo( 14400,   3600,  'ADT'),
        ttinfo( 10800,      0,  'AST'),
        ttinfo( 14400,   3600,  'ADT'),
        ttinfo( 10800,      0,  'AST'),
        ttinfo( 14400,   3600,  'ADT'),
        ttinfo( 10800,      0,  'AST'),
        ttinfo( 14400,   3600,  'ADT'),
        ttinfo( 10800,      0,  'AST'),
        ]

Baghdad = Baghdad() # Singleton

