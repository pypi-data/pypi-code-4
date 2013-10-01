'''
tzinfo timezone information for NZ_minus_CHAT.

Generated from the Olson timezone database:
    ftp://elsie.nci.nih.gov/pub/tz*.tar.gz
'''

from pytz.tzinfo import DstTzInfo
from pytz.tzinfo import memorized_datetime as datetime
from pytz.tzinfo import memorized_ttinfo as ttinfo

class NZ_minus_CHAT(DstTzInfo):
    '''NZ_minus_CHAT timezone definition. See datetime.tzinfo for details'''

    _zone = 'NZ_minus_CHAT'

    _utc_transition_times = [
        datetime(   1,  1,  1,  0,  0,  0), #  44028     0 LMT
        datetime(1956, 12, 31, 11, 46, 12), #  45900     0 CHAST
        datetime(1974, 11,  2, 14,  0,  0), #  49500  3600 CHADT
        datetime(1975,  2, 22, 14,  0,  0), #  45900     0 CHAST
        datetime(1975, 10, 25, 14,  0,  0), #  49500  3600 CHADT
        datetime(1976,  3,  6, 14,  0,  0), #  45900     0 CHAST
        datetime(1976, 10, 30, 14,  0,  0), #  49500  3600 CHADT
        datetime(1977,  3,  5, 14,  0,  0), #  45900     0 CHAST
        datetime(1977, 10, 29, 14,  0,  0), #  49500  3600 CHADT
        datetime(1978,  3,  4, 14,  0,  0), #  45900     0 CHAST
        datetime(1978, 10, 28, 14,  0,  0), #  49500  3600 CHADT
        datetime(1979,  3,  3, 14,  0,  0), #  45900     0 CHAST
        datetime(1979, 10, 27, 14,  0,  0), #  49500  3600 CHADT
        datetime(1980,  3,  1, 14,  0,  0), #  45900     0 CHAST
        datetime(1980, 10, 25, 14,  0,  0), #  49500  3600 CHADT
        datetime(1981,  2, 28, 14,  0,  0), #  45900     0 CHAST
        datetime(1981, 10, 24, 14,  0,  0), #  49500  3600 CHADT
        datetime(1982,  3,  6, 14,  0,  0), #  45900     0 CHAST
        datetime(1982, 10, 30, 14,  0,  0), #  49500  3600 CHADT
        datetime(1983,  3,  5, 14,  0,  0), #  45900     0 CHAST
        datetime(1983, 10, 29, 14,  0,  0), #  49500  3600 CHADT
        datetime(1984,  3,  3, 14,  0,  0), #  45900     0 CHAST
        datetime(1984, 10, 27, 14,  0,  0), #  49500  3600 CHADT
        datetime(1985,  3,  2, 14,  0,  0), #  45900     0 CHAST
        datetime(1985, 10, 26, 14,  0,  0), #  49500  3600 CHADT
        datetime(1986,  3,  1, 14,  0,  0), #  45900     0 CHAST
        datetime(1986, 10, 25, 14,  0,  0), #  49500  3600 CHADT
        datetime(1987,  2, 28, 14,  0,  0), #  45900     0 CHAST
        datetime(1987, 10, 24, 14,  0,  0), #  49500  3600 CHADT
        datetime(1988,  3,  5, 14,  0,  0), #  45900     0 CHAST
        datetime(1988, 10, 29, 14,  0,  0), #  49500  3600 CHADT
        datetime(1989,  3,  4, 14,  0,  0), #  45900     0 CHAST
        datetime(1989, 10,  7, 14,  0,  0), #  49500  3600 CHADT
        datetime(1990,  3, 17, 14,  0,  0), #  45900     0 CHAST
        datetime(1990, 10,  6, 14,  0,  0), #  49500  3600 CHADT
        datetime(1991,  3, 16, 14,  0,  0), #  45900     0 CHAST
        datetime(1991, 10,  5, 14,  0,  0), #  49500  3600 CHADT
        datetime(1992,  3, 14, 14,  0,  0), #  45900     0 CHAST
        datetime(1992, 10,  3, 14,  0,  0), #  49500  3600 CHADT
        datetime(1993,  3, 20, 14,  0,  0), #  45900     0 CHAST
        datetime(1993, 10,  2, 14,  0,  0), #  49500  3600 CHADT
        datetime(1994,  3, 19, 14,  0,  0), #  45900     0 CHAST
        datetime(1994, 10,  1, 14,  0,  0), #  49500  3600 CHADT
        datetime(1995,  3, 18, 14,  0,  0), #  45900     0 CHAST
        datetime(1995,  9, 30, 14,  0,  0), #  49500  3600 CHADT
        datetime(1996,  3, 16, 14,  0,  0), #  45900     0 CHAST
        datetime(1996, 10,  5, 14,  0,  0), #  49500  3600 CHADT
        datetime(1997,  3, 15, 14,  0,  0), #  45900     0 CHAST
        datetime(1997, 10,  4, 14,  0,  0), #  49500  3600 CHADT
        datetime(1998,  3, 14, 14,  0,  0), #  45900     0 CHAST
        datetime(1998, 10,  3, 14,  0,  0), #  49500  3600 CHADT
        datetime(1999,  3, 20, 14,  0,  0), #  45900     0 CHAST
        datetime(1999, 10,  2, 14,  0,  0), #  49500  3600 CHADT
        datetime(2000,  3, 18, 14,  0,  0), #  45900     0 CHAST
        datetime(2000,  9, 30, 14,  0,  0), #  49500  3600 CHADT
        datetime(2001,  3, 17, 14,  0,  0), #  45900     0 CHAST
        datetime(2001, 10,  6, 14,  0,  0), #  49500  3600 CHADT
        datetime(2002,  3, 16, 14,  0,  0), #  45900     0 CHAST
        datetime(2002, 10,  5, 14,  0,  0), #  49500  3600 CHADT
        datetime(2003,  3, 15, 14,  0,  0), #  45900     0 CHAST
        datetime(2003, 10,  4, 14,  0,  0), #  49500  3600 CHADT
        datetime(2004,  3, 20, 14,  0,  0), #  45900     0 CHAST
        datetime(2004, 10,  2, 14,  0,  0), #  49500  3600 CHADT
        datetime(2005,  3, 19, 14,  0,  0), #  45900     0 CHAST
        datetime(2005, 10,  1, 14,  0,  0), #  49500  3600 CHADT
        datetime(2006,  3, 18, 14,  0,  0), #  45900     0 CHAST
        datetime(2006,  9, 30, 14,  0,  0), #  49500  3600 CHADT
        datetime(2007,  3, 17, 14,  0,  0), #  45900     0 CHAST
        datetime(2007, 10,  6, 14,  0,  0), #  49500  3600 CHADT
        datetime(2008,  3, 15, 14,  0,  0), #  45900     0 CHAST
        datetime(2008, 10,  4, 14,  0,  0), #  49500  3600 CHADT
        datetime(2009,  3, 14, 14,  0,  0), #  45900     0 CHAST
        datetime(2009, 10,  3, 14,  0,  0), #  49500  3600 CHADT
        datetime(2010,  3, 20, 14,  0,  0), #  45900     0 CHAST
        datetime(2010, 10,  2, 14,  0,  0), #  49500  3600 CHADT
        datetime(2011,  3, 19, 14,  0,  0), #  45900     0 CHAST
        datetime(2011, 10,  1, 14,  0,  0), #  49500  3600 CHADT
        datetime(2012,  3, 17, 14,  0,  0), #  45900     0 CHAST
        datetime(2012, 10,  6, 14,  0,  0), #  49500  3600 CHADT
        datetime(2013,  3, 16, 14,  0,  0), #  45900     0 CHAST
        datetime(2013, 10,  5, 14,  0,  0), #  49500  3600 CHADT
        datetime(2014,  3, 15, 14,  0,  0), #  45900     0 CHAST
        datetime(2014, 10,  4, 14,  0,  0), #  49500  3600 CHADT
        datetime(2015,  3, 14, 14,  0,  0), #  45900     0 CHAST
        datetime(2015, 10,  3, 14,  0,  0), #  49500  3600 CHADT
        datetime(2016,  3, 19, 14,  0,  0), #  45900     0 CHAST
        datetime(2016, 10,  1, 14,  0,  0), #  49500  3600 CHADT
        datetime(2017,  3, 18, 14,  0,  0), #  45900     0 CHAST
        datetime(2017,  9, 30, 14,  0,  0), #  49500  3600 CHADT
        datetime(2018,  3, 17, 14,  0,  0), #  45900     0 CHAST
        datetime(2018, 10,  6, 14,  0,  0), #  49500  3600 CHADT
        datetime(2019,  3, 16, 14,  0,  0), #  45900     0 CHAST
        datetime(2019, 10,  5, 14,  0,  0), #  49500  3600 CHADT
        datetime(2020,  3, 14, 14,  0,  0), #  45900     0 CHAST
        datetime(2020, 10,  3, 14,  0,  0), #  49500  3600 CHADT
        datetime(2021,  3, 20, 14,  0,  0), #  45900     0 CHAST
        datetime(2021, 10,  2, 14,  0,  0), #  49500  3600 CHADT
        datetime(2022,  3, 19, 14,  0,  0), #  45900     0 CHAST
        datetime(2022, 10,  1, 14,  0,  0), #  49500  3600 CHADT
        datetime(2023,  3, 18, 14,  0,  0), #  45900     0 CHAST
        datetime(2023,  9, 30, 14,  0,  0), #  49500  3600 CHADT
        datetime(2024,  3, 16, 14,  0,  0), #  45900     0 CHAST
        datetime(2024, 10,  5, 14,  0,  0), #  49500  3600 CHADT
        datetime(2025,  3, 15, 14,  0,  0), #  45900     0 CHAST
        datetime(2025, 10,  4, 14,  0,  0), #  49500  3600 CHADT
        datetime(2026,  3, 14, 14,  0,  0), #  45900     0 CHAST
        datetime(2026, 10,  3, 14,  0,  0), #  49500  3600 CHADT
        datetime(2027,  3, 20, 14,  0,  0), #  45900     0 CHAST
        datetime(2027, 10,  2, 14,  0,  0), #  49500  3600 CHADT
        datetime(2028,  3, 18, 14,  0,  0), #  45900     0 CHAST
        datetime(2028,  9, 30, 14,  0,  0), #  49500  3600 CHADT
        datetime(2029,  3, 17, 14,  0,  0), #  45900     0 CHAST
        datetime(2029, 10,  6, 14,  0,  0), #  49500  3600 CHADT
        datetime(2030,  3, 16, 14,  0,  0), #  45900     0 CHAST
        datetime(2030, 10,  5, 14,  0,  0), #  49500  3600 CHADT
        datetime(2031,  3, 15, 14,  0,  0), #  45900     0 CHAST
        datetime(2031, 10,  4, 14,  0,  0), #  49500  3600 CHADT
        datetime(2032,  3, 20, 14,  0,  0), #  45900     0 CHAST
        datetime(2032, 10,  2, 14,  0,  0), #  49500  3600 CHADT
        datetime(2033,  3, 19, 14,  0,  0), #  45900     0 CHAST
        datetime(2033, 10,  1, 14,  0,  0), #  49500  3600 CHADT
        datetime(2034,  3, 18, 14,  0,  0), #  45900     0 CHAST
        datetime(2034,  9, 30, 14,  0,  0), #  49500  3600 CHADT
        datetime(2035,  3, 17, 14,  0,  0), #  45900     0 CHAST
        datetime(2035, 10,  6, 14,  0,  0), #  49500  3600 CHADT
        datetime(2036,  3, 15, 14,  0,  0), #  45900     0 CHAST
        datetime(2036, 10,  4, 14,  0,  0), #  49500  3600 CHADT
        datetime(2037,  3, 14, 14,  0,  0), #  45900     0 CHAST
        datetime(2037, 10,  3, 14,  0,  0), #  49500  3600 CHADT
        ]

    _transition_info = [
        ttinfo( 44028,      0,  'LMT'),
        ttinfo( 45900,      0, 'CHAST'),
        ttinfo( 49500,   3600, 'CHADT'),
        ttinfo( 45900,      0, 'CHAST'),
        ttinfo( 49500,   3600, 'CHADT'),
        ttinfo( 45900,      0, 'CHAST'),
        ttinfo( 49500,   3600, 'CHADT'),
        ttinfo( 45900,      0, 'CHAST'),
        ttinfo( 49500,   3600, 'CHADT'),
        ttinfo( 45900,      0, 'CHAST'),
        ttinfo( 49500,   3600, 'CHADT'),
        ttinfo( 45900,      0, 'CHAST'),
        ttinfo( 49500,   3600, 'CHADT'),
        ttinfo( 45900,      0, 'CHAST'),
        ttinfo( 49500,   3600, 'CHADT'),
        ttinfo( 45900,      0, 'CHAST'),
        ttinfo( 49500,   3600, 'CHADT'),
        ttinfo( 45900,      0, 'CHAST'),
        ttinfo( 49500,   3600, 'CHADT'),
        ttinfo( 45900,      0, 'CHAST'),
        ttinfo( 49500,   3600, 'CHADT'),
        ttinfo( 45900,      0, 'CHAST'),
        ttinfo( 49500,   3600, 'CHADT'),
        ttinfo( 45900,      0, 'CHAST'),
        ttinfo( 49500,   3600, 'CHADT'),
        ttinfo( 45900,      0, 'CHAST'),
        ttinfo( 49500,   3600, 'CHADT'),
        ttinfo( 45900,      0, 'CHAST'),
        ttinfo( 49500,   3600, 'CHADT'),
        ttinfo( 45900,      0, 'CHAST'),
        ttinfo( 49500,   3600, 'CHADT'),
        ttinfo( 45900,      0, 'CHAST'),
        ttinfo( 49500,   3600, 'CHADT'),
        ttinfo( 45900,      0, 'CHAST'),
        ttinfo( 49500,   3600, 'CHADT'),
        ttinfo( 45900,      0, 'CHAST'),
        ttinfo( 49500,   3600, 'CHADT'),
        ttinfo( 45900,      0, 'CHAST'),
        ttinfo( 49500,   3600, 'CHADT'),
        ttinfo( 45900,      0, 'CHAST'),
        ttinfo( 49500,   3600, 'CHADT'),
        ttinfo( 45900,      0, 'CHAST'),
        ttinfo( 49500,   3600, 'CHADT'),
        ttinfo( 45900,      0, 'CHAST'),
        ttinfo( 49500,   3600, 'CHADT'),
        ttinfo( 45900,      0, 'CHAST'),
        ttinfo( 49500,   3600, 'CHADT'),
        ttinfo( 45900,      0, 'CHAST'),
        ttinfo( 49500,   3600, 'CHADT'),
        ttinfo( 45900,      0, 'CHAST'),
        ttinfo( 49500,   3600, 'CHADT'),
        ttinfo( 45900,      0, 'CHAST'),
        ttinfo( 49500,   3600, 'CHADT'),
        ttinfo( 45900,      0, 'CHAST'),
        ttinfo( 49500,   3600, 'CHADT'),
        ttinfo( 45900,      0, 'CHAST'),
        ttinfo( 49500,   3600, 'CHADT'),
        ttinfo( 45900,      0, 'CHAST'),
        ttinfo( 49500,   3600, 'CHADT'),
        ttinfo( 45900,      0, 'CHAST'),
        ttinfo( 49500,   3600, 'CHADT'),
        ttinfo( 45900,      0, 'CHAST'),
        ttinfo( 49500,   3600, 'CHADT'),
        ttinfo( 45900,      0, 'CHAST'),
        ttinfo( 49500,   3600, 'CHADT'),
        ttinfo( 45900,      0, 'CHAST'),
        ttinfo( 49500,   3600, 'CHADT'),
        ttinfo( 45900,      0, 'CHAST'),
        ttinfo( 49500,   3600, 'CHADT'),
        ttinfo( 45900,      0, 'CHAST'),
        ttinfo( 49500,   3600, 'CHADT'),
        ttinfo( 45900,      0, 'CHAST'),
        ttinfo( 49500,   3600, 'CHADT'),
        ttinfo( 45900,      0, 'CHAST'),
        ttinfo( 49500,   3600, 'CHADT'),
        ttinfo( 45900,      0, 'CHAST'),
        ttinfo( 49500,   3600, 'CHADT'),
        ttinfo( 45900,      0, 'CHAST'),
        ttinfo( 49500,   3600, 'CHADT'),
        ttinfo( 45900,      0, 'CHAST'),
        ttinfo( 49500,   3600, 'CHADT'),
        ttinfo( 45900,      0, 'CHAST'),
        ttinfo( 49500,   3600, 'CHADT'),
        ttinfo( 45900,      0, 'CHAST'),
        ttinfo( 49500,   3600, 'CHADT'),
        ttinfo( 45900,      0, 'CHAST'),
        ttinfo( 49500,   3600, 'CHADT'),
        ttinfo( 45900,      0, 'CHAST'),
        ttinfo( 49500,   3600, 'CHADT'),
        ttinfo( 45900,      0, 'CHAST'),
        ttinfo( 49500,   3600, 'CHADT'),
        ttinfo( 45900,      0, 'CHAST'),
        ttinfo( 49500,   3600, 'CHADT'),
        ttinfo( 45900,      0, 'CHAST'),
        ttinfo( 49500,   3600, 'CHADT'),
        ttinfo( 45900,      0, 'CHAST'),
        ttinfo( 49500,   3600, 'CHADT'),
        ttinfo( 45900,      0, 'CHAST'),
        ttinfo( 49500,   3600, 'CHADT'),
        ttinfo( 45900,      0, 'CHAST'),
        ttinfo( 49500,   3600, 'CHADT'),
        ttinfo( 45900,      0, 'CHAST'),
        ttinfo( 49500,   3600, 'CHADT'),
        ttinfo( 45900,      0, 'CHAST'),
        ttinfo( 49500,   3600, 'CHADT'),
        ttinfo( 45900,      0, 'CHAST'),
        ttinfo( 49500,   3600, 'CHADT'),
        ttinfo( 45900,      0, 'CHAST'),
        ttinfo( 49500,   3600, 'CHADT'),
        ttinfo( 45900,      0, 'CHAST'),
        ttinfo( 49500,   3600, 'CHADT'),
        ttinfo( 45900,      0, 'CHAST'),
        ttinfo( 49500,   3600, 'CHADT'),
        ttinfo( 45900,      0, 'CHAST'),
        ttinfo( 49500,   3600, 'CHADT'),
        ttinfo( 45900,      0, 'CHAST'),
        ttinfo( 49500,   3600, 'CHADT'),
        ttinfo( 45900,      0, 'CHAST'),
        ttinfo( 49500,   3600, 'CHADT'),
        ttinfo( 45900,      0, 'CHAST'),
        ttinfo( 49500,   3600, 'CHADT'),
        ttinfo( 45900,      0, 'CHAST'),
        ttinfo( 49500,   3600, 'CHADT'),
        ttinfo( 45900,      0, 'CHAST'),
        ttinfo( 49500,   3600, 'CHADT'),
        ttinfo( 45900,      0, 'CHAST'),
        ttinfo( 49500,   3600, 'CHADT'),
        ttinfo( 45900,      0, 'CHAST'),
        ttinfo( 49500,   3600, 'CHADT'),
        ]

NZ_minus_CHAT = NZ_minus_CHAT() # Singleton

