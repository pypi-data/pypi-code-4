'''
tzinfo timezone information for America/Campo_Grande.

Generated from the Olson timezone database:
    ftp://elsie.nci.nih.gov/pub/tz*.tar.gz
'''

from pytz.tzinfo import DstTzInfo
from pytz.tzinfo import memorized_datetime as datetime
from pytz.tzinfo import memorized_ttinfo as ttinfo

class Campo_Grande(DstTzInfo):
    '''America/Campo_Grande timezone definition. See datetime.tzinfo for details'''

    _zone = 'America/Campo_Grande'

    _utc_transition_times = [
        datetime(   1,  1,  1,  0,  0,  0), # -13108     0 LMT
        datetime(1914,  1,  1,  3, 38, 28), # -14400     0 AMT
        datetime(1931, 10,  3, 15,  0,  0), # -10800  3600 AMST
        datetime(1932,  4,  1,  3,  0,  0), # -14400     0 AMT
        datetime(1932, 10,  3,  4,  0,  0), # -10800  3600 AMST
        datetime(1933,  4,  1,  3,  0,  0), # -14400     0 AMT
        datetime(1949, 12,  1,  4,  0,  0), # -10800  3600 AMST
        datetime(1950,  4, 16,  4,  0,  0), # -14400     0 AMT
        datetime(1950, 12,  1,  4,  0,  0), # -10800  3600 AMST
        datetime(1951,  4,  1,  3,  0,  0), # -14400     0 AMT
        datetime(1951, 12,  1,  4,  0,  0), # -10800  3600 AMST
        datetime(1952,  4,  1,  3,  0,  0), # -14400     0 AMT
        datetime(1952, 12,  1,  4,  0,  0), # -10800  3600 AMST
        datetime(1953,  3,  1,  3,  0,  0), # -14400     0 AMT
        datetime(1963, 12,  9,  4,  0,  0), # -10800  3600 AMST
        datetime(1964,  3,  1,  3,  0,  0), # -14400     0 AMT
        datetime(1965,  1, 31,  4,  0,  0), # -10800  3600 AMST
        datetime(1965,  3, 31,  3,  0,  0), # -14400     0 AMT
        datetime(1965, 12,  1,  4,  0,  0), # -10800  3600 AMST
        datetime(1966,  3,  1,  3,  0,  0), # -14400     0 AMT
        datetime(1966, 11,  1,  4,  0,  0), # -10800  3600 AMST
        datetime(1967,  3,  1,  3,  0,  0), # -14400     0 AMT
        datetime(1967, 11,  1,  4,  0,  0), # -10800  3600 AMST
        datetime(1968,  3,  1,  3,  0,  0), # -14400     0 AMT
        datetime(1985, 11,  2,  4,  0,  0), # -10800  3600 AMST
        datetime(1986,  3, 15,  3,  0,  0), # -14400     0 AMT
        datetime(1986, 10, 25,  4,  0,  0), # -10800  3600 AMST
        datetime(1987,  2, 14,  3,  0,  0), # -14400     0 AMT
        datetime(1987, 10, 25,  4,  0,  0), # -10800  3600 AMST
        datetime(1988,  2,  7,  3,  0,  0), # -14400     0 AMT
        datetime(1988, 10, 16,  4,  0,  0), # -10800  3600 AMST
        datetime(1989,  1, 29,  3,  0,  0), # -14400     0 AMT
        datetime(1989, 10, 15,  4,  0,  0), # -10800  3600 AMST
        datetime(1990,  2, 11,  3,  0,  0), # -14400     0 AMT
        datetime(1990, 10, 21,  4,  0,  0), # -10800  3600 AMST
        datetime(1991,  2, 17,  3,  0,  0), # -14400     0 AMT
        datetime(1991, 10, 20,  4,  0,  0), # -10800  3600 AMST
        datetime(1992,  2,  9,  3,  0,  0), # -14400     0 AMT
        datetime(1992, 10, 25,  4,  0,  0), # -10800  3600 AMST
        datetime(1993,  1, 31,  3,  0,  0), # -14400     0 AMT
        datetime(1993, 10, 17,  4,  0,  0), # -10800  3600 AMST
        datetime(1994,  2, 20,  3,  0,  0), # -14400     0 AMT
        datetime(1994, 10, 16,  4,  0,  0), # -10800  3600 AMST
        datetime(1995,  2, 19,  3,  0,  0), # -14400     0 AMT
        datetime(1995, 10, 15,  4,  0,  0), # -10800  3600 AMST
        datetime(1996,  2, 11,  3,  0,  0), # -14400     0 AMT
        datetime(1996, 10,  6,  4,  0,  0), # -10800  3600 AMST
        datetime(1997,  2, 16,  3,  0,  0), # -14400     0 AMT
        datetime(1997, 10,  6,  4,  0,  0), # -10800  3600 AMST
        datetime(1998,  3,  1,  3,  0,  0), # -14400     0 AMT
        datetime(1998, 10, 11,  4,  0,  0), # -10800  3600 AMST
        datetime(1999,  2, 21,  3,  0,  0), # -14400     0 AMT
        datetime(1999, 10,  3,  4,  0,  0), # -10800  3600 AMST
        datetime(2000,  2, 27,  3,  0,  0), # -14400     0 AMT
        datetime(2000, 10,  8,  4,  0,  0), # -10800  3600 AMST
        datetime(2001,  2, 18,  3,  0,  0), # -14400     0 AMT
        datetime(2001, 10, 14,  4,  0,  0), # -10800  3600 AMST
        datetime(2002,  2, 17,  3,  0,  0), # -14400     0 AMT
        datetime(2002, 11,  3,  4,  0,  0), # -10800  3600 AMST
        datetime(2003,  2, 16,  3,  0,  0), # -14400     0 AMT
        datetime(2003, 10, 19,  4,  0,  0), # -10800  3600 AMST
        datetime(2004,  2, 15,  3,  0,  0), # -14400     0 AMT
        datetime(2004, 10, 17,  4,  0,  0), # -10800  3600 AMST
        datetime(2005,  2, 20,  3,  0,  0), # -14400     0 AMT
        datetime(2005, 10, 16,  4,  0,  0), # -10800  3600 AMST
        datetime(2006,  2, 19,  3,  0,  0), # -14400     0 AMT
        datetime(2006, 10, 15,  4,  0,  0), # -10800  3600 AMST
        datetime(2007,  2, 18,  3,  0,  0), # -14400     0 AMT
        datetime(2007, 10, 21,  4,  0,  0), # -10800  3600 AMST
        datetime(2008,  2, 17,  3,  0,  0), # -14400     0 AMT
        datetime(2008, 10, 19,  4,  0,  0), # -10800  3600 AMST
        datetime(2009,  2, 15,  3,  0,  0), # -14400     0 AMT
        datetime(2009, 10, 18,  4,  0,  0), # -10800  3600 AMST
        datetime(2010,  2, 21,  3,  0,  0), # -14400     0 AMT
        datetime(2010, 10, 17,  4,  0,  0), # -10800  3600 AMST
        datetime(2011,  2, 20,  3,  0,  0), # -14400     0 AMT
        datetime(2011, 10, 16,  4,  0,  0), # -10800  3600 AMST
        datetime(2012,  2, 19,  3,  0,  0), # -14400     0 AMT
        datetime(2012, 10, 21,  4,  0,  0), # -10800  3600 AMST
        datetime(2013,  2, 17,  3,  0,  0), # -14400     0 AMT
        datetime(2013, 10, 20,  4,  0,  0), # -10800  3600 AMST
        datetime(2014,  2, 16,  3,  0,  0), # -14400     0 AMT
        datetime(2014, 10, 19,  4,  0,  0), # -10800  3600 AMST
        datetime(2015,  2, 15,  3,  0,  0), # -14400     0 AMT
        datetime(2015, 10, 18,  4,  0,  0), # -10800  3600 AMST
        datetime(2016,  2, 21,  3,  0,  0), # -14400     0 AMT
        datetime(2016, 10, 16,  4,  0,  0), # -10800  3600 AMST
        datetime(2017,  2, 19,  3,  0,  0), # -14400     0 AMT
        datetime(2017, 10, 15,  4,  0,  0), # -10800  3600 AMST
        datetime(2018,  2, 18,  3,  0,  0), # -14400     0 AMT
        datetime(2018, 10, 21,  4,  0,  0), # -10800  3600 AMST
        datetime(2019,  2, 17,  3,  0,  0), # -14400     0 AMT
        datetime(2019, 10, 20,  4,  0,  0), # -10800  3600 AMST
        datetime(2020,  2, 16,  3,  0,  0), # -14400     0 AMT
        datetime(2020, 10, 18,  4,  0,  0), # -10800  3600 AMST
        datetime(2021,  2, 21,  3,  0,  0), # -14400     0 AMT
        datetime(2021, 10, 17,  4,  0,  0), # -10800  3600 AMST
        datetime(2022,  2, 20,  3,  0,  0), # -14400     0 AMT
        datetime(2022, 10, 16,  4,  0,  0), # -10800  3600 AMST
        datetime(2023,  2, 19,  3,  0,  0), # -14400     0 AMT
        datetime(2023, 10, 15,  4,  0,  0), # -10800  3600 AMST
        datetime(2024,  2, 18,  3,  0,  0), # -14400     0 AMT
        datetime(2024, 10, 20,  4,  0,  0), # -10800  3600 AMST
        datetime(2025,  2, 16,  3,  0,  0), # -14400     0 AMT
        datetime(2025, 10, 19,  4,  0,  0), # -10800  3600 AMST
        datetime(2026,  2, 15,  3,  0,  0), # -14400     0 AMT
        datetime(2026, 10, 18,  4,  0,  0), # -10800  3600 AMST
        datetime(2027,  2, 21,  3,  0,  0), # -14400     0 AMT
        datetime(2027, 10, 17,  4,  0,  0), # -10800  3600 AMST
        datetime(2028,  2, 20,  3,  0,  0), # -14400     0 AMT
        datetime(2028, 10, 15,  4,  0,  0), # -10800  3600 AMST
        datetime(2029,  2, 18,  3,  0,  0), # -14400     0 AMT
        datetime(2029, 10, 21,  4,  0,  0), # -10800  3600 AMST
        datetime(2030,  2, 17,  3,  0,  0), # -14400     0 AMT
        datetime(2030, 10, 20,  4,  0,  0), # -10800  3600 AMST
        datetime(2031,  2, 16,  3,  0,  0), # -14400     0 AMT
        datetime(2031, 10, 19,  4,  0,  0), # -10800  3600 AMST
        datetime(2032,  2, 15,  3,  0,  0), # -14400     0 AMT
        datetime(2032, 10, 17,  4,  0,  0), # -10800  3600 AMST
        datetime(2033,  2, 20,  3,  0,  0), # -14400     0 AMT
        datetime(2033, 10, 16,  4,  0,  0), # -10800  3600 AMST
        datetime(2034,  2, 19,  3,  0,  0), # -14400     0 AMT
        datetime(2034, 10, 15,  4,  0,  0), # -10800  3600 AMST
        datetime(2035,  2, 18,  3,  0,  0), # -14400     0 AMT
        datetime(2035, 10, 21,  4,  0,  0), # -10800  3600 AMST
        datetime(2036,  2, 17,  3,  0,  0), # -14400     0 AMT
        datetime(2036, 10, 19,  4,  0,  0), # -10800  3600 AMST
        datetime(2037,  2, 15,  3,  0,  0), # -14400     0 AMT
        datetime(2037, 10, 18,  4,  0,  0), # -10800  3600 AMST
        ]

    _transition_info = [
        ttinfo(-13108,      0,  'LMT'),
        ttinfo(-14400,      0,  'AMT'),
        ttinfo(-10800,   3600, 'AMST'),
        ttinfo(-14400,      0,  'AMT'),
        ttinfo(-10800,   3600, 'AMST'),
        ttinfo(-14400,      0,  'AMT'),
        ttinfo(-10800,   3600, 'AMST'),
        ttinfo(-14400,      0,  'AMT'),
        ttinfo(-10800,   3600, 'AMST'),
        ttinfo(-14400,      0,  'AMT'),
        ttinfo(-10800,   3600, 'AMST'),
        ttinfo(-14400,      0,  'AMT'),
        ttinfo(-10800,   3600, 'AMST'),
        ttinfo(-14400,      0,  'AMT'),
        ttinfo(-10800,   3600, 'AMST'),
        ttinfo(-14400,      0,  'AMT'),
        ttinfo(-10800,   3600, 'AMST'),
        ttinfo(-14400,      0,  'AMT'),
        ttinfo(-10800,   3600, 'AMST'),
        ttinfo(-14400,      0,  'AMT'),
        ttinfo(-10800,   3600, 'AMST'),
        ttinfo(-14400,      0,  'AMT'),
        ttinfo(-10800,   3600, 'AMST'),
        ttinfo(-14400,      0,  'AMT'),
        ttinfo(-10800,   3600, 'AMST'),
        ttinfo(-14400,      0,  'AMT'),
        ttinfo(-10800,   3600, 'AMST'),
        ttinfo(-14400,      0,  'AMT'),
        ttinfo(-10800,   3600, 'AMST'),
        ttinfo(-14400,      0,  'AMT'),
        ttinfo(-10800,   3600, 'AMST'),
        ttinfo(-14400,      0,  'AMT'),
        ttinfo(-10800,   3600, 'AMST'),
        ttinfo(-14400,      0,  'AMT'),
        ttinfo(-10800,   3600, 'AMST'),
        ttinfo(-14400,      0,  'AMT'),
        ttinfo(-10800,   3600, 'AMST'),
        ttinfo(-14400,      0,  'AMT'),
        ttinfo(-10800,   3600, 'AMST'),
        ttinfo(-14400,      0,  'AMT'),
        ttinfo(-10800,   3600, 'AMST'),
        ttinfo(-14400,      0,  'AMT'),
        ttinfo(-10800,   3600, 'AMST'),
        ttinfo(-14400,      0,  'AMT'),
        ttinfo(-10800,   3600, 'AMST'),
        ttinfo(-14400,      0,  'AMT'),
        ttinfo(-10800,   3600, 'AMST'),
        ttinfo(-14400,      0,  'AMT'),
        ttinfo(-10800,   3600, 'AMST'),
        ttinfo(-14400,      0,  'AMT'),
        ttinfo(-10800,   3600, 'AMST'),
        ttinfo(-14400,      0,  'AMT'),
        ttinfo(-10800,   3600, 'AMST'),
        ttinfo(-14400,      0,  'AMT'),
        ttinfo(-10800,   3600, 'AMST'),
        ttinfo(-14400,      0,  'AMT'),
        ttinfo(-10800,   3600, 'AMST'),
        ttinfo(-14400,      0,  'AMT'),
        ttinfo(-10800,   3600, 'AMST'),
        ttinfo(-14400,      0,  'AMT'),
        ttinfo(-10800,   3600, 'AMST'),
        ttinfo(-14400,      0,  'AMT'),
        ttinfo(-10800,   3600, 'AMST'),
        ttinfo(-14400,      0,  'AMT'),
        ttinfo(-10800,   3600, 'AMST'),
        ttinfo(-14400,      0,  'AMT'),
        ttinfo(-10800,   3600, 'AMST'),
        ttinfo(-14400,      0,  'AMT'),
        ttinfo(-10800,   3600, 'AMST'),
        ttinfo(-14400,      0,  'AMT'),
        ttinfo(-10800,   3600, 'AMST'),
        ttinfo(-14400,      0,  'AMT'),
        ttinfo(-10800,   3600, 'AMST'),
        ttinfo(-14400,      0,  'AMT'),
        ttinfo(-10800,   3600, 'AMST'),
        ttinfo(-14400,      0,  'AMT'),
        ttinfo(-10800,   3600, 'AMST'),
        ttinfo(-14400,      0,  'AMT'),
        ttinfo(-10800,   3600, 'AMST'),
        ttinfo(-14400,      0,  'AMT'),
        ttinfo(-10800,   3600, 'AMST'),
        ttinfo(-14400,      0,  'AMT'),
        ttinfo(-10800,   3600, 'AMST'),
        ttinfo(-14400,      0,  'AMT'),
        ttinfo(-10800,   3600, 'AMST'),
        ttinfo(-14400,      0,  'AMT'),
        ttinfo(-10800,   3600, 'AMST'),
        ttinfo(-14400,      0,  'AMT'),
        ttinfo(-10800,   3600, 'AMST'),
        ttinfo(-14400,      0,  'AMT'),
        ttinfo(-10800,   3600, 'AMST'),
        ttinfo(-14400,      0,  'AMT'),
        ttinfo(-10800,   3600, 'AMST'),
        ttinfo(-14400,      0,  'AMT'),
        ttinfo(-10800,   3600, 'AMST'),
        ttinfo(-14400,      0,  'AMT'),
        ttinfo(-10800,   3600, 'AMST'),
        ttinfo(-14400,      0,  'AMT'),
        ttinfo(-10800,   3600, 'AMST'),
        ttinfo(-14400,      0,  'AMT'),
        ttinfo(-10800,   3600, 'AMST'),
        ttinfo(-14400,      0,  'AMT'),
        ttinfo(-10800,   3600, 'AMST'),
        ttinfo(-14400,      0,  'AMT'),
        ttinfo(-10800,   3600, 'AMST'),
        ttinfo(-14400,      0,  'AMT'),
        ttinfo(-10800,   3600, 'AMST'),
        ttinfo(-14400,      0,  'AMT'),
        ttinfo(-10800,   3600, 'AMST'),
        ttinfo(-14400,      0,  'AMT'),
        ttinfo(-10800,   3600, 'AMST'),
        ttinfo(-14400,      0,  'AMT'),
        ttinfo(-10800,   3600, 'AMST'),
        ttinfo(-14400,      0,  'AMT'),
        ttinfo(-10800,   3600, 'AMST'),
        ttinfo(-14400,      0,  'AMT'),
        ttinfo(-10800,   3600, 'AMST'),
        ttinfo(-14400,      0,  'AMT'),
        ttinfo(-10800,   3600, 'AMST'),
        ttinfo(-14400,      0,  'AMT'),
        ttinfo(-10800,   3600, 'AMST'),
        ttinfo(-14400,      0,  'AMT'),
        ttinfo(-10800,   3600, 'AMST'),
        ttinfo(-14400,      0,  'AMT'),
        ttinfo(-10800,   3600, 'AMST'),
        ttinfo(-14400,      0,  'AMT'),
        ttinfo(-10800,   3600, 'AMST'),
        ttinfo(-14400,      0,  'AMT'),
        ttinfo(-10800,   3600, 'AMST'),
        ]

Campo_Grande = Campo_Grande() # Singleton

