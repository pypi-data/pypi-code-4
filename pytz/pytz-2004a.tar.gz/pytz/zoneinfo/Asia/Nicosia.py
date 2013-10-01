'''
tzinfo timezone information for Asia/Nicosia.

Generated from the Olson timezone database:
    ftp://elsie.nci.nih.gov/pub/tz*.tar.gz
'''

from pytz.tzinfo import DstTzInfo
from pytz.tzinfo import memorized_datetime as datetime
from pytz.tzinfo import memorized_ttinfo as ttinfo

class Nicosia(DstTzInfo):
    '''Asia/Nicosia timezone definition. See datetime.tzinfo for details'''

    _zone = 'Asia/Nicosia'

    _utc_transition_times = [
        datetime(   1,  1,  1,  0,  0,  0), #   8008     0 LMT
        datetime(1921, 11, 13, 21, 46, 32), #   7200     0 EET
        datetime(1975,  4, 12, 22,  0,  0), #  10800  3600 EEST
        datetime(1975, 10, 11, 21,  0,  0), #   7200     0 EET
        datetime(1976,  5, 14, 22,  0,  0), #  10800  3600 EEST
        datetime(1976, 10, 10, 21,  0,  0), #   7200     0 EET
        datetime(1977,  4,  2, 22,  0,  0), #  10800  3600 EEST
        datetime(1977,  9, 24, 21,  0,  0), #   7200     0 EET
        datetime(1978,  4,  1, 22,  0,  0), #  10800  3600 EEST
        datetime(1978, 10,  1, 21,  0,  0), #   7200     0 EET
        datetime(1979,  3, 31, 22,  0,  0), #  10800  3600 EEST
        datetime(1979,  9, 29, 21,  0,  0), #   7200     0 EET
        datetime(1980,  4,  5, 22,  0,  0), #  10800  3600 EEST
        datetime(1980,  9, 27, 21,  0,  0), #   7200     0 EET
        datetime(1981,  3, 28, 22,  0,  0), #  10800  3600 EEST
        datetime(1981,  9, 26, 21,  0,  0), #   7200     0 EET
        datetime(1982,  3, 27, 22,  0,  0), #  10800  3600 EEST
        datetime(1982,  9, 25, 21,  0,  0), #   7200     0 EET
        datetime(1983,  3, 26, 22,  0,  0), #  10800  3600 EEST
        datetime(1983,  9, 24, 21,  0,  0), #   7200     0 EET
        datetime(1984,  3, 24, 22,  0,  0), #  10800  3600 EEST
        datetime(1984,  9, 29, 21,  0,  0), #   7200     0 EET
        datetime(1985,  3, 30, 22,  0,  0), #  10800  3600 EEST
        datetime(1985,  9, 28, 21,  0,  0), #   7200     0 EET
        datetime(1986,  3, 29, 22,  0,  0), #  10800  3600 EEST
        datetime(1986,  9, 27, 21,  0,  0), #   7200     0 EET
        datetime(1987,  3, 28, 22,  0,  0), #  10800  3600 EEST
        datetime(1987,  9, 26, 21,  0,  0), #   7200     0 EET
        datetime(1988,  3, 26, 22,  0,  0), #  10800  3600 EEST
        datetime(1988,  9, 24, 21,  0,  0), #   7200     0 EET
        datetime(1989,  3, 25, 22,  0,  0), #  10800  3600 EEST
        datetime(1989,  9, 23, 21,  0,  0), #   7200     0 EET
        datetime(1990,  3, 24, 22,  0,  0), #  10800  3600 EEST
        datetime(1990,  9, 29, 21,  0,  0), #   7200     0 EET
        datetime(1991,  3, 30, 22,  0,  0), #  10800  3600 EEST
        datetime(1991,  9, 28, 21,  0,  0), #   7200     0 EET
        datetime(1992,  3, 28, 22,  0,  0), #  10800  3600 EEST
        datetime(1992,  9, 26, 21,  0,  0), #   7200     0 EET
        datetime(1993,  3, 27, 22,  0,  0), #  10800  3600 EEST
        datetime(1993,  9, 25, 21,  0,  0), #   7200     0 EET
        datetime(1994,  3, 26, 22,  0,  0), #  10800  3600 EEST
        datetime(1994,  9, 24, 21,  0,  0), #   7200     0 EET
        datetime(1995,  3, 25, 22,  0,  0), #  10800  3600 EEST
        datetime(1995,  9, 23, 21,  0,  0), #   7200     0 EET
        datetime(1996,  3, 30, 22,  0,  0), #  10800  3600 EEST
        datetime(1996,  9, 28, 21,  0,  0), #   7200     0 EET
        datetime(1997,  3, 29, 22,  0,  0), #  10800  3600 EEST
        datetime(1997,  9, 27, 21,  0,  0), #   7200     0 EET
        datetime(1998,  3, 28, 22,  0,  0), #  10800  3600 EEST
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
        ttinfo(  8008,      0,  'LMT'),
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

Nicosia = Nicosia() # Singleton

