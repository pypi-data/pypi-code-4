'''
tzinfo timezone information for Cuba.

Generated from the Olson timezone database:
    ftp://elsie.nci.nih.gov/pub/tz*.tar.gz
'''

from pytz.tzinfo import DstTzInfo
from pytz.tzinfo import memorized_datetime as datetime
from pytz.tzinfo import memorized_ttinfo as ttinfo

class Cuba(DstTzInfo):
    '''Cuba timezone definition. See datetime.tzinfo for details'''

    _zone = 'Cuba'

    _utc_transition_times = [
        datetime(   1,  1,  1,  0,  0,  0), # -19776     0 HMT
        datetime(1925,  7, 19, 17, 29, 36), # -18000     0 CST
        datetime(1928,  6, 10,  5,  0,  0), # -14400  3600 CDT
        datetime(1928, 10, 10,  4,  0,  0), # -18000     0 CST
        datetime(1940,  6,  2,  5,  0,  0), # -14400  3600 CDT
        datetime(1940,  9,  1,  4,  0,  0), # -18000     0 CST
        datetime(1941,  6,  1,  5,  0,  0), # -14400  3600 CDT
        datetime(1941,  9,  7,  4,  0,  0), # -18000     0 CST
        datetime(1942,  6,  7,  5,  0,  0), # -14400  3600 CDT
        datetime(1942,  9,  6,  4,  0,  0), # -18000     0 CST
        datetime(1945,  6,  3,  5,  0,  0), # -14400  3600 CDT
        datetime(1945,  9,  2,  4,  0,  0), # -18000     0 CST
        datetime(1946,  6,  2,  5,  0,  0), # -14400  3600 CDT
        datetime(1946,  9,  1,  4,  0,  0), # -18000     0 CST
        datetime(1965,  6,  1,  5,  0,  0), # -14400  3600 CDT
        datetime(1965,  9, 30,  4,  0,  0), # -18000     0 CST
        datetime(1966,  5, 29,  5,  0,  0), # -14400  3600 CDT
        datetime(1966, 10,  2,  4,  0,  0), # -18000     0 CST
        datetime(1967,  4,  8,  5,  0,  0), # -14400  3600 CDT
        datetime(1967,  9, 10,  4,  0,  0), # -18000     0 CST
        datetime(1968,  4, 14,  5,  0,  0), # -14400  3600 CDT
        datetime(1968,  9,  8,  4,  0,  0), # -18000     0 CST
        datetime(1969,  4, 27,  5,  0,  0), # -14400  3600 CDT
        datetime(1969, 10, 26,  4,  0,  0), # -18000     0 CST
        datetime(1970,  4, 26,  5,  0,  0), # -14400  3600 CDT
        datetime(1970, 10, 25,  4,  0,  0), # -18000     0 CST
        datetime(1971,  4, 25,  5,  0,  0), # -14400  3600 CDT
        datetime(1971, 10, 31,  4,  0,  0), # -18000     0 CST
        datetime(1972,  4, 30,  5,  0,  0), # -14400  3600 CDT
        datetime(1972, 10,  8,  4,  0,  0), # -18000     0 CST
        datetime(1973,  4, 29,  5,  0,  0), # -14400  3600 CDT
        datetime(1973, 10,  8,  4,  0,  0), # -18000     0 CST
        datetime(1974,  4, 28,  5,  0,  0), # -14400  3600 CDT
        datetime(1974, 10,  8,  4,  0,  0), # -18000     0 CST
        datetime(1975,  4, 27,  5,  0,  0), # -14400  3600 CDT
        datetime(1975, 10, 26,  4,  0,  0), # -18000     0 CST
        datetime(1976,  4, 25,  5,  0,  0), # -14400  3600 CDT
        datetime(1976, 10, 31,  4,  0,  0), # -18000     0 CST
        datetime(1977,  4, 24,  5,  0,  0), # -14400  3600 CDT
        datetime(1977, 10, 30,  4,  0,  0), # -18000     0 CST
        datetime(1978,  5,  7,  5,  0,  0), # -14400  3600 CDT
        datetime(1978, 10,  8,  4,  0,  0), # -18000     0 CST
        datetime(1979,  3, 18,  5,  0,  0), # -14400  3600 CDT
        datetime(1979, 10, 14,  4,  0,  0), # -18000     0 CST
        datetime(1980,  3, 16,  5,  0,  0), # -14400  3600 CDT
        datetime(1980, 10, 12,  4,  0,  0), # -18000     0 CST
        datetime(1981,  5, 10,  5,  0,  0), # -14400  3600 CDT
        datetime(1981, 10, 11,  4,  0,  0), # -18000     0 CST
        datetime(1982,  5,  9,  5,  0,  0), # -14400  3600 CDT
        datetime(1982, 10, 10,  4,  0,  0), # -18000     0 CST
        datetime(1983,  5,  8,  5,  0,  0), # -14400  3600 CDT
        datetime(1983, 10,  9,  4,  0,  0), # -18000     0 CST
        datetime(1984,  5,  6,  5,  0,  0), # -14400  3600 CDT
        datetime(1984, 10, 14,  4,  0,  0), # -18000     0 CST
        datetime(1985,  5,  5,  5,  0,  0), # -14400  3600 CDT
        datetime(1985, 10, 13,  4,  0,  0), # -18000     0 CST
        datetime(1986,  3, 16,  5,  0,  0), # -14400  3600 CDT
        datetime(1986, 10, 12,  4,  0,  0), # -18000     0 CST
        datetime(1987,  3, 15,  5,  0,  0), # -14400  3600 CDT
        datetime(1987, 10, 11,  4,  0,  0), # -18000     0 CST
        datetime(1988,  3, 20,  5,  0,  0), # -14400  3600 CDT
        datetime(1988, 10,  9,  4,  0,  0), # -18000     0 CST
        datetime(1989,  3, 19,  5,  0,  0), # -14400  3600 CDT
        datetime(1989, 10,  8,  4,  0,  0), # -18000     0 CST
        datetime(1990,  4,  1,  5,  0,  0), # -14400  3600 CDT
        datetime(1990, 10, 14,  4,  0,  0), # -18000     0 CST
        datetime(1991,  4,  7,  5,  0,  0), # -14400  3600 CDT
        datetime(1991, 10, 13,  5,  0,  0), # -18000     0 CST
        datetime(1992,  4,  5,  5,  0,  0), # -14400  3600 CDT
        datetime(1992, 10, 11,  5,  0,  0), # -18000     0 CST
        datetime(1993,  4,  4,  5,  0,  0), # -14400  3600 CDT
        datetime(1993, 10, 10,  5,  0,  0), # -18000     0 CST
        datetime(1994,  4,  3,  5,  0,  0), # -14400  3600 CDT
        datetime(1994, 10,  9,  5,  0,  0), # -18000     0 CST
        datetime(1995,  4,  2,  5,  0,  0), # -14400  3600 CDT
        datetime(1995, 10,  8,  5,  0,  0), # -18000     0 CST
        datetime(1996,  4,  7,  5,  0,  0), # -14400  3600 CDT
        datetime(1996, 10,  6,  5,  0,  0), # -18000     0 CST
        datetime(1997,  4,  6,  5,  0,  0), # -14400  3600 CDT
        datetime(1997, 10, 12,  5,  0,  0), # -18000     0 CST
        datetime(1998,  3, 29,  5,  0,  0), # -14400  3600 CDT
        datetime(1998, 10, 25,  5,  0,  0), # -18000     0 CST
        datetime(1999,  3, 28,  5,  0,  0), # -14400  3600 CDT
        datetime(1999, 10, 31,  5,  0,  0), # -18000     0 CST
        datetime(2000,  4,  2,  5,  0,  0), # -14400  3600 CDT
        datetime(2000, 10, 29,  5,  0,  0), # -18000     0 CST
        datetime(2001,  4,  1,  5,  0,  0), # -14400  3600 CDT
        datetime(2001, 10, 28,  5,  0,  0), # -18000     0 CST
        datetime(2002,  4,  7,  5,  0,  0), # -14400  3600 CDT
        datetime(2002, 10, 27,  5,  0,  0), # -18000     0 CST
        datetime(2003,  4,  6,  5,  0,  0), # -14400  3600 CDT
        datetime(2003, 10, 26,  5,  0,  0), # -18000     0 CST
        datetime(2004,  4,  4,  5,  0,  0), # -14400  3600 CDT
        datetime(2004, 10, 31,  5,  0,  0), # -18000     0 CST
        datetime(2005,  4,  3,  5,  0,  0), # -14400  3600 CDT
        datetime(2005, 10, 30,  5,  0,  0), # -18000     0 CST
        datetime(2006,  4,  2,  5,  0,  0), # -14400  3600 CDT
        datetime(2006, 10, 29,  5,  0,  0), # -18000     0 CST
        datetime(2007,  4,  1,  5,  0,  0), # -14400  3600 CDT
        datetime(2007, 10, 28,  5,  0,  0), # -18000     0 CST
        datetime(2008,  4,  6,  5,  0,  0), # -14400  3600 CDT
        datetime(2008, 10, 26,  5,  0,  0), # -18000     0 CST
        datetime(2009,  4,  5,  5,  0,  0), # -14400  3600 CDT
        datetime(2009, 10, 25,  5,  0,  0), # -18000     0 CST
        datetime(2010,  4,  4,  5,  0,  0), # -14400  3600 CDT
        datetime(2010, 10, 31,  5,  0,  0), # -18000     0 CST
        datetime(2011,  4,  3,  5,  0,  0), # -14400  3600 CDT
        datetime(2011, 10, 30,  5,  0,  0), # -18000     0 CST
        datetime(2012,  4,  1,  5,  0,  0), # -14400  3600 CDT
        datetime(2012, 10, 28,  5,  0,  0), # -18000     0 CST
        datetime(2013,  4,  7,  5,  0,  0), # -14400  3600 CDT
        datetime(2013, 10, 27,  5,  0,  0), # -18000     0 CST
        datetime(2014,  4,  6,  5,  0,  0), # -14400  3600 CDT
        datetime(2014, 10, 26,  5,  0,  0), # -18000     0 CST
        datetime(2015,  4,  5,  5,  0,  0), # -14400  3600 CDT
        datetime(2015, 10, 25,  5,  0,  0), # -18000     0 CST
        datetime(2016,  4,  3,  5,  0,  0), # -14400  3600 CDT
        datetime(2016, 10, 30,  5,  0,  0), # -18000     0 CST
        datetime(2017,  4,  2,  5,  0,  0), # -14400  3600 CDT
        datetime(2017, 10, 29,  5,  0,  0), # -18000     0 CST
        datetime(2018,  4,  1,  5,  0,  0), # -14400  3600 CDT
        datetime(2018, 10, 28,  5,  0,  0), # -18000     0 CST
        datetime(2019,  4,  7,  5,  0,  0), # -14400  3600 CDT
        datetime(2019, 10, 27,  5,  0,  0), # -18000     0 CST
        datetime(2020,  4,  5,  5,  0,  0), # -14400  3600 CDT
        datetime(2020, 10, 25,  5,  0,  0), # -18000     0 CST
        datetime(2021,  4,  4,  5,  0,  0), # -14400  3600 CDT
        datetime(2021, 10, 31,  5,  0,  0), # -18000     0 CST
        datetime(2022,  4,  3,  5,  0,  0), # -14400  3600 CDT
        datetime(2022, 10, 30,  5,  0,  0), # -18000     0 CST
        datetime(2023,  4,  2,  5,  0,  0), # -14400  3600 CDT
        datetime(2023, 10, 29,  5,  0,  0), # -18000     0 CST
        datetime(2024,  4,  7,  5,  0,  0), # -14400  3600 CDT
        datetime(2024, 10, 27,  5,  0,  0), # -18000     0 CST
        datetime(2025,  4,  6,  5,  0,  0), # -14400  3600 CDT
        datetime(2025, 10, 26,  5,  0,  0), # -18000     0 CST
        datetime(2026,  4,  5,  5,  0,  0), # -14400  3600 CDT
        datetime(2026, 10, 25,  5,  0,  0), # -18000     0 CST
        datetime(2027,  4,  4,  5,  0,  0), # -14400  3600 CDT
        datetime(2027, 10, 31,  5,  0,  0), # -18000     0 CST
        datetime(2028,  4,  2,  5,  0,  0), # -14400  3600 CDT
        datetime(2028, 10, 29,  5,  0,  0), # -18000     0 CST
        datetime(2029,  4,  1,  5,  0,  0), # -14400  3600 CDT
        datetime(2029, 10, 28,  5,  0,  0), # -18000     0 CST
        datetime(2030,  4,  7,  5,  0,  0), # -14400  3600 CDT
        datetime(2030, 10, 27,  5,  0,  0), # -18000     0 CST
        datetime(2031,  4,  6,  5,  0,  0), # -14400  3600 CDT
        datetime(2031, 10, 26,  5,  0,  0), # -18000     0 CST
        datetime(2032,  4,  4,  5,  0,  0), # -14400  3600 CDT
        datetime(2032, 10, 31,  5,  0,  0), # -18000     0 CST
        datetime(2033,  4,  3,  5,  0,  0), # -14400  3600 CDT
        datetime(2033, 10, 30,  5,  0,  0), # -18000     0 CST
        datetime(2034,  4,  2,  5,  0,  0), # -14400  3600 CDT
        datetime(2034, 10, 29,  5,  0,  0), # -18000     0 CST
        datetime(2035,  4,  1,  5,  0,  0), # -14400  3600 CDT
        datetime(2035, 10, 28,  5,  0,  0), # -18000     0 CST
        datetime(2036,  4,  6,  5,  0,  0), # -14400  3600 CDT
        datetime(2036, 10, 26,  5,  0,  0), # -18000     0 CST
        datetime(2037,  4,  5,  5,  0,  0), # -14400  3600 CDT
        datetime(2037, 10, 25,  5,  0,  0), # -18000     0 CST
        ]

    _transition_info = [
        ttinfo(-19776,      0,  'HMT'),
        ttinfo(-18000,      0,  'CST'),
        ttinfo(-14400,   3600,  'CDT'),
        ttinfo(-18000,      0,  'CST'),
        ttinfo(-14400,   3600,  'CDT'),
        ttinfo(-18000,      0,  'CST'),
        ttinfo(-14400,   3600,  'CDT'),
        ttinfo(-18000,      0,  'CST'),
        ttinfo(-14400,   3600,  'CDT'),
        ttinfo(-18000,      0,  'CST'),
        ttinfo(-14400,   3600,  'CDT'),
        ttinfo(-18000,      0,  'CST'),
        ttinfo(-14400,   3600,  'CDT'),
        ttinfo(-18000,      0,  'CST'),
        ttinfo(-14400,   3600,  'CDT'),
        ttinfo(-18000,      0,  'CST'),
        ttinfo(-14400,   3600,  'CDT'),
        ttinfo(-18000,      0,  'CST'),
        ttinfo(-14400,   3600,  'CDT'),
        ttinfo(-18000,      0,  'CST'),
        ttinfo(-14400,   3600,  'CDT'),
        ttinfo(-18000,      0,  'CST'),
        ttinfo(-14400,   3600,  'CDT'),
        ttinfo(-18000,      0,  'CST'),
        ttinfo(-14400,   3600,  'CDT'),
        ttinfo(-18000,      0,  'CST'),
        ttinfo(-14400,   3600,  'CDT'),
        ttinfo(-18000,      0,  'CST'),
        ttinfo(-14400,   3600,  'CDT'),
        ttinfo(-18000,      0,  'CST'),
        ttinfo(-14400,   3600,  'CDT'),
        ttinfo(-18000,      0,  'CST'),
        ttinfo(-14400,   3600,  'CDT'),
        ttinfo(-18000,      0,  'CST'),
        ttinfo(-14400,   3600,  'CDT'),
        ttinfo(-18000,      0,  'CST'),
        ttinfo(-14400,   3600,  'CDT'),
        ttinfo(-18000,      0,  'CST'),
        ttinfo(-14400,   3600,  'CDT'),
        ttinfo(-18000,      0,  'CST'),
        ttinfo(-14400,   3600,  'CDT'),
        ttinfo(-18000,      0,  'CST'),
        ttinfo(-14400,   3600,  'CDT'),
        ttinfo(-18000,      0,  'CST'),
        ttinfo(-14400,   3600,  'CDT'),
        ttinfo(-18000,      0,  'CST'),
        ttinfo(-14400,   3600,  'CDT'),
        ttinfo(-18000,      0,  'CST'),
        ttinfo(-14400,   3600,  'CDT'),
        ttinfo(-18000,      0,  'CST'),
        ttinfo(-14400,   3600,  'CDT'),
        ttinfo(-18000,      0,  'CST'),
        ttinfo(-14400,   3600,  'CDT'),
        ttinfo(-18000,      0,  'CST'),
        ttinfo(-14400,   3600,  'CDT'),
        ttinfo(-18000,      0,  'CST'),
        ttinfo(-14400,   3600,  'CDT'),
        ttinfo(-18000,      0,  'CST'),
        ttinfo(-14400,   3600,  'CDT'),
        ttinfo(-18000,      0,  'CST'),
        ttinfo(-14400,   3600,  'CDT'),
        ttinfo(-18000,      0,  'CST'),
        ttinfo(-14400,   3600,  'CDT'),
        ttinfo(-18000,      0,  'CST'),
        ttinfo(-14400,   3600,  'CDT'),
        ttinfo(-18000,      0,  'CST'),
        ttinfo(-14400,   3600,  'CDT'),
        ttinfo(-18000,      0,  'CST'),
        ttinfo(-14400,   3600,  'CDT'),
        ttinfo(-18000,      0,  'CST'),
        ttinfo(-14400,   3600,  'CDT'),
        ttinfo(-18000,      0,  'CST'),
        ttinfo(-14400,   3600,  'CDT'),
        ttinfo(-18000,      0,  'CST'),
        ttinfo(-14400,   3600,  'CDT'),
        ttinfo(-18000,      0,  'CST'),
        ttinfo(-14400,   3600,  'CDT'),
        ttinfo(-18000,      0,  'CST'),
        ttinfo(-14400,   3600,  'CDT'),
        ttinfo(-18000,      0,  'CST'),
        ttinfo(-14400,   3600,  'CDT'),
        ttinfo(-18000,      0,  'CST'),
        ttinfo(-14400,   3600,  'CDT'),
        ttinfo(-18000,      0,  'CST'),
        ttinfo(-14400,   3600,  'CDT'),
        ttinfo(-18000,      0,  'CST'),
        ttinfo(-14400,   3600,  'CDT'),
        ttinfo(-18000,      0,  'CST'),
        ttinfo(-14400,   3600,  'CDT'),
        ttinfo(-18000,      0,  'CST'),
        ttinfo(-14400,   3600,  'CDT'),
        ttinfo(-18000,      0,  'CST'),
        ttinfo(-14400,   3600,  'CDT'),
        ttinfo(-18000,      0,  'CST'),
        ttinfo(-14400,   3600,  'CDT'),
        ttinfo(-18000,      0,  'CST'),
        ttinfo(-14400,   3600,  'CDT'),
        ttinfo(-18000,      0,  'CST'),
        ttinfo(-14400,   3600,  'CDT'),
        ttinfo(-18000,      0,  'CST'),
        ttinfo(-14400,   3600,  'CDT'),
        ttinfo(-18000,      0,  'CST'),
        ttinfo(-14400,   3600,  'CDT'),
        ttinfo(-18000,      0,  'CST'),
        ttinfo(-14400,   3600,  'CDT'),
        ttinfo(-18000,      0,  'CST'),
        ttinfo(-14400,   3600,  'CDT'),
        ttinfo(-18000,      0,  'CST'),
        ttinfo(-14400,   3600,  'CDT'),
        ttinfo(-18000,      0,  'CST'),
        ttinfo(-14400,   3600,  'CDT'),
        ttinfo(-18000,      0,  'CST'),
        ttinfo(-14400,   3600,  'CDT'),
        ttinfo(-18000,      0,  'CST'),
        ttinfo(-14400,   3600,  'CDT'),
        ttinfo(-18000,      0,  'CST'),
        ttinfo(-14400,   3600,  'CDT'),
        ttinfo(-18000,      0,  'CST'),
        ttinfo(-14400,   3600,  'CDT'),
        ttinfo(-18000,      0,  'CST'),
        ttinfo(-14400,   3600,  'CDT'),
        ttinfo(-18000,      0,  'CST'),
        ttinfo(-14400,   3600,  'CDT'),
        ttinfo(-18000,      0,  'CST'),
        ttinfo(-14400,   3600,  'CDT'),
        ttinfo(-18000,      0,  'CST'),
        ttinfo(-14400,   3600,  'CDT'),
        ttinfo(-18000,      0,  'CST'),
        ttinfo(-14400,   3600,  'CDT'),
        ttinfo(-18000,      0,  'CST'),
        ttinfo(-14400,   3600,  'CDT'),
        ttinfo(-18000,      0,  'CST'),
        ttinfo(-14400,   3600,  'CDT'),
        ttinfo(-18000,      0,  'CST'),
        ttinfo(-14400,   3600,  'CDT'),
        ttinfo(-18000,      0,  'CST'),
        ttinfo(-14400,   3600,  'CDT'),
        ttinfo(-18000,      0,  'CST'),
        ttinfo(-14400,   3600,  'CDT'),
        ttinfo(-18000,      0,  'CST'),
        ttinfo(-14400,   3600,  'CDT'),
        ttinfo(-18000,      0,  'CST'),
        ttinfo(-14400,   3600,  'CDT'),
        ttinfo(-18000,      0,  'CST'),
        ttinfo(-14400,   3600,  'CDT'),
        ttinfo(-18000,      0,  'CST'),
        ttinfo(-14400,   3600,  'CDT'),
        ttinfo(-18000,      0,  'CST'),
        ttinfo(-14400,   3600,  'CDT'),
        ttinfo(-18000,      0,  'CST'),
        ttinfo(-14400,   3600,  'CDT'),
        ttinfo(-18000,      0,  'CST'),
        ttinfo(-14400,   3600,  'CDT'),
        ttinfo(-18000,      0,  'CST'),
        ttinfo(-14400,   3600,  'CDT'),
        ttinfo(-18000,      0,  'CST'),
        ttinfo(-14400,   3600,  'CDT'),
        ttinfo(-18000,      0,  'CST'),
        ttinfo(-14400,   3600,  'CDT'),
        ttinfo(-18000,      0,  'CST'),
        ]

Cuba = Cuba() # Singleton

