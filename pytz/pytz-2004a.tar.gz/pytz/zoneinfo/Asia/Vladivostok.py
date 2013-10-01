'''
tzinfo timezone information for Asia/Vladivostok.

Generated from the Olson timezone database:
    ftp://elsie.nci.nih.gov/pub/tz*.tar.gz
'''

from pytz.tzinfo import DstTzInfo
from pytz.tzinfo import memorized_datetime as datetime
from pytz.tzinfo import memorized_ttinfo as ttinfo

class Vladivostok(DstTzInfo):
    '''Asia/Vladivostok timezone definition. See datetime.tzinfo for details'''

    _zone = 'Asia/Vladivostok'

    _utc_transition_times = [
        datetime(   1,  1,  1,  0,  0,  0), #  31664     0 LMT
        datetime(1922, 11, 14, 15, 12, 16), #  32400     0 VLAT
        datetime(1930,  6, 20, 15,  0,  0), #  36000     0 VLAT
        datetime(1981,  3, 31, 14,  0,  0), #  39600  3600 VLAST
        datetime(1981,  9, 30, 13,  0,  0), #  36000     0 VLAT
        datetime(1982,  3, 31, 14,  0,  0), #  39600  3600 VLAST
        datetime(1982,  9, 30, 13,  0,  0), #  36000     0 VLAT
        datetime(1983,  3, 31, 14,  0,  0), #  39600  3600 VLAST
        datetime(1983,  9, 30, 13,  0,  0), #  36000     0 VLAT
        datetime(1984,  3, 31, 14,  0,  0), #  39600  3600 VLAST
        datetime(1984,  9, 29, 16,  0,  0), #  36000     0 VLAT
        datetime(1985,  3, 30, 16,  0,  0), #  39600  3600 VLAST
        datetime(1985,  9, 28, 16,  0,  0), #  36000     0 VLAT
        datetime(1986,  3, 29, 16,  0,  0), #  39600  3600 VLAST
        datetime(1986,  9, 27, 16,  0,  0), #  36000     0 VLAT
        datetime(1987,  3, 28, 16,  0,  0), #  39600  3600 VLAST
        datetime(1987,  9, 26, 16,  0,  0), #  36000     0 VLAT
        datetime(1988,  3, 26, 16,  0,  0), #  39600  3600 VLAST
        datetime(1988,  9, 24, 16,  0,  0), #  36000     0 VLAT
        datetime(1989,  3, 25, 16,  0,  0), #  39600  3600 VLAST
        datetime(1989,  9, 23, 16,  0,  0), #  36000     0 VLAT
        datetime(1990,  3, 24, 16,  0,  0), #  39600  3600 VLAST
        datetime(1990,  9, 29, 16,  0,  0), #  36000     0 VLAT
        datetime(1991,  3, 30, 16,  0,  0), #  36000     0 VLASST
        datetime(1991,  9, 28, 17,  0,  0), #  32400     0 VLAST
        datetime(1992,  1, 18, 17,  0,  0), #  36000     0 VLAT
        datetime(1992,  3, 28, 13,  0,  0), #  39600  3600 VLAST
        datetime(1992,  9, 26, 12,  0,  0), #  36000     0 VLAT
        datetime(1993,  3, 27, 16,  0,  0), #  39600  3600 VLAST
        datetime(1993,  9, 25, 16,  0,  0), #  36000     0 VLAT
        datetime(1994,  3, 26, 16,  0,  0), #  39600  3600 VLAST
        datetime(1994,  9, 24, 16,  0,  0), #  36000     0 VLAT
        datetime(1995,  3, 25, 16,  0,  0), #  39600  3600 VLAST
        datetime(1995,  9, 23, 16,  0,  0), #  36000     0 VLAT
        datetime(1996,  3, 30, 16,  0,  0), #  39600  3600 VLAST
        datetime(1996, 10, 26, 16,  0,  0), #  36000     0 VLAT
        datetime(1997,  3, 29, 16,  0,  0), #  39600  3600 VLAST
        datetime(1997, 10, 25, 16,  0,  0), #  36000     0 VLAT
        datetime(1998,  3, 28, 16,  0,  0), #  39600  3600 VLAST
        datetime(1998, 10, 24, 16,  0,  0), #  36000     0 VLAT
        datetime(1999,  3, 27, 16,  0,  0), #  39600  3600 VLAST
        datetime(1999, 10, 30, 16,  0,  0), #  36000     0 VLAT
        datetime(2000,  3, 25, 16,  0,  0), #  39600  3600 VLAST
        datetime(2000, 10, 28, 16,  0,  0), #  36000     0 VLAT
        datetime(2001,  3, 24, 16,  0,  0), #  39600  3600 VLAST
        datetime(2001, 10, 27, 16,  0,  0), #  36000     0 VLAT
        datetime(2002,  3, 30, 16,  0,  0), #  39600  3600 VLAST
        datetime(2002, 10, 26, 16,  0,  0), #  36000     0 VLAT
        datetime(2003,  3, 29, 16,  0,  0), #  39600  3600 VLAST
        datetime(2003, 10, 25, 16,  0,  0), #  36000     0 VLAT
        datetime(2004,  3, 27, 16,  0,  0), #  39600  3600 VLAST
        datetime(2004, 10, 30, 16,  0,  0), #  36000     0 VLAT
        datetime(2005,  3, 26, 16,  0,  0), #  39600  3600 VLAST
        datetime(2005, 10, 29, 16,  0,  0), #  36000     0 VLAT
        datetime(2006,  3, 25, 16,  0,  0), #  39600  3600 VLAST
        datetime(2006, 10, 28, 16,  0,  0), #  36000     0 VLAT
        datetime(2007,  3, 24, 16,  0,  0), #  39600  3600 VLAST
        datetime(2007, 10, 27, 16,  0,  0), #  36000     0 VLAT
        datetime(2008,  3, 29, 16,  0,  0), #  39600  3600 VLAST
        datetime(2008, 10, 25, 16,  0,  0), #  36000     0 VLAT
        datetime(2009,  3, 28, 16,  0,  0), #  39600  3600 VLAST
        datetime(2009, 10, 24, 16,  0,  0), #  36000     0 VLAT
        datetime(2010,  3, 27, 16,  0,  0), #  39600  3600 VLAST
        datetime(2010, 10, 30, 16,  0,  0), #  36000     0 VLAT
        datetime(2011,  3, 26, 16,  0,  0), #  39600  3600 VLAST
        datetime(2011, 10, 29, 16,  0,  0), #  36000     0 VLAT
        datetime(2012,  3, 24, 16,  0,  0), #  39600  3600 VLAST
        datetime(2012, 10, 27, 16,  0,  0), #  36000     0 VLAT
        datetime(2013,  3, 30, 16,  0,  0), #  39600  3600 VLAST
        datetime(2013, 10, 26, 16,  0,  0), #  36000     0 VLAT
        datetime(2014,  3, 29, 16,  0,  0), #  39600  3600 VLAST
        datetime(2014, 10, 25, 16,  0,  0), #  36000     0 VLAT
        datetime(2015,  3, 28, 16,  0,  0), #  39600  3600 VLAST
        datetime(2015, 10, 24, 16,  0,  0), #  36000     0 VLAT
        datetime(2016,  3, 26, 16,  0,  0), #  39600  3600 VLAST
        datetime(2016, 10, 29, 16,  0,  0), #  36000     0 VLAT
        datetime(2017,  3, 25, 16,  0,  0), #  39600  3600 VLAST
        datetime(2017, 10, 28, 16,  0,  0), #  36000     0 VLAT
        datetime(2018,  3, 24, 16,  0,  0), #  39600  3600 VLAST
        datetime(2018, 10, 27, 16,  0,  0), #  36000     0 VLAT
        datetime(2019,  3, 30, 16,  0,  0), #  39600  3600 VLAST
        datetime(2019, 10, 26, 16,  0,  0), #  36000     0 VLAT
        datetime(2020,  3, 28, 16,  0,  0), #  39600  3600 VLAST
        datetime(2020, 10, 24, 16,  0,  0), #  36000     0 VLAT
        datetime(2021,  3, 27, 16,  0,  0), #  39600  3600 VLAST
        datetime(2021, 10, 30, 16,  0,  0), #  36000     0 VLAT
        datetime(2022,  3, 26, 16,  0,  0), #  39600  3600 VLAST
        datetime(2022, 10, 29, 16,  0,  0), #  36000     0 VLAT
        datetime(2023,  3, 25, 16,  0,  0), #  39600  3600 VLAST
        datetime(2023, 10, 28, 16,  0,  0), #  36000     0 VLAT
        datetime(2024,  3, 30, 16,  0,  0), #  39600  3600 VLAST
        datetime(2024, 10, 26, 16,  0,  0), #  36000     0 VLAT
        datetime(2025,  3, 29, 16,  0,  0), #  39600  3600 VLAST
        datetime(2025, 10, 25, 16,  0,  0), #  36000     0 VLAT
        datetime(2026,  3, 28, 16,  0,  0), #  39600  3600 VLAST
        datetime(2026, 10, 24, 16,  0,  0), #  36000     0 VLAT
        datetime(2027,  3, 27, 16,  0,  0), #  39600  3600 VLAST
        datetime(2027, 10, 30, 16,  0,  0), #  36000     0 VLAT
        datetime(2028,  3, 25, 16,  0,  0), #  39600  3600 VLAST
        datetime(2028, 10, 28, 16,  0,  0), #  36000     0 VLAT
        datetime(2029,  3, 24, 16,  0,  0), #  39600  3600 VLAST
        datetime(2029, 10, 27, 16,  0,  0), #  36000     0 VLAT
        datetime(2030,  3, 30, 16,  0,  0), #  39600  3600 VLAST
        datetime(2030, 10, 26, 16,  0,  0), #  36000     0 VLAT
        datetime(2031,  3, 29, 16,  0,  0), #  39600  3600 VLAST
        datetime(2031, 10, 25, 16,  0,  0), #  36000     0 VLAT
        datetime(2032,  3, 27, 16,  0,  0), #  39600  3600 VLAST
        datetime(2032, 10, 30, 16,  0,  0), #  36000     0 VLAT
        datetime(2033,  3, 26, 16,  0,  0), #  39600  3600 VLAST
        datetime(2033, 10, 29, 16,  0,  0), #  36000     0 VLAT
        datetime(2034,  3, 25, 16,  0,  0), #  39600  3600 VLAST
        datetime(2034, 10, 28, 16,  0,  0), #  36000     0 VLAT
        datetime(2035,  3, 24, 16,  0,  0), #  39600  3600 VLAST
        datetime(2035, 10, 27, 16,  0,  0), #  36000     0 VLAT
        datetime(2036,  3, 29, 16,  0,  0), #  39600  3600 VLAST
        datetime(2036, 10, 25, 16,  0,  0), #  36000     0 VLAT
        datetime(2037,  3, 28, 16,  0,  0), #  39600  3600 VLAST
        datetime(2037, 10, 24, 16,  0,  0), #  36000     0 VLAT
        ]

    _transition_info = [
        ttinfo( 31664,      0,  'LMT'),
        ttinfo( 32400,      0, 'VLAT'),
        ttinfo( 36000,      0, 'VLAT'),
        ttinfo( 39600,   3600, 'VLAST'),
        ttinfo( 36000,      0, 'VLAT'),
        ttinfo( 39600,   3600, 'VLAST'),
        ttinfo( 36000,      0, 'VLAT'),
        ttinfo( 39600,   3600, 'VLAST'),
        ttinfo( 36000,      0, 'VLAT'),
        ttinfo( 39600,   3600, 'VLAST'),
        ttinfo( 36000,      0, 'VLAT'),
        ttinfo( 39600,   3600, 'VLAST'),
        ttinfo( 36000,      0, 'VLAT'),
        ttinfo( 39600,   3600, 'VLAST'),
        ttinfo( 36000,      0, 'VLAT'),
        ttinfo( 39600,   3600, 'VLAST'),
        ttinfo( 36000,      0, 'VLAT'),
        ttinfo( 39600,   3600, 'VLAST'),
        ttinfo( 36000,      0, 'VLAT'),
        ttinfo( 39600,   3600, 'VLAST'),
        ttinfo( 36000,      0, 'VLAT'),
        ttinfo( 39600,   3600, 'VLAST'),
        ttinfo( 36000,      0, 'VLAT'),
        ttinfo( 36000,      0, 'VLASST'),
        ttinfo( 32400,      0, 'VLAST'),
        ttinfo( 36000,      0, 'VLAT'),
        ttinfo( 39600,   3600, 'VLAST'),
        ttinfo( 36000,      0, 'VLAT'),
        ttinfo( 39600,   3600, 'VLAST'),
        ttinfo( 36000,      0, 'VLAT'),
        ttinfo( 39600,   3600, 'VLAST'),
        ttinfo( 36000,      0, 'VLAT'),
        ttinfo( 39600,   3600, 'VLAST'),
        ttinfo( 36000,      0, 'VLAT'),
        ttinfo( 39600,   3600, 'VLAST'),
        ttinfo( 36000,      0, 'VLAT'),
        ttinfo( 39600,   3600, 'VLAST'),
        ttinfo( 36000,      0, 'VLAT'),
        ttinfo( 39600,   3600, 'VLAST'),
        ttinfo( 36000,      0, 'VLAT'),
        ttinfo( 39600,   3600, 'VLAST'),
        ttinfo( 36000,      0, 'VLAT'),
        ttinfo( 39600,   3600, 'VLAST'),
        ttinfo( 36000,      0, 'VLAT'),
        ttinfo( 39600,   3600, 'VLAST'),
        ttinfo( 36000,      0, 'VLAT'),
        ttinfo( 39600,   3600, 'VLAST'),
        ttinfo( 36000,      0, 'VLAT'),
        ttinfo( 39600,   3600, 'VLAST'),
        ttinfo( 36000,      0, 'VLAT'),
        ttinfo( 39600,   3600, 'VLAST'),
        ttinfo( 36000,      0, 'VLAT'),
        ttinfo( 39600,   3600, 'VLAST'),
        ttinfo( 36000,      0, 'VLAT'),
        ttinfo( 39600,   3600, 'VLAST'),
        ttinfo( 36000,      0, 'VLAT'),
        ttinfo( 39600,   3600, 'VLAST'),
        ttinfo( 36000,      0, 'VLAT'),
        ttinfo( 39600,   3600, 'VLAST'),
        ttinfo( 36000,      0, 'VLAT'),
        ttinfo( 39600,   3600, 'VLAST'),
        ttinfo( 36000,      0, 'VLAT'),
        ttinfo( 39600,   3600, 'VLAST'),
        ttinfo( 36000,      0, 'VLAT'),
        ttinfo( 39600,   3600, 'VLAST'),
        ttinfo( 36000,      0, 'VLAT'),
        ttinfo( 39600,   3600, 'VLAST'),
        ttinfo( 36000,      0, 'VLAT'),
        ttinfo( 39600,   3600, 'VLAST'),
        ttinfo( 36000,      0, 'VLAT'),
        ttinfo( 39600,   3600, 'VLAST'),
        ttinfo( 36000,      0, 'VLAT'),
        ttinfo( 39600,   3600, 'VLAST'),
        ttinfo( 36000,      0, 'VLAT'),
        ttinfo( 39600,   3600, 'VLAST'),
        ttinfo( 36000,      0, 'VLAT'),
        ttinfo( 39600,   3600, 'VLAST'),
        ttinfo( 36000,      0, 'VLAT'),
        ttinfo( 39600,   3600, 'VLAST'),
        ttinfo( 36000,      0, 'VLAT'),
        ttinfo( 39600,   3600, 'VLAST'),
        ttinfo( 36000,      0, 'VLAT'),
        ttinfo( 39600,   3600, 'VLAST'),
        ttinfo( 36000,      0, 'VLAT'),
        ttinfo( 39600,   3600, 'VLAST'),
        ttinfo( 36000,      0, 'VLAT'),
        ttinfo( 39600,   3600, 'VLAST'),
        ttinfo( 36000,      0, 'VLAT'),
        ttinfo( 39600,   3600, 'VLAST'),
        ttinfo( 36000,      0, 'VLAT'),
        ttinfo( 39600,   3600, 'VLAST'),
        ttinfo( 36000,      0, 'VLAT'),
        ttinfo( 39600,   3600, 'VLAST'),
        ttinfo( 36000,      0, 'VLAT'),
        ttinfo( 39600,   3600, 'VLAST'),
        ttinfo( 36000,      0, 'VLAT'),
        ttinfo( 39600,   3600, 'VLAST'),
        ttinfo( 36000,      0, 'VLAT'),
        ttinfo( 39600,   3600, 'VLAST'),
        ttinfo( 36000,      0, 'VLAT'),
        ttinfo( 39600,   3600, 'VLAST'),
        ttinfo( 36000,      0, 'VLAT'),
        ttinfo( 39600,   3600, 'VLAST'),
        ttinfo( 36000,      0, 'VLAT'),
        ttinfo( 39600,   3600, 'VLAST'),
        ttinfo( 36000,      0, 'VLAT'),
        ttinfo( 39600,   3600, 'VLAST'),
        ttinfo( 36000,      0, 'VLAT'),
        ttinfo( 39600,   3600, 'VLAST'),
        ttinfo( 36000,      0, 'VLAT'),
        ttinfo( 39600,   3600, 'VLAST'),
        ttinfo( 36000,      0, 'VLAT'),
        ttinfo( 39600,   3600, 'VLAST'),
        ttinfo( 36000,      0, 'VLAT'),
        ttinfo( 39600,   3600, 'VLAST'),
        ttinfo( 36000,      0, 'VLAT'),
        ttinfo( 39600,   3600, 'VLAST'),
        ttinfo( 36000,      0, 'VLAT'),
        ]

Vladivostok = Vladivostok() # Singleton

