'''
tzinfo timezone information for Asia/Almaty.

Generated from the Olson timezone database:
    ftp://elsie.nci.nih.gov/pub/tz*.tar.gz
'''

from pytz.tzinfo import DstTzInfo
from pytz.tzinfo import memorized_datetime as datetime
from pytz.tzinfo import memorized_ttinfo as ttinfo

class Almaty(DstTzInfo):
    '''Asia/Almaty timezone definition. See datetime.tzinfo for details'''

    _zone = 'Asia/Almaty'

    _utc_transition_times = [
        datetime(   1,  1,  1,  0,  0,  0), #  18468     0 LMT
        datetime(1924,  5,  1, 18, 52, 12), #  18000     0 ALMT
        datetime(1930,  6, 20, 19,  0,  0), #  21600     0 ALMT
        datetime(1981,  3, 31, 18,  0,  0), #  25200  3600 ALMST
        datetime(1981,  9, 30, 17,  0,  0), #  21600     0 ALMT
        datetime(1982,  3, 31, 18,  0,  0), #  25200  3600 ALMST
        datetime(1982,  9, 30, 17,  0,  0), #  21600     0 ALMT
        datetime(1983,  3, 31, 18,  0,  0), #  25200  3600 ALMST
        datetime(1983,  9, 30, 17,  0,  0), #  21600     0 ALMT
        datetime(1984,  3, 31, 18,  0,  0), #  25200  3600 ALMST
        datetime(1984,  9, 29, 20,  0,  0), #  21600     0 ALMT
        datetime(1985,  3, 30, 20,  0,  0), #  25200  3600 ALMST
        datetime(1985,  9, 28, 20,  0,  0), #  21600     0 ALMT
        datetime(1986,  3, 29, 20,  0,  0), #  25200  3600 ALMST
        datetime(1986,  9, 27, 20,  0,  0), #  21600     0 ALMT
        datetime(1987,  3, 28, 20,  0,  0), #  25200  3600 ALMST
        datetime(1987,  9, 26, 20,  0,  0), #  21600     0 ALMT
        datetime(1988,  3, 26, 20,  0,  0), #  25200  3600 ALMST
        datetime(1988,  9, 24, 20,  0,  0), #  21600     0 ALMT
        datetime(1989,  3, 25, 20,  0,  0), #  25200  3600 ALMST
        datetime(1989,  9, 23, 20,  0,  0), #  21600     0 ALMT
        datetime(1990,  3, 24, 20,  0,  0), #  25200  3600 ALMST
        datetime(1990,  9, 29, 20,  0,  0), #  21600     0 ALMT
        datetime(1990, 12, 31, 18,  0,  0), #  21600     0 ALMT
        datetime(1992,  3, 28, 17,  0,  0), #  25200  3600 ALMST
        datetime(1992,  9, 26, 16,  0,  0), #  21600     0 ALMT
        datetime(1993,  3, 27, 20,  0,  0), #  25200  3600 ALMST
        datetime(1993,  9, 25, 20,  0,  0), #  21600     0 ALMT
        datetime(1994,  3, 26, 20,  0,  0), #  25200  3600 ALMST
        datetime(1994,  9, 24, 20,  0,  0), #  21600     0 ALMT
        datetime(1995,  3, 25, 20,  0,  0), #  25200  3600 ALMST
        datetime(1995,  9, 23, 20,  0,  0), #  21600     0 ALMT
        datetime(1996,  3, 30, 20,  0,  0), #  25200  3600 ALMST
        datetime(1996, 10, 26, 20,  0,  0), #  21600     0 ALMT
        datetime(1997,  3, 29, 20,  0,  0), #  25200  3600 ALMST
        datetime(1997, 10, 25, 20,  0,  0), #  21600     0 ALMT
        datetime(1998,  3, 28, 20,  0,  0), #  25200  3600 ALMST
        datetime(1998, 10, 24, 20,  0,  0), #  21600     0 ALMT
        datetime(1999,  3, 27, 20,  0,  0), #  25200  3600 ALMST
        datetime(1999, 10, 30, 20,  0,  0), #  21600     0 ALMT
        datetime(2000,  3, 25, 20,  0,  0), #  25200  3600 ALMST
        datetime(2000, 10, 28, 20,  0,  0), #  21600     0 ALMT
        datetime(2001,  3, 24, 20,  0,  0), #  25200  3600 ALMST
        datetime(2001, 10, 27, 20,  0,  0), #  21600     0 ALMT
        datetime(2002,  3, 30, 20,  0,  0), #  25200  3600 ALMST
        datetime(2002, 10, 26, 20,  0,  0), #  21600     0 ALMT
        datetime(2003,  3, 29, 20,  0,  0), #  25200  3600 ALMST
        datetime(2003, 10, 25, 20,  0,  0), #  21600     0 ALMT
        datetime(2004,  3, 27, 20,  0,  0), #  25200  3600 ALMST
        datetime(2004, 10, 30, 20,  0,  0), #  21600     0 ALMT
        datetime(2005,  3, 26, 20,  0,  0), #  25200  3600 ALMST
        datetime(2005, 10, 29, 20,  0,  0), #  21600     0 ALMT
        datetime(2006,  3, 25, 20,  0,  0), #  25200  3600 ALMST
        datetime(2006, 10, 28, 20,  0,  0), #  21600     0 ALMT
        datetime(2007,  3, 24, 20,  0,  0), #  25200  3600 ALMST
        datetime(2007, 10, 27, 20,  0,  0), #  21600     0 ALMT
        datetime(2008,  3, 29, 20,  0,  0), #  25200  3600 ALMST
        datetime(2008, 10, 25, 20,  0,  0), #  21600     0 ALMT
        datetime(2009,  3, 28, 20,  0,  0), #  25200  3600 ALMST
        datetime(2009, 10, 24, 20,  0,  0), #  21600     0 ALMT
        datetime(2010,  3, 27, 20,  0,  0), #  25200  3600 ALMST
        datetime(2010, 10, 30, 20,  0,  0), #  21600     0 ALMT
        datetime(2011,  3, 26, 20,  0,  0), #  25200  3600 ALMST
        datetime(2011, 10, 29, 20,  0,  0), #  21600     0 ALMT
        datetime(2012,  3, 24, 20,  0,  0), #  25200  3600 ALMST
        datetime(2012, 10, 27, 20,  0,  0), #  21600     0 ALMT
        datetime(2013,  3, 30, 20,  0,  0), #  25200  3600 ALMST
        datetime(2013, 10, 26, 20,  0,  0), #  21600     0 ALMT
        datetime(2014,  3, 29, 20,  0,  0), #  25200  3600 ALMST
        datetime(2014, 10, 25, 20,  0,  0), #  21600     0 ALMT
        datetime(2015,  3, 28, 20,  0,  0), #  25200  3600 ALMST
        datetime(2015, 10, 24, 20,  0,  0), #  21600     0 ALMT
        datetime(2016,  3, 26, 20,  0,  0), #  25200  3600 ALMST
        datetime(2016, 10, 29, 20,  0,  0), #  21600     0 ALMT
        datetime(2017,  3, 25, 20,  0,  0), #  25200  3600 ALMST
        datetime(2017, 10, 28, 20,  0,  0), #  21600     0 ALMT
        datetime(2018,  3, 24, 20,  0,  0), #  25200  3600 ALMST
        datetime(2018, 10, 27, 20,  0,  0), #  21600     0 ALMT
        datetime(2019,  3, 30, 20,  0,  0), #  25200  3600 ALMST
        datetime(2019, 10, 26, 20,  0,  0), #  21600     0 ALMT
        datetime(2020,  3, 28, 20,  0,  0), #  25200  3600 ALMST
        datetime(2020, 10, 24, 20,  0,  0), #  21600     0 ALMT
        datetime(2021,  3, 27, 20,  0,  0), #  25200  3600 ALMST
        datetime(2021, 10, 30, 20,  0,  0), #  21600     0 ALMT
        datetime(2022,  3, 26, 20,  0,  0), #  25200  3600 ALMST
        datetime(2022, 10, 29, 20,  0,  0), #  21600     0 ALMT
        datetime(2023,  3, 25, 20,  0,  0), #  25200  3600 ALMST
        datetime(2023, 10, 28, 20,  0,  0), #  21600     0 ALMT
        datetime(2024,  3, 30, 20,  0,  0), #  25200  3600 ALMST
        datetime(2024, 10, 26, 20,  0,  0), #  21600     0 ALMT
        datetime(2025,  3, 29, 20,  0,  0), #  25200  3600 ALMST
        datetime(2025, 10, 25, 20,  0,  0), #  21600     0 ALMT
        datetime(2026,  3, 28, 20,  0,  0), #  25200  3600 ALMST
        datetime(2026, 10, 24, 20,  0,  0), #  21600     0 ALMT
        datetime(2027,  3, 27, 20,  0,  0), #  25200  3600 ALMST
        datetime(2027, 10, 30, 20,  0,  0), #  21600     0 ALMT
        datetime(2028,  3, 25, 20,  0,  0), #  25200  3600 ALMST
        datetime(2028, 10, 28, 20,  0,  0), #  21600     0 ALMT
        datetime(2029,  3, 24, 20,  0,  0), #  25200  3600 ALMST
        datetime(2029, 10, 27, 20,  0,  0), #  21600     0 ALMT
        datetime(2030,  3, 30, 20,  0,  0), #  25200  3600 ALMST
        datetime(2030, 10, 26, 20,  0,  0), #  21600     0 ALMT
        datetime(2031,  3, 29, 20,  0,  0), #  25200  3600 ALMST
        datetime(2031, 10, 25, 20,  0,  0), #  21600     0 ALMT
        datetime(2032,  3, 27, 20,  0,  0), #  25200  3600 ALMST
        datetime(2032, 10, 30, 20,  0,  0), #  21600     0 ALMT
        datetime(2033,  3, 26, 20,  0,  0), #  25200  3600 ALMST
        datetime(2033, 10, 29, 20,  0,  0), #  21600     0 ALMT
        datetime(2034,  3, 25, 20,  0,  0), #  25200  3600 ALMST
        datetime(2034, 10, 28, 20,  0,  0), #  21600     0 ALMT
        datetime(2035,  3, 24, 20,  0,  0), #  25200  3600 ALMST
        datetime(2035, 10, 27, 20,  0,  0), #  21600     0 ALMT
        datetime(2036,  3, 29, 20,  0,  0), #  25200  3600 ALMST
        datetime(2036, 10, 25, 20,  0,  0), #  21600     0 ALMT
        datetime(2037,  3, 28, 20,  0,  0), #  25200  3600 ALMST
        datetime(2037, 10, 24, 20,  0,  0), #  21600     0 ALMT
        ]

    _transition_info = [
        ttinfo( 18468,      0,  'LMT'),
        ttinfo( 18000,      0, 'ALMT'),
        ttinfo( 21600,      0, 'ALMT'),
        ttinfo( 25200,   3600, 'ALMST'),
        ttinfo( 21600,      0, 'ALMT'),
        ttinfo( 25200,   3600, 'ALMST'),
        ttinfo( 21600,      0, 'ALMT'),
        ttinfo( 25200,   3600, 'ALMST'),
        ttinfo( 21600,      0, 'ALMT'),
        ttinfo( 25200,   3600, 'ALMST'),
        ttinfo( 21600,      0, 'ALMT'),
        ttinfo( 25200,   3600, 'ALMST'),
        ttinfo( 21600,      0, 'ALMT'),
        ttinfo( 25200,   3600, 'ALMST'),
        ttinfo( 21600,      0, 'ALMT'),
        ttinfo( 25200,   3600, 'ALMST'),
        ttinfo( 21600,      0, 'ALMT'),
        ttinfo( 25200,   3600, 'ALMST'),
        ttinfo( 21600,      0, 'ALMT'),
        ttinfo( 25200,   3600, 'ALMST'),
        ttinfo( 21600,      0, 'ALMT'),
        ttinfo( 25200,   3600, 'ALMST'),
        ttinfo( 21600,      0, 'ALMT'),
        ttinfo( 21600,      0, 'ALMT'),
        ttinfo( 25200,   3600, 'ALMST'),
        ttinfo( 21600,      0, 'ALMT'),
        ttinfo( 25200,   3600, 'ALMST'),
        ttinfo( 21600,      0, 'ALMT'),
        ttinfo( 25200,   3600, 'ALMST'),
        ttinfo( 21600,      0, 'ALMT'),
        ttinfo( 25200,   3600, 'ALMST'),
        ttinfo( 21600,      0, 'ALMT'),
        ttinfo( 25200,   3600, 'ALMST'),
        ttinfo( 21600,      0, 'ALMT'),
        ttinfo( 25200,   3600, 'ALMST'),
        ttinfo( 21600,      0, 'ALMT'),
        ttinfo( 25200,   3600, 'ALMST'),
        ttinfo( 21600,      0, 'ALMT'),
        ttinfo( 25200,   3600, 'ALMST'),
        ttinfo( 21600,      0, 'ALMT'),
        ttinfo( 25200,   3600, 'ALMST'),
        ttinfo( 21600,      0, 'ALMT'),
        ttinfo( 25200,   3600, 'ALMST'),
        ttinfo( 21600,      0, 'ALMT'),
        ttinfo( 25200,   3600, 'ALMST'),
        ttinfo( 21600,      0, 'ALMT'),
        ttinfo( 25200,   3600, 'ALMST'),
        ttinfo( 21600,      0, 'ALMT'),
        ttinfo( 25200,   3600, 'ALMST'),
        ttinfo( 21600,      0, 'ALMT'),
        ttinfo( 25200,   3600, 'ALMST'),
        ttinfo( 21600,      0, 'ALMT'),
        ttinfo( 25200,   3600, 'ALMST'),
        ttinfo( 21600,      0, 'ALMT'),
        ttinfo( 25200,   3600, 'ALMST'),
        ttinfo( 21600,      0, 'ALMT'),
        ttinfo( 25200,   3600, 'ALMST'),
        ttinfo( 21600,      0, 'ALMT'),
        ttinfo( 25200,   3600, 'ALMST'),
        ttinfo( 21600,      0, 'ALMT'),
        ttinfo( 25200,   3600, 'ALMST'),
        ttinfo( 21600,      0, 'ALMT'),
        ttinfo( 25200,   3600, 'ALMST'),
        ttinfo( 21600,      0, 'ALMT'),
        ttinfo( 25200,   3600, 'ALMST'),
        ttinfo( 21600,      0, 'ALMT'),
        ttinfo( 25200,   3600, 'ALMST'),
        ttinfo( 21600,      0, 'ALMT'),
        ttinfo( 25200,   3600, 'ALMST'),
        ttinfo( 21600,      0, 'ALMT'),
        ttinfo( 25200,   3600, 'ALMST'),
        ttinfo( 21600,      0, 'ALMT'),
        ttinfo( 25200,   3600, 'ALMST'),
        ttinfo( 21600,      0, 'ALMT'),
        ttinfo( 25200,   3600, 'ALMST'),
        ttinfo( 21600,      0, 'ALMT'),
        ttinfo( 25200,   3600, 'ALMST'),
        ttinfo( 21600,      0, 'ALMT'),
        ttinfo( 25200,   3600, 'ALMST'),
        ttinfo( 21600,      0, 'ALMT'),
        ttinfo( 25200,   3600, 'ALMST'),
        ttinfo( 21600,      0, 'ALMT'),
        ttinfo( 25200,   3600, 'ALMST'),
        ttinfo( 21600,      0, 'ALMT'),
        ttinfo( 25200,   3600, 'ALMST'),
        ttinfo( 21600,      0, 'ALMT'),
        ttinfo( 25200,   3600, 'ALMST'),
        ttinfo( 21600,      0, 'ALMT'),
        ttinfo( 25200,   3600, 'ALMST'),
        ttinfo( 21600,      0, 'ALMT'),
        ttinfo( 25200,   3600, 'ALMST'),
        ttinfo( 21600,      0, 'ALMT'),
        ttinfo( 25200,   3600, 'ALMST'),
        ttinfo( 21600,      0, 'ALMT'),
        ttinfo( 25200,   3600, 'ALMST'),
        ttinfo( 21600,      0, 'ALMT'),
        ttinfo( 25200,   3600, 'ALMST'),
        ttinfo( 21600,      0, 'ALMT'),
        ttinfo( 25200,   3600, 'ALMST'),
        ttinfo( 21600,      0, 'ALMT'),
        ttinfo( 25200,   3600, 'ALMST'),
        ttinfo( 21600,      0, 'ALMT'),
        ttinfo( 25200,   3600, 'ALMST'),
        ttinfo( 21600,      0, 'ALMT'),
        ttinfo( 25200,   3600, 'ALMST'),
        ttinfo( 21600,      0, 'ALMT'),
        ttinfo( 25200,   3600, 'ALMST'),
        ttinfo( 21600,      0, 'ALMT'),
        ttinfo( 25200,   3600, 'ALMST'),
        ttinfo( 21600,      0, 'ALMT'),
        ttinfo( 25200,   3600, 'ALMST'),
        ttinfo( 21600,      0, 'ALMT'),
        ttinfo( 25200,   3600, 'ALMST'),
        ttinfo( 21600,      0, 'ALMT'),
        ttinfo( 25200,   3600, 'ALMST'),
        ttinfo( 21600,      0, 'ALMT'),
        ]

Almaty = Almaty() # Singleton

