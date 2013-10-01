'''
tzinfo timezone information for Asia/Istanbul.

Generated from the Olson timezone database:
    ftp://elsie.nci.nih.gov/pub/tz*.tar.gz
'''

from pytz.tzinfo import DstTzInfo
from pytz.tzinfo import memorized_datetime as datetime
from pytz.tzinfo import memorized_ttinfo as ttinfo

class Istanbul(DstTzInfo):
    '''Asia/Istanbul timezone definition. See datetime.tzinfo for details'''

    _zone = 'Asia/Istanbul'

    _utc_transition_times = [
        datetime(   1,  1,  1,  0,  0,  0), #   7016     0 IMT
        datetime(1910,  9, 30, 22,  3,  4), #   7200     0 EET
        datetime(1916,  4, 30, 22,  0,  0), #  10800  3600 EEST
        datetime(1916,  9, 30, 21,  0,  0), #   7200     0 EET
        datetime(1920,  3, 27, 22,  0,  0), #  10800  3600 EEST
        datetime(1920, 10, 24, 21,  0,  0), #   7200     0 EET
        datetime(1921,  4,  2, 22,  0,  0), #  10800  3600 EEST
        datetime(1921, 10,  2, 21,  0,  0), #   7200     0 EET
        datetime(1922,  3, 25, 22,  0,  0), #  10800  3600 EEST
        datetime(1922, 10,  7, 21,  0,  0), #   7200     0 EET
        datetime(1924,  5, 12, 22,  0,  0), #  10800  3600 EEST
        datetime(1924,  9, 30, 21,  0,  0), #   7200     0 EET
        datetime(1925,  4, 30, 22,  0,  0), #  10800  3600 EEST
        datetime(1925,  9, 30, 21,  0,  0), #   7200     0 EET
        datetime(1940,  6, 29, 22,  0,  0), #  10800  3600 EEST
        datetime(1940, 10,  4, 21,  0,  0), #   7200     0 EET
        datetime(1940, 11, 30, 22,  0,  0), #  10800  3600 EEST
        datetime(1941,  9, 20, 21,  0,  0), #   7200     0 EET
        datetime(1942,  3, 31, 22,  0,  0), #  10800  3600 EEST
        datetime(1942, 10, 31, 21,  0,  0), #   7200     0 EET
        datetime(1945,  4,  1, 22,  0,  0), #  10800  3600 EEST
        datetime(1945, 10,  7, 21,  0,  0), #   7200     0 EET
        datetime(1946,  5, 31, 22,  0,  0), #  10800  3600 EEST
        datetime(1946,  9, 30, 21,  0,  0), #   7200     0 EET
        datetime(1947,  4, 19, 22,  0,  0), #  10800  3600 EEST
        datetime(1947, 10,  4, 21,  0,  0), #   7200     0 EET
        datetime(1948,  4, 17, 22,  0,  0), #  10800  3600 EEST
        datetime(1948, 10,  2, 21,  0,  0), #   7200     0 EET
        datetime(1949,  4,  9, 22,  0,  0), #  10800  3600 EEST
        datetime(1949, 10,  1, 21,  0,  0), #   7200     0 EET
        datetime(1950,  4, 18, 22,  0,  0), #  10800  3600 EEST
        datetime(1950, 10,  7, 21,  0,  0), #   7200     0 EET
        datetime(1951,  4, 21, 22,  0,  0), #  10800  3600 EEST
        datetime(1951, 10,  7, 21,  0,  0), #   7200     0 EET
        datetime(1962,  7, 14, 22,  0,  0), #  10800  3600 EEST
        datetime(1962, 10,  7, 21,  0,  0), #   7200     0 EET
        datetime(1964,  5, 14, 22,  0,  0), #  10800  3600 EEST
        datetime(1964,  9, 30, 21,  0,  0), #   7200     0 EET
        datetime(1970,  5,  2, 22,  0,  0), #  10800  3600 EEST
        datetime(1970, 10,  3, 21,  0,  0), #   7200     0 EET
        datetime(1971,  5,  1, 22,  0,  0), #  10800  3600 EEST
        datetime(1971, 10,  2, 21,  0,  0), #   7200     0 EET
        datetime(1972,  5,  6, 22,  0,  0), #  10800  3600 EEST
        datetime(1972, 10,  7, 21,  0,  0), #   7200     0 EET
        datetime(1973,  6,  2, 23,  0,  0), #  10800  3600 EEST
        datetime(1973, 11,  4,  0,  0,  0), #   7200     0 EET
        datetime(1974,  3, 31,  0,  0,  0), #  10800  3600 EEST
        datetime(1974, 11,  3,  2,  0,  0), #   7200     0 EET
        datetime(1975,  3, 29, 22,  0,  0), #  10800  3600 EEST
        datetime(1975, 10, 25, 21,  0,  0), #   7200     0 EET
        datetime(1976,  5, 31, 22,  0,  0), #  10800  3600 EEST
        datetime(1976, 10, 30, 21,  0,  0), #   7200     0 EET
        datetime(1977,  4,  2, 22,  0,  0), #  10800  3600 EEST
        datetime(1977, 10, 15, 21,  0,  0), #   7200     0 EET
        datetime(1978,  4,  1, 22,  0,  0), #  10800  3600 EEST
        datetime(1978, 10, 14, 21,  0,  0), #  14400  3600 TRST
        datetime(1979, 10, 14, 20,  0,  0), #  10800     0 TRT
        datetime(1980,  4,  6,  0,  0,  0), #  14400  3600 TRST
        datetime(1980, 10, 12, 20,  0,  0), #  10800     0 TRT
        datetime(1981,  3, 29,  0,  0,  0), #  14400  3600 TRST
        datetime(1981, 10, 11, 20,  0,  0), #  10800     0 TRT
        datetime(1982,  3, 28,  0,  0,  0), #  14400  3600 TRST
        datetime(1982, 10, 10, 20,  0,  0), #  10800     0 TRT
        datetime(1983,  7, 30, 21,  0,  0), #  14400  3600 TRST
        datetime(1983, 10,  1, 20,  0,  0), #  10800     0 TRT
        datetime(1985,  4, 19, 21,  0,  0), #  10800     0 EEST
        datetime(1985,  9, 27, 21,  0,  0), #   7200     0 EET
        datetime(1986,  3, 30,  0,  0,  0), #  10800  3600 EEST
        datetime(1986,  9, 28,  0,  0,  0), #   7200     0 EET
        datetime(1987,  3, 29,  0,  0,  0), #  10800  3600 EEST
        datetime(1987,  9, 27,  0,  0,  0), #   7200     0 EET
        datetime(1988,  3, 27,  0,  0,  0), #  10800  3600 EEST
        datetime(1988,  9, 25,  0,  0,  0), #   7200     0 EET
        datetime(1989,  3, 26,  0,  0,  0), #  10800  3600 EEST
        datetime(1989,  9, 24,  0,  0,  0), #   7200     0 EET
        datetime(1990,  3, 25,  0,  0,  0), #  10800  3600 EEST
        datetime(1990,  9, 30,  0,  0,  0), #   7200     0 EET
        datetime(1990, 12, 31, 22,  0,  0), #   7200     0 EET
        datetime(1991,  3, 31,  1,  0,  0), #  10800  3600 EEST
        datetime(1991,  9, 29,  1,  0,  0), #   7200     0 EET
        datetime(1992,  3, 29,  1,  0,  0), #  10800  3600 EEST
        datetime(1992,  9, 27,  1,  0,  0), #   7200     0 EET
        datetime(1993,  3, 28,  1,  0,  0), #  10800  3600 EEST
        datetime(1993,  9, 26,  1,  0,  0), #   7200     0 EET
        datetime(1994,  3, 27,  1,  0,  0), #  10800  3600 EEST
        datetime(1994,  9, 25,  1,  0,  0), #   7200     0 EET
        datetime(1995,  3, 26,  1,  0,  0), #  10800  3600 EEST
        datetime(1995,  9, 24,  1,  0,  0), #   7200     0 EET
        datetime(1996,  3, 31,  1,  0,  0), #  10800  3600 EEST
        datetime(1996, 10, 27,  1,  0,  0), #   7200     0 EET
        datetime(1997,  3, 30,  1,  0,  0), #  10800  3600 EEST
        datetime(1997, 10, 26,  1,  0,  0), #   7200     0 EET
        datetime(1998,  3, 29,  1,  0,  0), #  10800  3600 EEST
        datetime(1998, 10, 25,  1,  0,  0), #   7200     0 EET
        datetime(1999,  3, 28,  1,  0,  0), #  10800  3600 EEST
        datetime(1999, 10, 31,  1,  0,  0), #   7200     0 EET
        datetime(2000,  3, 26,  1,  0,  0), #  10800  3600 EEST
        datetime(2000, 10, 29,  1,  0,  0), #   7200     0 EET
        datetime(2001,  3, 25,  1,  0,  0), #  10800  3600 EEST
        datetime(2001, 10, 28,  1,  0,  0), #   7200     0 EET
        datetime(2002,  3, 31,  1,  0,  0), #  10800  3600 EEST
        datetime(2002, 10, 27,  1,  0,  0), #   7200     0 EET
        datetime(2003,  3, 30,  1,  0,  0), #  10800  3600 EEST
        datetime(2003, 10, 26,  1,  0,  0), #   7200     0 EET
        datetime(2004,  3, 28,  1,  0,  0), #  10800  3600 EEST
        datetime(2004, 10, 31,  1,  0,  0), #   7200     0 EET
        datetime(2005,  3, 27,  1,  0,  0), #  10800  3600 EEST
        datetime(2005, 10, 30,  1,  0,  0), #   7200     0 EET
        datetime(2006,  3, 26,  1,  0,  0), #  10800  3600 EEST
        datetime(2006, 10, 29,  1,  0,  0), #   7200     0 EET
        datetime(2007,  3, 25,  1,  0,  0), #  10800  3600 EEST
        datetime(2007, 10, 28,  1,  0,  0), #   7200     0 EET
        datetime(2008,  3, 30,  1,  0,  0), #  10800  3600 EEST
        datetime(2008, 10, 26,  1,  0,  0), #   7200     0 EET
        datetime(2009,  3, 29,  1,  0,  0), #  10800  3600 EEST
        datetime(2009, 10, 25,  1,  0,  0), #   7200     0 EET
        datetime(2010,  3, 28,  1,  0,  0), #  10800  3600 EEST
        datetime(2010, 10, 31,  1,  0,  0), #   7200     0 EET
        datetime(2011,  3, 27,  1,  0,  0), #  10800  3600 EEST
        datetime(2011, 10, 30,  1,  0,  0), #   7200     0 EET
        datetime(2012,  3, 25,  1,  0,  0), #  10800  3600 EEST
        datetime(2012, 10, 28,  1,  0,  0), #   7200     0 EET
        datetime(2013,  3, 31,  1,  0,  0), #  10800  3600 EEST
        datetime(2013, 10, 27,  1,  0,  0), #   7200     0 EET
        datetime(2014,  3, 30,  1,  0,  0), #  10800  3600 EEST
        datetime(2014, 10, 26,  1,  0,  0), #   7200     0 EET
        datetime(2015,  3, 29,  1,  0,  0), #  10800  3600 EEST
        datetime(2015, 10, 25,  1,  0,  0), #   7200     0 EET
        datetime(2016,  3, 27,  1,  0,  0), #  10800  3600 EEST
        datetime(2016, 10, 30,  1,  0,  0), #   7200     0 EET
        datetime(2017,  3, 26,  1,  0,  0), #  10800  3600 EEST
        datetime(2017, 10, 29,  1,  0,  0), #   7200     0 EET
        datetime(2018,  3, 25,  1,  0,  0), #  10800  3600 EEST
        datetime(2018, 10, 28,  1,  0,  0), #   7200     0 EET
        datetime(2019,  3, 31,  1,  0,  0), #  10800  3600 EEST
        datetime(2019, 10, 27,  1,  0,  0), #   7200     0 EET
        datetime(2020,  3, 29,  1,  0,  0), #  10800  3600 EEST
        datetime(2020, 10, 25,  1,  0,  0), #   7200     0 EET
        datetime(2021,  3, 28,  1,  0,  0), #  10800  3600 EEST
        datetime(2021, 10, 31,  1,  0,  0), #   7200     0 EET
        datetime(2022,  3, 27,  1,  0,  0), #  10800  3600 EEST
        datetime(2022, 10, 30,  1,  0,  0), #   7200     0 EET
        datetime(2023,  3, 26,  1,  0,  0), #  10800  3600 EEST
        datetime(2023, 10, 29,  1,  0,  0), #   7200     0 EET
        datetime(2024,  3, 31,  1,  0,  0), #  10800  3600 EEST
        datetime(2024, 10, 27,  1,  0,  0), #   7200     0 EET
        datetime(2025,  3, 30,  1,  0,  0), #  10800  3600 EEST
        datetime(2025, 10, 26,  1,  0,  0), #   7200     0 EET
        datetime(2026,  3, 29,  1,  0,  0), #  10800  3600 EEST
        datetime(2026, 10, 25,  1,  0,  0), #   7200     0 EET
        datetime(2027,  3, 28,  1,  0,  0), #  10800  3600 EEST
        datetime(2027, 10, 31,  1,  0,  0), #   7200     0 EET
        datetime(2028,  3, 26,  1,  0,  0), #  10800  3600 EEST
        datetime(2028, 10, 29,  1,  0,  0), #   7200     0 EET
        datetime(2029,  3, 25,  1,  0,  0), #  10800  3600 EEST
        datetime(2029, 10, 28,  1,  0,  0), #   7200     0 EET
        datetime(2030,  3, 31,  1,  0,  0), #  10800  3600 EEST
        datetime(2030, 10, 27,  1,  0,  0), #   7200     0 EET
        datetime(2031,  3, 30,  1,  0,  0), #  10800  3600 EEST
        datetime(2031, 10, 26,  1,  0,  0), #   7200     0 EET
        datetime(2032,  3, 28,  1,  0,  0), #  10800  3600 EEST
        datetime(2032, 10, 31,  1,  0,  0), #   7200     0 EET
        datetime(2033,  3, 27,  1,  0,  0), #  10800  3600 EEST
        datetime(2033, 10, 30,  1,  0,  0), #   7200     0 EET
        datetime(2034,  3, 26,  1,  0,  0), #  10800  3600 EEST
        datetime(2034, 10, 29,  1,  0,  0), #   7200     0 EET
        datetime(2035,  3, 25,  1,  0,  0), #  10800  3600 EEST
        datetime(2035, 10, 28,  1,  0,  0), #   7200     0 EET
        datetime(2036,  3, 30,  1,  0,  0), #  10800  3600 EEST
        datetime(2036, 10, 26,  1,  0,  0), #   7200     0 EET
        datetime(2037,  3, 29,  1,  0,  0), #  10800  3600 EEST
        datetime(2037, 10, 25,  1,  0,  0), #   7200     0 EET
        ]

    _transition_info = [
        ttinfo(  7016,      0,  'IMT'),
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
        ttinfo( 14400,   3600, 'TRST'),
        ttinfo( 10800,      0,  'TRT'),
        ttinfo( 14400,   3600, 'TRST'),
        ttinfo( 10800,      0,  'TRT'),
        ttinfo( 14400,   3600, 'TRST'),
        ttinfo( 10800,      0,  'TRT'),
        ttinfo( 14400,   3600, 'TRST'),
        ttinfo( 10800,      0,  'TRT'),
        ttinfo( 14400,   3600, 'TRST'),
        ttinfo( 10800,      0,  'TRT'),
        ttinfo( 10800,      0, 'EEST'),
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

Istanbul = Istanbul() # Singleton

