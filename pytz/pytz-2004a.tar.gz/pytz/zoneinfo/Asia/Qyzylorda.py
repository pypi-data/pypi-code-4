'''
tzinfo timezone information for Asia/Qyzylorda.

Generated from the Olson timezone database:
    ftp://elsie.nci.nih.gov/pub/tz*.tar.gz
'''

from pytz.tzinfo import DstTzInfo
from pytz.tzinfo import memorized_datetime as datetime
from pytz.tzinfo import memorized_ttinfo as ttinfo

class Qyzylorda(DstTzInfo):
    '''Asia/Qyzylorda timezone definition. See datetime.tzinfo for details'''

    _zone = 'Asia/Qyzylorda'

    _utc_transition_times = [
        datetime(   1,  1,  1,  0,  0,  0), #  15712     0 LMT
        datetime(1924,  5,  1, 19, 38,  8), #  14400     0 KIZT
        datetime(1930,  6, 20, 20,  0,  0), #  18000     0 KIZT
        datetime(1981,  3, 31, 19,  0,  0), #  21600  3600 KIZST
        datetime(1981,  9, 30, 18,  0,  0), #  21600     0 KIZT
        datetime(1982,  3, 31, 18,  0,  0), #  21600     0 KIZST
        datetime(1982,  9, 30, 18,  0,  0), #  18000     0 KIZT
        datetime(1983,  3, 31, 19,  0,  0), #  21600  3600 KIZST
        datetime(1983,  9, 30, 18,  0,  0), #  18000     0 KIZT
        datetime(1984,  3, 31, 19,  0,  0), #  21600  3600 KIZST
        datetime(1984,  9, 29, 21,  0,  0), #  18000     0 KIZT
        datetime(1985,  3, 30, 21,  0,  0), #  21600  3600 KIZST
        datetime(1985,  9, 28, 21,  0,  0), #  18000     0 KIZT
        datetime(1986,  3, 29, 21,  0,  0), #  21600  3600 KIZST
        datetime(1986,  9, 27, 21,  0,  0), #  18000     0 KIZT
        datetime(1987,  3, 28, 21,  0,  0), #  21600  3600 KIZST
        datetime(1987,  9, 26, 21,  0,  0), #  18000     0 KIZT
        datetime(1988,  3, 26, 21,  0,  0), #  21600  3600 KIZST
        datetime(1988,  9, 24, 21,  0,  0), #  18000     0 KIZT
        datetime(1989,  3, 25, 21,  0,  0), #  21600  3600 KIZST
        datetime(1989,  9, 23, 21,  0,  0), #  18000     0 KIZT
        datetime(1990,  3, 24, 21,  0,  0), #  21600  3600 KIZST
        datetime(1990,  9, 29, 21,  0,  0), #  18000     0 KIZT
        datetime(1990, 12, 31, 19,  0,  0), #  18000     0 KIZT
        datetime(1991, 12, 15, 19,  0,  0), #  18000     0 QYZT
        datetime(1992,  1, 18, 21,  0,  0), #  21600     0 QYZT
        datetime(1992,  3, 28, 17,  0,  0), #  25200  3600 QYZST
        datetime(1992,  9, 26, 16,  0,  0), #  21600     0 QYZT
        datetime(1993,  3, 27, 20,  0,  0), #  25200  3600 QYZST
        datetime(1993,  9, 25, 20,  0,  0), #  21600     0 QYZT
        datetime(1994,  3, 26, 20,  0,  0), #  25200  3600 QYZST
        datetime(1994,  9, 24, 20,  0,  0), #  21600     0 QYZT
        datetime(1995,  3, 25, 20,  0,  0), #  25200  3600 QYZST
        datetime(1995,  9, 23, 20,  0,  0), #  21600     0 QYZT
        datetime(1996,  3, 30, 20,  0,  0), #  25200  3600 QYZST
        datetime(1996, 10, 26, 20,  0,  0), #  21600     0 QYZT
        datetime(1997,  3, 29, 20,  0,  0), #  25200  3600 QYZST
        datetime(1997, 10, 25, 20,  0,  0), #  21600     0 QYZT
        datetime(1998,  3, 28, 20,  0,  0), #  25200  3600 QYZST
        datetime(1998, 10, 24, 20,  0,  0), #  21600     0 QYZT
        datetime(1999,  3, 27, 20,  0,  0), #  25200  3600 QYZST
        datetime(1999, 10, 30, 20,  0,  0), #  21600     0 QYZT
        datetime(2000,  3, 25, 20,  0,  0), #  25200  3600 QYZST
        datetime(2000, 10, 28, 20,  0,  0), #  21600     0 QYZT
        datetime(2001,  3, 24, 20,  0,  0), #  25200  3600 QYZST
        datetime(2001, 10, 27, 20,  0,  0), #  21600     0 QYZT
        datetime(2002,  3, 30, 20,  0,  0), #  25200  3600 QYZST
        datetime(2002, 10, 26, 20,  0,  0), #  21600     0 QYZT
        datetime(2003,  3, 29, 20,  0,  0), #  25200  3600 QYZST
        datetime(2003, 10, 25, 20,  0,  0), #  21600     0 QYZT
        datetime(2004,  3, 27, 20,  0,  0), #  25200  3600 QYZST
        datetime(2004, 10, 30, 20,  0,  0), #  21600     0 QYZT
        datetime(2005,  3, 26, 20,  0,  0), #  25200  3600 QYZST
        datetime(2005, 10, 29, 20,  0,  0), #  21600     0 QYZT
        datetime(2006,  3, 25, 20,  0,  0), #  25200  3600 QYZST
        datetime(2006, 10, 28, 20,  0,  0), #  21600     0 QYZT
        datetime(2007,  3, 24, 20,  0,  0), #  25200  3600 QYZST
        datetime(2007, 10, 27, 20,  0,  0), #  21600     0 QYZT
        datetime(2008,  3, 29, 20,  0,  0), #  25200  3600 QYZST
        datetime(2008, 10, 25, 20,  0,  0), #  21600     0 QYZT
        datetime(2009,  3, 28, 20,  0,  0), #  25200  3600 QYZST
        datetime(2009, 10, 24, 20,  0,  0), #  21600     0 QYZT
        datetime(2010,  3, 27, 20,  0,  0), #  25200  3600 QYZST
        datetime(2010, 10, 30, 20,  0,  0), #  21600     0 QYZT
        datetime(2011,  3, 26, 20,  0,  0), #  25200  3600 QYZST
        datetime(2011, 10, 29, 20,  0,  0), #  21600     0 QYZT
        datetime(2012,  3, 24, 20,  0,  0), #  25200  3600 QYZST
        datetime(2012, 10, 27, 20,  0,  0), #  21600     0 QYZT
        datetime(2013,  3, 30, 20,  0,  0), #  25200  3600 QYZST
        datetime(2013, 10, 26, 20,  0,  0), #  21600     0 QYZT
        datetime(2014,  3, 29, 20,  0,  0), #  25200  3600 QYZST
        datetime(2014, 10, 25, 20,  0,  0), #  21600     0 QYZT
        datetime(2015,  3, 28, 20,  0,  0), #  25200  3600 QYZST
        datetime(2015, 10, 24, 20,  0,  0), #  21600     0 QYZT
        datetime(2016,  3, 26, 20,  0,  0), #  25200  3600 QYZST
        datetime(2016, 10, 29, 20,  0,  0), #  21600     0 QYZT
        datetime(2017,  3, 25, 20,  0,  0), #  25200  3600 QYZST
        datetime(2017, 10, 28, 20,  0,  0), #  21600     0 QYZT
        datetime(2018,  3, 24, 20,  0,  0), #  25200  3600 QYZST
        datetime(2018, 10, 27, 20,  0,  0), #  21600     0 QYZT
        datetime(2019,  3, 30, 20,  0,  0), #  25200  3600 QYZST
        datetime(2019, 10, 26, 20,  0,  0), #  21600     0 QYZT
        datetime(2020,  3, 28, 20,  0,  0), #  25200  3600 QYZST
        datetime(2020, 10, 24, 20,  0,  0), #  21600     0 QYZT
        datetime(2021,  3, 27, 20,  0,  0), #  25200  3600 QYZST
        datetime(2021, 10, 30, 20,  0,  0), #  21600     0 QYZT
        datetime(2022,  3, 26, 20,  0,  0), #  25200  3600 QYZST
        datetime(2022, 10, 29, 20,  0,  0), #  21600     0 QYZT
        datetime(2023,  3, 25, 20,  0,  0), #  25200  3600 QYZST
        datetime(2023, 10, 28, 20,  0,  0), #  21600     0 QYZT
        datetime(2024,  3, 30, 20,  0,  0), #  25200  3600 QYZST
        datetime(2024, 10, 26, 20,  0,  0), #  21600     0 QYZT
        datetime(2025,  3, 29, 20,  0,  0), #  25200  3600 QYZST
        datetime(2025, 10, 25, 20,  0,  0), #  21600     0 QYZT
        datetime(2026,  3, 28, 20,  0,  0), #  25200  3600 QYZST
        datetime(2026, 10, 24, 20,  0,  0), #  21600     0 QYZT
        datetime(2027,  3, 27, 20,  0,  0), #  25200  3600 QYZST
        datetime(2027, 10, 30, 20,  0,  0), #  21600     0 QYZT
        datetime(2028,  3, 25, 20,  0,  0), #  25200  3600 QYZST
        datetime(2028, 10, 28, 20,  0,  0), #  21600     0 QYZT
        datetime(2029,  3, 24, 20,  0,  0), #  25200  3600 QYZST
        datetime(2029, 10, 27, 20,  0,  0), #  21600     0 QYZT
        datetime(2030,  3, 30, 20,  0,  0), #  25200  3600 QYZST
        datetime(2030, 10, 26, 20,  0,  0), #  21600     0 QYZT
        datetime(2031,  3, 29, 20,  0,  0), #  25200  3600 QYZST
        datetime(2031, 10, 25, 20,  0,  0), #  21600     0 QYZT
        datetime(2032,  3, 27, 20,  0,  0), #  25200  3600 QYZST
        datetime(2032, 10, 30, 20,  0,  0), #  21600     0 QYZT
        datetime(2033,  3, 26, 20,  0,  0), #  25200  3600 QYZST
        datetime(2033, 10, 29, 20,  0,  0), #  21600     0 QYZT
        datetime(2034,  3, 25, 20,  0,  0), #  25200  3600 QYZST
        datetime(2034, 10, 28, 20,  0,  0), #  21600     0 QYZT
        datetime(2035,  3, 24, 20,  0,  0), #  25200  3600 QYZST
        datetime(2035, 10, 27, 20,  0,  0), #  21600     0 QYZT
        datetime(2036,  3, 29, 20,  0,  0), #  25200  3600 QYZST
        datetime(2036, 10, 25, 20,  0,  0), #  21600     0 QYZT
        datetime(2037,  3, 28, 20,  0,  0), #  25200  3600 QYZST
        datetime(2037, 10, 24, 20,  0,  0), #  21600     0 QYZT
        ]

    _transition_info = [
        ttinfo( 15712,      0,  'LMT'),
        ttinfo( 14400,      0, 'KIZT'),
        ttinfo( 18000,      0, 'KIZT'),
        ttinfo( 21600,   3600, 'KIZST'),
        ttinfo( 21600,      0, 'KIZT'),
        ttinfo( 21600,      0, 'KIZST'),
        ttinfo( 18000,      0, 'KIZT'),
        ttinfo( 21600,   3600, 'KIZST'),
        ttinfo( 18000,      0, 'KIZT'),
        ttinfo( 21600,   3600, 'KIZST'),
        ttinfo( 18000,      0, 'KIZT'),
        ttinfo( 21600,   3600, 'KIZST'),
        ttinfo( 18000,      0, 'KIZT'),
        ttinfo( 21600,   3600, 'KIZST'),
        ttinfo( 18000,      0, 'KIZT'),
        ttinfo( 21600,   3600, 'KIZST'),
        ttinfo( 18000,      0, 'KIZT'),
        ttinfo( 21600,   3600, 'KIZST'),
        ttinfo( 18000,      0, 'KIZT'),
        ttinfo( 21600,   3600, 'KIZST'),
        ttinfo( 18000,      0, 'KIZT'),
        ttinfo( 21600,   3600, 'KIZST'),
        ttinfo( 18000,      0, 'KIZT'),
        ttinfo( 18000,      0, 'KIZT'),
        ttinfo( 18000,      0, 'QYZT'),
        ttinfo( 21600,      0, 'QYZT'),
        ttinfo( 25200,   3600, 'QYZST'),
        ttinfo( 21600,      0, 'QYZT'),
        ttinfo( 25200,   3600, 'QYZST'),
        ttinfo( 21600,      0, 'QYZT'),
        ttinfo( 25200,   3600, 'QYZST'),
        ttinfo( 21600,      0, 'QYZT'),
        ttinfo( 25200,   3600, 'QYZST'),
        ttinfo( 21600,      0, 'QYZT'),
        ttinfo( 25200,   3600, 'QYZST'),
        ttinfo( 21600,      0, 'QYZT'),
        ttinfo( 25200,   3600, 'QYZST'),
        ttinfo( 21600,      0, 'QYZT'),
        ttinfo( 25200,   3600, 'QYZST'),
        ttinfo( 21600,      0, 'QYZT'),
        ttinfo( 25200,   3600, 'QYZST'),
        ttinfo( 21600,      0, 'QYZT'),
        ttinfo( 25200,   3600, 'QYZST'),
        ttinfo( 21600,      0, 'QYZT'),
        ttinfo( 25200,   3600, 'QYZST'),
        ttinfo( 21600,      0, 'QYZT'),
        ttinfo( 25200,   3600, 'QYZST'),
        ttinfo( 21600,      0, 'QYZT'),
        ttinfo( 25200,   3600, 'QYZST'),
        ttinfo( 21600,      0, 'QYZT'),
        ttinfo( 25200,   3600, 'QYZST'),
        ttinfo( 21600,      0, 'QYZT'),
        ttinfo( 25200,   3600, 'QYZST'),
        ttinfo( 21600,      0, 'QYZT'),
        ttinfo( 25200,   3600, 'QYZST'),
        ttinfo( 21600,      0, 'QYZT'),
        ttinfo( 25200,   3600, 'QYZST'),
        ttinfo( 21600,      0, 'QYZT'),
        ttinfo( 25200,   3600, 'QYZST'),
        ttinfo( 21600,      0, 'QYZT'),
        ttinfo( 25200,   3600, 'QYZST'),
        ttinfo( 21600,      0, 'QYZT'),
        ttinfo( 25200,   3600, 'QYZST'),
        ttinfo( 21600,      0, 'QYZT'),
        ttinfo( 25200,   3600, 'QYZST'),
        ttinfo( 21600,      0, 'QYZT'),
        ttinfo( 25200,   3600, 'QYZST'),
        ttinfo( 21600,      0, 'QYZT'),
        ttinfo( 25200,   3600, 'QYZST'),
        ttinfo( 21600,      0, 'QYZT'),
        ttinfo( 25200,   3600, 'QYZST'),
        ttinfo( 21600,      0, 'QYZT'),
        ttinfo( 25200,   3600, 'QYZST'),
        ttinfo( 21600,      0, 'QYZT'),
        ttinfo( 25200,   3600, 'QYZST'),
        ttinfo( 21600,      0, 'QYZT'),
        ttinfo( 25200,   3600, 'QYZST'),
        ttinfo( 21600,      0, 'QYZT'),
        ttinfo( 25200,   3600, 'QYZST'),
        ttinfo( 21600,      0, 'QYZT'),
        ttinfo( 25200,   3600, 'QYZST'),
        ttinfo( 21600,      0, 'QYZT'),
        ttinfo( 25200,   3600, 'QYZST'),
        ttinfo( 21600,      0, 'QYZT'),
        ttinfo( 25200,   3600, 'QYZST'),
        ttinfo( 21600,      0, 'QYZT'),
        ttinfo( 25200,   3600, 'QYZST'),
        ttinfo( 21600,      0, 'QYZT'),
        ttinfo( 25200,   3600, 'QYZST'),
        ttinfo( 21600,      0, 'QYZT'),
        ttinfo( 25200,   3600, 'QYZST'),
        ttinfo( 21600,      0, 'QYZT'),
        ttinfo( 25200,   3600, 'QYZST'),
        ttinfo( 21600,      0, 'QYZT'),
        ttinfo( 25200,   3600, 'QYZST'),
        ttinfo( 21600,      0, 'QYZT'),
        ttinfo( 25200,   3600, 'QYZST'),
        ttinfo( 21600,      0, 'QYZT'),
        ttinfo( 25200,   3600, 'QYZST'),
        ttinfo( 21600,      0, 'QYZT'),
        ttinfo( 25200,   3600, 'QYZST'),
        ttinfo( 21600,      0, 'QYZT'),
        ttinfo( 25200,   3600, 'QYZST'),
        ttinfo( 21600,      0, 'QYZT'),
        ttinfo( 25200,   3600, 'QYZST'),
        ttinfo( 21600,      0, 'QYZT'),
        ttinfo( 25200,   3600, 'QYZST'),
        ttinfo( 21600,      0, 'QYZT'),
        ttinfo( 25200,   3600, 'QYZST'),
        ttinfo( 21600,      0, 'QYZT'),
        ttinfo( 25200,   3600, 'QYZST'),
        ttinfo( 21600,      0, 'QYZT'),
        ttinfo( 25200,   3600, 'QYZST'),
        ttinfo( 21600,      0, 'QYZT'),
        ttinfo( 25200,   3600, 'QYZST'),
        ttinfo( 21600,      0, 'QYZT'),
        ttinfo( 25200,   3600, 'QYZST'),
        ttinfo( 21600,      0, 'QYZT'),
        ]

Qyzylorda = Qyzylorda() # Singleton

