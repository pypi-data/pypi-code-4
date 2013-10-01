'''
tzinfo timezone information for Asia/Jerusalem.

Generated from the Olson timezone database:
    ftp://elsie.nci.nih.gov/pub/tz*.tar.gz
'''

from pytz.tzinfo import DstTzInfo
from pytz.tzinfo import memorized_datetime as datetime
from pytz.tzinfo import memorized_ttinfo as ttinfo

class Jerusalem(DstTzInfo):
    '''Asia/Jerusalem timezone definition. See datetime.tzinfo for details'''

    _zone = 'Asia/Jerusalem'

    _utc_transition_times = [
        datetime(   1,  1,  1,  0,  0,  0), #   8440     0 JMT
        datetime(1917, 12, 31, 21, 39, 20), #   7200     0 IST
        datetime(1940,  5, 31, 22,  0,  0), #  10800  3600 IDT
        datetime(1942, 10, 31, 21,  0,  0), #   7200     0 IST
        datetime(1943,  4,  1,  0,  0,  0), #  10800  3600 IDT
        datetime(1943, 10, 31, 21,  0,  0), #   7200     0 IST
        datetime(1944,  3, 31, 22,  0,  0), #  10800  3600 IDT
        datetime(1944, 10, 31, 21,  0,  0), #   7200     0 IST
        datetime(1945,  4, 15, 22,  0,  0), #  10800  3600 IDT
        datetime(1945, 10, 31, 23,  0,  0), #   7200     0 IST
        datetime(1946,  4, 16,  0,  0,  0), #  10800  3600 IDT
        datetime(1946, 10, 31, 21,  0,  0), #   7200     0 IST
        datetime(1948,  5, 22, 22,  0,  0), #  14400  7200 IDDT
        datetime(1948,  8, 31, 20,  0,  0), #  10800 -3600 IDT
        datetime(1948, 10, 31, 23,  0,  0), #   7200     0 IST
        datetime(1949,  4, 30, 22,  0,  0), #  10800  3600 IDT
        datetime(1949, 10, 31, 23,  0,  0), #   7200     0 IST
        datetime(1950,  4, 15, 22,  0,  0), #  10800  3600 IDT
        datetime(1950,  9, 15,  0,  0,  0), #   7200     0 IST
        datetime(1951,  3, 31, 22,  0,  0), #  10800  3600 IDT
        datetime(1951, 11, 11,  0,  0,  0), #   7200     0 IST
        datetime(1952,  4, 20,  0,  0,  0), #  10800  3600 IDT
        datetime(1952, 10, 19,  0,  0,  0), #   7200     0 IST
        datetime(1953,  4, 12,  0,  0,  0), #  10800  3600 IDT
        datetime(1953,  9, 13,  0,  0,  0), #   7200     0 IST
        datetime(1954,  6, 12, 22,  0,  0), #  10800  3600 IDT
        datetime(1954,  9, 11, 21,  0,  0), #   7200     0 IST
        datetime(1955,  6, 11,  0,  0,  0), #  10800  3600 IDT
        datetime(1955,  9, 10, 21,  0,  0), #   7200     0 IST
        datetime(1956,  6,  2, 22,  0,  0), #  10800  3600 IDT
        datetime(1956,  9, 30,  0,  0,  0), #   7200     0 IST
        datetime(1957,  4, 29,  0,  0,  0), #  10800  3600 IDT
        datetime(1957,  9, 21, 21,  0,  0), #   7200     0 IST
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
        datetime(1996,  3, 14, 22,  0,  0), #  10800  3600 IDT
        datetime(1996,  9, 15, 21,  0,  0), #   7200     0 IST
        datetime(1997,  3, 20, 22,  0,  0), #  10800  3600 IDT
        datetime(1997,  9, 13, 21,  0,  0), #   7200     0 IST
        datetime(1998,  3, 19, 22,  0,  0), #  10800  3600 IDT
        datetime(1998,  9,  5, 21,  0,  0), #   7200     0 IST
        datetime(1999,  4,  2,  0,  0,  0), #  10800  3600 IDT
        datetime(1999,  9,  2, 23,  0,  0), #   7200     0 IST
        datetime(2000,  4, 14,  0,  0,  0), #  10800  3600 IDT
        datetime(2000, 10,  5, 22,  0,  0), #   7200     0 IST
        datetime(2001,  4,  8, 23,  0,  0), #  10800  3600 IDT
        datetime(2001,  9, 23, 22,  0,  0), #   7200     0 IST
        datetime(2002,  3, 28, 23,  0,  0), #  10800  3600 IDT
        datetime(2002, 10,  6, 22,  0,  0), #   7200     0 IST
        datetime(2003,  3, 27, 23,  0,  0), #  10800  3600 IDT
        datetime(2003, 10,  2, 22,  0,  0), #   7200     0 IST
        datetime(2004,  4,  6, 23,  0,  0), #  10800  3600 IDT
        datetime(2004,  9, 21, 22,  0,  0), #   7200     0 IST
        datetime(2005,  3, 31, 23,  0,  0), #  10800  3600 IDT
        datetime(2005,  9, 30, 22,  0,  0), #   7200     0 IST
        datetime(2006,  3, 31, 23,  0,  0), #  10800  3600 IDT
        datetime(2006,  9, 30, 22,  0,  0), #   7200     0 IST
        datetime(2007,  3, 31, 23,  0,  0), #  10800  3600 IDT
        datetime(2007,  9, 30, 22,  0,  0), #   7200     0 IST
        datetime(2008,  3, 31, 23,  0,  0), #  10800  3600 IDT
        datetime(2008,  9, 30, 22,  0,  0), #   7200     0 IST
        datetime(2009,  3, 31, 23,  0,  0), #  10800  3600 IDT
        datetime(2009,  9, 30, 22,  0,  0), #   7200     0 IST
        datetime(2010,  3, 31, 23,  0,  0), #  10800  3600 IDT
        datetime(2010,  9, 30, 22,  0,  0), #   7200     0 IST
        datetime(2011,  3, 31, 23,  0,  0), #  10800  3600 IDT
        datetime(2011,  9, 30, 22,  0,  0), #   7200     0 IST
        datetime(2012,  3, 31, 23,  0,  0), #  10800  3600 IDT
        datetime(2012,  9, 30, 22,  0,  0), #   7200     0 IST
        datetime(2013,  3, 31, 23,  0,  0), #  10800  3600 IDT
        datetime(2013,  9, 30, 22,  0,  0), #   7200     0 IST
        datetime(2014,  3, 31, 23,  0,  0), #  10800  3600 IDT
        datetime(2014,  9, 30, 22,  0,  0), #   7200     0 IST
        datetime(2015,  3, 31, 23,  0,  0), #  10800  3600 IDT
        datetime(2015,  9, 30, 22,  0,  0), #   7200     0 IST
        datetime(2016,  3, 31, 23,  0,  0), #  10800  3600 IDT
        datetime(2016,  9, 30, 22,  0,  0), #   7200     0 IST
        datetime(2017,  3, 31, 23,  0,  0), #  10800  3600 IDT
        datetime(2017,  9, 30, 22,  0,  0), #   7200     0 IST
        datetime(2018,  3, 31, 23,  0,  0), #  10800  3600 IDT
        datetime(2018,  9, 30, 22,  0,  0), #   7200     0 IST
        datetime(2019,  3, 31, 23,  0,  0), #  10800  3600 IDT
        datetime(2019,  9, 30, 22,  0,  0), #   7200     0 IST
        datetime(2020,  3, 31, 23,  0,  0), #  10800  3600 IDT
        datetime(2020,  9, 30, 22,  0,  0), #   7200     0 IST
        datetime(2021,  3, 31, 23,  0,  0), #  10800  3600 IDT
        datetime(2021,  9, 30, 22,  0,  0), #   7200     0 IST
        datetime(2022,  3, 31, 23,  0,  0), #  10800  3600 IDT
        datetime(2022,  9, 30, 22,  0,  0), #   7200     0 IST
        datetime(2023,  3, 31, 23,  0,  0), #  10800  3600 IDT
        datetime(2023,  9, 30, 22,  0,  0), #   7200     0 IST
        datetime(2024,  3, 31, 23,  0,  0), #  10800  3600 IDT
        datetime(2024,  9, 30, 22,  0,  0), #   7200     0 IST
        datetime(2025,  3, 31, 23,  0,  0), #  10800  3600 IDT
        datetime(2025,  9, 30, 22,  0,  0), #   7200     0 IST
        datetime(2026,  3, 31, 23,  0,  0), #  10800  3600 IDT
        datetime(2026,  9, 30, 22,  0,  0), #   7200     0 IST
        datetime(2027,  3, 31, 23,  0,  0), #  10800  3600 IDT
        datetime(2027,  9, 30, 22,  0,  0), #   7200     0 IST
        datetime(2028,  3, 31, 23,  0,  0), #  10800  3600 IDT
        datetime(2028,  9, 30, 22,  0,  0), #   7200     0 IST
        datetime(2029,  3, 31, 23,  0,  0), #  10800  3600 IDT
        datetime(2029,  9, 30, 22,  0,  0), #   7200     0 IST
        datetime(2030,  3, 31, 23,  0,  0), #  10800  3600 IDT
        datetime(2030,  9, 30, 22,  0,  0), #   7200     0 IST
        datetime(2031,  3, 31, 23,  0,  0), #  10800  3600 IDT
        datetime(2031,  9, 30, 22,  0,  0), #   7200     0 IST
        datetime(2032,  3, 31, 23,  0,  0), #  10800  3600 IDT
        datetime(2032,  9, 30, 22,  0,  0), #   7200     0 IST
        datetime(2033,  3, 31, 23,  0,  0), #  10800  3600 IDT
        datetime(2033,  9, 30, 22,  0,  0), #   7200     0 IST
        datetime(2034,  3, 31, 23,  0,  0), #  10800  3600 IDT
        datetime(2034,  9, 30, 22,  0,  0), #   7200     0 IST
        datetime(2035,  3, 31, 23,  0,  0), #  10800  3600 IDT
        datetime(2035,  9, 30, 22,  0,  0), #   7200     0 IST
        datetime(2036,  3, 31, 23,  0,  0), #  10800  3600 IDT
        datetime(2036,  9, 30, 22,  0,  0), #   7200     0 IST
        datetime(2037,  3, 31, 23,  0,  0), #  10800  3600 IDT
        datetime(2037,  9, 30, 22,  0,  0), #   7200     0 IST
        ]

    _transition_info = [
        ttinfo(  8440,      0,  'JMT'),
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
        ttinfo( 14400,   7200, 'IDDT'),
        ttinfo( 10800,  -3600,  'IDT'),
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
        ]

Jerusalem = Jerusalem() # Singleton

