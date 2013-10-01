'''
tzinfo timezone information for Asia/Yerevan.

Generated from the Olson timezone database:
    ftp://elsie.nci.nih.gov/pub/tz*.tar.gz
'''

from pytz.tzinfo import DstTzInfo
from pytz.tzinfo import memorized_datetime as datetime
from pytz.tzinfo import memorized_ttinfo as ttinfo

class Yerevan(DstTzInfo):
    '''Asia/Yerevan timezone definition. See datetime.tzinfo for details'''

    _zone = 'Asia/Yerevan'

    _utc_transition_times = [
        datetime(   1,  1,  1,  0,  0,  0), #  10680     0 LMT
        datetime(1924,  5,  1, 21,  2,  0), #  10800     0 YERT
        datetime(1957,  2, 28, 21,  0,  0), #  14400     0 YERT
        datetime(1981,  3, 31, 20,  0,  0), #  18000  3600 YERST
        datetime(1981,  9, 30, 19,  0,  0), #  14400     0 YERT
        datetime(1982,  3, 31, 20,  0,  0), #  18000  3600 YERST
        datetime(1982,  9, 30, 19,  0,  0), #  14400     0 YERT
        datetime(1983,  3, 31, 20,  0,  0), #  18000  3600 YERST
        datetime(1983,  9, 30, 19,  0,  0), #  14400     0 YERT
        datetime(1984,  3, 31, 20,  0,  0), #  18000  3600 YERST
        datetime(1984,  9, 29, 22,  0,  0), #  14400     0 YERT
        datetime(1985,  3, 30, 22,  0,  0), #  18000  3600 YERST
        datetime(1985,  9, 28, 22,  0,  0), #  14400     0 YERT
        datetime(1986,  3, 29, 22,  0,  0), #  18000  3600 YERST
        datetime(1986,  9, 27, 22,  0,  0), #  14400     0 YERT
        datetime(1987,  3, 28, 22,  0,  0), #  18000  3600 YERST
        datetime(1987,  9, 26, 22,  0,  0), #  14400     0 YERT
        datetime(1988,  3, 26, 22,  0,  0), #  18000  3600 YERST
        datetime(1988,  9, 24, 22,  0,  0), #  14400     0 YERT
        datetime(1989,  3, 25, 22,  0,  0), #  18000  3600 YERST
        datetime(1989,  9, 23, 22,  0,  0), #  14400     0 YERT
        datetime(1990,  3, 24, 22,  0,  0), #  18000  3600 YERST
        datetime(1990,  9, 29, 22,  0,  0), #  14400     0 YERT
        datetime(1991,  3, 30, 22,  0,  0), #  14400     0 YERST
        datetime(1991,  9, 22, 20,  0,  0), #  14400     0 AMST
        datetime(1991,  9, 28, 23,  0,  0), #  10800     0 AMT
        datetime(1992,  3, 28, 20,  0,  0), #  14400  3600 AMST
        datetime(1992,  9, 26, 19,  0,  0), #  10800     0 AMT
        datetime(1993,  3, 27, 23,  0,  0), #  14400  3600 AMST
        datetime(1993,  9, 25, 23,  0,  0), #  10800     0 AMT
        datetime(1994,  3, 26, 23,  0,  0), #  14400  3600 AMST
        datetime(1994,  9, 24, 23,  0,  0), #  10800     0 AMT
        datetime(1995,  3, 25, 23,  0,  0), #  14400  3600 AMST
        datetime(1995,  9, 23, 23,  0,  0), #  14400     0 AMT
        datetime(1996, 12, 31, 20,  0,  0), #  14400     0 AMT
        datetime(1997,  3, 29, 22,  0,  0), #  18000  3600 AMST
        datetime(1997, 10, 25, 22,  0,  0), #  14400     0 AMT
        datetime(1998,  3, 28, 22,  0,  0), #  18000  3600 AMST
        datetime(1998, 10, 24, 22,  0,  0), #  14400     0 AMT
        datetime(1999,  3, 27, 22,  0,  0), #  18000  3600 AMST
        datetime(1999, 10, 30, 22,  0,  0), #  14400     0 AMT
        datetime(2000,  3, 25, 22,  0,  0), #  18000  3600 AMST
        datetime(2000, 10, 28, 22,  0,  0), #  14400     0 AMT
        datetime(2001,  3, 24, 22,  0,  0), #  18000  3600 AMST
        datetime(2001, 10, 27, 22,  0,  0), #  14400     0 AMT
        datetime(2002,  3, 30, 22,  0,  0), #  18000  3600 AMST
        datetime(2002, 10, 26, 22,  0,  0), #  14400     0 AMT
        datetime(2003,  3, 29, 22,  0,  0), #  18000  3600 AMST
        datetime(2003, 10, 25, 22,  0,  0), #  14400     0 AMT
        datetime(2004,  3, 27, 22,  0,  0), #  18000  3600 AMST
        datetime(2004, 10, 30, 22,  0,  0), #  14400     0 AMT
        datetime(2005,  3, 26, 22,  0,  0), #  18000  3600 AMST
        datetime(2005, 10, 29, 22,  0,  0), #  14400     0 AMT
        datetime(2006,  3, 25, 22,  0,  0), #  18000  3600 AMST
        datetime(2006, 10, 28, 22,  0,  0), #  14400     0 AMT
        datetime(2007,  3, 24, 22,  0,  0), #  18000  3600 AMST
        datetime(2007, 10, 27, 22,  0,  0), #  14400     0 AMT
        datetime(2008,  3, 29, 22,  0,  0), #  18000  3600 AMST
        datetime(2008, 10, 25, 22,  0,  0), #  14400     0 AMT
        datetime(2009,  3, 28, 22,  0,  0), #  18000  3600 AMST
        datetime(2009, 10, 24, 22,  0,  0), #  14400     0 AMT
        datetime(2010,  3, 27, 22,  0,  0), #  18000  3600 AMST
        datetime(2010, 10, 30, 22,  0,  0), #  14400     0 AMT
        datetime(2011,  3, 26, 22,  0,  0), #  18000  3600 AMST
        datetime(2011, 10, 29, 22,  0,  0), #  14400     0 AMT
        datetime(2012,  3, 24, 22,  0,  0), #  18000  3600 AMST
        datetime(2012, 10, 27, 22,  0,  0), #  14400     0 AMT
        datetime(2013,  3, 30, 22,  0,  0), #  18000  3600 AMST
        datetime(2013, 10, 26, 22,  0,  0), #  14400     0 AMT
        datetime(2014,  3, 29, 22,  0,  0), #  18000  3600 AMST
        datetime(2014, 10, 25, 22,  0,  0), #  14400     0 AMT
        datetime(2015,  3, 28, 22,  0,  0), #  18000  3600 AMST
        datetime(2015, 10, 24, 22,  0,  0), #  14400     0 AMT
        datetime(2016,  3, 26, 22,  0,  0), #  18000  3600 AMST
        datetime(2016, 10, 29, 22,  0,  0), #  14400     0 AMT
        datetime(2017,  3, 25, 22,  0,  0), #  18000  3600 AMST
        datetime(2017, 10, 28, 22,  0,  0), #  14400     0 AMT
        datetime(2018,  3, 24, 22,  0,  0), #  18000  3600 AMST
        datetime(2018, 10, 27, 22,  0,  0), #  14400     0 AMT
        datetime(2019,  3, 30, 22,  0,  0), #  18000  3600 AMST
        datetime(2019, 10, 26, 22,  0,  0), #  14400     0 AMT
        datetime(2020,  3, 28, 22,  0,  0), #  18000  3600 AMST
        datetime(2020, 10, 24, 22,  0,  0), #  14400     0 AMT
        datetime(2021,  3, 27, 22,  0,  0), #  18000  3600 AMST
        datetime(2021, 10, 30, 22,  0,  0), #  14400     0 AMT
        datetime(2022,  3, 26, 22,  0,  0), #  18000  3600 AMST
        datetime(2022, 10, 29, 22,  0,  0), #  14400     0 AMT
        datetime(2023,  3, 25, 22,  0,  0), #  18000  3600 AMST
        datetime(2023, 10, 28, 22,  0,  0), #  14400     0 AMT
        datetime(2024,  3, 30, 22,  0,  0), #  18000  3600 AMST
        datetime(2024, 10, 26, 22,  0,  0), #  14400     0 AMT
        datetime(2025,  3, 29, 22,  0,  0), #  18000  3600 AMST
        datetime(2025, 10, 25, 22,  0,  0), #  14400     0 AMT
        datetime(2026,  3, 28, 22,  0,  0), #  18000  3600 AMST
        datetime(2026, 10, 24, 22,  0,  0), #  14400     0 AMT
        datetime(2027,  3, 27, 22,  0,  0), #  18000  3600 AMST
        datetime(2027, 10, 30, 22,  0,  0), #  14400     0 AMT
        datetime(2028,  3, 25, 22,  0,  0), #  18000  3600 AMST
        datetime(2028, 10, 28, 22,  0,  0), #  14400     0 AMT
        datetime(2029,  3, 24, 22,  0,  0), #  18000  3600 AMST
        datetime(2029, 10, 27, 22,  0,  0), #  14400     0 AMT
        datetime(2030,  3, 30, 22,  0,  0), #  18000  3600 AMST
        datetime(2030, 10, 26, 22,  0,  0), #  14400     0 AMT
        datetime(2031,  3, 29, 22,  0,  0), #  18000  3600 AMST
        datetime(2031, 10, 25, 22,  0,  0), #  14400     0 AMT
        datetime(2032,  3, 27, 22,  0,  0), #  18000  3600 AMST
        datetime(2032, 10, 30, 22,  0,  0), #  14400     0 AMT
        datetime(2033,  3, 26, 22,  0,  0), #  18000  3600 AMST
        datetime(2033, 10, 29, 22,  0,  0), #  14400     0 AMT
        datetime(2034,  3, 25, 22,  0,  0), #  18000  3600 AMST
        datetime(2034, 10, 28, 22,  0,  0), #  14400     0 AMT
        datetime(2035,  3, 24, 22,  0,  0), #  18000  3600 AMST
        datetime(2035, 10, 27, 22,  0,  0), #  14400     0 AMT
        datetime(2036,  3, 29, 22,  0,  0), #  18000  3600 AMST
        datetime(2036, 10, 25, 22,  0,  0), #  14400     0 AMT
        datetime(2037,  3, 28, 22,  0,  0), #  18000  3600 AMST
        datetime(2037, 10, 24, 22,  0,  0), #  14400     0 AMT
        ]

    _transition_info = [
        ttinfo( 10680,      0,  'LMT'),
        ttinfo( 10800,      0, 'YERT'),
        ttinfo( 14400,      0, 'YERT'),
        ttinfo( 18000,   3600, 'YERST'),
        ttinfo( 14400,      0, 'YERT'),
        ttinfo( 18000,   3600, 'YERST'),
        ttinfo( 14400,      0, 'YERT'),
        ttinfo( 18000,   3600, 'YERST'),
        ttinfo( 14400,      0, 'YERT'),
        ttinfo( 18000,   3600, 'YERST'),
        ttinfo( 14400,      0, 'YERT'),
        ttinfo( 18000,   3600, 'YERST'),
        ttinfo( 14400,      0, 'YERT'),
        ttinfo( 18000,   3600, 'YERST'),
        ttinfo( 14400,      0, 'YERT'),
        ttinfo( 18000,   3600, 'YERST'),
        ttinfo( 14400,      0, 'YERT'),
        ttinfo( 18000,   3600, 'YERST'),
        ttinfo( 14400,      0, 'YERT'),
        ttinfo( 18000,   3600, 'YERST'),
        ttinfo( 14400,      0, 'YERT'),
        ttinfo( 18000,   3600, 'YERST'),
        ttinfo( 14400,      0, 'YERT'),
        ttinfo( 14400,      0, 'YERST'),
        ttinfo( 14400,      0, 'AMST'),
        ttinfo( 10800,      0,  'AMT'),
        ttinfo( 14400,   3600, 'AMST'),
        ttinfo( 10800,      0,  'AMT'),
        ttinfo( 14400,   3600, 'AMST'),
        ttinfo( 10800,      0,  'AMT'),
        ttinfo( 14400,   3600, 'AMST'),
        ttinfo( 10800,      0,  'AMT'),
        ttinfo( 14400,   3600, 'AMST'),
        ttinfo( 14400,      0,  'AMT'),
        ttinfo( 14400,      0,  'AMT'),
        ttinfo( 18000,   3600, 'AMST'),
        ttinfo( 14400,      0,  'AMT'),
        ttinfo( 18000,   3600, 'AMST'),
        ttinfo( 14400,      0,  'AMT'),
        ttinfo( 18000,   3600, 'AMST'),
        ttinfo( 14400,      0,  'AMT'),
        ttinfo( 18000,   3600, 'AMST'),
        ttinfo( 14400,      0,  'AMT'),
        ttinfo( 18000,   3600, 'AMST'),
        ttinfo( 14400,      0,  'AMT'),
        ttinfo( 18000,   3600, 'AMST'),
        ttinfo( 14400,      0,  'AMT'),
        ttinfo( 18000,   3600, 'AMST'),
        ttinfo( 14400,      0,  'AMT'),
        ttinfo( 18000,   3600, 'AMST'),
        ttinfo( 14400,      0,  'AMT'),
        ttinfo( 18000,   3600, 'AMST'),
        ttinfo( 14400,      0,  'AMT'),
        ttinfo( 18000,   3600, 'AMST'),
        ttinfo( 14400,      0,  'AMT'),
        ttinfo( 18000,   3600, 'AMST'),
        ttinfo( 14400,      0,  'AMT'),
        ttinfo( 18000,   3600, 'AMST'),
        ttinfo( 14400,      0,  'AMT'),
        ttinfo( 18000,   3600, 'AMST'),
        ttinfo( 14400,      0,  'AMT'),
        ttinfo( 18000,   3600, 'AMST'),
        ttinfo( 14400,      0,  'AMT'),
        ttinfo( 18000,   3600, 'AMST'),
        ttinfo( 14400,      0,  'AMT'),
        ttinfo( 18000,   3600, 'AMST'),
        ttinfo( 14400,      0,  'AMT'),
        ttinfo( 18000,   3600, 'AMST'),
        ttinfo( 14400,      0,  'AMT'),
        ttinfo( 18000,   3600, 'AMST'),
        ttinfo( 14400,      0,  'AMT'),
        ttinfo( 18000,   3600, 'AMST'),
        ttinfo( 14400,      0,  'AMT'),
        ttinfo( 18000,   3600, 'AMST'),
        ttinfo( 14400,      0,  'AMT'),
        ttinfo( 18000,   3600, 'AMST'),
        ttinfo( 14400,      0,  'AMT'),
        ttinfo( 18000,   3600, 'AMST'),
        ttinfo( 14400,      0,  'AMT'),
        ttinfo( 18000,   3600, 'AMST'),
        ttinfo( 14400,      0,  'AMT'),
        ttinfo( 18000,   3600, 'AMST'),
        ttinfo( 14400,      0,  'AMT'),
        ttinfo( 18000,   3600, 'AMST'),
        ttinfo( 14400,      0,  'AMT'),
        ttinfo( 18000,   3600, 'AMST'),
        ttinfo( 14400,      0,  'AMT'),
        ttinfo( 18000,   3600, 'AMST'),
        ttinfo( 14400,      0,  'AMT'),
        ttinfo( 18000,   3600, 'AMST'),
        ttinfo( 14400,      0,  'AMT'),
        ttinfo( 18000,   3600, 'AMST'),
        ttinfo( 14400,      0,  'AMT'),
        ttinfo( 18000,   3600, 'AMST'),
        ttinfo( 14400,      0,  'AMT'),
        ttinfo( 18000,   3600, 'AMST'),
        ttinfo( 14400,      0,  'AMT'),
        ttinfo( 18000,   3600, 'AMST'),
        ttinfo( 14400,      0,  'AMT'),
        ttinfo( 18000,   3600, 'AMST'),
        ttinfo( 14400,      0,  'AMT'),
        ttinfo( 18000,   3600, 'AMST'),
        ttinfo( 14400,      0,  'AMT'),
        ttinfo( 18000,   3600, 'AMST'),
        ttinfo( 14400,      0,  'AMT'),
        ttinfo( 18000,   3600, 'AMST'),
        ttinfo( 14400,      0,  'AMT'),
        ttinfo( 18000,   3600, 'AMST'),
        ttinfo( 14400,      0,  'AMT'),
        ttinfo( 18000,   3600, 'AMST'),
        ttinfo( 14400,      0,  'AMT'),
        ttinfo( 18000,   3600, 'AMST'),
        ttinfo( 14400,      0,  'AMT'),
        ttinfo( 18000,   3600, 'AMST'),
        ttinfo( 14400,      0,  'AMT'),
        ttinfo( 18000,   3600, 'AMST'),
        ttinfo( 14400,      0,  'AMT'),
        ]

Yerevan = Yerevan() # Singleton

