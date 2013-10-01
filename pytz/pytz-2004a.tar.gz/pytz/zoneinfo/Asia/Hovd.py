'''
tzinfo timezone information for Asia/Hovd.

Generated from the Olson timezone database:
    ftp://elsie.nci.nih.gov/pub/tz*.tar.gz
'''

from pytz.tzinfo import DstTzInfo
from pytz.tzinfo import memorized_datetime as datetime
from pytz.tzinfo import memorized_ttinfo as ttinfo

class Hovd(DstTzInfo):
    '''Asia/Hovd timezone definition. See datetime.tzinfo for details'''

    _zone = 'Asia/Hovd'

    _utc_transition_times = [
        datetime(   1,  1,  1,  0,  0,  0), #  21996     0 LMT
        datetime(1905,  7, 31, 17, 53, 24), #  21600     0 HOVT
        datetime(1977, 12, 31, 18,  0,  0), #  25200     0 HOVT
        datetime(1983,  3, 31, 17,  0,  0), #  28800  3600 HOVST
        datetime(1983,  9, 30, 16,  0,  0), #  25200     0 HOVT
        datetime(1984,  3, 31, 17,  0,  0), #  28800  3600 HOVST
        datetime(1984,  9, 29, 19,  0,  0), #  25200     0 HOVT
        datetime(1985,  3, 30, 19,  0,  0), #  28800  3600 HOVST
        datetime(1985,  9, 28, 19,  0,  0), #  25200     0 HOVT
        datetime(1986,  3, 29, 19,  0,  0), #  28800  3600 HOVST
        datetime(1986,  9, 27, 19,  0,  0), #  25200     0 HOVT
        datetime(1987,  3, 28, 19,  0,  0), #  28800  3600 HOVST
        datetime(1987,  9, 26, 19,  0,  0), #  25200     0 HOVT
        datetime(1988,  3, 26, 19,  0,  0), #  28800  3600 HOVST
        datetime(1988,  9, 24, 19,  0,  0), #  25200     0 HOVT
        datetime(1989,  3, 25, 19,  0,  0), #  28800  3600 HOVST
        datetime(1989,  9, 23, 19,  0,  0), #  25200     0 HOVT
        datetime(1990,  3, 24, 19,  0,  0), #  28800  3600 HOVST
        datetime(1990,  9, 29, 19,  0,  0), #  25200     0 HOVT
        datetime(1991,  3, 30, 19,  0,  0), #  28800  3600 HOVST
        datetime(1991,  9, 28, 19,  0,  0), #  25200     0 HOVT
        datetime(1992,  3, 28, 19,  0,  0), #  28800  3600 HOVST
        datetime(1992,  9, 26, 19,  0,  0), #  25200     0 HOVT
        datetime(1993,  3, 27, 19,  0,  0), #  28800  3600 HOVST
        datetime(1993,  9, 25, 19,  0,  0), #  25200     0 HOVT
        datetime(1994,  3, 26, 19,  0,  0), #  28800  3600 HOVST
        datetime(1994,  9, 24, 19,  0,  0), #  25200     0 HOVT
        datetime(1995,  3, 25, 19,  0,  0), #  28800  3600 HOVST
        datetime(1995,  9, 23, 19,  0,  0), #  25200     0 HOVT
        datetime(1996,  3, 30, 19,  0,  0), #  28800  3600 HOVST
        datetime(1996,  9, 28, 19,  0,  0), #  25200     0 HOVT
        datetime(1997,  3, 29, 19,  0,  0), #  28800  3600 HOVST
        datetime(1997,  9, 27, 19,  0,  0), #  25200     0 HOVT
        datetime(1998,  3, 28, 19,  0,  0), #  28800  3600 HOVST
        datetime(1998,  9, 26, 19,  0,  0), #  25200     0 HOVT
        datetime(2001,  4, 27, 19,  0,  0), #  28800  3600 HOVST
        datetime(2001,  9, 28, 18,  0,  0), #  25200     0 HOVT
        datetime(2002,  3, 29, 19,  0,  0), #  28800  3600 HOVST
        datetime(2002,  9, 27, 18,  0,  0), #  25200     0 HOVT
        datetime(2003,  3, 28, 19,  0,  0), #  28800  3600 HOVST
        datetime(2003,  9, 26, 18,  0,  0), #  25200     0 HOVT
        datetime(2004,  3, 26, 19,  0,  0), #  28800  3600 HOVST
        datetime(2004,  9, 24, 18,  0,  0), #  25200     0 HOVT
        datetime(2005,  3, 25, 19,  0,  0), #  28800  3600 HOVST
        datetime(2005,  9, 23, 18,  0,  0), #  25200     0 HOVT
        datetime(2006,  3, 24, 19,  0,  0), #  28800  3600 HOVST
        datetime(2006,  9, 29, 18,  0,  0), #  25200     0 HOVT
        datetime(2007,  3, 30, 19,  0,  0), #  28800  3600 HOVST
        datetime(2007,  9, 28, 18,  0,  0), #  25200     0 HOVT
        datetime(2008,  3, 28, 19,  0,  0), #  28800  3600 HOVST
        datetime(2008,  9, 26, 18,  0,  0), #  25200     0 HOVT
        datetime(2009,  3, 27, 19,  0,  0), #  28800  3600 HOVST
        datetime(2009,  9, 25, 18,  0,  0), #  25200     0 HOVT
        datetime(2010,  3, 26, 19,  0,  0), #  28800  3600 HOVST
        datetime(2010,  9, 24, 18,  0,  0), #  25200     0 HOVT
        datetime(2011,  3, 25, 19,  0,  0), #  28800  3600 HOVST
        datetime(2011,  9, 23, 18,  0,  0), #  25200     0 HOVT
        datetime(2012,  3, 30, 19,  0,  0), #  28800  3600 HOVST
        datetime(2012,  9, 28, 18,  0,  0), #  25200     0 HOVT
        datetime(2013,  3, 29, 19,  0,  0), #  28800  3600 HOVST
        datetime(2013,  9, 27, 18,  0,  0), #  25200     0 HOVT
        datetime(2014,  3, 28, 19,  0,  0), #  28800  3600 HOVST
        datetime(2014,  9, 26, 18,  0,  0), #  25200     0 HOVT
        datetime(2015,  3, 27, 19,  0,  0), #  28800  3600 HOVST
        datetime(2015,  9, 25, 18,  0,  0), #  25200     0 HOVT
        datetime(2016,  3, 25, 19,  0,  0), #  28800  3600 HOVST
        datetime(2016,  9, 23, 18,  0,  0), #  25200     0 HOVT
        datetime(2017,  3, 24, 19,  0,  0), #  28800  3600 HOVST
        datetime(2017,  9, 29, 18,  0,  0), #  25200     0 HOVT
        datetime(2018,  3, 30, 19,  0,  0), #  28800  3600 HOVST
        datetime(2018,  9, 28, 18,  0,  0), #  25200     0 HOVT
        datetime(2019,  3, 29, 19,  0,  0), #  28800  3600 HOVST
        datetime(2019,  9, 27, 18,  0,  0), #  25200     0 HOVT
        datetime(2020,  3, 27, 19,  0,  0), #  28800  3600 HOVST
        datetime(2020,  9, 25, 18,  0,  0), #  25200     0 HOVT
        datetime(2021,  3, 26, 19,  0,  0), #  28800  3600 HOVST
        datetime(2021,  9, 24, 18,  0,  0), #  25200     0 HOVT
        datetime(2022,  3, 25, 19,  0,  0), #  28800  3600 HOVST
        datetime(2022,  9, 23, 18,  0,  0), #  25200     0 HOVT
        datetime(2023,  3, 24, 19,  0,  0), #  28800  3600 HOVST
        datetime(2023,  9, 29, 18,  0,  0), #  25200     0 HOVT
        datetime(2024,  3, 29, 19,  0,  0), #  28800  3600 HOVST
        datetime(2024,  9, 27, 18,  0,  0), #  25200     0 HOVT
        datetime(2025,  3, 28, 19,  0,  0), #  28800  3600 HOVST
        datetime(2025,  9, 26, 18,  0,  0), #  25200     0 HOVT
        datetime(2026,  3, 27, 19,  0,  0), #  28800  3600 HOVST
        datetime(2026,  9, 25, 18,  0,  0), #  25200     0 HOVT
        datetime(2027,  3, 26, 19,  0,  0), #  28800  3600 HOVST
        datetime(2027,  9, 24, 18,  0,  0), #  25200     0 HOVT
        datetime(2028,  3, 24, 19,  0,  0), #  28800  3600 HOVST
        datetime(2028,  9, 29, 18,  0,  0), #  25200     0 HOVT
        datetime(2029,  3, 30, 19,  0,  0), #  28800  3600 HOVST
        datetime(2029,  9, 28, 18,  0,  0), #  25200     0 HOVT
        datetime(2030,  3, 29, 19,  0,  0), #  28800  3600 HOVST
        datetime(2030,  9, 27, 18,  0,  0), #  25200     0 HOVT
        datetime(2031,  3, 28, 19,  0,  0), #  28800  3600 HOVST
        datetime(2031,  9, 26, 18,  0,  0), #  25200     0 HOVT
        datetime(2032,  3, 26, 19,  0,  0), #  28800  3600 HOVST
        datetime(2032,  9, 24, 18,  0,  0), #  25200     0 HOVT
        datetime(2033,  3, 25, 19,  0,  0), #  28800  3600 HOVST
        datetime(2033,  9, 23, 18,  0,  0), #  25200     0 HOVT
        datetime(2034,  3, 24, 19,  0,  0), #  28800  3600 HOVST
        datetime(2034,  9, 29, 18,  0,  0), #  25200     0 HOVT
        datetime(2035,  3, 30, 19,  0,  0), #  28800  3600 HOVST
        datetime(2035,  9, 28, 18,  0,  0), #  25200     0 HOVT
        datetime(2036,  3, 28, 19,  0,  0), #  28800  3600 HOVST
        datetime(2036,  9, 26, 18,  0,  0), #  25200     0 HOVT
        datetime(2037,  3, 27, 19,  0,  0), #  28800  3600 HOVST
        datetime(2037,  9, 25, 18,  0,  0), #  25200     0 HOVT
        ]

    _transition_info = [
        ttinfo( 21996,      0,  'LMT'),
        ttinfo( 21600,      0, 'HOVT'),
        ttinfo( 25200,      0, 'HOVT'),
        ttinfo( 28800,   3600, 'HOVST'),
        ttinfo( 25200,      0, 'HOVT'),
        ttinfo( 28800,   3600, 'HOVST'),
        ttinfo( 25200,      0, 'HOVT'),
        ttinfo( 28800,   3600, 'HOVST'),
        ttinfo( 25200,      0, 'HOVT'),
        ttinfo( 28800,   3600, 'HOVST'),
        ttinfo( 25200,      0, 'HOVT'),
        ttinfo( 28800,   3600, 'HOVST'),
        ttinfo( 25200,      0, 'HOVT'),
        ttinfo( 28800,   3600, 'HOVST'),
        ttinfo( 25200,      0, 'HOVT'),
        ttinfo( 28800,   3600, 'HOVST'),
        ttinfo( 25200,      0, 'HOVT'),
        ttinfo( 28800,   3600, 'HOVST'),
        ttinfo( 25200,      0, 'HOVT'),
        ttinfo( 28800,   3600, 'HOVST'),
        ttinfo( 25200,      0, 'HOVT'),
        ttinfo( 28800,   3600, 'HOVST'),
        ttinfo( 25200,      0, 'HOVT'),
        ttinfo( 28800,   3600, 'HOVST'),
        ttinfo( 25200,      0, 'HOVT'),
        ttinfo( 28800,   3600, 'HOVST'),
        ttinfo( 25200,      0, 'HOVT'),
        ttinfo( 28800,   3600, 'HOVST'),
        ttinfo( 25200,      0, 'HOVT'),
        ttinfo( 28800,   3600, 'HOVST'),
        ttinfo( 25200,      0, 'HOVT'),
        ttinfo( 28800,   3600, 'HOVST'),
        ttinfo( 25200,      0, 'HOVT'),
        ttinfo( 28800,   3600, 'HOVST'),
        ttinfo( 25200,      0, 'HOVT'),
        ttinfo( 28800,   3600, 'HOVST'),
        ttinfo( 25200,      0, 'HOVT'),
        ttinfo( 28800,   3600, 'HOVST'),
        ttinfo( 25200,      0, 'HOVT'),
        ttinfo( 28800,   3600, 'HOVST'),
        ttinfo( 25200,      0, 'HOVT'),
        ttinfo( 28800,   3600, 'HOVST'),
        ttinfo( 25200,      0, 'HOVT'),
        ttinfo( 28800,   3600, 'HOVST'),
        ttinfo( 25200,      0, 'HOVT'),
        ttinfo( 28800,   3600, 'HOVST'),
        ttinfo( 25200,      0, 'HOVT'),
        ttinfo( 28800,   3600, 'HOVST'),
        ttinfo( 25200,      0, 'HOVT'),
        ttinfo( 28800,   3600, 'HOVST'),
        ttinfo( 25200,      0, 'HOVT'),
        ttinfo( 28800,   3600, 'HOVST'),
        ttinfo( 25200,      0, 'HOVT'),
        ttinfo( 28800,   3600, 'HOVST'),
        ttinfo( 25200,      0, 'HOVT'),
        ttinfo( 28800,   3600, 'HOVST'),
        ttinfo( 25200,      0, 'HOVT'),
        ttinfo( 28800,   3600, 'HOVST'),
        ttinfo( 25200,      0, 'HOVT'),
        ttinfo( 28800,   3600, 'HOVST'),
        ttinfo( 25200,      0, 'HOVT'),
        ttinfo( 28800,   3600, 'HOVST'),
        ttinfo( 25200,      0, 'HOVT'),
        ttinfo( 28800,   3600, 'HOVST'),
        ttinfo( 25200,      0, 'HOVT'),
        ttinfo( 28800,   3600, 'HOVST'),
        ttinfo( 25200,      0, 'HOVT'),
        ttinfo( 28800,   3600, 'HOVST'),
        ttinfo( 25200,      0, 'HOVT'),
        ttinfo( 28800,   3600, 'HOVST'),
        ttinfo( 25200,      0, 'HOVT'),
        ttinfo( 28800,   3600, 'HOVST'),
        ttinfo( 25200,      0, 'HOVT'),
        ttinfo( 28800,   3600, 'HOVST'),
        ttinfo( 25200,      0, 'HOVT'),
        ttinfo( 28800,   3600, 'HOVST'),
        ttinfo( 25200,      0, 'HOVT'),
        ttinfo( 28800,   3600, 'HOVST'),
        ttinfo( 25200,      0, 'HOVT'),
        ttinfo( 28800,   3600, 'HOVST'),
        ttinfo( 25200,      0, 'HOVT'),
        ttinfo( 28800,   3600, 'HOVST'),
        ttinfo( 25200,      0, 'HOVT'),
        ttinfo( 28800,   3600, 'HOVST'),
        ttinfo( 25200,      0, 'HOVT'),
        ttinfo( 28800,   3600, 'HOVST'),
        ttinfo( 25200,      0, 'HOVT'),
        ttinfo( 28800,   3600, 'HOVST'),
        ttinfo( 25200,      0, 'HOVT'),
        ttinfo( 28800,   3600, 'HOVST'),
        ttinfo( 25200,      0, 'HOVT'),
        ttinfo( 28800,   3600, 'HOVST'),
        ttinfo( 25200,      0, 'HOVT'),
        ttinfo( 28800,   3600, 'HOVST'),
        ttinfo( 25200,      0, 'HOVT'),
        ttinfo( 28800,   3600, 'HOVST'),
        ttinfo( 25200,      0, 'HOVT'),
        ttinfo( 28800,   3600, 'HOVST'),
        ttinfo( 25200,      0, 'HOVT'),
        ttinfo( 28800,   3600, 'HOVST'),
        ttinfo( 25200,      0, 'HOVT'),
        ttinfo( 28800,   3600, 'HOVST'),
        ttinfo( 25200,      0, 'HOVT'),
        ttinfo( 28800,   3600, 'HOVST'),
        ttinfo( 25200,      0, 'HOVT'),
        ttinfo( 28800,   3600, 'HOVST'),
        ttinfo( 25200,      0, 'HOVT'),
        ttinfo( 28800,   3600, 'HOVST'),
        ttinfo( 25200,      0, 'HOVT'),
        ]

Hovd = Hovd() # Singleton

