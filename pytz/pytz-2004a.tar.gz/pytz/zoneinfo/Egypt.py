'''
tzinfo timezone information for Egypt.

Generated from the Olson timezone database:
    ftp://elsie.nci.nih.gov/pub/tz*.tar.gz
'''

from pytz.tzinfo import DstTzInfo
from pytz.tzinfo import memorized_datetime as datetime
from pytz.tzinfo import memorized_ttinfo as ttinfo

class Egypt(DstTzInfo):
    '''Egypt timezone definition. See datetime.tzinfo for details'''

    _zone = 'Egypt'

    _utc_transition_times = [
        datetime(   1,  1,  1,  0,  0,  0), #   7200     0 EET
        datetime(1940,  7, 14, 22,  0,  0), #  10800  3600 EEST
        datetime(1940,  9, 30, 21,  0,  0), #   7200     0 EET
        datetime(1941,  4, 14, 22,  0,  0), #  10800  3600 EEST
        datetime(1941,  9, 15, 21,  0,  0), #   7200     0 EET
        datetime(1942,  3, 31, 22,  0,  0), #  10800  3600 EEST
        datetime(1942, 10, 26, 21,  0,  0), #   7200     0 EET
        datetime(1943,  3, 31, 22,  0,  0), #  10800  3600 EEST
        datetime(1943, 10, 31, 21,  0,  0), #   7200     0 EET
        datetime(1944,  3, 31, 22,  0,  0), #  10800  3600 EEST
        datetime(1944, 10, 31, 21,  0,  0), #   7200     0 EET
        datetime(1945,  4, 15, 22,  0,  0), #  10800  3600 EEST
        datetime(1945, 10, 31, 21,  0,  0), #   7200     0 EET
        datetime(1957,  5,  9, 22,  0,  0), #  10800  3600 EEST
        datetime(1957,  9, 30, 21,  0,  0), #   7200     0 EET
        datetime(1958,  4, 30, 22,  0,  0), #  10800  3600 EEST
        datetime(1958,  9, 30, 21,  0,  0), #   7200     0 EET
        datetime(1959,  4, 30, 23,  0,  0), #  10800  3600 EEST
        datetime(1959,  9, 30,  0,  0,  0), #   7200     0 EET
        datetime(1960,  4, 30, 23,  0,  0), #  10800  3600 EEST
        datetime(1960,  9, 30,  0,  0,  0), #   7200     0 EET
        datetime(1961,  4, 30, 23,  0,  0), #  10800  3600 EEST
        datetime(1961,  9, 30,  0,  0,  0), #   7200     0 EET
        datetime(1962,  4, 30, 23,  0,  0), #  10800  3600 EEST
        datetime(1962,  9, 30,  0,  0,  0), #   7200     0 EET
        datetime(1963,  4, 30, 23,  0,  0), #  10800  3600 EEST
        datetime(1963,  9, 30,  0,  0,  0), #   7200     0 EET
        datetime(1964,  4, 30, 23,  0,  0), #  10800  3600 EEST
        datetime(1964,  9, 30,  0,  0,  0), #   7200     0 EET
        datetime(1965,  4, 30, 23,  0,  0), #  10800  3600 EEST
        datetime(1965,  9, 30,  0,  0,  0), #   7200     0 EET
        datetime(1966,  4, 30, 23,  0,  0), #  10800  3600 EEST
        datetime(1966, 10,  1,  0,  0,  0), #   7200     0 EET
        datetime(1967,  4, 30, 23,  0,  0), #  10800  3600 EEST
        datetime(1967, 10,  1,  0,  0,  0), #   7200     0 EET
        datetime(1968,  4, 30, 23,  0,  0), #  10800  3600 EEST
        datetime(1968, 10,  1,  0,  0,  0), #   7200     0 EET
        datetime(1969,  4, 30, 23,  0,  0), #  10800  3600 EEST
        datetime(1969, 10,  1,  0,  0,  0), #   7200     0 EET
        datetime(1970,  4, 30, 23,  0,  0), #  10800  3600 EEST
        datetime(1970, 10,  1,  0,  0,  0), #   7200     0 EET
        datetime(1971,  4, 30, 23,  0,  0), #  10800  3600 EEST
        datetime(1971, 10,  1,  0,  0,  0), #   7200     0 EET
        datetime(1972,  4, 30, 23,  0,  0), #  10800  3600 EEST
        datetime(1972, 10,  1,  0,  0,  0), #   7200     0 EET
        datetime(1973,  4, 30, 23,  0,  0), #  10800  3600 EEST
        datetime(1973, 10,  1,  0,  0,  0), #   7200     0 EET
        datetime(1974,  4, 30, 23,  0,  0), #  10800  3600 EEST
        datetime(1974, 10,  1,  0,  0,  0), #   7200     0 EET
        datetime(1975,  4, 30, 23,  0,  0), #  10800  3600 EEST
        datetime(1975, 10,  1,  0,  0,  0), #   7200     0 EET
        datetime(1976,  4, 30, 23,  0,  0), #  10800  3600 EEST
        datetime(1976, 10,  1,  0,  0,  0), #   7200     0 EET
        datetime(1977,  4, 30, 23,  0,  0), #  10800  3600 EEST
        datetime(1977, 10,  1,  0,  0,  0), #   7200     0 EET
        datetime(1978,  4, 30, 23,  0,  0), #  10800  3600 EEST
        datetime(1978, 10,  1,  0,  0,  0), #   7200     0 EET
        datetime(1979,  4, 30, 23,  0,  0), #  10800  3600 EEST
        datetime(1979, 10,  1,  0,  0,  0), #   7200     0 EET
        datetime(1980,  4, 30, 23,  0,  0), #  10800  3600 EEST
        datetime(1980, 10,  1,  0,  0,  0), #   7200     0 EET
        datetime(1981,  4, 30, 23,  0,  0), #  10800  3600 EEST
        datetime(1981, 10,  1,  0,  0,  0), #   7200     0 EET
        datetime(1982,  7, 24, 23,  0,  0), #  10800  3600 EEST
        datetime(1982, 10,  1,  0,  0,  0), #   7200     0 EET
        datetime(1983,  7, 11, 23,  0,  0), #  10800  3600 EEST
        datetime(1983, 10,  1,  0,  0,  0), #   7200     0 EET
        datetime(1984,  4, 30, 23,  0,  0), #  10800  3600 EEST
        datetime(1984, 10,  1,  0,  0,  0), #   7200     0 EET
        datetime(1985,  4, 30, 23,  0,  0), #  10800  3600 EEST
        datetime(1985, 10,  1,  0,  0,  0), #   7200     0 EET
        datetime(1986,  4, 30, 23,  0,  0), #  10800  3600 EEST
        datetime(1986, 10,  1,  0,  0,  0), #   7200     0 EET
        datetime(1987,  4, 30, 23,  0,  0), #  10800  3600 EEST
        datetime(1987, 10,  1,  0,  0,  0), #   7200     0 EET
        datetime(1988,  4, 30, 23,  0,  0), #  10800  3600 EEST
        datetime(1988, 10,  1,  0,  0,  0), #   7200     0 EET
        datetime(1989,  5,  5, 23,  0,  0), #  10800  3600 EEST
        datetime(1989, 10,  1,  0,  0,  0), #   7200     0 EET
        datetime(1990,  4, 30, 23,  0,  0), #  10800  3600 EEST
        datetime(1990, 10,  1,  0,  0,  0), #   7200     0 EET
        datetime(1991,  4, 30, 23,  0,  0), #  10800  3600 EEST
        datetime(1991, 10,  1,  0,  0,  0), #   7200     0 EET
        datetime(1992,  4, 30, 23,  0,  0), #  10800  3600 EEST
        datetime(1992, 10,  1,  0,  0,  0), #   7200     0 EET
        datetime(1993,  4, 30, 23,  0,  0), #  10800  3600 EEST
        datetime(1993, 10,  1,  0,  0,  0), #   7200     0 EET
        datetime(1994,  4, 30, 23,  0,  0), #  10800  3600 EEST
        datetime(1994, 10,  1,  0,  0,  0), #   7200     0 EET
        datetime(1995,  4, 27, 22,  0,  0), #  10800  3600 EEST
        datetime(1995,  9, 28, 21,  0,  0), #   7200     0 EET
        datetime(1996,  4, 25, 22,  0,  0), #  10800  3600 EEST
        datetime(1996,  9, 26, 21,  0,  0), #   7200     0 EET
        datetime(1997,  4, 24, 22,  0,  0), #  10800  3600 EEST
        datetime(1997,  9, 25, 21,  0,  0), #   7200     0 EET
        datetime(1998,  4, 23, 22,  0,  0), #  10800  3600 EEST
        datetime(1998,  9, 24, 21,  0,  0), #   7200     0 EET
        datetime(1999,  4, 29, 22,  0,  0), #  10800  3600 EEST
        datetime(1999,  9, 30, 21,  0,  0), #   7200     0 EET
        datetime(2000,  4, 27, 22,  0,  0), #  10800  3600 EEST
        datetime(2000,  9, 28, 21,  0,  0), #   7200     0 EET
        datetime(2001,  4, 26, 22,  0,  0), #  10800  3600 EEST
        datetime(2001,  9, 27, 21,  0,  0), #   7200     0 EET
        datetime(2002,  4, 25, 22,  0,  0), #  10800  3600 EEST
        datetime(2002,  9, 26, 21,  0,  0), #   7200     0 EET
        datetime(2003,  4, 24, 22,  0,  0), #  10800  3600 EEST
        datetime(2003,  9, 25, 21,  0,  0), #   7200     0 EET
        datetime(2004,  4, 29, 22,  0,  0), #  10800  3600 EEST
        datetime(2004,  9, 30, 21,  0,  0), #   7200     0 EET
        datetime(2005,  4, 28, 22,  0,  0), #  10800  3600 EEST
        datetime(2005,  9, 29, 21,  0,  0), #   7200     0 EET
        datetime(2006,  4, 27, 22,  0,  0), #  10800  3600 EEST
        datetime(2006,  9, 28, 21,  0,  0), #   7200     0 EET
        datetime(2007,  4, 26, 22,  0,  0), #  10800  3600 EEST
        datetime(2007,  9, 27, 21,  0,  0), #   7200     0 EET
        datetime(2008,  4, 24, 22,  0,  0), #  10800  3600 EEST
        datetime(2008,  9, 25, 21,  0,  0), #   7200     0 EET
        datetime(2009,  4, 23, 22,  0,  0), #  10800  3600 EEST
        datetime(2009,  9, 24, 21,  0,  0), #   7200     0 EET
        datetime(2010,  4, 29, 22,  0,  0), #  10800  3600 EEST
        datetime(2010,  9, 30, 21,  0,  0), #   7200     0 EET
        datetime(2011,  4, 28, 22,  0,  0), #  10800  3600 EEST
        datetime(2011,  9, 29, 21,  0,  0), #   7200     0 EET
        datetime(2012,  4, 26, 22,  0,  0), #  10800  3600 EEST
        datetime(2012,  9, 27, 21,  0,  0), #   7200     0 EET
        datetime(2013,  4, 25, 22,  0,  0), #  10800  3600 EEST
        datetime(2013,  9, 26, 21,  0,  0), #   7200     0 EET
        datetime(2014,  4, 24, 22,  0,  0), #  10800  3600 EEST
        datetime(2014,  9, 25, 21,  0,  0), #   7200     0 EET
        datetime(2015,  4, 23, 22,  0,  0), #  10800  3600 EEST
        datetime(2015,  9, 24, 21,  0,  0), #   7200     0 EET
        datetime(2016,  4, 28, 22,  0,  0), #  10800  3600 EEST
        datetime(2016,  9, 29, 21,  0,  0), #   7200     0 EET
        datetime(2017,  4, 27, 22,  0,  0), #  10800  3600 EEST
        datetime(2017,  9, 28, 21,  0,  0), #   7200     0 EET
        datetime(2018,  4, 26, 22,  0,  0), #  10800  3600 EEST
        datetime(2018,  9, 27, 21,  0,  0), #   7200     0 EET
        datetime(2019,  4, 25, 22,  0,  0), #  10800  3600 EEST
        datetime(2019,  9, 26, 21,  0,  0), #   7200     0 EET
        datetime(2020,  4, 23, 22,  0,  0), #  10800  3600 EEST
        datetime(2020,  9, 24, 21,  0,  0), #   7200     0 EET
        datetime(2021,  4, 29, 22,  0,  0), #  10800  3600 EEST
        datetime(2021,  9, 30, 21,  0,  0), #   7200     0 EET
        datetime(2022,  4, 28, 22,  0,  0), #  10800  3600 EEST
        datetime(2022,  9, 29, 21,  0,  0), #   7200     0 EET
        datetime(2023,  4, 27, 22,  0,  0), #  10800  3600 EEST
        datetime(2023,  9, 28, 21,  0,  0), #   7200     0 EET
        datetime(2024,  4, 25, 22,  0,  0), #  10800  3600 EEST
        datetime(2024,  9, 26, 21,  0,  0), #   7200     0 EET
        datetime(2025,  4, 24, 22,  0,  0), #  10800  3600 EEST
        datetime(2025,  9, 25, 21,  0,  0), #   7200     0 EET
        datetime(2026,  4, 23, 22,  0,  0), #  10800  3600 EEST
        datetime(2026,  9, 24, 21,  0,  0), #   7200     0 EET
        datetime(2027,  4, 29, 22,  0,  0), #  10800  3600 EEST
        datetime(2027,  9, 30, 21,  0,  0), #   7200     0 EET
        datetime(2028,  4, 27, 22,  0,  0), #  10800  3600 EEST
        datetime(2028,  9, 28, 21,  0,  0), #   7200     0 EET
        datetime(2029,  4, 26, 22,  0,  0), #  10800  3600 EEST
        datetime(2029,  9, 27, 21,  0,  0), #   7200     0 EET
        datetime(2030,  4, 25, 22,  0,  0), #  10800  3600 EEST
        datetime(2030,  9, 26, 21,  0,  0), #   7200     0 EET
        datetime(2031,  4, 24, 22,  0,  0), #  10800  3600 EEST
        datetime(2031,  9, 25, 21,  0,  0), #   7200     0 EET
        datetime(2032,  4, 29, 22,  0,  0), #  10800  3600 EEST
        datetime(2032,  9, 30, 21,  0,  0), #   7200     0 EET
        datetime(2033,  4, 28, 22,  0,  0), #  10800  3600 EEST
        datetime(2033,  9, 29, 21,  0,  0), #   7200     0 EET
        datetime(2034,  4, 27, 22,  0,  0), #  10800  3600 EEST
        datetime(2034,  9, 28, 21,  0,  0), #   7200     0 EET
        datetime(2035,  4, 26, 22,  0,  0), #  10800  3600 EEST
        datetime(2035,  9, 27, 21,  0,  0), #   7200     0 EET
        datetime(2036,  4, 24, 22,  0,  0), #  10800  3600 EEST
        datetime(2036,  9, 25, 21,  0,  0), #   7200     0 EET
        datetime(2037,  4, 23, 22,  0,  0), #  10800  3600 EEST
        datetime(2037,  9, 24, 21,  0,  0), #   7200     0 EET
        ]

    _transition_info = [
        ttinfo(  7200,      0,  'EET'),
        ttinfo( 10800,   3600, 'EEST'),
        ttinfo(  7200,      0,  'EET'),
        ttinfo( 10800,   3600, 'EEST'),
        ttinfo(  7200,      0,  'EET'),
        ttinfo( 10800,   3600, 'EEST'),
        ttinfo(  7200,      0,  'EET'),
        ttinfo( 10800,   3600, 'EEST'),
        ttinfo(  7200,      0,  'EET'),
        ttinfo( 10800,   3600, 'EEST'),
        ttinfo(  7200,      0,  'EET'),
        ttinfo( 10800,   3600, 'EEST'),
        ttinfo(  7200,      0,  'EET'),
        ttinfo( 10800,   3600, 'EEST'),
        ttinfo(  7200,      0,  'EET'),
        ttinfo( 10800,   3600, 'EEST'),
        ttinfo(  7200,      0,  'EET'),
        ttinfo( 10800,   3600, 'EEST'),
        ttinfo(  7200,      0,  'EET'),
        ttinfo( 10800,   3600, 'EEST'),
        ttinfo(  7200,      0,  'EET'),
        ttinfo( 10800,   3600, 'EEST'),
        ttinfo(  7200,      0,  'EET'),
        ttinfo( 10800,   3600, 'EEST'),
        ttinfo(  7200,      0,  'EET'),
        ttinfo( 10800,   3600, 'EEST'),
        ttinfo(  7200,      0,  'EET'),
        ttinfo( 10800,   3600, 'EEST'),
        ttinfo(  7200,      0,  'EET'),
        ttinfo( 10800,   3600, 'EEST'),
        ttinfo(  7200,      0,  'EET'),
        ttinfo( 10800,   3600, 'EEST'),
        ttinfo(  7200,      0,  'EET'),
        ttinfo( 10800,   3600, 'EEST'),
        ttinfo(  7200,      0,  'EET'),
        ttinfo( 10800,   3600, 'EEST'),
        ttinfo(  7200,      0,  'EET'),
        ttinfo( 10800,   3600, 'EEST'),
        ttinfo(  7200,      0,  'EET'),
        ttinfo( 10800,   3600, 'EEST'),
        ttinfo(  7200,      0,  'EET'),
        ttinfo( 10800,   3600, 'EEST'),
        ttinfo(  7200,      0,  'EET'),
        ttinfo( 10800,   3600, 'EEST'),
        ttinfo(  7200,      0,  'EET'),
        ttinfo( 10800,   3600, 'EEST'),
        ttinfo(  7200,      0,  'EET'),
        ttinfo( 10800,   3600, 'EEST'),
        ttinfo(  7200,      0,  'EET'),
        ttinfo( 10800,   3600, 'EEST'),
        ttinfo(  7200,      0,  'EET'),
        ttinfo( 10800,   3600, 'EEST'),
        ttinfo(  7200,      0,  'EET'),
        ttinfo( 10800,   3600, 'EEST'),
        ttinfo(  7200,      0,  'EET'),
        ttinfo( 10800,   3600, 'EEST'),
        ttinfo(  7200,      0,  'EET'),
        ttinfo( 10800,   3600, 'EEST'),
        ttinfo(  7200,      0,  'EET'),
        ttinfo( 10800,   3600, 'EEST'),
        ttinfo(  7200,      0,  'EET'),
        ttinfo( 10800,   3600, 'EEST'),
        ttinfo(  7200,      0,  'EET'),
        ttinfo( 10800,   3600, 'EEST'),
        ttinfo(  7200,      0,  'EET'),
        ttinfo( 10800,   3600, 'EEST'),
        ttinfo(  7200,      0,  'EET'),
        ttinfo( 10800,   3600, 'EEST'),
        ttinfo(  7200,      0,  'EET'),
        ttinfo( 10800,   3600, 'EEST'),
        ttinfo(  7200,      0,  'EET'),
        ttinfo( 10800,   3600, 'EEST'),
        ttinfo(  7200,      0,  'EET'),
        ttinfo( 10800,   3600, 'EEST'),
        ttinfo(  7200,      0,  'EET'),
        ttinfo( 10800,   3600, 'EEST'),
        ttinfo(  7200,      0,  'EET'),
        ttinfo( 10800,   3600, 'EEST'),
        ttinfo(  7200,      0,  'EET'),
        ttinfo( 10800,   3600, 'EEST'),
        ttinfo(  7200,      0,  'EET'),
        ttinfo( 10800,   3600, 'EEST'),
        ttinfo(  7200,      0,  'EET'),
        ttinfo( 10800,   3600, 'EEST'),
        ttinfo(  7200,      0,  'EET'),
        ttinfo( 10800,   3600, 'EEST'),
        ttinfo(  7200,      0,  'EET'),
        ttinfo( 10800,   3600, 'EEST'),
        ttinfo(  7200,      0,  'EET'),
        ttinfo( 10800,   3600, 'EEST'),
        ttinfo(  7200,      0,  'EET'),
        ttinfo( 10800,   3600, 'EEST'),
        ttinfo(  7200,      0,  'EET'),
        ttinfo( 10800,   3600, 'EEST'),
        ttinfo(  7200,      0,  'EET'),
        ttinfo( 10800,   3600, 'EEST'),
        ttinfo(  7200,      0,  'EET'),
        ttinfo( 10800,   3600, 'EEST'),
        ttinfo(  7200,      0,  'EET'),
        ttinfo( 10800,   3600, 'EEST'),
        ttinfo(  7200,      0,  'EET'),
        ttinfo( 10800,   3600, 'EEST'),
        ttinfo(  7200,      0,  'EET'),
        ttinfo( 10800,   3600, 'EEST'),
        ttinfo(  7200,      0,  'EET'),
        ttinfo( 10800,   3600, 'EEST'),
        ttinfo(  7200,      0,  'EET'),
        ttinfo( 10800,   3600, 'EEST'),
        ttinfo(  7200,      0,  'EET'),
        ttinfo( 10800,   3600, 'EEST'),
        ttinfo(  7200,      0,  'EET'),
        ttinfo( 10800,   3600, 'EEST'),
        ttinfo(  7200,      0,  'EET'),
        ttinfo( 10800,   3600, 'EEST'),
        ttinfo(  7200,      0,  'EET'),
        ttinfo( 10800,   3600, 'EEST'),
        ttinfo(  7200,      0,  'EET'),
        ttinfo( 10800,   3600, 'EEST'),
        ttinfo(  7200,      0,  'EET'),
        ttinfo( 10800,   3600, 'EEST'),
        ttinfo(  7200,      0,  'EET'),
        ttinfo( 10800,   3600, 'EEST'),
        ttinfo(  7200,      0,  'EET'),
        ttinfo( 10800,   3600, 'EEST'),
        ttinfo(  7200,      0,  'EET'),
        ttinfo( 10800,   3600, 'EEST'),
        ttinfo(  7200,      0,  'EET'),
        ttinfo( 10800,   3600, 'EEST'),
        ttinfo(  7200,      0,  'EET'),
        ttinfo( 10800,   3600, 'EEST'),
        ttinfo(  7200,      0,  'EET'),
        ttinfo( 10800,   3600, 'EEST'),
        ttinfo(  7200,      0,  'EET'),
        ttinfo( 10800,   3600, 'EEST'),
        ttinfo(  7200,      0,  'EET'),
        ttinfo( 10800,   3600, 'EEST'),
        ttinfo(  7200,      0,  'EET'),
        ttinfo( 10800,   3600, 'EEST'),
        ttinfo(  7200,      0,  'EET'),
        ttinfo( 10800,   3600, 'EEST'),
        ttinfo(  7200,      0,  'EET'),
        ttinfo( 10800,   3600, 'EEST'),
        ttinfo(  7200,      0,  'EET'),
        ttinfo( 10800,   3600, 'EEST'),
        ttinfo(  7200,      0,  'EET'),
        ttinfo( 10800,   3600, 'EEST'),
        ttinfo(  7200,      0,  'EET'),
        ttinfo( 10800,   3600, 'EEST'),
        ttinfo(  7200,      0,  'EET'),
        ttinfo( 10800,   3600, 'EEST'),
        ttinfo(  7200,      0,  'EET'),
        ttinfo( 10800,   3600, 'EEST'),
        ttinfo(  7200,      0,  'EET'),
        ttinfo( 10800,   3600, 'EEST'),
        ttinfo(  7200,      0,  'EET'),
        ttinfo( 10800,   3600, 'EEST'),
        ttinfo(  7200,      0,  'EET'),
        ttinfo( 10800,   3600, 'EEST'),
        ttinfo(  7200,      0,  'EET'),
        ttinfo( 10800,   3600, 'EEST'),
        ttinfo(  7200,      0,  'EET'),
        ttinfo( 10800,   3600, 'EEST'),
        ttinfo(  7200,      0,  'EET'),
        ttinfo( 10800,   3600, 'EEST'),
        ttinfo(  7200,      0,  'EET'),
        ttinfo( 10800,   3600, 'EEST'),
        ttinfo(  7200,      0,  'EET'),
        ttinfo( 10800,   3600, 'EEST'),
        ttinfo(  7200,      0,  'EET'),
        ttinfo( 10800,   3600, 'EEST'),
        ttinfo(  7200,      0,  'EET'),
        ttinfo( 10800,   3600, 'EEST'),
        ttinfo(  7200,      0,  'EET'),
        ttinfo( 10800,   3600, 'EEST'),
        ttinfo(  7200,      0,  'EET'),
        ]

Egypt = Egypt() # Singleton

