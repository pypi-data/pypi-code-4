'''
tzinfo timezone information for America/Santiago.

Generated from the Olson timezone database:
    ftp://elsie.nci.nih.gov/pub/tz*.tar.gz
'''

from pytz.tzinfo import DstTzInfo
from pytz.tzinfo import memorized_datetime as datetime
from pytz.tzinfo import memorized_ttinfo as ttinfo

class Santiago(DstTzInfo):
    '''America/Santiago timezone definition. See datetime.tzinfo for details'''

    _zone = 'America/Santiago'

    _utc_transition_times = [
        datetime(   1,  1,  1,  0,  0,  0), # -16960     0 SMT
        datetime(1910,  1,  1,  4, 42, 40), # -18000     0 CLT
        datetime(1918,  9,  1,  5,  0,  0), # -14400  3600 CLST
        datetime(1919,  7,  2,  4,  0,  0), # -18000     0 CLT
        datetime(1927,  9,  1,  5,  0,  0), # -14400  3600 CLST
        datetime(1928,  4,  1,  4,  0,  0), # -18000     0 CLT
        datetime(1928,  9,  1,  5,  0,  0), # -14400  3600 CLST
        datetime(1929,  4,  1,  4,  0,  0), # -18000     0 CLT
        datetime(1929,  9,  1,  5,  0,  0), # -14400  3600 CLST
        datetime(1930,  4,  1,  4,  0,  0), # -18000     0 CLT
        datetime(1930,  9,  1,  5,  0,  0), # -14400  3600 CLST
        datetime(1931,  4,  1,  4,  0,  0), # -18000     0 CLT
        datetime(1931,  9,  1,  5,  0,  0), # -14400  3600 CLST
        datetime(1932,  4,  1,  4,  0,  0), # -18000     0 CLT
        datetime(1932,  9,  1,  5,  0,  0), # -14400     0 CLT
        datetime(1966, 10,  9,  4,  0,  0), # -10800  3600 CLST
        datetime(1967,  3, 12,  3,  0,  0), # -14400     0 CLT
        datetime(1967, 10, 15,  4,  0,  0), # -10800  3600 CLST
        datetime(1968,  3, 10,  3,  0,  0), # -14400     0 CLT
        datetime(1968, 10, 13,  4,  0,  0), # -10800  3600 CLST
        datetime(1969,  3,  9,  3,  0,  0), # -14400     0 CLT
        datetime(1969, 10, 12,  4,  0,  0), # -10800  3600 CLST
        datetime(1970,  3, 15,  3,  0,  0), # -14400     0 CLT
        datetime(1970, 10, 11,  4,  0,  0), # -10800  3600 CLST
        datetime(1971,  3, 14,  3,  0,  0), # -14400     0 CLT
        datetime(1971, 10, 10,  4,  0,  0), # -10800  3600 CLST
        datetime(1972,  3, 12,  3,  0,  0), # -14400     0 CLT
        datetime(1972, 10, 15,  4,  0,  0), # -10800  3600 CLST
        datetime(1973,  3, 11,  3,  0,  0), # -14400     0 CLT
        datetime(1973, 10, 14,  4,  0,  0), # -10800  3600 CLST
        datetime(1974,  3, 10,  3,  0,  0), # -14400     0 CLT
        datetime(1974, 10, 13,  4,  0,  0), # -10800  3600 CLST
        datetime(1975,  3,  9,  3,  0,  0), # -14400     0 CLT
        datetime(1975, 10, 12,  4,  0,  0), # -10800  3600 CLST
        datetime(1976,  3, 14,  3,  0,  0), # -14400     0 CLT
        datetime(1976, 10, 10,  4,  0,  0), # -10800  3600 CLST
        datetime(1977,  3, 13,  3,  0,  0), # -14400     0 CLT
        datetime(1977, 10,  9,  4,  0,  0), # -10800  3600 CLST
        datetime(1978,  3, 12,  3,  0,  0), # -14400     0 CLT
        datetime(1978, 10, 15,  4,  0,  0), # -10800  3600 CLST
        datetime(1979,  3, 11,  3,  0,  0), # -14400     0 CLT
        datetime(1979, 10, 14,  4,  0,  0), # -10800  3600 CLST
        datetime(1980,  3,  9,  3,  0,  0), # -14400     0 CLT
        datetime(1980, 10, 12,  4,  0,  0), # -10800  3600 CLST
        datetime(1981,  3, 15,  3,  0,  0), # -14400     0 CLT
        datetime(1981, 10, 11,  4,  0,  0), # -10800  3600 CLST
        datetime(1982,  3, 14,  3,  0,  0), # -14400     0 CLT
        datetime(1982, 10, 10,  4,  0,  0), # -10800  3600 CLST
        datetime(1983,  3, 13,  3,  0,  0), # -14400     0 CLT
        datetime(1983, 10,  9,  4,  0,  0), # -10800  3600 CLST
        datetime(1984,  3, 11,  3,  0,  0), # -14400     0 CLT
        datetime(1984, 10, 14,  4,  0,  0), # -10800  3600 CLST
        datetime(1985,  3, 10,  3,  0,  0), # -14400     0 CLT
        datetime(1985, 10, 13,  4,  0,  0), # -10800  3600 CLST
        datetime(1986,  3,  9,  3,  0,  0), # -14400     0 CLT
        datetime(1986, 10, 12,  4,  0,  0), # -10800  3600 CLST
        datetime(1987,  3, 15,  3,  0,  0), # -14400     0 CLT
        datetime(1987, 10, 11,  4,  0,  0), # -10800  3600 CLST
        datetime(1988,  3, 13,  3,  0,  0), # -14400     0 CLT
        datetime(1988, 10,  9,  4,  0,  0), # -10800  3600 CLST
        datetime(1989,  3, 12,  3,  0,  0), # -14400     0 CLT
        datetime(1989, 10, 15,  4,  0,  0), # -10800  3600 CLST
        datetime(1990,  3, 11,  3,  0,  0), # -14400     0 CLT
        datetime(1990, 10, 14,  4,  0,  0), # -10800  3600 CLST
        datetime(1991,  3, 10,  3,  0,  0), # -14400     0 CLT
        datetime(1991, 10, 13,  4,  0,  0), # -10800  3600 CLST
        datetime(1992,  3, 15,  3,  0,  0), # -14400     0 CLT
        datetime(1992, 10, 11,  4,  0,  0), # -10800  3600 CLST
        datetime(1993,  3, 14,  3,  0,  0), # -14400     0 CLT
        datetime(1993, 10, 10,  4,  0,  0), # -10800  3600 CLST
        datetime(1994,  3, 13,  3,  0,  0), # -14400     0 CLT
        datetime(1994, 10,  9,  4,  0,  0), # -10800  3600 CLST
        datetime(1995,  3, 12,  3,  0,  0), # -14400     0 CLT
        datetime(1995, 10, 15,  4,  0,  0), # -10800  3600 CLST
        datetime(1996,  3, 10,  3,  0,  0), # -14400     0 CLT
        datetime(1996, 10, 13,  4,  0,  0), # -10800  3600 CLST
        datetime(1997,  3,  9,  3,  0,  0), # -14400     0 CLT
        datetime(1997, 10, 12,  4,  0,  0), # -10800  3600 CLST
        datetime(1998,  3, 15,  3,  0,  0), # -14400     0 CLT
        datetime(1998,  9, 27,  4,  0,  0), # -10800  3600 CLST
        datetime(1999,  4,  4,  3,  0,  0), # -14400     0 CLT
        datetime(1999, 10, 10,  4,  0,  0), # -10800  3600 CLST
        datetime(2000,  3, 12,  3,  0,  0), # -14400     0 CLT
        datetime(2000, 10, 15,  4,  0,  0), # -10800  3600 CLST
        datetime(2001,  3, 11,  3,  0,  0), # -14400     0 CLT
        datetime(2001, 10, 14,  4,  0,  0), # -10800  3600 CLST
        datetime(2002,  3, 10,  3,  0,  0), # -14400     0 CLT
        datetime(2002, 10, 13,  4,  0,  0), # -10800  3600 CLST
        datetime(2003,  3,  9,  3,  0,  0), # -14400     0 CLT
        datetime(2003, 10, 12,  4,  0,  0), # -10800  3600 CLST
        datetime(2004,  3, 14,  3,  0,  0), # -14400     0 CLT
        datetime(2004, 10, 10,  4,  0,  0), # -10800  3600 CLST
        datetime(2005,  3, 13,  3,  0,  0), # -14400     0 CLT
        datetime(2005, 10,  9,  4,  0,  0), # -10800  3600 CLST
        datetime(2006,  3, 12,  3,  0,  0), # -14400     0 CLT
        datetime(2006, 10, 15,  4,  0,  0), # -10800  3600 CLST
        datetime(2007,  3, 11,  3,  0,  0), # -14400     0 CLT
        datetime(2007, 10, 14,  4,  0,  0), # -10800  3600 CLST
        datetime(2008,  3,  9,  3,  0,  0), # -14400     0 CLT
        datetime(2008, 10, 12,  4,  0,  0), # -10800  3600 CLST
        datetime(2009,  3, 15,  3,  0,  0), # -14400     0 CLT
        datetime(2009, 10, 11,  4,  0,  0), # -10800  3600 CLST
        datetime(2010,  3, 14,  3,  0,  0), # -14400     0 CLT
        datetime(2010, 10, 10,  4,  0,  0), # -10800  3600 CLST
        datetime(2011,  3, 13,  3,  0,  0), # -14400     0 CLT
        datetime(2011, 10,  9,  4,  0,  0), # -10800  3600 CLST
        datetime(2012,  3, 11,  3,  0,  0), # -14400     0 CLT
        datetime(2012, 10, 14,  4,  0,  0), # -10800  3600 CLST
        datetime(2013,  3, 10,  3,  0,  0), # -14400     0 CLT
        datetime(2013, 10, 13,  4,  0,  0), # -10800  3600 CLST
        datetime(2014,  3,  9,  3,  0,  0), # -14400     0 CLT
        datetime(2014, 10, 12,  4,  0,  0), # -10800  3600 CLST
        datetime(2015,  3, 15,  3,  0,  0), # -14400     0 CLT
        datetime(2015, 10, 11,  4,  0,  0), # -10800  3600 CLST
        datetime(2016,  3, 13,  3,  0,  0), # -14400     0 CLT
        datetime(2016, 10,  9,  4,  0,  0), # -10800  3600 CLST
        datetime(2017,  3, 12,  3,  0,  0), # -14400     0 CLT
        datetime(2017, 10, 15,  4,  0,  0), # -10800  3600 CLST
        datetime(2018,  3, 11,  3,  0,  0), # -14400     0 CLT
        datetime(2018, 10, 14,  4,  0,  0), # -10800  3600 CLST
        datetime(2019,  3, 10,  3,  0,  0), # -14400     0 CLT
        datetime(2019, 10, 13,  4,  0,  0), # -10800  3600 CLST
        datetime(2020,  3, 15,  3,  0,  0), # -14400     0 CLT
        datetime(2020, 10, 11,  4,  0,  0), # -10800  3600 CLST
        datetime(2021,  3, 14,  3,  0,  0), # -14400     0 CLT
        datetime(2021, 10, 10,  4,  0,  0), # -10800  3600 CLST
        datetime(2022,  3, 13,  3,  0,  0), # -14400     0 CLT
        datetime(2022, 10,  9,  4,  0,  0), # -10800  3600 CLST
        datetime(2023,  3, 12,  3,  0,  0), # -14400     0 CLT
        datetime(2023, 10, 15,  4,  0,  0), # -10800  3600 CLST
        datetime(2024,  3, 10,  3,  0,  0), # -14400     0 CLT
        datetime(2024, 10, 13,  4,  0,  0), # -10800  3600 CLST
        datetime(2025,  3,  9,  3,  0,  0), # -14400     0 CLT
        datetime(2025, 10, 12,  4,  0,  0), # -10800  3600 CLST
        datetime(2026,  3, 15,  3,  0,  0), # -14400     0 CLT
        datetime(2026, 10, 11,  4,  0,  0), # -10800  3600 CLST
        datetime(2027,  3, 14,  3,  0,  0), # -14400     0 CLT
        datetime(2027, 10, 10,  4,  0,  0), # -10800  3600 CLST
        datetime(2028,  3, 12,  3,  0,  0), # -14400     0 CLT
        datetime(2028, 10, 15,  4,  0,  0), # -10800  3600 CLST
        datetime(2029,  3, 11,  3,  0,  0), # -14400     0 CLT
        datetime(2029, 10, 14,  4,  0,  0), # -10800  3600 CLST
        datetime(2030,  3, 10,  3,  0,  0), # -14400     0 CLT
        datetime(2030, 10, 13,  4,  0,  0), # -10800  3600 CLST
        datetime(2031,  3,  9,  3,  0,  0), # -14400     0 CLT
        datetime(2031, 10, 12,  4,  0,  0), # -10800  3600 CLST
        datetime(2032,  3, 14,  3,  0,  0), # -14400     0 CLT
        datetime(2032, 10, 10,  4,  0,  0), # -10800  3600 CLST
        datetime(2033,  3, 13,  3,  0,  0), # -14400     0 CLT
        datetime(2033, 10,  9,  4,  0,  0), # -10800  3600 CLST
        datetime(2034,  3, 12,  3,  0,  0), # -14400     0 CLT
        datetime(2034, 10, 15,  4,  0,  0), # -10800  3600 CLST
        datetime(2035,  3, 11,  3,  0,  0), # -14400     0 CLT
        datetime(2035, 10, 14,  4,  0,  0), # -10800  3600 CLST
        datetime(2036,  3,  9,  3,  0,  0), # -14400     0 CLT
        datetime(2036, 10, 12,  4,  0,  0), # -10800  3600 CLST
        datetime(2037,  3, 15,  3,  0,  0), # -14400     0 CLT
        datetime(2037, 10, 11,  4,  0,  0), # -10800  3600 CLST
        ]

    _transition_info = [
        ttinfo(-16960,      0,  'SMT'),
        ttinfo(-18000,      0,  'CLT'),
        ttinfo(-14400,   3600, 'CLST'),
        ttinfo(-18000,      0,  'CLT'),
        ttinfo(-14400,   3600, 'CLST'),
        ttinfo(-18000,      0,  'CLT'),
        ttinfo(-14400,   3600, 'CLST'),
        ttinfo(-18000,      0,  'CLT'),
        ttinfo(-14400,   3600, 'CLST'),
        ttinfo(-18000,      0,  'CLT'),
        ttinfo(-14400,   3600, 'CLST'),
        ttinfo(-18000,      0,  'CLT'),
        ttinfo(-14400,   3600, 'CLST'),
        ttinfo(-18000,      0,  'CLT'),
        ttinfo(-14400,      0,  'CLT'),
        ttinfo(-10800,   3600, 'CLST'),
        ttinfo(-14400,      0,  'CLT'),
        ttinfo(-10800,   3600, 'CLST'),
        ttinfo(-14400,      0,  'CLT'),
        ttinfo(-10800,   3600, 'CLST'),
        ttinfo(-14400,      0,  'CLT'),
        ttinfo(-10800,   3600, 'CLST'),
        ttinfo(-14400,      0,  'CLT'),
        ttinfo(-10800,   3600, 'CLST'),
        ttinfo(-14400,      0,  'CLT'),
        ttinfo(-10800,   3600, 'CLST'),
        ttinfo(-14400,      0,  'CLT'),
        ttinfo(-10800,   3600, 'CLST'),
        ttinfo(-14400,      0,  'CLT'),
        ttinfo(-10800,   3600, 'CLST'),
        ttinfo(-14400,      0,  'CLT'),
        ttinfo(-10800,   3600, 'CLST'),
        ttinfo(-14400,      0,  'CLT'),
        ttinfo(-10800,   3600, 'CLST'),
        ttinfo(-14400,      0,  'CLT'),
        ttinfo(-10800,   3600, 'CLST'),
        ttinfo(-14400,      0,  'CLT'),
        ttinfo(-10800,   3600, 'CLST'),
        ttinfo(-14400,      0,  'CLT'),
        ttinfo(-10800,   3600, 'CLST'),
        ttinfo(-14400,      0,  'CLT'),
        ttinfo(-10800,   3600, 'CLST'),
        ttinfo(-14400,      0,  'CLT'),
        ttinfo(-10800,   3600, 'CLST'),
        ttinfo(-14400,      0,  'CLT'),
        ttinfo(-10800,   3600, 'CLST'),
        ttinfo(-14400,      0,  'CLT'),
        ttinfo(-10800,   3600, 'CLST'),
        ttinfo(-14400,      0,  'CLT'),
        ttinfo(-10800,   3600, 'CLST'),
        ttinfo(-14400,      0,  'CLT'),
        ttinfo(-10800,   3600, 'CLST'),
        ttinfo(-14400,      0,  'CLT'),
        ttinfo(-10800,   3600, 'CLST'),
        ttinfo(-14400,      0,  'CLT'),
        ttinfo(-10800,   3600, 'CLST'),
        ttinfo(-14400,      0,  'CLT'),
        ttinfo(-10800,   3600, 'CLST'),
        ttinfo(-14400,      0,  'CLT'),
        ttinfo(-10800,   3600, 'CLST'),
        ttinfo(-14400,      0,  'CLT'),
        ttinfo(-10800,   3600, 'CLST'),
        ttinfo(-14400,      0,  'CLT'),
        ttinfo(-10800,   3600, 'CLST'),
        ttinfo(-14400,      0,  'CLT'),
        ttinfo(-10800,   3600, 'CLST'),
        ttinfo(-14400,      0,  'CLT'),
        ttinfo(-10800,   3600, 'CLST'),
        ttinfo(-14400,      0,  'CLT'),
        ttinfo(-10800,   3600, 'CLST'),
        ttinfo(-14400,      0,  'CLT'),
        ttinfo(-10800,   3600, 'CLST'),
        ttinfo(-14400,      0,  'CLT'),
        ttinfo(-10800,   3600, 'CLST'),
        ttinfo(-14400,      0,  'CLT'),
        ttinfo(-10800,   3600, 'CLST'),
        ttinfo(-14400,      0,  'CLT'),
        ttinfo(-10800,   3600, 'CLST'),
        ttinfo(-14400,      0,  'CLT'),
        ttinfo(-10800,   3600, 'CLST'),
        ttinfo(-14400,      0,  'CLT'),
        ttinfo(-10800,   3600, 'CLST'),
        ttinfo(-14400,      0,  'CLT'),
        ttinfo(-10800,   3600, 'CLST'),
        ttinfo(-14400,      0,  'CLT'),
        ttinfo(-10800,   3600, 'CLST'),
        ttinfo(-14400,      0,  'CLT'),
        ttinfo(-10800,   3600, 'CLST'),
        ttinfo(-14400,      0,  'CLT'),
        ttinfo(-10800,   3600, 'CLST'),
        ttinfo(-14400,      0,  'CLT'),
        ttinfo(-10800,   3600, 'CLST'),
        ttinfo(-14400,      0,  'CLT'),
        ttinfo(-10800,   3600, 'CLST'),
        ttinfo(-14400,      0,  'CLT'),
        ttinfo(-10800,   3600, 'CLST'),
        ttinfo(-14400,      0,  'CLT'),
        ttinfo(-10800,   3600, 'CLST'),
        ttinfo(-14400,      0,  'CLT'),
        ttinfo(-10800,   3600, 'CLST'),
        ttinfo(-14400,      0,  'CLT'),
        ttinfo(-10800,   3600, 'CLST'),
        ttinfo(-14400,      0,  'CLT'),
        ttinfo(-10800,   3600, 'CLST'),
        ttinfo(-14400,      0,  'CLT'),
        ttinfo(-10800,   3600, 'CLST'),
        ttinfo(-14400,      0,  'CLT'),
        ttinfo(-10800,   3600, 'CLST'),
        ttinfo(-14400,      0,  'CLT'),
        ttinfo(-10800,   3600, 'CLST'),
        ttinfo(-14400,      0,  'CLT'),
        ttinfo(-10800,   3600, 'CLST'),
        ttinfo(-14400,      0,  'CLT'),
        ttinfo(-10800,   3600, 'CLST'),
        ttinfo(-14400,      0,  'CLT'),
        ttinfo(-10800,   3600, 'CLST'),
        ttinfo(-14400,      0,  'CLT'),
        ttinfo(-10800,   3600, 'CLST'),
        ttinfo(-14400,      0,  'CLT'),
        ttinfo(-10800,   3600, 'CLST'),
        ttinfo(-14400,      0,  'CLT'),
        ttinfo(-10800,   3600, 'CLST'),
        ttinfo(-14400,      0,  'CLT'),
        ttinfo(-10800,   3600, 'CLST'),
        ttinfo(-14400,      0,  'CLT'),
        ttinfo(-10800,   3600, 'CLST'),
        ttinfo(-14400,      0,  'CLT'),
        ttinfo(-10800,   3600, 'CLST'),
        ttinfo(-14400,      0,  'CLT'),
        ttinfo(-10800,   3600, 'CLST'),
        ttinfo(-14400,      0,  'CLT'),
        ttinfo(-10800,   3600, 'CLST'),
        ttinfo(-14400,      0,  'CLT'),
        ttinfo(-10800,   3600, 'CLST'),
        ttinfo(-14400,      0,  'CLT'),
        ttinfo(-10800,   3600, 'CLST'),
        ttinfo(-14400,      0,  'CLT'),
        ttinfo(-10800,   3600, 'CLST'),
        ttinfo(-14400,      0,  'CLT'),
        ttinfo(-10800,   3600, 'CLST'),
        ttinfo(-14400,      0,  'CLT'),
        ttinfo(-10800,   3600, 'CLST'),
        ttinfo(-14400,      0,  'CLT'),
        ttinfo(-10800,   3600, 'CLST'),
        ttinfo(-14400,      0,  'CLT'),
        ttinfo(-10800,   3600, 'CLST'),
        ttinfo(-14400,      0,  'CLT'),
        ttinfo(-10800,   3600, 'CLST'),
        ttinfo(-14400,      0,  'CLT'),
        ttinfo(-10800,   3600, 'CLST'),
        ttinfo(-14400,      0,  'CLT'),
        ttinfo(-10800,   3600, 'CLST'),
        ttinfo(-14400,      0,  'CLT'),
        ttinfo(-10800,   3600, 'CLST'),
        ttinfo(-14400,      0,  'CLT'),
        ttinfo(-10800,   3600, 'CLST'),
        ttinfo(-14400,      0,  'CLT'),
        ttinfo(-10800,   3600, 'CLST'),
        ]

Santiago = Santiago() # Singleton

