'''
tzinfo timezone information for America/Kentucky/Monticello.

Generated from the Olson timezone database:
    ftp://elsie.nci.nih.gov/pub/tz*.tar.gz
'''

from pytz.tzinfo import DstTzInfo
from pytz.tzinfo import memorized_datetime as datetime
from pytz.tzinfo import memorized_ttinfo as ttinfo

class Monticello(DstTzInfo):
    '''America/Kentucky/Monticello timezone definition. See datetime.tzinfo for details'''

    _zone = 'America/Kentucky/Monticello'

    _utc_transition_times = [
        datetime(   1,  1,  1,  0,  0,  0), # -21600     0 CST
        datetime(1918,  3, 31,  8,  0,  0), # -18000  3600 CDT
        datetime(1918, 10, 27,  7,  0,  0), # -21600     0 CST
        datetime(1919,  3, 30,  8,  0,  0), # -18000  3600 CDT
        datetime(1919, 10, 26,  7,  0,  0), # -21600     0 CST
        datetime(1942,  2,  9,  8,  0,  0), # -18000  3600 CWT
        datetime(1945,  8, 14, 23,  0,  0), # -18000     0 CPT
        datetime(1945,  9, 30,  7,  0,  0), # -21600     0 CST
        datetime(1968,  4, 28,  8,  0,  0), # -18000  3600 CDT
        datetime(1968, 10, 27,  7,  0,  0), # -21600     0 CST
        datetime(1969,  4, 27,  8,  0,  0), # -18000  3600 CDT
        datetime(1969, 10, 26,  7,  0,  0), # -21600     0 CST
        datetime(1970,  4, 26,  8,  0,  0), # -18000  3600 CDT
        datetime(1970, 10, 25,  7,  0,  0), # -21600     0 CST
        datetime(1971,  4, 25,  8,  0,  0), # -18000  3600 CDT
        datetime(1971, 10, 31,  7,  0,  0), # -21600     0 CST
        datetime(1972,  4, 30,  8,  0,  0), # -18000  3600 CDT
        datetime(1972, 10, 29,  7,  0,  0), # -21600     0 CST
        datetime(1973,  4, 29,  8,  0,  0), # -18000  3600 CDT
        datetime(1973, 10, 28,  7,  0,  0), # -21600     0 CST
        datetime(1974,  1,  6,  8,  0,  0), # -18000  3600 CDT
        datetime(1974, 10, 27,  7,  0,  0), # -21600     0 CST
        datetime(1975,  2, 23,  8,  0,  0), # -18000  3600 CDT
        datetime(1975, 10, 26,  7,  0,  0), # -21600     0 CST
        datetime(1976,  4, 25,  8,  0,  0), # -18000  3600 CDT
        datetime(1976, 10, 31,  7,  0,  0), # -21600     0 CST
        datetime(1977,  4, 24,  8,  0,  0), # -18000  3600 CDT
        datetime(1977, 10, 30,  7,  0,  0), # -21600     0 CST
        datetime(1978,  4, 30,  8,  0,  0), # -18000  3600 CDT
        datetime(1978, 10, 29,  7,  0,  0), # -21600     0 CST
        datetime(1979,  4, 29,  8,  0,  0), # -18000  3600 CDT
        datetime(1979, 10, 28,  7,  0,  0), # -21600     0 CST
        datetime(1980,  4, 27,  8,  0,  0), # -18000  3600 CDT
        datetime(1980, 10, 26,  7,  0,  0), # -21600     0 CST
        datetime(1981,  4, 26,  8,  0,  0), # -18000  3600 CDT
        datetime(1981, 10, 25,  7,  0,  0), # -21600     0 CST
        datetime(1982,  4, 25,  8,  0,  0), # -18000  3600 CDT
        datetime(1982, 10, 31,  7,  0,  0), # -21600     0 CST
        datetime(1983,  4, 24,  8,  0,  0), # -18000  3600 CDT
        datetime(1983, 10, 30,  7,  0,  0), # -21600     0 CST
        datetime(1984,  4, 29,  8,  0,  0), # -18000  3600 CDT
        datetime(1984, 10, 28,  7,  0,  0), # -21600     0 CST
        datetime(1985,  4, 28,  8,  0,  0), # -18000  3600 CDT
        datetime(1985, 10, 27,  7,  0,  0), # -21600     0 CST
        datetime(1986,  4, 27,  8,  0,  0), # -18000  3600 CDT
        datetime(1986, 10, 26,  7,  0,  0), # -21600     0 CST
        datetime(1987,  4,  5,  8,  0,  0), # -18000  3600 CDT
        datetime(1987, 10, 25,  7,  0,  0), # -21600     0 CST
        datetime(1988,  4,  3,  8,  0,  0), # -18000  3600 CDT
        datetime(1988, 10, 30,  7,  0,  0), # -21600     0 CST
        datetime(1989,  4,  2,  8,  0,  0), # -18000  3600 CDT
        datetime(1989, 10, 29,  7,  0,  0), # -21600     0 CST
        datetime(1990,  4,  1,  8,  0,  0), # -18000  3600 CDT
        datetime(1990, 10, 28,  7,  0,  0), # -21600     0 CST
        datetime(1991,  4,  7,  8,  0,  0), # -18000  3600 CDT
        datetime(1991, 10, 27,  7,  0,  0), # -21600     0 CST
        datetime(1992,  4,  5,  8,  0,  0), # -18000  3600 CDT
        datetime(1992, 10, 25,  7,  0,  0), # -21600     0 CST
        datetime(1993,  4,  4,  8,  0,  0), # -18000  3600 CDT
        datetime(1993, 10, 31,  7,  0,  0), # -21600     0 CST
        datetime(1994,  4,  3,  8,  0,  0), # -18000  3600 CDT
        datetime(1994, 10, 30,  7,  0,  0), # -21600     0 CST
        datetime(1995,  4,  2,  8,  0,  0), # -18000  3600 CDT
        datetime(1995, 10, 29,  7,  0,  0), # -21600     0 CST
        datetime(1996,  4,  7,  8,  0,  0), # -18000  3600 CDT
        datetime(1996, 10, 27,  7,  0,  0), # -21600     0 CST
        datetime(1997,  4,  6,  8,  0,  0), # -18000  3600 CDT
        datetime(1997, 10, 26,  7,  0,  0), # -21600     0 CST
        datetime(1998,  4,  5,  8,  0,  0), # -18000  3600 CDT
        datetime(1998, 10, 25,  7,  0,  0), # -21600     0 CST
        datetime(1999,  4,  4,  8,  0,  0), # -18000  3600 CDT
        datetime(1999, 10, 31,  7,  0,  0), # -21600     0 CST
        datetime(2000,  4,  2,  8,  0,  0), # -18000  3600 CDT
        datetime(2000, 10, 29,  7,  0,  0), # -18000     0 EST
        datetime(2001,  4,  1,  7,  0,  0), # -14400  3600 EDT
        datetime(2001, 10, 28,  6,  0,  0), # -18000     0 EST
        datetime(2002,  4,  7,  7,  0,  0), # -14400  3600 EDT
        datetime(2002, 10, 27,  6,  0,  0), # -18000     0 EST
        datetime(2003,  4,  6,  7,  0,  0), # -14400  3600 EDT
        datetime(2003, 10, 26,  6,  0,  0), # -18000     0 EST
        datetime(2004,  4,  4,  7,  0,  0), # -14400  3600 EDT
        datetime(2004, 10, 31,  6,  0,  0), # -18000     0 EST
        datetime(2005,  4,  3,  7,  0,  0), # -14400  3600 EDT
        datetime(2005, 10, 30,  6,  0,  0), # -18000     0 EST
        datetime(2006,  4,  2,  7,  0,  0), # -14400  3600 EDT
        datetime(2006, 10, 29,  6,  0,  0), # -18000     0 EST
        datetime(2007,  4,  1,  7,  0,  0), # -14400  3600 EDT
        datetime(2007, 10, 28,  6,  0,  0), # -18000     0 EST
        datetime(2008,  4,  6,  7,  0,  0), # -14400  3600 EDT
        datetime(2008, 10, 26,  6,  0,  0), # -18000     0 EST
        datetime(2009,  4,  5,  7,  0,  0), # -14400  3600 EDT
        datetime(2009, 10, 25,  6,  0,  0), # -18000     0 EST
        datetime(2010,  4,  4,  7,  0,  0), # -14400  3600 EDT
        datetime(2010, 10, 31,  6,  0,  0), # -18000     0 EST
        datetime(2011,  4,  3,  7,  0,  0), # -14400  3600 EDT
        datetime(2011, 10, 30,  6,  0,  0), # -18000     0 EST
        datetime(2012,  4,  1,  7,  0,  0), # -14400  3600 EDT
        datetime(2012, 10, 28,  6,  0,  0), # -18000     0 EST
        datetime(2013,  4,  7,  7,  0,  0), # -14400  3600 EDT
        datetime(2013, 10, 27,  6,  0,  0), # -18000     0 EST
        datetime(2014,  4,  6,  7,  0,  0), # -14400  3600 EDT
        datetime(2014, 10, 26,  6,  0,  0), # -18000     0 EST
        datetime(2015,  4,  5,  7,  0,  0), # -14400  3600 EDT
        datetime(2015, 10, 25,  6,  0,  0), # -18000     0 EST
        datetime(2016,  4,  3,  7,  0,  0), # -14400  3600 EDT
        datetime(2016, 10, 30,  6,  0,  0), # -18000     0 EST
        datetime(2017,  4,  2,  7,  0,  0), # -14400  3600 EDT
        datetime(2017, 10, 29,  6,  0,  0), # -18000     0 EST
        datetime(2018,  4,  1,  7,  0,  0), # -14400  3600 EDT
        datetime(2018, 10, 28,  6,  0,  0), # -18000     0 EST
        datetime(2019,  4,  7,  7,  0,  0), # -14400  3600 EDT
        datetime(2019, 10, 27,  6,  0,  0), # -18000     0 EST
        datetime(2020,  4,  5,  7,  0,  0), # -14400  3600 EDT
        datetime(2020, 10, 25,  6,  0,  0), # -18000     0 EST
        datetime(2021,  4,  4,  7,  0,  0), # -14400  3600 EDT
        datetime(2021, 10, 31,  6,  0,  0), # -18000     0 EST
        datetime(2022,  4,  3,  7,  0,  0), # -14400  3600 EDT
        datetime(2022, 10, 30,  6,  0,  0), # -18000     0 EST
        datetime(2023,  4,  2,  7,  0,  0), # -14400  3600 EDT
        datetime(2023, 10, 29,  6,  0,  0), # -18000     0 EST
        datetime(2024,  4,  7,  7,  0,  0), # -14400  3600 EDT
        datetime(2024, 10, 27,  6,  0,  0), # -18000     0 EST
        datetime(2025,  4,  6,  7,  0,  0), # -14400  3600 EDT
        datetime(2025, 10, 26,  6,  0,  0), # -18000     0 EST
        datetime(2026,  4,  5,  7,  0,  0), # -14400  3600 EDT
        datetime(2026, 10, 25,  6,  0,  0), # -18000     0 EST
        datetime(2027,  4,  4,  7,  0,  0), # -14400  3600 EDT
        datetime(2027, 10, 31,  6,  0,  0), # -18000     0 EST
        datetime(2028,  4,  2,  7,  0,  0), # -14400  3600 EDT
        datetime(2028, 10, 29,  6,  0,  0), # -18000     0 EST
        datetime(2029,  4,  1,  7,  0,  0), # -14400  3600 EDT
        datetime(2029, 10, 28,  6,  0,  0), # -18000     0 EST
        datetime(2030,  4,  7,  7,  0,  0), # -14400  3600 EDT
        datetime(2030, 10, 27,  6,  0,  0), # -18000     0 EST
        datetime(2031,  4,  6,  7,  0,  0), # -14400  3600 EDT
        datetime(2031, 10, 26,  6,  0,  0), # -18000     0 EST
        datetime(2032,  4,  4,  7,  0,  0), # -14400  3600 EDT
        datetime(2032, 10, 31,  6,  0,  0), # -18000     0 EST
        datetime(2033,  4,  3,  7,  0,  0), # -14400  3600 EDT
        datetime(2033, 10, 30,  6,  0,  0), # -18000     0 EST
        datetime(2034,  4,  2,  7,  0,  0), # -14400  3600 EDT
        datetime(2034, 10, 29,  6,  0,  0), # -18000     0 EST
        datetime(2035,  4,  1,  7,  0,  0), # -14400  3600 EDT
        datetime(2035, 10, 28,  6,  0,  0), # -18000     0 EST
        datetime(2036,  4,  6,  7,  0,  0), # -14400  3600 EDT
        datetime(2036, 10, 26,  6,  0,  0), # -18000     0 EST
        datetime(2037,  4,  5,  7,  0,  0), # -14400  3600 EDT
        datetime(2037, 10, 25,  6,  0,  0), # -18000     0 EST
        ]

    _transition_info = [
        ttinfo(-21600,      0,  'CST'),
        ttinfo(-18000,   3600,  'CDT'),
        ttinfo(-21600,      0,  'CST'),
        ttinfo(-18000,   3600,  'CDT'),
        ttinfo(-21600,      0,  'CST'),
        ttinfo(-18000,   3600,  'CWT'),
        ttinfo(-18000,      0,  'CPT'),
        ttinfo(-21600,      0,  'CST'),
        ttinfo(-18000,   3600,  'CDT'),
        ttinfo(-21600,      0,  'CST'),
        ttinfo(-18000,   3600,  'CDT'),
        ttinfo(-21600,      0,  'CST'),
        ttinfo(-18000,   3600,  'CDT'),
        ttinfo(-21600,      0,  'CST'),
        ttinfo(-18000,   3600,  'CDT'),
        ttinfo(-21600,      0,  'CST'),
        ttinfo(-18000,   3600,  'CDT'),
        ttinfo(-21600,      0,  'CST'),
        ttinfo(-18000,   3600,  'CDT'),
        ttinfo(-21600,      0,  'CST'),
        ttinfo(-18000,   3600,  'CDT'),
        ttinfo(-21600,      0,  'CST'),
        ttinfo(-18000,   3600,  'CDT'),
        ttinfo(-21600,      0,  'CST'),
        ttinfo(-18000,   3600,  'CDT'),
        ttinfo(-21600,      0,  'CST'),
        ttinfo(-18000,   3600,  'CDT'),
        ttinfo(-21600,      0,  'CST'),
        ttinfo(-18000,   3600,  'CDT'),
        ttinfo(-21600,      0,  'CST'),
        ttinfo(-18000,   3600,  'CDT'),
        ttinfo(-21600,      0,  'CST'),
        ttinfo(-18000,   3600,  'CDT'),
        ttinfo(-21600,      0,  'CST'),
        ttinfo(-18000,   3600,  'CDT'),
        ttinfo(-21600,      0,  'CST'),
        ttinfo(-18000,   3600,  'CDT'),
        ttinfo(-21600,      0,  'CST'),
        ttinfo(-18000,   3600,  'CDT'),
        ttinfo(-21600,      0,  'CST'),
        ttinfo(-18000,   3600,  'CDT'),
        ttinfo(-21600,      0,  'CST'),
        ttinfo(-18000,   3600,  'CDT'),
        ttinfo(-21600,      0,  'CST'),
        ttinfo(-18000,   3600,  'CDT'),
        ttinfo(-21600,      0,  'CST'),
        ttinfo(-18000,   3600,  'CDT'),
        ttinfo(-21600,      0,  'CST'),
        ttinfo(-18000,   3600,  'CDT'),
        ttinfo(-21600,      0,  'CST'),
        ttinfo(-18000,   3600,  'CDT'),
        ttinfo(-21600,      0,  'CST'),
        ttinfo(-18000,   3600,  'CDT'),
        ttinfo(-21600,      0,  'CST'),
        ttinfo(-18000,   3600,  'CDT'),
        ttinfo(-21600,      0,  'CST'),
        ttinfo(-18000,   3600,  'CDT'),
        ttinfo(-21600,      0,  'CST'),
        ttinfo(-18000,   3600,  'CDT'),
        ttinfo(-21600,      0,  'CST'),
        ttinfo(-18000,   3600,  'CDT'),
        ttinfo(-21600,      0,  'CST'),
        ttinfo(-18000,   3600,  'CDT'),
        ttinfo(-21600,      0,  'CST'),
        ttinfo(-18000,   3600,  'CDT'),
        ttinfo(-21600,      0,  'CST'),
        ttinfo(-18000,   3600,  'CDT'),
        ttinfo(-21600,      0,  'CST'),
        ttinfo(-18000,   3600,  'CDT'),
        ttinfo(-21600,      0,  'CST'),
        ttinfo(-18000,   3600,  'CDT'),
        ttinfo(-21600,      0,  'CST'),
        ttinfo(-18000,   3600,  'CDT'),
        ttinfo(-18000,      0,  'EST'),
        ttinfo(-14400,   3600,  'EDT'),
        ttinfo(-18000,      0,  'EST'),
        ttinfo(-14400,   3600,  'EDT'),
        ttinfo(-18000,      0,  'EST'),
        ttinfo(-14400,   3600,  'EDT'),
        ttinfo(-18000,      0,  'EST'),
        ttinfo(-14400,   3600,  'EDT'),
        ttinfo(-18000,      0,  'EST'),
        ttinfo(-14400,   3600,  'EDT'),
        ttinfo(-18000,      0,  'EST'),
        ttinfo(-14400,   3600,  'EDT'),
        ttinfo(-18000,      0,  'EST'),
        ttinfo(-14400,   3600,  'EDT'),
        ttinfo(-18000,      0,  'EST'),
        ttinfo(-14400,   3600,  'EDT'),
        ttinfo(-18000,      0,  'EST'),
        ttinfo(-14400,   3600,  'EDT'),
        ttinfo(-18000,      0,  'EST'),
        ttinfo(-14400,   3600,  'EDT'),
        ttinfo(-18000,      0,  'EST'),
        ttinfo(-14400,   3600,  'EDT'),
        ttinfo(-18000,      0,  'EST'),
        ttinfo(-14400,   3600,  'EDT'),
        ttinfo(-18000,      0,  'EST'),
        ttinfo(-14400,   3600,  'EDT'),
        ttinfo(-18000,      0,  'EST'),
        ttinfo(-14400,   3600,  'EDT'),
        ttinfo(-18000,      0,  'EST'),
        ttinfo(-14400,   3600,  'EDT'),
        ttinfo(-18000,      0,  'EST'),
        ttinfo(-14400,   3600,  'EDT'),
        ttinfo(-18000,      0,  'EST'),
        ttinfo(-14400,   3600,  'EDT'),
        ttinfo(-18000,      0,  'EST'),
        ttinfo(-14400,   3600,  'EDT'),
        ttinfo(-18000,      0,  'EST'),
        ttinfo(-14400,   3600,  'EDT'),
        ttinfo(-18000,      0,  'EST'),
        ttinfo(-14400,   3600,  'EDT'),
        ttinfo(-18000,      0,  'EST'),
        ttinfo(-14400,   3600,  'EDT'),
        ttinfo(-18000,      0,  'EST'),
        ttinfo(-14400,   3600,  'EDT'),
        ttinfo(-18000,      0,  'EST'),
        ttinfo(-14400,   3600,  'EDT'),
        ttinfo(-18000,      0,  'EST'),
        ttinfo(-14400,   3600,  'EDT'),
        ttinfo(-18000,      0,  'EST'),
        ttinfo(-14400,   3600,  'EDT'),
        ttinfo(-18000,      0,  'EST'),
        ttinfo(-14400,   3600,  'EDT'),
        ttinfo(-18000,      0,  'EST'),
        ttinfo(-14400,   3600,  'EDT'),
        ttinfo(-18000,      0,  'EST'),
        ttinfo(-14400,   3600,  'EDT'),
        ttinfo(-18000,      0,  'EST'),
        ttinfo(-14400,   3600,  'EDT'),
        ttinfo(-18000,      0,  'EST'),
        ttinfo(-14400,   3600,  'EDT'),
        ttinfo(-18000,      0,  'EST'),
        ttinfo(-14400,   3600,  'EDT'),
        ttinfo(-18000,      0,  'EST'),
        ttinfo(-14400,   3600,  'EDT'),
        ttinfo(-18000,      0,  'EST'),
        ttinfo(-14400,   3600,  'EDT'),
        ttinfo(-18000,      0,  'EST'),
        ttinfo(-14400,   3600,  'EDT'),
        ttinfo(-18000,      0,  'EST'),
        ttinfo(-14400,   3600,  'EDT'),
        ttinfo(-18000,      0,  'EST'),
        ttinfo(-14400,   3600,  'EDT'),
        ttinfo(-18000,      0,  'EST'),
        ttinfo(-14400,   3600,  'EDT'),
        ttinfo(-18000,      0,  'EST'),
        ]

Monticello = Monticello() # Singleton

