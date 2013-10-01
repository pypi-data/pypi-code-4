'''
tzinfo timezone information for Navajo.

Generated from the Olson timezone database:
    ftp://elsie.nci.nih.gov/pub/tz*.tar.gz
'''

from pytz.tzinfo import DstTzInfo
from pytz.tzinfo import memorized_datetime as datetime
from pytz.tzinfo import memorized_ttinfo as ttinfo

class Navajo(DstTzInfo):
    '''Navajo timezone definition. See datetime.tzinfo for details'''

    _zone = 'Navajo'

    _utc_transition_times = [
        datetime(   1,  1,  1,  0,  0,  0), # -25200     0 MST
        datetime(1918,  3, 31,  9,  0,  0), # -21600  3600 MDT
        datetime(1918, 10, 27,  8,  0,  0), # -25200     0 MST
        datetime(1919,  3, 30,  9,  0,  0), # -21600  3600 MDT
        datetime(1919, 10, 26,  8,  0,  0), # -25200     0 MST
        datetime(1920,  3, 28,  9,  0,  0), # -21600  3600 MDT
        datetime(1920, 10, 31,  8,  0,  0), # -25200     0 MST
        datetime(1921,  3, 27,  9,  0,  0), # -21600  3600 MDT
        datetime(1921,  5, 22,  8,  0,  0), # -25200     0 MST
        datetime(1942,  2,  9,  9,  0,  0), # -21600  3600 MWT
        datetime(1945,  8, 14, 23,  0,  0), # -21600     0 MPT
        datetime(1945,  9, 30,  8,  0,  0), # -25200     0 MST
        datetime(1965,  4, 25,  9,  0,  0), # -21600  3600 MDT
        datetime(1965, 10, 31,  8,  0,  0), # -25200     0 MST
        datetime(1966,  4, 24,  9,  0,  0), # -21600  3600 MDT
        datetime(1966, 10, 30,  8,  0,  0), # -25200     0 MST
        datetime(1967,  4, 30,  9,  0,  0), # -21600  3600 MDT
        datetime(1967, 10, 29,  8,  0,  0), # -25200     0 MST
        datetime(1968,  4, 28,  9,  0,  0), # -21600  3600 MDT
        datetime(1968, 10, 27,  8,  0,  0), # -25200     0 MST
        datetime(1969,  4, 27,  9,  0,  0), # -21600  3600 MDT
        datetime(1969, 10, 26,  8,  0,  0), # -25200     0 MST
        datetime(1970,  4, 26,  9,  0,  0), # -21600  3600 MDT
        datetime(1970, 10, 25,  8,  0,  0), # -25200     0 MST
        datetime(1971,  4, 25,  9,  0,  0), # -21600  3600 MDT
        datetime(1971, 10, 31,  8,  0,  0), # -25200     0 MST
        datetime(1972,  4, 30,  9,  0,  0), # -21600  3600 MDT
        datetime(1972, 10, 29,  8,  0,  0), # -25200     0 MST
        datetime(1973,  4, 29,  9,  0,  0), # -21600  3600 MDT
        datetime(1973, 10, 28,  8,  0,  0), # -25200     0 MST
        datetime(1974,  1,  6,  9,  0,  0), # -21600  3600 MDT
        datetime(1974, 10, 27,  8,  0,  0), # -25200     0 MST
        datetime(1975,  2, 23,  9,  0,  0), # -21600  3600 MDT
        datetime(1975, 10, 26,  8,  0,  0), # -25200     0 MST
        datetime(1976,  4, 25,  9,  0,  0), # -21600  3600 MDT
        datetime(1976, 10, 31,  8,  0,  0), # -25200     0 MST
        datetime(1977,  4, 24,  9,  0,  0), # -21600  3600 MDT
        datetime(1977, 10, 30,  8,  0,  0), # -25200     0 MST
        datetime(1978,  4, 30,  9,  0,  0), # -21600  3600 MDT
        datetime(1978, 10, 29,  8,  0,  0), # -25200     0 MST
        datetime(1979,  4, 29,  9,  0,  0), # -21600  3600 MDT
        datetime(1979, 10, 28,  8,  0,  0), # -25200     0 MST
        datetime(1980,  4, 27,  9,  0,  0), # -21600  3600 MDT
        datetime(1980, 10, 26,  8,  0,  0), # -25200     0 MST
        datetime(1981,  4, 26,  9,  0,  0), # -21600  3600 MDT
        datetime(1981, 10, 25,  8,  0,  0), # -25200     0 MST
        datetime(1982,  4, 25,  9,  0,  0), # -21600  3600 MDT
        datetime(1982, 10, 31,  8,  0,  0), # -25200     0 MST
        datetime(1983,  4, 24,  9,  0,  0), # -21600  3600 MDT
        datetime(1983, 10, 30,  8,  0,  0), # -25200     0 MST
        datetime(1984,  4, 29,  9,  0,  0), # -21600  3600 MDT
        datetime(1984, 10, 28,  8,  0,  0), # -25200     0 MST
        datetime(1985,  4, 28,  9,  0,  0), # -21600  3600 MDT
        datetime(1985, 10, 27,  8,  0,  0), # -25200     0 MST
        datetime(1986,  4, 27,  9,  0,  0), # -21600  3600 MDT
        datetime(1986, 10, 26,  8,  0,  0), # -25200     0 MST
        datetime(1987,  4,  5,  9,  0,  0), # -21600  3600 MDT
        datetime(1987, 10, 25,  8,  0,  0), # -25200     0 MST
        datetime(1988,  4,  3,  9,  0,  0), # -21600  3600 MDT
        datetime(1988, 10, 30,  8,  0,  0), # -25200     0 MST
        datetime(1989,  4,  2,  9,  0,  0), # -21600  3600 MDT
        datetime(1989, 10, 29,  8,  0,  0), # -25200     0 MST
        datetime(1990,  4,  1,  9,  0,  0), # -21600  3600 MDT
        datetime(1990, 10, 28,  8,  0,  0), # -25200     0 MST
        datetime(1991,  4,  7,  9,  0,  0), # -21600  3600 MDT
        datetime(1991, 10, 27,  8,  0,  0), # -25200     0 MST
        datetime(1992,  4,  5,  9,  0,  0), # -21600  3600 MDT
        datetime(1992, 10, 25,  8,  0,  0), # -25200     0 MST
        datetime(1993,  4,  4,  9,  0,  0), # -21600  3600 MDT
        datetime(1993, 10, 31,  8,  0,  0), # -25200     0 MST
        datetime(1994,  4,  3,  9,  0,  0), # -21600  3600 MDT
        datetime(1994, 10, 30,  8,  0,  0), # -25200     0 MST
        datetime(1995,  4,  2,  9,  0,  0), # -21600  3600 MDT
        datetime(1995, 10, 29,  8,  0,  0), # -25200     0 MST
        datetime(1996,  4,  7,  9,  0,  0), # -21600  3600 MDT
        datetime(1996, 10, 27,  8,  0,  0), # -25200     0 MST
        datetime(1997,  4,  6,  9,  0,  0), # -21600  3600 MDT
        datetime(1997, 10, 26,  8,  0,  0), # -25200     0 MST
        datetime(1998,  4,  5,  9,  0,  0), # -21600  3600 MDT
        datetime(1998, 10, 25,  8,  0,  0), # -25200     0 MST
        datetime(1999,  4,  4,  9,  0,  0), # -21600  3600 MDT
        datetime(1999, 10, 31,  8,  0,  0), # -25200     0 MST
        datetime(2000,  4,  2,  9,  0,  0), # -21600  3600 MDT
        datetime(2000, 10, 29,  8,  0,  0), # -25200     0 MST
        datetime(2001,  4,  1,  9,  0,  0), # -21600  3600 MDT
        datetime(2001, 10, 28,  8,  0,  0), # -25200     0 MST
        datetime(2002,  4,  7,  9,  0,  0), # -21600  3600 MDT
        datetime(2002, 10, 27,  8,  0,  0), # -25200     0 MST
        datetime(2003,  4,  6,  9,  0,  0), # -21600  3600 MDT
        datetime(2003, 10, 26,  8,  0,  0), # -25200     0 MST
        datetime(2004,  4,  4,  9,  0,  0), # -21600  3600 MDT
        datetime(2004, 10, 31,  8,  0,  0), # -25200     0 MST
        datetime(2005,  4,  3,  9,  0,  0), # -21600  3600 MDT
        datetime(2005, 10, 30,  8,  0,  0), # -25200     0 MST
        datetime(2006,  4,  2,  9,  0,  0), # -21600  3600 MDT
        datetime(2006, 10, 29,  8,  0,  0), # -25200     0 MST
        datetime(2007,  4,  1,  9,  0,  0), # -21600  3600 MDT
        datetime(2007, 10, 28,  8,  0,  0), # -25200     0 MST
        datetime(2008,  4,  6,  9,  0,  0), # -21600  3600 MDT
        datetime(2008, 10, 26,  8,  0,  0), # -25200     0 MST
        datetime(2009,  4,  5,  9,  0,  0), # -21600  3600 MDT
        datetime(2009, 10, 25,  8,  0,  0), # -25200     0 MST
        datetime(2010,  4,  4,  9,  0,  0), # -21600  3600 MDT
        datetime(2010, 10, 31,  8,  0,  0), # -25200     0 MST
        datetime(2011,  4,  3,  9,  0,  0), # -21600  3600 MDT
        datetime(2011, 10, 30,  8,  0,  0), # -25200     0 MST
        datetime(2012,  4,  1,  9,  0,  0), # -21600  3600 MDT
        datetime(2012, 10, 28,  8,  0,  0), # -25200     0 MST
        datetime(2013,  4,  7,  9,  0,  0), # -21600  3600 MDT
        datetime(2013, 10, 27,  8,  0,  0), # -25200     0 MST
        datetime(2014,  4,  6,  9,  0,  0), # -21600  3600 MDT
        datetime(2014, 10, 26,  8,  0,  0), # -25200     0 MST
        datetime(2015,  4,  5,  9,  0,  0), # -21600  3600 MDT
        datetime(2015, 10, 25,  8,  0,  0), # -25200     0 MST
        datetime(2016,  4,  3,  9,  0,  0), # -21600  3600 MDT
        datetime(2016, 10, 30,  8,  0,  0), # -25200     0 MST
        datetime(2017,  4,  2,  9,  0,  0), # -21600  3600 MDT
        datetime(2017, 10, 29,  8,  0,  0), # -25200     0 MST
        datetime(2018,  4,  1,  9,  0,  0), # -21600  3600 MDT
        datetime(2018, 10, 28,  8,  0,  0), # -25200     0 MST
        datetime(2019,  4,  7,  9,  0,  0), # -21600  3600 MDT
        datetime(2019, 10, 27,  8,  0,  0), # -25200     0 MST
        datetime(2020,  4,  5,  9,  0,  0), # -21600  3600 MDT
        datetime(2020, 10, 25,  8,  0,  0), # -25200     0 MST
        datetime(2021,  4,  4,  9,  0,  0), # -21600  3600 MDT
        datetime(2021, 10, 31,  8,  0,  0), # -25200     0 MST
        datetime(2022,  4,  3,  9,  0,  0), # -21600  3600 MDT
        datetime(2022, 10, 30,  8,  0,  0), # -25200     0 MST
        datetime(2023,  4,  2,  9,  0,  0), # -21600  3600 MDT
        datetime(2023, 10, 29,  8,  0,  0), # -25200     0 MST
        datetime(2024,  4,  7,  9,  0,  0), # -21600  3600 MDT
        datetime(2024, 10, 27,  8,  0,  0), # -25200     0 MST
        datetime(2025,  4,  6,  9,  0,  0), # -21600  3600 MDT
        datetime(2025, 10, 26,  8,  0,  0), # -25200     0 MST
        datetime(2026,  4,  5,  9,  0,  0), # -21600  3600 MDT
        datetime(2026, 10, 25,  8,  0,  0), # -25200     0 MST
        datetime(2027,  4,  4,  9,  0,  0), # -21600  3600 MDT
        datetime(2027, 10, 31,  8,  0,  0), # -25200     0 MST
        datetime(2028,  4,  2,  9,  0,  0), # -21600  3600 MDT
        datetime(2028, 10, 29,  8,  0,  0), # -25200     0 MST
        datetime(2029,  4,  1,  9,  0,  0), # -21600  3600 MDT
        datetime(2029, 10, 28,  8,  0,  0), # -25200     0 MST
        datetime(2030,  4,  7,  9,  0,  0), # -21600  3600 MDT
        datetime(2030, 10, 27,  8,  0,  0), # -25200     0 MST
        datetime(2031,  4,  6,  9,  0,  0), # -21600  3600 MDT
        datetime(2031, 10, 26,  8,  0,  0), # -25200     0 MST
        datetime(2032,  4,  4,  9,  0,  0), # -21600  3600 MDT
        datetime(2032, 10, 31,  8,  0,  0), # -25200     0 MST
        datetime(2033,  4,  3,  9,  0,  0), # -21600  3600 MDT
        datetime(2033, 10, 30,  8,  0,  0), # -25200     0 MST
        datetime(2034,  4,  2,  9,  0,  0), # -21600  3600 MDT
        datetime(2034, 10, 29,  8,  0,  0), # -25200     0 MST
        datetime(2035,  4,  1,  9,  0,  0), # -21600  3600 MDT
        datetime(2035, 10, 28,  8,  0,  0), # -25200     0 MST
        datetime(2036,  4,  6,  9,  0,  0), # -21600  3600 MDT
        datetime(2036, 10, 26,  8,  0,  0), # -25200     0 MST
        datetime(2037,  4,  5,  9,  0,  0), # -21600  3600 MDT
        datetime(2037, 10, 25,  8,  0,  0), # -25200     0 MST
        ]

    _transition_info = [
        ttinfo(-25200,      0,  'MST'),
        ttinfo(-21600,   3600,  'MDT'),
        ttinfo(-25200,      0,  'MST'),
        ttinfo(-21600,   3600,  'MDT'),
        ttinfo(-25200,      0,  'MST'),
        ttinfo(-21600,   3600,  'MDT'),
        ttinfo(-25200,      0,  'MST'),
        ttinfo(-21600,   3600,  'MDT'),
        ttinfo(-25200,      0,  'MST'),
        ttinfo(-21600,   3600,  'MWT'),
        ttinfo(-21600,      0,  'MPT'),
        ttinfo(-25200,      0,  'MST'),
        ttinfo(-21600,   3600,  'MDT'),
        ttinfo(-25200,      0,  'MST'),
        ttinfo(-21600,   3600,  'MDT'),
        ttinfo(-25200,      0,  'MST'),
        ttinfo(-21600,   3600,  'MDT'),
        ttinfo(-25200,      0,  'MST'),
        ttinfo(-21600,   3600,  'MDT'),
        ttinfo(-25200,      0,  'MST'),
        ttinfo(-21600,   3600,  'MDT'),
        ttinfo(-25200,      0,  'MST'),
        ttinfo(-21600,   3600,  'MDT'),
        ttinfo(-25200,      0,  'MST'),
        ttinfo(-21600,   3600,  'MDT'),
        ttinfo(-25200,      0,  'MST'),
        ttinfo(-21600,   3600,  'MDT'),
        ttinfo(-25200,      0,  'MST'),
        ttinfo(-21600,   3600,  'MDT'),
        ttinfo(-25200,      0,  'MST'),
        ttinfo(-21600,   3600,  'MDT'),
        ttinfo(-25200,      0,  'MST'),
        ttinfo(-21600,   3600,  'MDT'),
        ttinfo(-25200,      0,  'MST'),
        ttinfo(-21600,   3600,  'MDT'),
        ttinfo(-25200,      0,  'MST'),
        ttinfo(-21600,   3600,  'MDT'),
        ttinfo(-25200,      0,  'MST'),
        ttinfo(-21600,   3600,  'MDT'),
        ttinfo(-25200,      0,  'MST'),
        ttinfo(-21600,   3600,  'MDT'),
        ttinfo(-25200,      0,  'MST'),
        ttinfo(-21600,   3600,  'MDT'),
        ttinfo(-25200,      0,  'MST'),
        ttinfo(-21600,   3600,  'MDT'),
        ttinfo(-25200,      0,  'MST'),
        ttinfo(-21600,   3600,  'MDT'),
        ttinfo(-25200,      0,  'MST'),
        ttinfo(-21600,   3600,  'MDT'),
        ttinfo(-25200,      0,  'MST'),
        ttinfo(-21600,   3600,  'MDT'),
        ttinfo(-25200,      0,  'MST'),
        ttinfo(-21600,   3600,  'MDT'),
        ttinfo(-25200,      0,  'MST'),
        ttinfo(-21600,   3600,  'MDT'),
        ttinfo(-25200,      0,  'MST'),
        ttinfo(-21600,   3600,  'MDT'),
        ttinfo(-25200,      0,  'MST'),
        ttinfo(-21600,   3600,  'MDT'),
        ttinfo(-25200,      0,  'MST'),
        ttinfo(-21600,   3600,  'MDT'),
        ttinfo(-25200,      0,  'MST'),
        ttinfo(-21600,   3600,  'MDT'),
        ttinfo(-25200,      0,  'MST'),
        ttinfo(-21600,   3600,  'MDT'),
        ttinfo(-25200,      0,  'MST'),
        ttinfo(-21600,   3600,  'MDT'),
        ttinfo(-25200,      0,  'MST'),
        ttinfo(-21600,   3600,  'MDT'),
        ttinfo(-25200,      0,  'MST'),
        ttinfo(-21600,   3600,  'MDT'),
        ttinfo(-25200,      0,  'MST'),
        ttinfo(-21600,   3600,  'MDT'),
        ttinfo(-25200,      0,  'MST'),
        ttinfo(-21600,   3600,  'MDT'),
        ttinfo(-25200,      0,  'MST'),
        ttinfo(-21600,   3600,  'MDT'),
        ttinfo(-25200,      0,  'MST'),
        ttinfo(-21600,   3600,  'MDT'),
        ttinfo(-25200,      0,  'MST'),
        ttinfo(-21600,   3600,  'MDT'),
        ttinfo(-25200,      0,  'MST'),
        ttinfo(-21600,   3600,  'MDT'),
        ttinfo(-25200,      0,  'MST'),
        ttinfo(-21600,   3600,  'MDT'),
        ttinfo(-25200,      0,  'MST'),
        ttinfo(-21600,   3600,  'MDT'),
        ttinfo(-25200,      0,  'MST'),
        ttinfo(-21600,   3600,  'MDT'),
        ttinfo(-25200,      0,  'MST'),
        ttinfo(-21600,   3600,  'MDT'),
        ttinfo(-25200,      0,  'MST'),
        ttinfo(-21600,   3600,  'MDT'),
        ttinfo(-25200,      0,  'MST'),
        ttinfo(-21600,   3600,  'MDT'),
        ttinfo(-25200,      0,  'MST'),
        ttinfo(-21600,   3600,  'MDT'),
        ttinfo(-25200,      0,  'MST'),
        ttinfo(-21600,   3600,  'MDT'),
        ttinfo(-25200,      0,  'MST'),
        ttinfo(-21600,   3600,  'MDT'),
        ttinfo(-25200,      0,  'MST'),
        ttinfo(-21600,   3600,  'MDT'),
        ttinfo(-25200,      0,  'MST'),
        ttinfo(-21600,   3600,  'MDT'),
        ttinfo(-25200,      0,  'MST'),
        ttinfo(-21600,   3600,  'MDT'),
        ttinfo(-25200,      0,  'MST'),
        ttinfo(-21600,   3600,  'MDT'),
        ttinfo(-25200,      0,  'MST'),
        ttinfo(-21600,   3600,  'MDT'),
        ttinfo(-25200,      0,  'MST'),
        ttinfo(-21600,   3600,  'MDT'),
        ttinfo(-25200,      0,  'MST'),
        ttinfo(-21600,   3600,  'MDT'),
        ttinfo(-25200,      0,  'MST'),
        ttinfo(-21600,   3600,  'MDT'),
        ttinfo(-25200,      0,  'MST'),
        ttinfo(-21600,   3600,  'MDT'),
        ttinfo(-25200,      0,  'MST'),
        ttinfo(-21600,   3600,  'MDT'),
        ttinfo(-25200,      0,  'MST'),
        ttinfo(-21600,   3600,  'MDT'),
        ttinfo(-25200,      0,  'MST'),
        ttinfo(-21600,   3600,  'MDT'),
        ttinfo(-25200,      0,  'MST'),
        ttinfo(-21600,   3600,  'MDT'),
        ttinfo(-25200,      0,  'MST'),
        ttinfo(-21600,   3600,  'MDT'),
        ttinfo(-25200,      0,  'MST'),
        ttinfo(-21600,   3600,  'MDT'),
        ttinfo(-25200,      0,  'MST'),
        ttinfo(-21600,   3600,  'MDT'),
        ttinfo(-25200,      0,  'MST'),
        ttinfo(-21600,   3600,  'MDT'),
        ttinfo(-25200,      0,  'MST'),
        ttinfo(-21600,   3600,  'MDT'),
        ttinfo(-25200,      0,  'MST'),
        ttinfo(-21600,   3600,  'MDT'),
        ttinfo(-25200,      0,  'MST'),
        ttinfo(-21600,   3600,  'MDT'),
        ttinfo(-25200,      0,  'MST'),
        ttinfo(-21600,   3600,  'MDT'),
        ttinfo(-25200,      0,  'MST'),
        ttinfo(-21600,   3600,  'MDT'),
        ttinfo(-25200,      0,  'MST'),
        ttinfo(-21600,   3600,  'MDT'),
        ttinfo(-25200,      0,  'MST'),
        ttinfo(-21600,   3600,  'MDT'),
        ttinfo(-25200,      0,  'MST'),
        ttinfo(-21600,   3600,  'MDT'),
        ttinfo(-25200,      0,  'MST'),
        ttinfo(-21600,   3600,  'MDT'),
        ttinfo(-25200,      0,  'MST'),
        ttinfo(-21600,   3600,  'MDT'),
        ttinfo(-25200,      0,  'MST'),
        ttinfo(-21600,   3600,  'MDT'),
        ttinfo(-25200,      0,  'MST'),
        ]

Navajo = Navajo() # Singleton

