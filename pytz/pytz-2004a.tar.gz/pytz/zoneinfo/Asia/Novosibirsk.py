'''
tzinfo timezone information for Asia/Novosibirsk.

Generated from the Olson timezone database:
    ftp://elsie.nci.nih.gov/pub/tz*.tar.gz
'''

from pytz.tzinfo import DstTzInfo
from pytz.tzinfo import memorized_datetime as datetime
from pytz.tzinfo import memorized_ttinfo as ttinfo

class Novosibirsk(DstTzInfo):
    '''Asia/Novosibirsk timezone definition. See datetime.tzinfo for details'''

    _zone = 'Asia/Novosibirsk'

    _utc_transition_times = [
        datetime(   1,  1,  1,  0,  0,  0), #  19900     0 LMT
        datetime(1919, 12, 14,  0, 28, 20), #  21600     0 NOVT
        datetime(1930,  6, 20, 18,  0,  0), #  25200     0 NOVT
        datetime(1981,  3, 31, 17,  0,  0), #  28800  3600 NOVST
        datetime(1981,  9, 30, 16,  0,  0), #  25200     0 NOVT
        datetime(1982,  3, 31, 17,  0,  0), #  28800  3600 NOVST
        datetime(1982,  9, 30, 16,  0,  0), #  25200     0 NOVT
        datetime(1983,  3, 31, 17,  0,  0), #  28800  3600 NOVST
        datetime(1983,  9, 30, 16,  0,  0), #  25200     0 NOVT
        datetime(1984,  3, 31, 17,  0,  0), #  28800  3600 NOVST
        datetime(1984,  9, 29, 19,  0,  0), #  25200     0 NOVT
        datetime(1985,  3, 30, 19,  0,  0), #  28800  3600 NOVST
        datetime(1985,  9, 28, 19,  0,  0), #  25200     0 NOVT
        datetime(1986,  3, 29, 19,  0,  0), #  28800  3600 NOVST
        datetime(1986,  9, 27, 19,  0,  0), #  25200     0 NOVT
        datetime(1987,  3, 28, 19,  0,  0), #  28800  3600 NOVST
        datetime(1987,  9, 26, 19,  0,  0), #  25200     0 NOVT
        datetime(1988,  3, 26, 19,  0,  0), #  28800  3600 NOVST
        datetime(1988,  9, 24, 19,  0,  0), #  25200     0 NOVT
        datetime(1989,  3, 25, 19,  0,  0), #  28800  3600 NOVST
        datetime(1989,  9, 23, 19,  0,  0), #  25200     0 NOVT
        datetime(1990,  3, 24, 19,  0,  0), #  28800  3600 NOVST
        datetime(1990,  9, 29, 19,  0,  0), #  25200     0 NOVT
        datetime(1991,  3, 30, 19,  0,  0), #  25200     0 NOVST
        datetime(1991,  9, 28, 20,  0,  0), #  21600     0 NOVT
        datetime(1992,  1, 18, 20,  0,  0), #  25200     0 NOVT
        datetime(1992,  3, 28, 16,  0,  0), #  28800  3600 NOVST
        datetime(1992,  9, 26, 15,  0,  0), #  25200     0 NOVT
        datetime(1993,  3, 27, 19,  0,  0), #  28800  3600 NOVST
        datetime(1993,  5, 22, 16,  0,  0), #  25200 -3600 NOVST
        datetime(1993,  9, 25, 20,  0,  0), #  21600     0 NOVT
        datetime(1994,  3, 26, 20,  0,  0), #  25200  3600 NOVST
        datetime(1994,  9, 24, 20,  0,  0), #  21600     0 NOVT
        datetime(1995,  3, 25, 20,  0,  0), #  25200  3600 NOVST
        datetime(1995,  9, 23, 20,  0,  0), #  21600     0 NOVT
        datetime(1996,  3, 30, 20,  0,  0), #  25200  3600 NOVST
        datetime(1996, 10, 26, 20,  0,  0), #  21600     0 NOVT
        datetime(1997,  3, 29, 20,  0,  0), #  25200  3600 NOVST
        datetime(1997, 10, 25, 20,  0,  0), #  21600     0 NOVT
        datetime(1998,  3, 28, 20,  0,  0), #  25200  3600 NOVST
        datetime(1998, 10, 24, 20,  0,  0), #  21600     0 NOVT
        datetime(1999,  3, 27, 20,  0,  0), #  25200  3600 NOVST
        datetime(1999, 10, 30, 20,  0,  0), #  21600     0 NOVT
        datetime(2000,  3, 25, 20,  0,  0), #  25200  3600 NOVST
        datetime(2000, 10, 28, 20,  0,  0), #  21600     0 NOVT
        datetime(2001,  3, 24, 20,  0,  0), #  25200  3600 NOVST
        datetime(2001, 10, 27, 20,  0,  0), #  21600     0 NOVT
        datetime(2002,  3, 30, 20,  0,  0), #  25200  3600 NOVST
        datetime(2002, 10, 26, 20,  0,  0), #  21600     0 NOVT
        datetime(2003,  3, 29, 20,  0,  0), #  25200  3600 NOVST
        datetime(2003, 10, 25, 20,  0,  0), #  21600     0 NOVT
        datetime(2004,  3, 27, 20,  0,  0), #  25200  3600 NOVST
        datetime(2004, 10, 30, 20,  0,  0), #  21600     0 NOVT
        datetime(2005,  3, 26, 20,  0,  0), #  25200  3600 NOVST
        datetime(2005, 10, 29, 20,  0,  0), #  21600     0 NOVT
        datetime(2006,  3, 25, 20,  0,  0), #  25200  3600 NOVST
        datetime(2006, 10, 28, 20,  0,  0), #  21600     0 NOVT
        datetime(2007,  3, 24, 20,  0,  0), #  25200  3600 NOVST
        datetime(2007, 10, 27, 20,  0,  0), #  21600     0 NOVT
        datetime(2008,  3, 29, 20,  0,  0), #  25200  3600 NOVST
        datetime(2008, 10, 25, 20,  0,  0), #  21600     0 NOVT
        datetime(2009,  3, 28, 20,  0,  0), #  25200  3600 NOVST
        datetime(2009, 10, 24, 20,  0,  0), #  21600     0 NOVT
        datetime(2010,  3, 27, 20,  0,  0), #  25200  3600 NOVST
        datetime(2010, 10, 30, 20,  0,  0), #  21600     0 NOVT
        datetime(2011,  3, 26, 20,  0,  0), #  25200  3600 NOVST
        datetime(2011, 10, 29, 20,  0,  0), #  21600     0 NOVT
        datetime(2012,  3, 24, 20,  0,  0), #  25200  3600 NOVST
        datetime(2012, 10, 27, 20,  0,  0), #  21600     0 NOVT
        datetime(2013,  3, 30, 20,  0,  0), #  25200  3600 NOVST
        datetime(2013, 10, 26, 20,  0,  0), #  21600     0 NOVT
        datetime(2014,  3, 29, 20,  0,  0), #  25200  3600 NOVST
        datetime(2014, 10, 25, 20,  0,  0), #  21600     0 NOVT
        datetime(2015,  3, 28, 20,  0,  0), #  25200  3600 NOVST
        datetime(2015, 10, 24, 20,  0,  0), #  21600     0 NOVT
        datetime(2016,  3, 26, 20,  0,  0), #  25200  3600 NOVST
        datetime(2016, 10, 29, 20,  0,  0), #  21600     0 NOVT
        datetime(2017,  3, 25, 20,  0,  0), #  25200  3600 NOVST
        datetime(2017, 10, 28, 20,  0,  0), #  21600     0 NOVT
        datetime(2018,  3, 24, 20,  0,  0), #  25200  3600 NOVST
        datetime(2018, 10, 27, 20,  0,  0), #  21600     0 NOVT
        datetime(2019,  3, 30, 20,  0,  0), #  25200  3600 NOVST
        datetime(2019, 10, 26, 20,  0,  0), #  21600     0 NOVT
        datetime(2020,  3, 28, 20,  0,  0), #  25200  3600 NOVST
        datetime(2020, 10, 24, 20,  0,  0), #  21600     0 NOVT
        datetime(2021,  3, 27, 20,  0,  0), #  25200  3600 NOVST
        datetime(2021, 10, 30, 20,  0,  0), #  21600     0 NOVT
        datetime(2022,  3, 26, 20,  0,  0), #  25200  3600 NOVST
        datetime(2022, 10, 29, 20,  0,  0), #  21600     0 NOVT
        datetime(2023,  3, 25, 20,  0,  0), #  25200  3600 NOVST
        datetime(2023, 10, 28, 20,  0,  0), #  21600     0 NOVT
        datetime(2024,  3, 30, 20,  0,  0), #  25200  3600 NOVST
        datetime(2024, 10, 26, 20,  0,  0), #  21600     0 NOVT
        datetime(2025,  3, 29, 20,  0,  0), #  25200  3600 NOVST
        datetime(2025, 10, 25, 20,  0,  0), #  21600     0 NOVT
        datetime(2026,  3, 28, 20,  0,  0), #  25200  3600 NOVST
        datetime(2026, 10, 24, 20,  0,  0), #  21600     0 NOVT
        datetime(2027,  3, 27, 20,  0,  0), #  25200  3600 NOVST
        datetime(2027, 10, 30, 20,  0,  0), #  21600     0 NOVT
        datetime(2028,  3, 25, 20,  0,  0), #  25200  3600 NOVST
        datetime(2028, 10, 28, 20,  0,  0), #  21600     0 NOVT
        datetime(2029,  3, 24, 20,  0,  0), #  25200  3600 NOVST
        datetime(2029, 10, 27, 20,  0,  0), #  21600     0 NOVT
        datetime(2030,  3, 30, 20,  0,  0), #  25200  3600 NOVST
        datetime(2030, 10, 26, 20,  0,  0), #  21600     0 NOVT
        datetime(2031,  3, 29, 20,  0,  0), #  25200  3600 NOVST
        datetime(2031, 10, 25, 20,  0,  0), #  21600     0 NOVT
        datetime(2032,  3, 27, 20,  0,  0), #  25200  3600 NOVST
        datetime(2032, 10, 30, 20,  0,  0), #  21600     0 NOVT
        datetime(2033,  3, 26, 20,  0,  0), #  25200  3600 NOVST
        datetime(2033, 10, 29, 20,  0,  0), #  21600     0 NOVT
        datetime(2034,  3, 25, 20,  0,  0), #  25200  3600 NOVST
        datetime(2034, 10, 28, 20,  0,  0), #  21600     0 NOVT
        datetime(2035,  3, 24, 20,  0,  0), #  25200  3600 NOVST
        datetime(2035, 10, 27, 20,  0,  0), #  21600     0 NOVT
        datetime(2036,  3, 29, 20,  0,  0), #  25200  3600 NOVST
        datetime(2036, 10, 25, 20,  0,  0), #  21600     0 NOVT
        datetime(2037,  3, 28, 20,  0,  0), #  25200  3600 NOVST
        datetime(2037, 10, 24, 20,  0,  0), #  21600     0 NOVT
        ]

    _transition_info = [
        ttinfo( 19900,      0,  'LMT'),
        ttinfo( 21600,      0, 'NOVT'),
        ttinfo( 25200,      0, 'NOVT'),
        ttinfo( 28800,   3600, 'NOVST'),
        ttinfo( 25200,      0, 'NOVT'),
        ttinfo( 28800,   3600, 'NOVST'),
        ttinfo( 25200,      0, 'NOVT'),
        ttinfo( 28800,   3600, 'NOVST'),
        ttinfo( 25200,      0, 'NOVT'),
        ttinfo( 28800,   3600, 'NOVST'),
        ttinfo( 25200,      0, 'NOVT'),
        ttinfo( 28800,   3600, 'NOVST'),
        ttinfo( 25200,      0, 'NOVT'),
        ttinfo( 28800,   3600, 'NOVST'),
        ttinfo( 25200,      0, 'NOVT'),
        ttinfo( 28800,   3600, 'NOVST'),
        ttinfo( 25200,      0, 'NOVT'),
        ttinfo( 28800,   3600, 'NOVST'),
        ttinfo( 25200,      0, 'NOVT'),
        ttinfo( 28800,   3600, 'NOVST'),
        ttinfo( 25200,      0, 'NOVT'),
        ttinfo( 28800,   3600, 'NOVST'),
        ttinfo( 25200,      0, 'NOVT'),
        ttinfo( 25200,      0, 'NOVST'),
        ttinfo( 21600,      0, 'NOVT'),
        ttinfo( 25200,      0, 'NOVT'),
        ttinfo( 28800,   3600, 'NOVST'),
        ttinfo( 25200,      0, 'NOVT'),
        ttinfo( 28800,   3600, 'NOVST'),
        ttinfo( 25200,  -3600, 'NOVST'),
        ttinfo( 21600,      0, 'NOVT'),
        ttinfo( 25200,   3600, 'NOVST'),
        ttinfo( 21600,      0, 'NOVT'),
        ttinfo( 25200,   3600, 'NOVST'),
        ttinfo( 21600,      0, 'NOVT'),
        ttinfo( 25200,   3600, 'NOVST'),
        ttinfo( 21600,      0, 'NOVT'),
        ttinfo( 25200,   3600, 'NOVST'),
        ttinfo( 21600,      0, 'NOVT'),
        ttinfo( 25200,   3600, 'NOVST'),
        ttinfo( 21600,      0, 'NOVT'),
        ttinfo( 25200,   3600, 'NOVST'),
        ttinfo( 21600,      0, 'NOVT'),
        ttinfo( 25200,   3600, 'NOVST'),
        ttinfo( 21600,      0, 'NOVT'),
        ttinfo( 25200,   3600, 'NOVST'),
        ttinfo( 21600,      0, 'NOVT'),
        ttinfo( 25200,   3600, 'NOVST'),
        ttinfo( 21600,      0, 'NOVT'),
        ttinfo( 25200,   3600, 'NOVST'),
        ttinfo( 21600,      0, 'NOVT'),
        ttinfo( 25200,   3600, 'NOVST'),
        ttinfo( 21600,      0, 'NOVT'),
        ttinfo( 25200,   3600, 'NOVST'),
        ttinfo( 21600,      0, 'NOVT'),
        ttinfo( 25200,   3600, 'NOVST'),
        ttinfo( 21600,      0, 'NOVT'),
        ttinfo( 25200,   3600, 'NOVST'),
        ttinfo( 21600,      0, 'NOVT'),
        ttinfo( 25200,   3600, 'NOVST'),
        ttinfo( 21600,      0, 'NOVT'),
        ttinfo( 25200,   3600, 'NOVST'),
        ttinfo( 21600,      0, 'NOVT'),
        ttinfo( 25200,   3600, 'NOVST'),
        ttinfo( 21600,      0, 'NOVT'),
        ttinfo( 25200,   3600, 'NOVST'),
        ttinfo( 21600,      0, 'NOVT'),
        ttinfo( 25200,   3600, 'NOVST'),
        ttinfo( 21600,      0, 'NOVT'),
        ttinfo( 25200,   3600, 'NOVST'),
        ttinfo( 21600,      0, 'NOVT'),
        ttinfo( 25200,   3600, 'NOVST'),
        ttinfo( 21600,      0, 'NOVT'),
        ttinfo( 25200,   3600, 'NOVST'),
        ttinfo( 21600,      0, 'NOVT'),
        ttinfo( 25200,   3600, 'NOVST'),
        ttinfo( 21600,      0, 'NOVT'),
        ttinfo( 25200,   3600, 'NOVST'),
        ttinfo( 21600,      0, 'NOVT'),
        ttinfo( 25200,   3600, 'NOVST'),
        ttinfo( 21600,      0, 'NOVT'),
        ttinfo( 25200,   3600, 'NOVST'),
        ttinfo( 21600,      0, 'NOVT'),
        ttinfo( 25200,   3600, 'NOVST'),
        ttinfo( 21600,      0, 'NOVT'),
        ttinfo( 25200,   3600, 'NOVST'),
        ttinfo( 21600,      0, 'NOVT'),
        ttinfo( 25200,   3600, 'NOVST'),
        ttinfo( 21600,      0, 'NOVT'),
        ttinfo( 25200,   3600, 'NOVST'),
        ttinfo( 21600,      0, 'NOVT'),
        ttinfo( 25200,   3600, 'NOVST'),
        ttinfo( 21600,      0, 'NOVT'),
        ttinfo( 25200,   3600, 'NOVST'),
        ttinfo( 21600,      0, 'NOVT'),
        ttinfo( 25200,   3600, 'NOVST'),
        ttinfo( 21600,      0, 'NOVT'),
        ttinfo( 25200,   3600, 'NOVST'),
        ttinfo( 21600,      0, 'NOVT'),
        ttinfo( 25200,   3600, 'NOVST'),
        ttinfo( 21600,      0, 'NOVT'),
        ttinfo( 25200,   3600, 'NOVST'),
        ttinfo( 21600,      0, 'NOVT'),
        ttinfo( 25200,   3600, 'NOVST'),
        ttinfo( 21600,      0, 'NOVT'),
        ttinfo( 25200,   3600, 'NOVST'),
        ttinfo( 21600,      0, 'NOVT'),
        ttinfo( 25200,   3600, 'NOVST'),
        ttinfo( 21600,      0, 'NOVT'),
        ttinfo( 25200,   3600, 'NOVST'),
        ttinfo( 21600,      0, 'NOVT'),
        ttinfo( 25200,   3600, 'NOVST'),
        ttinfo( 21600,      0, 'NOVT'),
        ttinfo( 25200,   3600, 'NOVST'),
        ttinfo( 21600,      0, 'NOVT'),
        ttinfo( 25200,   3600, 'NOVST'),
        ttinfo( 21600,      0, 'NOVT'),
        ttinfo( 25200,   3600, 'NOVST'),
        ttinfo( 21600,      0, 'NOVT'),
        ]

Novosibirsk = Novosibirsk() # Singleton

