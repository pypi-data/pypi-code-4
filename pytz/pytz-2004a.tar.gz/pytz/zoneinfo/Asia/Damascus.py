'''
tzinfo timezone information for Asia/Damascus.

Generated from the Olson timezone database:
    ftp://elsie.nci.nih.gov/pub/tz*.tar.gz
'''

from pytz.tzinfo import DstTzInfo
from pytz.tzinfo import memorized_datetime as datetime
from pytz.tzinfo import memorized_ttinfo as ttinfo

class Damascus(DstTzInfo):
    '''Asia/Damascus timezone definition. See datetime.tzinfo for details'''

    _zone = 'Asia/Damascus'

    _utc_transition_times = [
        datetime(   1,  1,  1,  0,  0,  0), #   8712     0 LMT
        datetime(1919, 12, 31, 21, 34, 48), #   7200     0 EET
        datetime(1920,  4, 18,  0,  0,  0), #  10800  3600 EEST
        datetime(1920, 10,  2, 23,  0,  0), #   7200     0 EET
        datetime(1921,  4, 17,  0,  0,  0), #  10800  3600 EEST
        datetime(1921, 10,  1, 23,  0,  0), #   7200     0 EET
        datetime(1922,  4, 16,  0,  0,  0), #  10800  3600 EEST
        datetime(1922,  9, 30, 23,  0,  0), #   7200     0 EET
        datetime(1923,  4, 15,  0,  0,  0), #  10800  3600 EEST
        datetime(1923, 10,  6, 23,  0,  0), #   7200     0 EET
        datetime(1962,  4, 29,  0,  0,  0), #  10800  3600 EEST
        datetime(1962,  9, 30, 23,  0,  0), #   7200     0 EET
        datetime(1963,  5,  1,  0,  0,  0), #  10800  3600 EEST
        datetime(1963,  9, 29, 23,  0,  0), #   7200     0 EET
        datetime(1964,  5,  1,  0,  0,  0), #  10800  3600 EEST
        datetime(1964,  9, 30, 23,  0,  0), #   7200     0 EET
        datetime(1965,  5,  1,  0,  0,  0), #  10800  3600 EEST
        datetime(1965,  9, 29, 23,  0,  0), #   7200     0 EET
        datetime(1966,  4, 24,  0,  0,  0), #  10800  3600 EEST
        datetime(1966,  9, 30, 23,  0,  0), #   7200     0 EET
        datetime(1967,  5,  1,  0,  0,  0), #  10800  3600 EEST
        datetime(1967,  9, 30, 23,  0,  0), #   7200     0 EET
        datetime(1968,  5,  1,  0,  0,  0), #  10800  3600 EEST
        datetime(1968,  9, 30, 23,  0,  0), #   7200     0 EET
        datetime(1969,  5,  1,  0,  0,  0), #  10800  3600 EEST
        datetime(1969,  9, 30, 23,  0,  0), #   7200     0 EET
        datetime(1970,  5,  1,  0,  0,  0), #  10800  3600 EEST
        datetime(1970,  9, 30, 23,  0,  0), #   7200     0 EET
        datetime(1971,  5,  1,  0,  0,  0), #  10800  3600 EEST
        datetime(1971,  9, 30, 23,  0,  0), #   7200     0 EET
        datetime(1972,  5,  1,  0,  0,  0), #  10800  3600 EEST
        datetime(1972,  9, 30, 23,  0,  0), #   7200     0 EET
        datetime(1973,  5,  1,  0,  0,  0), #  10800  3600 EEST
        datetime(1973,  9, 30, 23,  0,  0), #   7200     0 EET
        datetime(1974,  5,  1,  0,  0,  0), #  10800  3600 EEST
        datetime(1974,  9, 30, 23,  0,  0), #   7200     0 EET
        datetime(1975,  5,  1,  0,  0,  0), #  10800  3600 EEST
        datetime(1975,  9, 30, 23,  0,  0), #   7200     0 EET
        datetime(1976,  5,  1,  0,  0,  0), #  10800  3600 EEST
        datetime(1976,  9, 30, 23,  0,  0), #   7200     0 EET
        datetime(1977,  5,  1,  0,  0,  0), #  10800  3600 EEST
        datetime(1977,  8, 31, 23,  0,  0), #   7200     0 EET
        datetime(1978,  5,  1,  0,  0,  0), #  10800  3600 EEST
        datetime(1978,  8, 31, 23,  0,  0), #   7200     0 EET
        datetime(1983,  4,  9,  0,  0,  0), #  10800  3600 EEST
        datetime(1983,  9, 30, 23,  0,  0), #   7200     0 EET
        datetime(1984,  4,  9,  0,  0,  0), #  10800  3600 EEST
        datetime(1984,  9, 30, 23,  0,  0), #   7200     0 EET
        datetime(1986,  2, 16,  0,  0,  0), #  10800  3600 EEST
        datetime(1986, 10,  8, 23,  0,  0), #   7200     0 EET
        datetime(1987,  3,  1,  0,  0,  0), #  10800  3600 EEST
        datetime(1987, 10, 30, 23,  0,  0), #   7200     0 EET
        datetime(1988,  3, 15,  0,  0,  0), #  10800  3600 EEST
        datetime(1988, 10, 30, 23,  0,  0), #   7200     0 EET
        datetime(1989,  3, 31,  0,  0,  0), #  10800  3600 EEST
        datetime(1989,  9, 30, 23,  0,  0), #   7200     0 EET
        datetime(1990,  4,  1,  0,  0,  0), #  10800  3600 EEST
        datetime(1990,  9, 29, 23,  0,  0), #   7200     0 EET
        datetime(1991,  3, 31, 22,  0,  0), #  10800  3600 EEST
        datetime(1991,  9, 30, 21,  0,  0), #   7200     0 EET
        datetime(1992,  4,  7, 22,  0,  0), #  10800  3600 EEST
        datetime(1992,  9, 30, 21,  0,  0), #   7200     0 EET
        datetime(1993,  3, 25, 22,  0,  0), #  10800  3600 EEST
        datetime(1993,  9, 24, 21,  0,  0), #   7200     0 EET
        datetime(1994,  3, 31, 22,  0,  0), #  10800  3600 EEST
        datetime(1994,  9, 30, 21,  0,  0), #   7200     0 EET
        datetime(1995,  3, 31, 22,  0,  0), #  10800  3600 EEST
        datetime(1995,  9, 30, 21,  0,  0), #   7200     0 EET
        datetime(1996,  3, 31, 22,  0,  0), #  10800  3600 EEST
        datetime(1996,  9, 30, 21,  0,  0), #   7200     0 EET
        datetime(1997,  3, 30, 22,  0,  0), #  10800  3600 EEST
        datetime(1997,  9, 30, 21,  0,  0), #   7200     0 EET
        datetime(1998,  3, 29, 22,  0,  0), #  10800  3600 EEST
        datetime(1998,  9, 30, 21,  0,  0), #   7200     0 EET
        datetime(1999,  3, 31, 22,  0,  0), #  10800  3600 EEST
        datetime(1999,  9, 30, 21,  0,  0), #   7200     0 EET
        datetime(2000,  3, 31, 22,  0,  0), #  10800  3600 EEST
        datetime(2000,  9, 30, 21,  0,  0), #   7200     0 EET
        datetime(2001,  3, 31, 22,  0,  0), #  10800  3600 EEST
        datetime(2001,  9, 30, 21,  0,  0), #   7200     0 EET
        datetime(2002,  3, 31, 22,  0,  0), #  10800  3600 EEST
        datetime(2002,  9, 30, 21,  0,  0), #   7200     0 EET
        datetime(2003,  3, 31, 22,  0,  0), #  10800  3600 EEST
        datetime(2003,  9, 30, 21,  0,  0), #   7200     0 EET
        datetime(2004,  3, 31, 22,  0,  0), #  10800  3600 EEST
        datetime(2004,  9, 30, 21,  0,  0), #   7200     0 EET
        datetime(2005,  3, 31, 22,  0,  0), #  10800  3600 EEST
        datetime(2005,  9, 30, 21,  0,  0), #   7200     0 EET
        datetime(2006,  3, 31, 22,  0,  0), #  10800  3600 EEST
        datetime(2006,  9, 30, 21,  0,  0), #   7200     0 EET
        datetime(2007,  3, 31, 22,  0,  0), #  10800  3600 EEST
        datetime(2007,  9, 30, 21,  0,  0), #   7200     0 EET
        datetime(2008,  3, 31, 22,  0,  0), #  10800  3600 EEST
        datetime(2008,  9, 30, 21,  0,  0), #   7200     0 EET
        datetime(2009,  3, 31, 22,  0,  0), #  10800  3600 EEST
        datetime(2009,  9, 30, 21,  0,  0), #   7200     0 EET
        datetime(2010,  3, 31, 22,  0,  0), #  10800  3600 EEST
        datetime(2010,  9, 30, 21,  0,  0), #   7200     0 EET
        datetime(2011,  3, 31, 22,  0,  0), #  10800  3600 EEST
        datetime(2011,  9, 30, 21,  0,  0), #   7200     0 EET
        datetime(2012,  3, 31, 22,  0,  0), #  10800  3600 EEST
        datetime(2012,  9, 30, 21,  0,  0), #   7200     0 EET
        datetime(2013,  3, 31, 22,  0,  0), #  10800  3600 EEST
        datetime(2013,  9, 30, 21,  0,  0), #   7200     0 EET
        datetime(2014,  3, 31, 22,  0,  0), #  10800  3600 EEST
        datetime(2014,  9, 30, 21,  0,  0), #   7200     0 EET
        datetime(2015,  3, 31, 22,  0,  0), #  10800  3600 EEST
        datetime(2015,  9, 30, 21,  0,  0), #   7200     0 EET
        datetime(2016,  3, 31, 22,  0,  0), #  10800  3600 EEST
        datetime(2016,  9, 30, 21,  0,  0), #   7200     0 EET
        datetime(2017,  3, 31, 22,  0,  0), #  10800  3600 EEST
        datetime(2017,  9, 30, 21,  0,  0), #   7200     0 EET
        datetime(2018,  3, 31, 22,  0,  0), #  10800  3600 EEST
        datetime(2018,  9, 30, 21,  0,  0), #   7200     0 EET
        datetime(2019,  3, 31, 22,  0,  0), #  10800  3600 EEST
        datetime(2019,  9, 30, 21,  0,  0), #   7200     0 EET
        datetime(2020,  3, 31, 22,  0,  0), #  10800  3600 EEST
        datetime(2020,  9, 30, 21,  0,  0), #   7200     0 EET
        datetime(2021,  3, 31, 22,  0,  0), #  10800  3600 EEST
        datetime(2021,  9, 30, 21,  0,  0), #   7200     0 EET
        datetime(2022,  3, 31, 22,  0,  0), #  10800  3600 EEST
        datetime(2022,  9, 30, 21,  0,  0), #   7200     0 EET
        datetime(2023,  3, 31, 22,  0,  0), #  10800  3600 EEST
        datetime(2023,  9, 30, 21,  0,  0), #   7200     0 EET
        datetime(2024,  3, 31, 22,  0,  0), #  10800  3600 EEST
        datetime(2024,  9, 30, 21,  0,  0), #   7200     0 EET
        datetime(2025,  3, 31, 22,  0,  0), #  10800  3600 EEST
        datetime(2025,  9, 30, 21,  0,  0), #   7200     0 EET
        datetime(2026,  3, 31, 22,  0,  0), #  10800  3600 EEST
        datetime(2026,  9, 30, 21,  0,  0), #   7200     0 EET
        datetime(2027,  3, 31, 22,  0,  0), #  10800  3600 EEST
        datetime(2027,  9, 30, 21,  0,  0), #   7200     0 EET
        datetime(2028,  3, 31, 22,  0,  0), #  10800  3600 EEST
        datetime(2028,  9, 30, 21,  0,  0), #   7200     0 EET
        datetime(2029,  3, 31, 22,  0,  0), #  10800  3600 EEST
        datetime(2029,  9, 30, 21,  0,  0), #   7200     0 EET
        datetime(2030,  3, 31, 22,  0,  0), #  10800  3600 EEST
        datetime(2030,  9, 30, 21,  0,  0), #   7200     0 EET
        datetime(2031,  3, 31, 22,  0,  0), #  10800  3600 EEST
        datetime(2031,  9, 30, 21,  0,  0), #   7200     0 EET
        datetime(2032,  3, 31, 22,  0,  0), #  10800  3600 EEST
        datetime(2032,  9, 30, 21,  0,  0), #   7200     0 EET
        datetime(2033,  3, 31, 22,  0,  0), #  10800  3600 EEST
        datetime(2033,  9, 30, 21,  0,  0), #   7200     0 EET
        datetime(2034,  3, 31, 22,  0,  0), #  10800  3600 EEST
        datetime(2034,  9, 30, 21,  0,  0), #   7200     0 EET
        datetime(2035,  3, 31, 22,  0,  0), #  10800  3600 EEST
        datetime(2035,  9, 30, 21,  0,  0), #   7200     0 EET
        datetime(2036,  3, 31, 22,  0,  0), #  10800  3600 EEST
        datetime(2036,  9, 30, 21,  0,  0), #   7200     0 EET
        datetime(2037,  3, 31, 22,  0,  0), #  10800  3600 EEST
        datetime(2037,  9, 30, 21,  0,  0), #   7200     0 EET
        ]

    _transition_info = [
        ttinfo(  8712,      0,  'LMT'),
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

Damascus = Damascus() # Singleton

