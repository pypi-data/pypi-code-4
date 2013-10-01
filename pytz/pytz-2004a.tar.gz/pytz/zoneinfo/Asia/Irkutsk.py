'''
tzinfo timezone information for Asia/Irkutsk.

Generated from the Olson timezone database:
    ftp://elsie.nci.nih.gov/pub/tz*.tar.gz
'''

from pytz.tzinfo import DstTzInfo
from pytz.tzinfo import memorized_datetime as datetime
from pytz.tzinfo import memorized_ttinfo as ttinfo

class Irkutsk(DstTzInfo):
    '''Asia/Irkutsk timezone definition. See datetime.tzinfo for details'''

    _zone = 'Asia/Irkutsk'

    _utc_transition_times = [
        datetime(   1,  1,  1,  0,  0,  0), #  25040     0 IMT
        datetime(1920,  1, 24, 17,  2, 40), #  25200     0 IRKT
        datetime(1930,  6, 20, 17,  0,  0), #  28800     0 IRKT
        datetime(1981,  3, 31, 16,  0,  0), #  32400  3600 IRKST
        datetime(1981,  9, 30, 15,  0,  0), #  28800     0 IRKT
        datetime(1982,  3, 31, 16,  0,  0), #  32400  3600 IRKST
        datetime(1982,  9, 30, 15,  0,  0), #  28800     0 IRKT
        datetime(1983,  3, 31, 16,  0,  0), #  32400  3600 IRKST
        datetime(1983,  9, 30, 15,  0,  0), #  28800     0 IRKT
        datetime(1984,  3, 31, 16,  0,  0), #  32400  3600 IRKST
        datetime(1984,  9, 29, 18,  0,  0), #  28800     0 IRKT
        datetime(1985,  3, 30, 18,  0,  0), #  32400  3600 IRKST
        datetime(1985,  9, 28, 18,  0,  0), #  28800     0 IRKT
        datetime(1986,  3, 29, 18,  0,  0), #  32400  3600 IRKST
        datetime(1986,  9, 27, 18,  0,  0), #  28800     0 IRKT
        datetime(1987,  3, 28, 18,  0,  0), #  32400  3600 IRKST
        datetime(1987,  9, 26, 18,  0,  0), #  28800     0 IRKT
        datetime(1988,  3, 26, 18,  0,  0), #  32400  3600 IRKST
        datetime(1988,  9, 24, 18,  0,  0), #  28800     0 IRKT
        datetime(1989,  3, 25, 18,  0,  0), #  32400  3600 IRKST
        datetime(1989,  9, 23, 18,  0,  0), #  28800     0 IRKT
        datetime(1990,  3, 24, 18,  0,  0), #  32400  3600 IRKST
        datetime(1990,  9, 29, 18,  0,  0), #  28800     0 IRKT
        datetime(1991,  3, 30, 18,  0,  0), #  28800     0 IRKST
        datetime(1991,  9, 28, 19,  0,  0), #  25200     0 IRKT
        datetime(1992,  1, 18, 19,  0,  0), #  28800     0 IRKT
        datetime(1992,  3, 28, 15,  0,  0), #  32400  3600 IRKST
        datetime(1992,  9, 26, 14,  0,  0), #  28800     0 IRKT
        datetime(1993,  3, 27, 18,  0,  0), #  32400  3600 IRKST
        datetime(1993,  9, 25, 18,  0,  0), #  28800     0 IRKT
        datetime(1994,  3, 26, 18,  0,  0), #  32400  3600 IRKST
        datetime(1994,  9, 24, 18,  0,  0), #  28800     0 IRKT
        datetime(1995,  3, 25, 18,  0,  0), #  32400  3600 IRKST
        datetime(1995,  9, 23, 18,  0,  0), #  28800     0 IRKT
        datetime(1996,  3, 30, 18,  0,  0), #  32400  3600 IRKST
        datetime(1996, 10, 26, 18,  0,  0), #  28800     0 IRKT
        datetime(1997,  3, 29, 18,  0,  0), #  32400  3600 IRKST
        datetime(1997, 10, 25, 18,  0,  0), #  28800     0 IRKT
        datetime(1998,  3, 28, 18,  0,  0), #  32400  3600 IRKST
        datetime(1998, 10, 24, 18,  0,  0), #  28800     0 IRKT
        datetime(1999,  3, 27, 18,  0,  0), #  32400  3600 IRKST
        datetime(1999, 10, 30, 18,  0,  0), #  28800     0 IRKT
        datetime(2000,  3, 25, 18,  0,  0), #  32400  3600 IRKST
        datetime(2000, 10, 28, 18,  0,  0), #  28800     0 IRKT
        datetime(2001,  3, 24, 18,  0,  0), #  32400  3600 IRKST
        datetime(2001, 10, 27, 18,  0,  0), #  28800     0 IRKT
        datetime(2002,  3, 30, 18,  0,  0), #  32400  3600 IRKST
        datetime(2002, 10, 26, 18,  0,  0), #  28800     0 IRKT
        datetime(2003,  3, 29, 18,  0,  0), #  32400  3600 IRKST
        datetime(2003, 10, 25, 18,  0,  0), #  28800     0 IRKT
        datetime(2004,  3, 27, 18,  0,  0), #  32400  3600 IRKST
        datetime(2004, 10, 30, 18,  0,  0), #  28800     0 IRKT
        datetime(2005,  3, 26, 18,  0,  0), #  32400  3600 IRKST
        datetime(2005, 10, 29, 18,  0,  0), #  28800     0 IRKT
        datetime(2006,  3, 25, 18,  0,  0), #  32400  3600 IRKST
        datetime(2006, 10, 28, 18,  0,  0), #  28800     0 IRKT
        datetime(2007,  3, 24, 18,  0,  0), #  32400  3600 IRKST
        datetime(2007, 10, 27, 18,  0,  0), #  28800     0 IRKT
        datetime(2008,  3, 29, 18,  0,  0), #  32400  3600 IRKST
        datetime(2008, 10, 25, 18,  0,  0), #  28800     0 IRKT
        datetime(2009,  3, 28, 18,  0,  0), #  32400  3600 IRKST
        datetime(2009, 10, 24, 18,  0,  0), #  28800     0 IRKT
        datetime(2010,  3, 27, 18,  0,  0), #  32400  3600 IRKST
        datetime(2010, 10, 30, 18,  0,  0), #  28800     0 IRKT
        datetime(2011,  3, 26, 18,  0,  0), #  32400  3600 IRKST
        datetime(2011, 10, 29, 18,  0,  0), #  28800     0 IRKT
        datetime(2012,  3, 24, 18,  0,  0), #  32400  3600 IRKST
        datetime(2012, 10, 27, 18,  0,  0), #  28800     0 IRKT
        datetime(2013,  3, 30, 18,  0,  0), #  32400  3600 IRKST
        datetime(2013, 10, 26, 18,  0,  0), #  28800     0 IRKT
        datetime(2014,  3, 29, 18,  0,  0), #  32400  3600 IRKST
        datetime(2014, 10, 25, 18,  0,  0), #  28800     0 IRKT
        datetime(2015,  3, 28, 18,  0,  0), #  32400  3600 IRKST
        datetime(2015, 10, 24, 18,  0,  0), #  28800     0 IRKT
        datetime(2016,  3, 26, 18,  0,  0), #  32400  3600 IRKST
        datetime(2016, 10, 29, 18,  0,  0), #  28800     0 IRKT
        datetime(2017,  3, 25, 18,  0,  0), #  32400  3600 IRKST
        datetime(2017, 10, 28, 18,  0,  0), #  28800     0 IRKT
        datetime(2018,  3, 24, 18,  0,  0), #  32400  3600 IRKST
        datetime(2018, 10, 27, 18,  0,  0), #  28800     0 IRKT
        datetime(2019,  3, 30, 18,  0,  0), #  32400  3600 IRKST
        datetime(2019, 10, 26, 18,  0,  0), #  28800     0 IRKT
        datetime(2020,  3, 28, 18,  0,  0), #  32400  3600 IRKST
        datetime(2020, 10, 24, 18,  0,  0), #  28800     0 IRKT
        datetime(2021,  3, 27, 18,  0,  0), #  32400  3600 IRKST
        datetime(2021, 10, 30, 18,  0,  0), #  28800     0 IRKT
        datetime(2022,  3, 26, 18,  0,  0), #  32400  3600 IRKST
        datetime(2022, 10, 29, 18,  0,  0), #  28800     0 IRKT
        datetime(2023,  3, 25, 18,  0,  0), #  32400  3600 IRKST
        datetime(2023, 10, 28, 18,  0,  0), #  28800     0 IRKT
        datetime(2024,  3, 30, 18,  0,  0), #  32400  3600 IRKST
        datetime(2024, 10, 26, 18,  0,  0), #  28800     0 IRKT
        datetime(2025,  3, 29, 18,  0,  0), #  32400  3600 IRKST
        datetime(2025, 10, 25, 18,  0,  0), #  28800     0 IRKT
        datetime(2026,  3, 28, 18,  0,  0), #  32400  3600 IRKST
        datetime(2026, 10, 24, 18,  0,  0), #  28800     0 IRKT
        datetime(2027,  3, 27, 18,  0,  0), #  32400  3600 IRKST
        datetime(2027, 10, 30, 18,  0,  0), #  28800     0 IRKT
        datetime(2028,  3, 25, 18,  0,  0), #  32400  3600 IRKST
        datetime(2028, 10, 28, 18,  0,  0), #  28800     0 IRKT
        datetime(2029,  3, 24, 18,  0,  0), #  32400  3600 IRKST
        datetime(2029, 10, 27, 18,  0,  0), #  28800     0 IRKT
        datetime(2030,  3, 30, 18,  0,  0), #  32400  3600 IRKST
        datetime(2030, 10, 26, 18,  0,  0), #  28800     0 IRKT
        datetime(2031,  3, 29, 18,  0,  0), #  32400  3600 IRKST
        datetime(2031, 10, 25, 18,  0,  0), #  28800     0 IRKT
        datetime(2032,  3, 27, 18,  0,  0), #  32400  3600 IRKST
        datetime(2032, 10, 30, 18,  0,  0), #  28800     0 IRKT
        datetime(2033,  3, 26, 18,  0,  0), #  32400  3600 IRKST
        datetime(2033, 10, 29, 18,  0,  0), #  28800     0 IRKT
        datetime(2034,  3, 25, 18,  0,  0), #  32400  3600 IRKST
        datetime(2034, 10, 28, 18,  0,  0), #  28800     0 IRKT
        datetime(2035,  3, 24, 18,  0,  0), #  32400  3600 IRKST
        datetime(2035, 10, 27, 18,  0,  0), #  28800     0 IRKT
        datetime(2036,  3, 29, 18,  0,  0), #  32400  3600 IRKST
        datetime(2036, 10, 25, 18,  0,  0), #  28800     0 IRKT
        datetime(2037,  3, 28, 18,  0,  0), #  32400  3600 IRKST
        datetime(2037, 10, 24, 18,  0,  0), #  28800     0 IRKT
        ]

    _transition_info = [
        ttinfo( 25040,      0,  'IMT'),
        ttinfo( 25200,      0, 'IRKT'),
        ttinfo( 28800,      0, 'IRKT'),
        ttinfo( 32400,   3600, 'IRKST'),
        ttinfo( 28800,      0, 'IRKT'),
        ttinfo( 32400,   3600, 'IRKST'),
        ttinfo( 28800,      0, 'IRKT'),
        ttinfo( 32400,   3600, 'IRKST'),
        ttinfo( 28800,      0, 'IRKT'),
        ttinfo( 32400,   3600, 'IRKST'),
        ttinfo( 28800,      0, 'IRKT'),
        ttinfo( 32400,   3600, 'IRKST'),
        ttinfo( 28800,      0, 'IRKT'),
        ttinfo( 32400,   3600, 'IRKST'),
        ttinfo( 28800,      0, 'IRKT'),
        ttinfo( 32400,   3600, 'IRKST'),
        ttinfo( 28800,      0, 'IRKT'),
        ttinfo( 32400,   3600, 'IRKST'),
        ttinfo( 28800,      0, 'IRKT'),
        ttinfo( 32400,   3600, 'IRKST'),
        ttinfo( 28800,      0, 'IRKT'),
        ttinfo( 32400,   3600, 'IRKST'),
        ttinfo( 28800,      0, 'IRKT'),
        ttinfo( 28800,      0, 'IRKST'),
        ttinfo( 25200,      0, 'IRKT'),
        ttinfo( 28800,      0, 'IRKT'),
        ttinfo( 32400,   3600, 'IRKST'),
        ttinfo( 28800,      0, 'IRKT'),
        ttinfo( 32400,   3600, 'IRKST'),
        ttinfo( 28800,      0, 'IRKT'),
        ttinfo( 32400,   3600, 'IRKST'),
        ttinfo( 28800,      0, 'IRKT'),
        ttinfo( 32400,   3600, 'IRKST'),
        ttinfo( 28800,      0, 'IRKT'),
        ttinfo( 32400,   3600, 'IRKST'),
        ttinfo( 28800,      0, 'IRKT'),
        ttinfo( 32400,   3600, 'IRKST'),
        ttinfo( 28800,      0, 'IRKT'),
        ttinfo( 32400,   3600, 'IRKST'),
        ttinfo( 28800,      0, 'IRKT'),
        ttinfo( 32400,   3600, 'IRKST'),
        ttinfo( 28800,      0, 'IRKT'),
        ttinfo( 32400,   3600, 'IRKST'),
        ttinfo( 28800,      0, 'IRKT'),
        ttinfo( 32400,   3600, 'IRKST'),
        ttinfo( 28800,      0, 'IRKT'),
        ttinfo( 32400,   3600, 'IRKST'),
        ttinfo( 28800,      0, 'IRKT'),
        ttinfo( 32400,   3600, 'IRKST'),
        ttinfo( 28800,      0, 'IRKT'),
        ttinfo( 32400,   3600, 'IRKST'),
        ttinfo( 28800,      0, 'IRKT'),
        ttinfo( 32400,   3600, 'IRKST'),
        ttinfo( 28800,      0, 'IRKT'),
        ttinfo( 32400,   3600, 'IRKST'),
        ttinfo( 28800,      0, 'IRKT'),
        ttinfo( 32400,   3600, 'IRKST'),
        ttinfo( 28800,      0, 'IRKT'),
        ttinfo( 32400,   3600, 'IRKST'),
        ttinfo( 28800,      0, 'IRKT'),
        ttinfo( 32400,   3600, 'IRKST'),
        ttinfo( 28800,      0, 'IRKT'),
        ttinfo( 32400,   3600, 'IRKST'),
        ttinfo( 28800,      0, 'IRKT'),
        ttinfo( 32400,   3600, 'IRKST'),
        ttinfo( 28800,      0, 'IRKT'),
        ttinfo( 32400,   3600, 'IRKST'),
        ttinfo( 28800,      0, 'IRKT'),
        ttinfo( 32400,   3600, 'IRKST'),
        ttinfo( 28800,      0, 'IRKT'),
        ttinfo( 32400,   3600, 'IRKST'),
        ttinfo( 28800,      0, 'IRKT'),
        ttinfo( 32400,   3600, 'IRKST'),
        ttinfo( 28800,      0, 'IRKT'),
        ttinfo( 32400,   3600, 'IRKST'),
        ttinfo( 28800,      0, 'IRKT'),
        ttinfo( 32400,   3600, 'IRKST'),
        ttinfo( 28800,      0, 'IRKT'),
        ttinfo( 32400,   3600, 'IRKST'),
        ttinfo( 28800,      0, 'IRKT'),
        ttinfo( 32400,   3600, 'IRKST'),
        ttinfo( 28800,      0, 'IRKT'),
        ttinfo( 32400,   3600, 'IRKST'),
        ttinfo( 28800,      0, 'IRKT'),
        ttinfo( 32400,   3600, 'IRKST'),
        ttinfo( 28800,      0, 'IRKT'),
        ttinfo( 32400,   3600, 'IRKST'),
        ttinfo( 28800,      0, 'IRKT'),
        ttinfo( 32400,   3600, 'IRKST'),
        ttinfo( 28800,      0, 'IRKT'),
        ttinfo( 32400,   3600, 'IRKST'),
        ttinfo( 28800,      0, 'IRKT'),
        ttinfo( 32400,   3600, 'IRKST'),
        ttinfo( 28800,      0, 'IRKT'),
        ttinfo( 32400,   3600, 'IRKST'),
        ttinfo( 28800,      0, 'IRKT'),
        ttinfo( 32400,   3600, 'IRKST'),
        ttinfo( 28800,      0, 'IRKT'),
        ttinfo( 32400,   3600, 'IRKST'),
        ttinfo( 28800,      0, 'IRKT'),
        ttinfo( 32400,   3600, 'IRKST'),
        ttinfo( 28800,      0, 'IRKT'),
        ttinfo( 32400,   3600, 'IRKST'),
        ttinfo( 28800,      0, 'IRKT'),
        ttinfo( 32400,   3600, 'IRKST'),
        ttinfo( 28800,      0, 'IRKT'),
        ttinfo( 32400,   3600, 'IRKST'),
        ttinfo( 28800,      0, 'IRKT'),
        ttinfo( 32400,   3600, 'IRKST'),
        ttinfo( 28800,      0, 'IRKT'),
        ttinfo( 32400,   3600, 'IRKST'),
        ttinfo( 28800,      0, 'IRKT'),
        ttinfo( 32400,   3600, 'IRKST'),
        ttinfo( 28800,      0, 'IRKT'),
        ttinfo( 32400,   3600, 'IRKST'),
        ttinfo( 28800,      0, 'IRKT'),
        ttinfo( 32400,   3600, 'IRKST'),
        ttinfo( 28800,      0, 'IRKT'),
        ]

Irkutsk = Irkutsk() # Singleton

