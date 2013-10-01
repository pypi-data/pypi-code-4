'''
tzinfo timezone information for Asia/Gaza.

Generated from the Olson timezone database:
    ftp://elsie.nci.nih.gov/pub/tz*.tar.gz
'''

from pytz.tzinfo import DstTzInfo
from pytz.tzinfo import memorized_datetime as datetime
from pytz.tzinfo import memorized_ttinfo as ttinfo

class Gaza(DstTzInfo):
    '''Asia/Gaza timezone definition. See datetime.tzinfo for details'''

    _zone = 'Asia/Gaza'

    _utc_transition_times = [
        datetime(   1,  1,  1,  0,  0,  0), #   7200     0 EET
        datetime(1940,  5, 31, 22,  0,  0), #  10800  3600 EET
        datetime(1942, 10, 31, 21,  0,  0), #   7200     0 EET
        datetime(1943,  4,  1,  0,  0,  0), #  10800  3600 EET
        datetime(1943, 10, 31, 21,  0,  0), #   7200     0 EET
        datetime(1944,  3, 31, 22,  0,  0), #  10800  3600 EET
        datetime(1944, 10, 31, 21,  0,  0), #   7200     0 EET
        datetime(1945,  4, 15, 22,  0,  0), #  10800  3600 EET
        datetime(1945, 10, 31, 23,  0,  0), #   7200     0 EET
        datetime(1946,  4, 16,  0,  0,  0), #  10800  3600 EET
        datetime(1946, 10, 31, 21,  0,  0), #   7200     0 EET
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
        datetime(1967,  6,  4, 21,  0,  0), #   7200     0 IST
        datetime(1974,  7,  6, 22,  0,  0), #  10800  3600 IDT
        datetime(1974, 10, 12, 21,  0,  0), #   7200     0 IST
        datetime(1975,  4, 19, 22,  0,  0), #  10800  3600 IDT
        datetime(1975,  8, 30, 21,  0,  0), #   7200     0 IST
        datetime(1985,  4, 13, 22,  0,  0), #  10800  3600 IDT
        datetime(1985,  9, 14, 21,  0,  0), #   7200     0 IST
        datetime(1986,  5, 17, 22,  0,  0), #  10800  3600 IDT
        datetime(1986,  9,  6, 21,  0,  0), #   7200     0 IST
        datetime(1987,  4, 14, 22,  0,  0), #  10800  3600 IDT
        datetime(1987,  9, 12, 21,  0,  0), #   7200     0 IST
        datetime(1988,  4,  8, 22,  0,  0), #  10800  3600 IDT
        datetime(1988,  9,  2, 21,  0,  0), #   7200     0 IST
        datetime(1989,  4, 29, 22,  0,  0), #  10800  3600 IDT
        datetime(1989,  9,  2, 21,  0,  0), #   7200     0 IST
        datetime(1990,  3, 24, 22,  0,  0), #  10800  3600 IDT
        datetime(1990,  8, 25, 21,  0,  0), #   7200     0 IST
        datetime(1991,  3, 23, 22,  0,  0), #  10800  3600 IDT
        datetime(1991,  8, 31, 21,  0,  0), #   7200     0 IST
        datetime(1992,  3, 28, 22,  0,  0), #  10800  3600 IDT
        datetime(1992,  9,  5, 21,  0,  0), #   7200     0 IST
        datetime(1993,  4,  1, 22,  0,  0), #  10800  3600 IDT
        datetime(1993,  9,  4, 21,  0,  0), #   7200     0 IST
        datetime(1994,  3, 31, 22,  0,  0), #  10800  3600 IDT
        datetime(1994,  8, 27, 21,  0,  0), #   7200     0 IST
        datetime(1995,  3, 30, 22,  0,  0), #  10800  3600 IDT
        datetime(1995,  9,  2, 21,  0,  0), #   7200     0 IST
        datetime(1995, 12, 31, 22,  0,  0), #   7200     0 EET
        datetime(1996,  4,  4, 22,  0,  0), #  10800  3600 EEST
        datetime(1996,  9, 19, 22,  0,  0), #   7200     0 EET
        datetime(1997,  4,  3, 22,  0,  0), #  10800  3600 EEST
        datetime(1997,  9, 18, 22,  0,  0), #   7200     0 EET
        datetime(1998,  4,  2, 22,  0,  0), #  10800  3600 EEST
        datetime(1998,  9, 17, 22,  0,  0), #   7200     0 EET
        datetime(1998, 12, 31, 22,  0,  0), #   7200     0 EET
        datetime(1999,  4, 15, 22,  0,  0), #  10800  3600 EEST
        datetime(1999, 10, 14, 21,  0,  0), #   7200     0 EET
        datetime(2000,  4, 20, 22,  0,  0), #  10800  3600 EEST
        datetime(2000, 10, 19, 21,  0,  0), #   7200     0 EET
        datetime(2001,  4, 19, 22,  0,  0), #  10800  3600 EEST
        datetime(2001, 10, 18, 21,  0,  0), #   7200     0 EET
        datetime(2002,  4, 18, 22,  0,  0), #  10800  3600 EEST
        datetime(2002, 10, 17, 21,  0,  0), #   7200     0 EET
        datetime(2003,  4, 17, 22,  0,  0), #  10800  3600 EEST
        datetime(2003, 10, 16, 21,  0,  0), #   7200     0 EET
        datetime(2004,  4, 15, 22,  0,  0), #  10800  3600 EEST
        datetime(2004, 10, 14, 21,  0,  0), #   7200     0 EET
        datetime(2005,  4, 14, 22,  0,  0), #  10800  3600 EEST
        datetime(2005, 10, 20, 21,  0,  0), #   7200     0 EET
        datetime(2006,  4, 20, 22,  0,  0), #  10800  3600 EEST
        datetime(2006, 10, 19, 21,  0,  0), #   7200     0 EET
        datetime(2007,  4, 19, 22,  0,  0), #  10800  3600 EEST
        datetime(2007, 10, 18, 21,  0,  0), #   7200     0 EET
        datetime(2008,  4, 17, 22,  0,  0), #  10800  3600 EEST
        datetime(2008, 10, 16, 21,  0,  0), #   7200     0 EET
        datetime(2009,  4, 16, 22,  0,  0), #  10800  3600 EEST
        datetime(2009, 10, 15, 21,  0,  0), #   7200     0 EET
        datetime(2010,  4, 15, 22,  0,  0), #  10800  3600 EEST
        datetime(2010, 10, 14, 21,  0,  0), #   7200     0 EET
        datetime(2011,  4, 14, 22,  0,  0), #  10800  3600 EEST
        datetime(2011, 10, 20, 21,  0,  0), #   7200     0 EET
        datetime(2012,  4, 19, 22,  0,  0), #  10800  3600 EEST
        datetime(2012, 10, 18, 21,  0,  0), #   7200     0 EET
        datetime(2013,  4, 18, 22,  0,  0), #  10800  3600 EEST
        datetime(2013, 10, 17, 21,  0,  0), #   7200     0 EET
        datetime(2014,  4, 17, 22,  0,  0), #  10800  3600 EEST
        datetime(2014, 10, 16, 21,  0,  0), #   7200     0 EET
        datetime(2015,  4, 16, 22,  0,  0), #  10800  3600 EEST
        datetime(2015, 10, 15, 21,  0,  0), #   7200     0 EET
        datetime(2016,  4, 14, 22,  0,  0), #  10800  3600 EEST
        datetime(2016, 10, 20, 21,  0,  0), #   7200     0 EET
        datetime(2017,  4, 20, 22,  0,  0), #  10800  3600 EEST
        datetime(2017, 10, 19, 21,  0,  0), #   7200     0 EET
        datetime(2018,  4, 19, 22,  0,  0), #  10800  3600 EEST
        datetime(2018, 10, 18, 21,  0,  0), #   7200     0 EET
        datetime(2019,  4, 18, 22,  0,  0), #  10800  3600 EEST
        datetime(2019, 10, 17, 21,  0,  0), #   7200     0 EET
        datetime(2020,  4, 16, 22,  0,  0), #  10800  3600 EEST
        datetime(2020, 10, 15, 21,  0,  0), #   7200     0 EET
        datetime(2021,  4, 15, 22,  0,  0), #  10800  3600 EEST
        datetime(2021, 10, 14, 21,  0,  0), #   7200     0 EET
        datetime(2022,  4, 14, 22,  0,  0), #  10800  3600 EEST
        datetime(2022, 10, 20, 21,  0,  0), #   7200     0 EET
        datetime(2023,  4, 20, 22,  0,  0), #  10800  3600 EEST
        datetime(2023, 10, 19, 21,  0,  0), #   7200     0 EET
        datetime(2024,  4, 18, 22,  0,  0), #  10800  3600 EEST
        datetime(2024, 10, 17, 21,  0,  0), #   7200     0 EET
        datetime(2025,  4, 17, 22,  0,  0), #  10800  3600 EEST
        datetime(2025, 10, 16, 21,  0,  0), #   7200     0 EET
        datetime(2026,  4, 16, 22,  0,  0), #  10800  3600 EEST
        datetime(2026, 10, 15, 21,  0,  0), #   7200     0 EET
        datetime(2027,  4, 15, 22,  0,  0), #  10800  3600 EEST
        datetime(2027, 10, 14, 21,  0,  0), #   7200     0 EET
        datetime(2028,  4, 20, 22,  0,  0), #  10800  3600 EEST
        datetime(2028, 10, 19, 21,  0,  0), #   7200     0 EET
        datetime(2029,  4, 19, 22,  0,  0), #  10800  3600 EEST
        datetime(2029, 10, 18, 21,  0,  0), #   7200     0 EET
        datetime(2030,  4, 18, 22,  0,  0), #  10800  3600 EEST
        datetime(2030, 10, 17, 21,  0,  0), #   7200     0 EET
        datetime(2031,  4, 17, 22,  0,  0), #  10800  3600 EEST
        datetime(2031, 10, 16, 21,  0,  0), #   7200     0 EET
        datetime(2032,  4, 15, 22,  0,  0), #  10800  3600 EEST
        datetime(2032, 10, 14, 21,  0,  0), #   7200     0 EET
        datetime(2033,  4, 14, 22,  0,  0), #  10800  3600 EEST
        datetime(2033, 10, 20, 21,  0,  0), #   7200     0 EET
        datetime(2034,  4, 20, 22,  0,  0), #  10800  3600 EEST
        datetime(2034, 10, 19, 21,  0,  0), #   7200     0 EET
        datetime(2035,  4, 19, 22,  0,  0), #  10800  3600 EEST
        datetime(2035, 10, 18, 21,  0,  0), #   7200     0 EET
        datetime(2036,  4, 17, 22,  0,  0), #  10800  3600 EEST
        datetime(2036, 10, 16, 21,  0,  0), #   7200     0 EET
        datetime(2037,  4, 16, 22,  0,  0), #  10800  3600 EEST
        datetime(2037, 10, 15, 21,  0,  0), #   7200     0 EET
        ]

    _transition_info = [
        ttinfo(  7200,      0,  'EET'),
        ttinfo( 10800,   3600,  'EET'),
        ttinfo(  7200,      0,  'EET'),
        ttinfo( 10800,   3600,  'EET'),
        ttinfo(  7200,      0,  'EET'),
        ttinfo( 10800,   3600,  'EET'),
        ttinfo(  7200,      0,  'EET'),
        ttinfo( 10800,   3600,  'EET'),
        ttinfo(  7200,      0,  'EET'),
        ttinfo( 10800,   3600,  'EET'),
        ttinfo(  7200,      0,  'EET'),
        ttinfo( 10800,   3600, 'EEST'),
        ttinfo(  7200,      0,  'EET'),
        ttinfo( 10800,   3600, 'EEST'),
        ttinfo(  7200,      0,  'EET'),
        ttinfo( 10800,   3600, 'EEST'),
        ttinfo(  7200,      0,  'EET'),
        ttinfo( 10800,   3600, 'EEST'),
        ttinfo(  7200,      0,  'EET'),
        ttinfo( 10800,   3600, 'EEST'),
        ttinfo(  7200,      0,  'EET'),
        ttinfo( 10800,   3600, 'EEST'),
        ttinfo(  7200,      0,  'EET'),
        ttinfo( 10800,   3600, 'EEST'),
        ttinfo(  7200,      0,  'EET'),
        ttinfo( 10800,   3600, 'EEST'),
        ttinfo(  7200,      0,  'EET'),
        ttinfo( 10800,   3600, 'EEST'),
        ttinfo(  7200,      0,  'EET'),
        ttinfo( 10800,   3600, 'EEST'),
        ttinfo(  7200,      0,  'EET'),
        ttinfo( 10800,   3600, 'EEST'),
        ttinfo(  7200,      0,  'IST'),
        ttinfo( 10800,   3600,  'IDT'),
        ttinfo(  7200,      0,  'IST'),
        ttinfo( 10800,   3600,  'IDT'),
        ttinfo(  7200,      0,  'IST'),
        ttinfo( 10800,   3600,  'IDT'),
        ttinfo(  7200,      0,  'IST'),
        ttinfo( 10800,   3600,  'IDT'),
        ttinfo(  7200,      0,  'IST'),
        ttinfo( 10800,   3600,  'IDT'),
        ttinfo(  7200,      0,  'IST'),
        ttinfo( 10800,   3600,  'IDT'),
        ttinfo(  7200,      0,  'IST'),
        ttinfo( 10800,   3600,  'IDT'),
        ttinfo(  7200,      0,  'IST'),
        ttinfo( 10800,   3600,  'IDT'),
        ttinfo(  7200,      0,  'IST'),
        ttinfo( 10800,   3600,  'IDT'),
        ttinfo(  7200,      0,  'IST'),
        ttinfo( 10800,   3600,  'IDT'),
        ttinfo(  7200,      0,  'IST'),
        ttinfo( 10800,   3600,  'IDT'),
        ttinfo(  7200,      0,  'IST'),
        ttinfo( 10800,   3600,  'IDT'),
        ttinfo(  7200,      0,  'IST'),
        ttinfo( 10800,   3600,  'IDT'),
        ttinfo(  7200,      0,  'IST'),
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
        ]

Gaza = Gaza() # Singleton

