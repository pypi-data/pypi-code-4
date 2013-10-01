'''
tzinfo timezone information for Atlantic/Bermuda.

Generated from the Olson timezone database:
    ftp://elsie.nci.nih.gov/pub/tz*.tar.gz
'''

from pytz.tzinfo import DstTzInfo
from pytz.tzinfo import memorized_datetime as datetime
from pytz.tzinfo import memorized_ttinfo as ttinfo

class Bermuda(DstTzInfo):
    '''Atlantic/Bermuda timezone definition. See datetime.tzinfo for details'''

    _zone = 'Atlantic/Bermuda'

    _utc_transition_times = [
        datetime(   1,  1,  1,  0,  0,  0), # -15544     0 LMT
        datetime(1930,  1,  1,  6, 19,  4), # -14400     0 AST
        datetime(1974,  4, 28,  6,  0,  0), # -10800  3600 ADT
        datetime(1974, 10, 27,  5,  0,  0), # -14400     0 AST
        datetime(1975,  4, 27,  6,  0,  0), # -10800  3600 ADT
        datetime(1975, 10, 26,  5,  0,  0), # -14400     0 AST
        datetime(1976,  4, 25,  6,  0,  0), # -10800  3600 ADT
        datetime(1976, 10, 31,  5,  0,  0), # -14400     0 AST
        datetime(1977,  4, 24,  6,  0,  0), # -10800  3600 ADT
        datetime(1977, 10, 30,  5,  0,  0), # -14400     0 AST
        datetime(1978,  4, 30,  6,  0,  0), # -10800  3600 ADT
        datetime(1978, 10, 29,  5,  0,  0), # -14400     0 AST
        datetime(1979,  4, 29,  6,  0,  0), # -10800  3600 ADT
        datetime(1979, 10, 28,  5,  0,  0), # -14400     0 AST
        datetime(1980,  4, 27,  6,  0,  0), # -10800  3600 ADT
        datetime(1980, 10, 26,  5,  0,  0), # -14400     0 AST
        datetime(1981,  4, 26,  6,  0,  0), # -10800  3600 ADT
        datetime(1981, 10, 25,  5,  0,  0), # -14400     0 AST
        datetime(1982,  4, 25,  6,  0,  0), # -10800  3600 ADT
        datetime(1982, 10, 31,  5,  0,  0), # -14400     0 AST
        datetime(1983,  4, 24,  6,  0,  0), # -10800  3600 ADT
        datetime(1983, 10, 30,  5,  0,  0), # -14400     0 AST
        datetime(1984,  4, 29,  6,  0,  0), # -10800  3600 ADT
        datetime(1984, 10, 28,  5,  0,  0), # -14400     0 AST
        datetime(1985,  4, 28,  6,  0,  0), # -10800  3600 ADT
        datetime(1985, 10, 27,  5,  0,  0), # -14400     0 AST
        datetime(1986,  4, 27,  6,  0,  0), # -10800  3600 ADT
        datetime(1986, 10, 26,  5,  0,  0), # -14400     0 AST
        datetime(1987,  4,  5,  6,  0,  0), # -10800  3600 ADT
        datetime(1987, 10, 25,  5,  0,  0), # -14400     0 AST
        datetime(1988,  4,  3,  6,  0,  0), # -10800  3600 ADT
        datetime(1988, 10, 30,  5,  0,  0), # -14400     0 AST
        datetime(1989,  4,  2,  6,  0,  0), # -10800  3600 ADT
        datetime(1989, 10, 29,  5,  0,  0), # -14400     0 AST
        datetime(1990,  4,  1,  6,  0,  0), # -10800  3600 ADT
        datetime(1990, 10, 28,  5,  0,  0), # -14400     0 AST
        datetime(1991,  4,  7,  6,  0,  0), # -10800  3600 ADT
        datetime(1991, 10, 27,  5,  0,  0), # -14400     0 AST
        datetime(1992,  4,  5,  6,  0,  0), # -10800  3600 ADT
        datetime(1992, 10, 25,  5,  0,  0), # -14400     0 AST
        datetime(1993,  4,  4,  6,  0,  0), # -10800  3600 ADT
        datetime(1993, 10, 31,  5,  0,  0), # -14400     0 AST
        datetime(1994,  4,  3,  6,  0,  0), # -10800  3600 ADT
        datetime(1994, 10, 30,  5,  0,  0), # -14400     0 AST
        datetime(1995,  4,  2,  6,  0,  0), # -10800  3600 ADT
        datetime(1995, 10, 29,  5,  0,  0), # -14400     0 AST
        datetime(1996,  4,  7,  6,  0,  0), # -10800  3600 ADT
        datetime(1996, 10, 27,  5,  0,  0), # -14400     0 AST
        datetime(1997,  4,  6,  6,  0,  0), # -10800  3600 ADT
        datetime(1997, 10, 26,  5,  0,  0), # -14400     0 AST
        datetime(1998,  4,  5,  6,  0,  0), # -10800  3600 ADT
        datetime(1998, 10, 25,  5,  0,  0), # -14400     0 AST
        datetime(1999,  4,  4,  6,  0,  0), # -10800  3600 ADT
        datetime(1999, 10, 31,  5,  0,  0), # -14400     0 AST
        datetime(2000,  4,  2,  6,  0,  0), # -10800  3600 ADT
        datetime(2000, 10, 29,  5,  0,  0), # -14400     0 AST
        datetime(2001,  4,  1,  6,  0,  0), # -10800  3600 ADT
        datetime(2001, 10, 28,  5,  0,  0), # -14400     0 AST
        datetime(2002,  4,  7,  6,  0,  0), # -10800  3600 ADT
        datetime(2002, 10, 27,  5,  0,  0), # -14400     0 AST
        datetime(2003,  4,  6,  6,  0,  0), # -10800  3600 ADT
        datetime(2003, 10, 26,  5,  0,  0), # -14400     0 AST
        datetime(2004,  4,  4,  6,  0,  0), # -10800  3600 ADT
        datetime(2004, 10, 31,  5,  0,  0), # -14400     0 AST
        datetime(2005,  4,  3,  6,  0,  0), # -10800  3600 ADT
        datetime(2005, 10, 30,  5,  0,  0), # -14400     0 AST
        datetime(2006,  4,  2,  6,  0,  0), # -10800  3600 ADT
        datetime(2006, 10, 29,  5,  0,  0), # -14400     0 AST
        datetime(2007,  4,  1,  6,  0,  0), # -10800  3600 ADT
        datetime(2007, 10, 28,  5,  0,  0), # -14400     0 AST
        datetime(2008,  4,  6,  6,  0,  0), # -10800  3600 ADT
        datetime(2008, 10, 26,  5,  0,  0), # -14400     0 AST
        datetime(2009,  4,  5,  6,  0,  0), # -10800  3600 ADT
        datetime(2009, 10, 25,  5,  0,  0), # -14400     0 AST
        datetime(2010,  4,  4,  6,  0,  0), # -10800  3600 ADT
        datetime(2010, 10, 31,  5,  0,  0), # -14400     0 AST
        datetime(2011,  4,  3,  6,  0,  0), # -10800  3600 ADT
        datetime(2011, 10, 30,  5,  0,  0), # -14400     0 AST
        datetime(2012,  4,  1,  6,  0,  0), # -10800  3600 ADT
        datetime(2012, 10, 28,  5,  0,  0), # -14400     0 AST
        datetime(2013,  4,  7,  6,  0,  0), # -10800  3600 ADT
        datetime(2013, 10, 27,  5,  0,  0), # -14400     0 AST
        datetime(2014,  4,  6,  6,  0,  0), # -10800  3600 ADT
        datetime(2014, 10, 26,  5,  0,  0), # -14400     0 AST
        datetime(2015,  4,  5,  6,  0,  0), # -10800  3600 ADT
        datetime(2015, 10, 25,  5,  0,  0), # -14400     0 AST
        datetime(2016,  4,  3,  6,  0,  0), # -10800  3600 ADT
        datetime(2016, 10, 30,  5,  0,  0), # -14400     0 AST
        datetime(2017,  4,  2,  6,  0,  0), # -10800  3600 ADT
        datetime(2017, 10, 29,  5,  0,  0), # -14400     0 AST
        datetime(2018,  4,  1,  6,  0,  0), # -10800  3600 ADT
        datetime(2018, 10, 28,  5,  0,  0), # -14400     0 AST
        datetime(2019,  4,  7,  6,  0,  0), # -10800  3600 ADT
        datetime(2019, 10, 27,  5,  0,  0), # -14400     0 AST
        datetime(2020,  4,  5,  6,  0,  0), # -10800  3600 ADT
        datetime(2020, 10, 25,  5,  0,  0), # -14400     0 AST
        datetime(2021,  4,  4,  6,  0,  0), # -10800  3600 ADT
        datetime(2021, 10, 31,  5,  0,  0), # -14400     0 AST
        datetime(2022,  4,  3,  6,  0,  0), # -10800  3600 ADT
        datetime(2022, 10, 30,  5,  0,  0), # -14400     0 AST
        datetime(2023,  4,  2,  6,  0,  0), # -10800  3600 ADT
        datetime(2023, 10, 29,  5,  0,  0), # -14400     0 AST
        datetime(2024,  4,  7,  6,  0,  0), # -10800  3600 ADT
        datetime(2024, 10, 27,  5,  0,  0), # -14400     0 AST
        datetime(2025,  4,  6,  6,  0,  0), # -10800  3600 ADT
        datetime(2025, 10, 26,  5,  0,  0), # -14400     0 AST
        datetime(2026,  4,  5,  6,  0,  0), # -10800  3600 ADT
        datetime(2026, 10, 25,  5,  0,  0), # -14400     0 AST
        datetime(2027,  4,  4,  6,  0,  0), # -10800  3600 ADT
        datetime(2027, 10, 31,  5,  0,  0), # -14400     0 AST
        datetime(2028,  4,  2,  6,  0,  0), # -10800  3600 ADT
        datetime(2028, 10, 29,  5,  0,  0), # -14400     0 AST
        datetime(2029,  4,  1,  6,  0,  0), # -10800  3600 ADT
        datetime(2029, 10, 28,  5,  0,  0), # -14400     0 AST
        datetime(2030,  4,  7,  6,  0,  0), # -10800  3600 ADT
        datetime(2030, 10, 27,  5,  0,  0), # -14400     0 AST
        datetime(2031,  4,  6,  6,  0,  0), # -10800  3600 ADT
        datetime(2031, 10, 26,  5,  0,  0), # -14400     0 AST
        datetime(2032,  4,  4,  6,  0,  0), # -10800  3600 ADT
        datetime(2032, 10, 31,  5,  0,  0), # -14400     0 AST
        datetime(2033,  4,  3,  6,  0,  0), # -10800  3600 ADT
        datetime(2033, 10, 30,  5,  0,  0), # -14400     0 AST
        datetime(2034,  4,  2,  6,  0,  0), # -10800  3600 ADT
        datetime(2034, 10, 29,  5,  0,  0), # -14400     0 AST
        datetime(2035,  4,  1,  6,  0,  0), # -10800  3600 ADT
        datetime(2035, 10, 28,  5,  0,  0), # -14400     0 AST
        datetime(2036,  4,  6,  6,  0,  0), # -10800  3600 ADT
        datetime(2036, 10, 26,  5,  0,  0), # -14400     0 AST
        datetime(2037,  4,  5,  6,  0,  0), # -10800  3600 ADT
        datetime(2037, 10, 25,  5,  0,  0), # -14400     0 AST
        ]

    _transition_info = [
        ttinfo(-15544,      0,  'LMT'),
        ttinfo(-14400,      0,  'AST'),
        ttinfo(-10800,   3600,  'ADT'),
        ttinfo(-14400,      0,  'AST'),
        ttinfo(-10800,   3600,  'ADT'),
        ttinfo(-14400,      0,  'AST'),
        ttinfo(-10800,   3600,  'ADT'),
        ttinfo(-14400,      0,  'AST'),
        ttinfo(-10800,   3600,  'ADT'),
        ttinfo(-14400,      0,  'AST'),
        ttinfo(-10800,   3600,  'ADT'),
        ttinfo(-14400,      0,  'AST'),
        ttinfo(-10800,   3600,  'ADT'),
        ttinfo(-14400,      0,  'AST'),
        ttinfo(-10800,   3600,  'ADT'),
        ttinfo(-14400,      0,  'AST'),
        ttinfo(-10800,   3600,  'ADT'),
        ttinfo(-14400,      0,  'AST'),
        ttinfo(-10800,   3600,  'ADT'),
        ttinfo(-14400,      0,  'AST'),
        ttinfo(-10800,   3600,  'ADT'),
        ttinfo(-14400,      0,  'AST'),
        ttinfo(-10800,   3600,  'ADT'),
        ttinfo(-14400,      0,  'AST'),
        ttinfo(-10800,   3600,  'ADT'),
        ttinfo(-14400,      0,  'AST'),
        ttinfo(-10800,   3600,  'ADT'),
        ttinfo(-14400,      0,  'AST'),
        ttinfo(-10800,   3600,  'ADT'),
        ttinfo(-14400,      0,  'AST'),
        ttinfo(-10800,   3600,  'ADT'),
        ttinfo(-14400,      0,  'AST'),
        ttinfo(-10800,   3600,  'ADT'),
        ttinfo(-14400,      0,  'AST'),
        ttinfo(-10800,   3600,  'ADT'),
        ttinfo(-14400,      0,  'AST'),
        ttinfo(-10800,   3600,  'ADT'),
        ttinfo(-14400,      0,  'AST'),
        ttinfo(-10800,   3600,  'ADT'),
        ttinfo(-14400,      0,  'AST'),
        ttinfo(-10800,   3600,  'ADT'),
        ttinfo(-14400,      0,  'AST'),
        ttinfo(-10800,   3600,  'ADT'),
        ttinfo(-14400,      0,  'AST'),
        ttinfo(-10800,   3600,  'ADT'),
        ttinfo(-14400,      0,  'AST'),
        ttinfo(-10800,   3600,  'ADT'),
        ttinfo(-14400,      0,  'AST'),
        ttinfo(-10800,   3600,  'ADT'),
        ttinfo(-14400,      0,  'AST'),
        ttinfo(-10800,   3600,  'ADT'),
        ttinfo(-14400,      0,  'AST'),
        ttinfo(-10800,   3600,  'ADT'),
        ttinfo(-14400,      0,  'AST'),
        ttinfo(-10800,   3600,  'ADT'),
        ttinfo(-14400,      0,  'AST'),
        ttinfo(-10800,   3600,  'ADT'),
        ttinfo(-14400,      0,  'AST'),
        ttinfo(-10800,   3600,  'ADT'),
        ttinfo(-14400,      0,  'AST'),
        ttinfo(-10800,   3600,  'ADT'),
        ttinfo(-14400,      0,  'AST'),
        ttinfo(-10800,   3600,  'ADT'),
        ttinfo(-14400,      0,  'AST'),
        ttinfo(-10800,   3600,  'ADT'),
        ttinfo(-14400,      0,  'AST'),
        ttinfo(-10800,   3600,  'ADT'),
        ttinfo(-14400,      0,  'AST'),
        ttinfo(-10800,   3600,  'ADT'),
        ttinfo(-14400,      0,  'AST'),
        ttinfo(-10800,   3600,  'ADT'),
        ttinfo(-14400,      0,  'AST'),
        ttinfo(-10800,   3600,  'ADT'),
        ttinfo(-14400,      0,  'AST'),
        ttinfo(-10800,   3600,  'ADT'),
        ttinfo(-14400,      0,  'AST'),
        ttinfo(-10800,   3600,  'ADT'),
        ttinfo(-14400,      0,  'AST'),
        ttinfo(-10800,   3600,  'ADT'),
        ttinfo(-14400,      0,  'AST'),
        ttinfo(-10800,   3600,  'ADT'),
        ttinfo(-14400,      0,  'AST'),
        ttinfo(-10800,   3600,  'ADT'),
        ttinfo(-14400,      0,  'AST'),
        ttinfo(-10800,   3600,  'ADT'),
        ttinfo(-14400,      0,  'AST'),
        ttinfo(-10800,   3600,  'ADT'),
        ttinfo(-14400,      0,  'AST'),
        ttinfo(-10800,   3600,  'ADT'),
        ttinfo(-14400,      0,  'AST'),
        ttinfo(-10800,   3600,  'ADT'),
        ttinfo(-14400,      0,  'AST'),
        ttinfo(-10800,   3600,  'ADT'),
        ttinfo(-14400,      0,  'AST'),
        ttinfo(-10800,   3600,  'ADT'),
        ttinfo(-14400,      0,  'AST'),
        ttinfo(-10800,   3600,  'ADT'),
        ttinfo(-14400,      0,  'AST'),
        ttinfo(-10800,   3600,  'ADT'),
        ttinfo(-14400,      0,  'AST'),
        ttinfo(-10800,   3600,  'ADT'),
        ttinfo(-14400,      0,  'AST'),
        ttinfo(-10800,   3600,  'ADT'),
        ttinfo(-14400,      0,  'AST'),
        ttinfo(-10800,   3600,  'ADT'),
        ttinfo(-14400,      0,  'AST'),
        ttinfo(-10800,   3600,  'ADT'),
        ttinfo(-14400,      0,  'AST'),
        ttinfo(-10800,   3600,  'ADT'),
        ttinfo(-14400,      0,  'AST'),
        ttinfo(-10800,   3600,  'ADT'),
        ttinfo(-14400,      0,  'AST'),
        ttinfo(-10800,   3600,  'ADT'),
        ttinfo(-14400,      0,  'AST'),
        ttinfo(-10800,   3600,  'ADT'),
        ttinfo(-14400,      0,  'AST'),
        ttinfo(-10800,   3600,  'ADT'),
        ttinfo(-14400,      0,  'AST'),
        ttinfo(-10800,   3600,  'ADT'),
        ttinfo(-14400,      0,  'AST'),
        ttinfo(-10800,   3600,  'ADT'),
        ttinfo(-14400,      0,  'AST'),
        ttinfo(-10800,   3600,  'ADT'),
        ttinfo(-14400,      0,  'AST'),
        ttinfo(-10800,   3600,  'ADT'),
        ttinfo(-14400,      0,  'AST'),
        ttinfo(-10800,   3600,  'ADT'),
        ttinfo(-14400,      0,  'AST'),
        ttinfo(-10800,   3600,  'ADT'),
        ttinfo(-14400,      0,  'AST'),
        ]

Bermuda = Bermuda() # Singleton

