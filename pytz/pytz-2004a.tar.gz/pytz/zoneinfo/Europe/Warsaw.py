'''
tzinfo timezone information for Europe/Warsaw.

Generated from the Olson timezone database:
    ftp://elsie.nci.nih.gov/pub/tz*.tar.gz
'''

from pytz.tzinfo import DstTzInfo
from pytz.tzinfo import memorized_datetime as datetime
from pytz.tzinfo import memorized_ttinfo as ttinfo

class Warsaw(DstTzInfo):
    '''Europe/Warsaw timezone definition. See datetime.tzinfo for details'''

    _zone = 'Europe/Warsaw'

    _utc_transition_times = [
        datetime(   1,  1,  1,  0,  0,  0), #   5040     0 WMT
        datetime(1915,  8,  4, 22, 36,  0), #   3600     0 CET
        datetime(1916,  4, 30, 22,  0,  0), #   7200  3600 CEST
        datetime(1916,  9, 30, 23,  0,  0), #   3600     0 CET
        datetime(1917,  4, 16,  1,  0,  0), #   7200  3600 CEST
        datetime(1917,  9, 17,  1,  0,  0), #   3600     0 CET
        datetime(1918,  4, 15,  1,  0,  0), #   7200  3600 CEST
        datetime(1918,  9, 16,  1,  0,  0), #   7200     0 EET
        datetime(1919,  4, 15,  0,  0,  0), #  10800  3600 EEST
        datetime(1919,  9, 16,  0,  0,  0), #   7200     0 EET
        datetime(1922,  5, 31, 22,  0,  0), #   3600     0 CET
        datetime(1940,  6, 23,  1,  0,  0), #   7200  3600 CEST
        datetime(1942, 11,  2,  1,  0,  0), #   3600     0 CET
        datetime(1943,  3, 29,  1,  0,  0), #   7200  3600 CEST
        datetime(1943, 10,  4,  1,  0,  0), #   3600     0 CET
        datetime(1944,  4,  3,  1,  0,  0), #   7200  3600 CEST
        datetime(1944,  9, 30, 22,  0,  0), #   3600     0 CET
        datetime(1945,  4, 28, 23,  0,  0), #   7200  3600 CEST
        datetime(1945, 10, 31, 22,  0,  0), #   3600     0 CET
        datetime(1946,  4, 13, 23,  0,  0), #   7200  3600 CEST
        datetime(1946,  9,  6, 22,  0,  0), #   3600     0 CET
        datetime(1947,  5,  3, 23,  0,  0), #   7200  3600 CEST
        datetime(1947, 10,  4, 22,  0,  0), #   3600     0 CET
        datetime(1948,  4, 17, 23,  0,  0), #   7200  3600 CEST
        datetime(1948, 10,  2, 22,  0,  0), #   3600     0 CET
        datetime(1957,  6,  2,  0,  0,  0), #   7200  3600 CEST
        datetime(1957,  9, 29,  0,  0,  0), #   3600     0 CET
        datetime(1958,  3, 30,  0,  0,  0), #   7200  3600 CEST
        datetime(1958,  9, 28,  0,  0,  0), #   3600     0 CET
        datetime(1959,  5, 31,  0,  0,  0), #   7200  3600 CEST
        datetime(1959, 10,  4,  0,  0,  0), #   3600     0 CET
        datetime(1960,  4,  3,  0,  0,  0), #   7200  3600 CEST
        datetime(1960, 10,  2,  0,  0,  0), #   3600     0 CET
        datetime(1961,  5, 28,  0,  0,  0), #   7200  3600 CEST
        datetime(1961, 10,  1,  0,  0,  0), #   3600     0 CET
        datetime(1962,  5, 27,  0,  0,  0), #   7200  3600 CEST
        datetime(1962,  9, 30,  0,  0,  0), #   3600     0 CET
        datetime(1963,  5, 26,  0,  0,  0), #   7200  3600 CEST
        datetime(1963,  9, 29,  0,  0,  0), #   3600     0 CET
        datetime(1964,  5, 31,  0,  0,  0), #   7200  3600 CEST
        datetime(1964,  9, 27,  0,  0,  0), #   3600     0 CET
        datetime(1977,  4,  3,  0,  0,  0), #   7200  3600 CEST
        datetime(1977,  9, 25,  0,  0,  0), #   3600     0 CET
        datetime(1978,  4,  2,  0,  0,  0), #   7200  3600 CEST
        datetime(1978, 10,  1,  0,  0,  0), #   3600     0 CET
        datetime(1979,  4,  1,  0,  0,  0), #   7200  3600 CEST
        datetime(1979,  9, 30,  0,  0,  0), #   3600     0 CET
        datetime(1980,  4,  6,  0,  0,  0), #   7200  3600 CEST
        datetime(1980,  9, 28,  0,  0,  0), #   3600     0 CET
        datetime(1981,  3, 29,  0,  0,  0), #   7200  3600 CEST
        datetime(1981,  9, 27,  0,  0,  0), #   3600     0 CET
        datetime(1982,  3, 28,  0,  0,  0), #   7200  3600 CEST
        datetime(1982,  9, 26,  0,  0,  0), #   3600     0 CET
        datetime(1983,  3, 27,  0,  0,  0), #   7200  3600 CEST
        datetime(1983,  9, 25,  0,  0,  0), #   3600     0 CET
        datetime(1984,  3, 25,  0,  0,  0), #   7200  3600 CEST
        datetime(1984,  9, 30,  0,  0,  0), #   3600     0 CET
        datetime(1985,  3, 31,  0,  0,  0), #   7200  3600 CEST
        datetime(1985,  9, 29,  0,  0,  0), #   3600     0 CET
        datetime(1986,  3, 30,  0,  0,  0), #   7200  3600 CEST
        datetime(1986,  9, 28,  0,  0,  0), #   3600     0 CET
        datetime(1987,  3, 29,  0,  0,  0), #   7200  3600 CEST
        datetime(1987,  9, 27,  0,  0,  0), #   3600     0 CET
        datetime(1988,  3, 27,  0,  0,  0), #   7200  3600 CEST
        datetime(1988,  9, 25,  0,  0,  0), #   3600     0 CET
        datetime(1989,  3, 26,  0,  0,  0), #   7200  3600 CEST
        datetime(1989,  9, 24,  0,  0,  0), #   3600     0 CET
        datetime(1990,  3, 25,  0,  0,  0), #   7200  3600 CEST
        datetime(1990,  9, 30,  0,  0,  0), #   3600     0 CET
        datetime(1991,  3, 31,  0,  0,  0), #   7200  3600 CEST
        datetime(1991,  9, 29,  0,  0,  0), #   3600     0 CET
        datetime(1992,  3, 29,  0,  0,  0), #   7200  3600 CEST
        datetime(1992,  9, 27,  0,  0,  0), #   3600     0 CET
        datetime(1993,  3, 28,  0,  0,  0), #   7200  3600 CEST
        datetime(1993,  9, 26,  0,  0,  0), #   3600     0 CET
        datetime(1994,  3, 27,  0,  0,  0), #   7200  3600 CEST
        datetime(1994,  9, 25,  0,  0,  0), #   3600     0 CET
        datetime(1995,  3, 26,  0,  0,  0), #   7200  3600 CEST
        datetime(1995,  9, 24,  0,  0,  0), #   3600     0 CET
        datetime(1996,  3, 31,  0,  0,  0), #   7200  3600 CEST
        datetime(1996, 10, 27,  0,  0,  0), #   3600     0 CET
        datetime(1997,  3, 30,  0,  0,  0), #   7200  3600 CEST
        datetime(1997, 10, 26,  0,  0,  0), #   3600     0 CET
        datetime(1998,  3, 29,  0,  0,  0), #   7200  3600 CEST
        datetime(1998, 10, 25,  0,  0,  0), #   3600     0 CET
        datetime(1998, 12, 31, 23,  0,  0), #   3600     0 CET
        datetime(1999,  3, 28,  1,  0,  0), #   7200  3600 CEST
        datetime(1999, 10, 31,  1,  0,  0), #   3600     0 CET
        datetime(2000,  3, 26,  1,  0,  0), #   7200  3600 CEST
        datetime(2000, 10, 29,  1,  0,  0), #   3600     0 CET
        datetime(2001,  3, 25,  1,  0,  0), #   7200  3600 CEST
        datetime(2001, 10, 28,  1,  0,  0), #   3600     0 CET
        datetime(2002,  3, 31,  1,  0,  0), #   7200  3600 CEST
        datetime(2002, 10, 27,  1,  0,  0), #   3600     0 CET
        datetime(2003,  3, 30,  1,  0,  0), #   7200  3600 CEST
        datetime(2003, 10, 26,  1,  0,  0), #   3600     0 CET
        datetime(2004,  3, 28,  1,  0,  0), #   7200  3600 CEST
        datetime(2004, 10, 31,  1,  0,  0), #   3600     0 CET
        datetime(2005,  3, 27,  1,  0,  0), #   7200  3600 CEST
        datetime(2005, 10, 30,  1,  0,  0), #   3600     0 CET
        datetime(2006,  3, 26,  1,  0,  0), #   7200  3600 CEST
        datetime(2006, 10, 29,  1,  0,  0), #   3600     0 CET
        datetime(2007,  3, 25,  1,  0,  0), #   7200  3600 CEST
        datetime(2007, 10, 28,  1,  0,  0), #   3600     0 CET
        datetime(2008,  3, 30,  1,  0,  0), #   7200  3600 CEST
        datetime(2008, 10, 26,  1,  0,  0), #   3600     0 CET
        datetime(2009,  3, 29,  1,  0,  0), #   7200  3600 CEST
        datetime(2009, 10, 25,  1,  0,  0), #   3600     0 CET
        datetime(2010,  3, 28,  1,  0,  0), #   7200  3600 CEST
        datetime(2010, 10, 31,  1,  0,  0), #   3600     0 CET
        datetime(2011,  3, 27,  1,  0,  0), #   7200  3600 CEST
        datetime(2011, 10, 30,  1,  0,  0), #   3600     0 CET
        datetime(2012,  3, 25,  1,  0,  0), #   7200  3600 CEST
        datetime(2012, 10, 28,  1,  0,  0), #   3600     0 CET
        datetime(2013,  3, 31,  1,  0,  0), #   7200  3600 CEST
        datetime(2013, 10, 27,  1,  0,  0), #   3600     0 CET
        datetime(2014,  3, 30,  1,  0,  0), #   7200  3600 CEST
        datetime(2014, 10, 26,  1,  0,  0), #   3600     0 CET
        datetime(2015,  3, 29,  1,  0,  0), #   7200  3600 CEST
        datetime(2015, 10, 25,  1,  0,  0), #   3600     0 CET
        datetime(2016,  3, 27,  1,  0,  0), #   7200  3600 CEST
        datetime(2016, 10, 30,  1,  0,  0), #   3600     0 CET
        datetime(2017,  3, 26,  1,  0,  0), #   7200  3600 CEST
        datetime(2017, 10, 29,  1,  0,  0), #   3600     0 CET
        datetime(2018,  3, 25,  1,  0,  0), #   7200  3600 CEST
        datetime(2018, 10, 28,  1,  0,  0), #   3600     0 CET
        datetime(2019,  3, 31,  1,  0,  0), #   7200  3600 CEST
        datetime(2019, 10, 27,  1,  0,  0), #   3600     0 CET
        datetime(2020,  3, 29,  1,  0,  0), #   7200  3600 CEST
        datetime(2020, 10, 25,  1,  0,  0), #   3600     0 CET
        datetime(2021,  3, 28,  1,  0,  0), #   7200  3600 CEST
        datetime(2021, 10, 31,  1,  0,  0), #   3600     0 CET
        datetime(2022,  3, 27,  1,  0,  0), #   7200  3600 CEST
        datetime(2022, 10, 30,  1,  0,  0), #   3600     0 CET
        datetime(2023,  3, 26,  1,  0,  0), #   7200  3600 CEST
        datetime(2023, 10, 29,  1,  0,  0), #   3600     0 CET
        datetime(2024,  3, 31,  1,  0,  0), #   7200  3600 CEST
        datetime(2024, 10, 27,  1,  0,  0), #   3600     0 CET
        datetime(2025,  3, 30,  1,  0,  0), #   7200  3600 CEST
        datetime(2025, 10, 26,  1,  0,  0), #   3600     0 CET
        datetime(2026,  3, 29,  1,  0,  0), #   7200  3600 CEST
        datetime(2026, 10, 25,  1,  0,  0), #   3600     0 CET
        datetime(2027,  3, 28,  1,  0,  0), #   7200  3600 CEST
        datetime(2027, 10, 31,  1,  0,  0), #   3600     0 CET
        datetime(2028,  3, 26,  1,  0,  0), #   7200  3600 CEST
        datetime(2028, 10, 29,  1,  0,  0), #   3600     0 CET
        datetime(2029,  3, 25,  1,  0,  0), #   7200  3600 CEST
        datetime(2029, 10, 28,  1,  0,  0), #   3600     0 CET
        datetime(2030,  3, 31,  1,  0,  0), #   7200  3600 CEST
        datetime(2030, 10, 27,  1,  0,  0), #   3600     0 CET
        datetime(2031,  3, 30,  1,  0,  0), #   7200  3600 CEST
        datetime(2031, 10, 26,  1,  0,  0), #   3600     0 CET
        datetime(2032,  3, 28,  1,  0,  0), #   7200  3600 CEST
        datetime(2032, 10, 31,  1,  0,  0), #   3600     0 CET
        datetime(2033,  3, 27,  1,  0,  0), #   7200  3600 CEST
        datetime(2033, 10, 30,  1,  0,  0), #   3600     0 CET
        datetime(2034,  3, 26,  1,  0,  0), #   7200  3600 CEST
        datetime(2034, 10, 29,  1,  0,  0), #   3600     0 CET
        datetime(2035,  3, 25,  1,  0,  0), #   7200  3600 CEST
        datetime(2035, 10, 28,  1,  0,  0), #   3600     0 CET
        datetime(2036,  3, 30,  1,  0,  0), #   7200  3600 CEST
        datetime(2036, 10, 26,  1,  0,  0), #   3600     0 CET
        datetime(2037,  3, 29,  1,  0,  0), #   7200  3600 CEST
        datetime(2037, 10, 25,  1,  0,  0), #   3600     0 CET
        ]

    _transition_info = [
        ttinfo(  5040,      0,  'WMT'),
        ttinfo(  3600,      0,  'CET'),
        ttinfo(  7200,   3600, 'CEST'),
        ttinfo(  3600,      0,  'CET'),
        ttinfo(  7200,   3600, 'CEST'),
        ttinfo(  3600,      0,  'CET'),
        ttinfo(  7200,   3600, 'CEST'),
        ttinfo(  7200,      0,  'EET'),
        ttinfo( 10800,   3600, 'EEST'),
        ttinfo(  7200,      0,  'EET'),
        ttinfo(  3600,      0,  'CET'),
        ttinfo(  7200,   3600, 'CEST'),
        ttinfo(  3600,      0,  'CET'),
        ttinfo(  7200,   3600, 'CEST'),
        ttinfo(  3600,      0,  'CET'),
        ttinfo(  7200,   3600, 'CEST'),
        ttinfo(  3600,      0,  'CET'),
        ttinfo(  7200,   3600, 'CEST'),
        ttinfo(  3600,      0,  'CET'),
        ttinfo(  7200,   3600, 'CEST'),
        ttinfo(  3600,      0,  'CET'),
        ttinfo(  7200,   3600, 'CEST'),
        ttinfo(  3600,      0,  'CET'),
        ttinfo(  7200,   3600, 'CEST'),
        ttinfo(  3600,      0,  'CET'),
        ttinfo(  7200,   3600, 'CEST'),
        ttinfo(  3600,      0,  'CET'),
        ttinfo(  7200,   3600, 'CEST'),
        ttinfo(  3600,      0,  'CET'),
        ttinfo(  7200,   3600, 'CEST'),
        ttinfo(  3600,      0,  'CET'),
        ttinfo(  7200,   3600, 'CEST'),
        ttinfo(  3600,      0,  'CET'),
        ttinfo(  7200,   3600, 'CEST'),
        ttinfo(  3600,      0,  'CET'),
        ttinfo(  7200,   3600, 'CEST'),
        ttinfo(  3600,      0,  'CET'),
        ttinfo(  7200,   3600, 'CEST'),
        ttinfo(  3600,      0,  'CET'),
        ttinfo(  7200,   3600, 'CEST'),
        ttinfo(  3600,      0,  'CET'),
        ttinfo(  7200,   3600, 'CEST'),
        ttinfo(  3600,      0,  'CET'),
        ttinfo(  7200,   3600, 'CEST'),
        ttinfo(  3600,      0,  'CET'),
        ttinfo(  7200,   3600, 'CEST'),
        ttinfo(  3600,      0,  'CET'),
        ttinfo(  7200,   3600, 'CEST'),
        ttinfo(  3600,      0,  'CET'),
        ttinfo(  7200,   3600, 'CEST'),
        ttinfo(  3600,      0,  'CET'),
        ttinfo(  7200,   3600, 'CEST'),
        ttinfo(  3600,      0,  'CET'),
        ttinfo(  7200,   3600, 'CEST'),
        ttinfo(  3600,      0,  'CET'),
        ttinfo(  7200,   3600, 'CEST'),
        ttinfo(  3600,      0,  'CET'),
        ttinfo(  7200,   3600, 'CEST'),
        ttinfo(  3600,      0,  'CET'),
        ttinfo(  7200,   3600, 'CEST'),
        ttinfo(  3600,      0,  'CET'),
        ttinfo(  7200,   3600, 'CEST'),
        ttinfo(  3600,      0,  'CET'),
        ttinfo(  7200,   3600, 'CEST'),
        ttinfo(  3600,      0,  'CET'),
        ttinfo(  7200,   3600, 'CEST'),
        ttinfo(  3600,      0,  'CET'),
        ttinfo(  7200,   3600, 'CEST'),
        ttinfo(  3600,      0,  'CET'),
        ttinfo(  7200,   3600, 'CEST'),
        ttinfo(  3600,      0,  'CET'),
        ttinfo(  7200,   3600, 'CEST'),
        ttinfo(  3600,      0,  'CET'),
        ttinfo(  7200,   3600, 'CEST'),
        ttinfo(  3600,      0,  'CET'),
        ttinfo(  7200,   3600, 'CEST'),
        ttinfo(  3600,      0,  'CET'),
        ttinfo(  7200,   3600, 'CEST'),
        ttinfo(  3600,      0,  'CET'),
        ttinfo(  7200,   3600, 'CEST'),
        ttinfo(  3600,      0,  'CET'),
        ttinfo(  7200,   3600, 'CEST'),
        ttinfo(  3600,      0,  'CET'),
        ttinfo(  7200,   3600, 'CEST'),
        ttinfo(  3600,      0,  'CET'),
        ttinfo(  3600,      0,  'CET'),
        ttinfo(  7200,   3600, 'CEST'),
        ttinfo(  3600,      0,  'CET'),
        ttinfo(  7200,   3600, 'CEST'),
        ttinfo(  3600,      0,  'CET'),
        ttinfo(  7200,   3600, 'CEST'),
        ttinfo(  3600,      0,  'CET'),
        ttinfo(  7200,   3600, 'CEST'),
        ttinfo(  3600,      0,  'CET'),
        ttinfo(  7200,   3600, 'CEST'),
        ttinfo(  3600,      0,  'CET'),
        ttinfo(  7200,   3600, 'CEST'),
        ttinfo(  3600,      0,  'CET'),
        ttinfo(  7200,   3600, 'CEST'),
        ttinfo(  3600,      0,  'CET'),
        ttinfo(  7200,   3600, 'CEST'),
        ttinfo(  3600,      0,  'CET'),
        ttinfo(  7200,   3600, 'CEST'),
        ttinfo(  3600,      0,  'CET'),
        ttinfo(  7200,   3600, 'CEST'),
        ttinfo(  3600,      0,  'CET'),
        ttinfo(  7200,   3600, 'CEST'),
        ttinfo(  3600,      0,  'CET'),
        ttinfo(  7200,   3600, 'CEST'),
        ttinfo(  3600,      0,  'CET'),
        ttinfo(  7200,   3600, 'CEST'),
        ttinfo(  3600,      0,  'CET'),
        ttinfo(  7200,   3600, 'CEST'),
        ttinfo(  3600,      0,  'CET'),
        ttinfo(  7200,   3600, 'CEST'),
        ttinfo(  3600,      0,  'CET'),
        ttinfo(  7200,   3600, 'CEST'),
        ttinfo(  3600,      0,  'CET'),
        ttinfo(  7200,   3600, 'CEST'),
        ttinfo(  3600,      0,  'CET'),
        ttinfo(  7200,   3600, 'CEST'),
        ttinfo(  3600,      0,  'CET'),
        ttinfo(  7200,   3600, 'CEST'),
        ttinfo(  3600,      0,  'CET'),
        ttinfo(  7200,   3600, 'CEST'),
        ttinfo(  3600,      0,  'CET'),
        ttinfo(  7200,   3600, 'CEST'),
        ttinfo(  3600,      0,  'CET'),
        ttinfo(  7200,   3600, 'CEST'),
        ttinfo(  3600,      0,  'CET'),
        ttinfo(  7200,   3600, 'CEST'),
        ttinfo(  3600,      0,  'CET'),
        ttinfo(  7200,   3600, 'CEST'),
        ttinfo(  3600,      0,  'CET'),
        ttinfo(  7200,   3600, 'CEST'),
        ttinfo(  3600,      0,  'CET'),
        ttinfo(  7200,   3600, 'CEST'),
        ttinfo(  3600,      0,  'CET'),
        ttinfo(  7200,   3600, 'CEST'),
        ttinfo(  3600,      0,  'CET'),
        ttinfo(  7200,   3600, 'CEST'),
        ttinfo(  3600,      0,  'CET'),
        ttinfo(  7200,   3600, 'CEST'),
        ttinfo(  3600,      0,  'CET'),
        ttinfo(  7200,   3600, 'CEST'),
        ttinfo(  3600,      0,  'CET'),
        ttinfo(  7200,   3600, 'CEST'),
        ttinfo(  3600,      0,  'CET'),
        ttinfo(  7200,   3600, 'CEST'),
        ttinfo(  3600,      0,  'CET'),
        ttinfo(  7200,   3600, 'CEST'),
        ttinfo(  3600,      0,  'CET'),
        ttinfo(  7200,   3600, 'CEST'),
        ttinfo(  3600,      0,  'CET'),
        ttinfo(  7200,   3600, 'CEST'),
        ttinfo(  3600,      0,  'CET'),
        ttinfo(  7200,   3600, 'CEST'),
        ttinfo(  3600,      0,  'CET'),
        ttinfo(  7200,   3600, 'CEST'),
        ttinfo(  3600,      0,  'CET'),
        ttinfo(  7200,   3600, 'CEST'),
        ttinfo(  3600,      0,  'CET'),
        ttinfo(  7200,   3600, 'CEST'),
        ttinfo(  3600,      0,  'CET'),
        ]

Warsaw = Warsaw() # Singleton

