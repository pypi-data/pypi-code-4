'''
tzinfo timezone information for Asia/Sakhalin.

Generated from the Olson timezone database:
    ftp://elsie.nci.nih.gov/pub/tz*.tar.gz
'''

from pytz.tzinfo import DstTzInfo
from pytz.tzinfo import memorized_datetime as datetime
from pytz.tzinfo import memorized_ttinfo as ttinfo

class Sakhalin(DstTzInfo):
    '''Asia/Sakhalin timezone definition. See datetime.tzinfo for details'''

    _zone = 'Asia/Sakhalin'

    _utc_transition_times = [
        datetime(   1,  1,  1,  0,  0,  0), #  34248     0 LMT
        datetime(1905,  8, 22, 14, 29, 12), #  32400     0 CJT
        datetime(1937, 12, 31, 15,  0,  0), #  32400     0 JST
        datetime(1945,  8, 24, 15,  0,  0), #  39600     0 SAKT
        datetime(1981,  3, 31, 13,  0,  0), #  43200  3600 SAKST
        datetime(1981,  9, 30, 12,  0,  0), #  39600     0 SAKT
        datetime(1982,  3, 31, 13,  0,  0), #  43200  3600 SAKST
        datetime(1982,  9, 30, 12,  0,  0), #  39600     0 SAKT
        datetime(1983,  3, 31, 13,  0,  0), #  43200  3600 SAKST
        datetime(1983,  9, 30, 12,  0,  0), #  39600     0 SAKT
        datetime(1984,  3, 31, 13,  0,  0), #  43200  3600 SAKST
        datetime(1984,  9, 29, 15,  0,  0), #  39600     0 SAKT
        datetime(1985,  3, 30, 15,  0,  0), #  43200  3600 SAKST
        datetime(1985,  9, 28, 15,  0,  0), #  39600     0 SAKT
        datetime(1986,  3, 29, 15,  0,  0), #  43200  3600 SAKST
        datetime(1986,  9, 27, 15,  0,  0), #  39600     0 SAKT
        datetime(1987,  3, 28, 15,  0,  0), #  43200  3600 SAKST
        datetime(1987,  9, 26, 15,  0,  0), #  39600     0 SAKT
        datetime(1988,  3, 26, 15,  0,  0), #  43200  3600 SAKST
        datetime(1988,  9, 24, 15,  0,  0), #  39600     0 SAKT
        datetime(1989,  3, 25, 15,  0,  0), #  43200  3600 SAKST
        datetime(1989,  9, 23, 15,  0,  0), #  39600     0 SAKT
        datetime(1990,  3, 24, 15,  0,  0), #  43200  3600 SAKST
        datetime(1990,  9, 29, 15,  0,  0), #  39600     0 SAKT
        datetime(1991,  3, 30, 15,  0,  0), #  39600     0 SAKST
        datetime(1991,  9, 28, 16,  0,  0), #  36000     0 SAKT
        datetime(1992,  1, 18, 16,  0,  0), #  39600     0 SAKT
        datetime(1992,  3, 28, 12,  0,  0), #  43200  3600 SAKST
        datetime(1992,  9, 26, 11,  0,  0), #  39600     0 SAKT
        datetime(1993,  3, 27, 15,  0,  0), #  43200  3600 SAKST
        datetime(1993,  9, 25, 15,  0,  0), #  39600     0 SAKT
        datetime(1994,  3, 26, 15,  0,  0), #  43200  3600 SAKST
        datetime(1994,  9, 24, 15,  0,  0), #  39600     0 SAKT
        datetime(1995,  3, 25, 15,  0,  0), #  43200  3600 SAKST
        datetime(1995,  9, 23, 15,  0,  0), #  39600     0 SAKT
        datetime(1996,  3, 30, 15,  0,  0), #  43200  3600 SAKST
        datetime(1996, 10, 26, 15,  0,  0), #  39600     0 SAKT
        datetime(1997,  3, 29, 15,  0,  0), #  39600     0 SAKST
        datetime(1997, 10, 25, 16,  0,  0), #  36000     0 SAKT
        datetime(1998,  3, 28, 16,  0,  0), #  39600  3600 SAKST
        datetime(1998, 10, 24, 16,  0,  0), #  36000     0 SAKT
        datetime(1999,  3, 27, 16,  0,  0), #  39600  3600 SAKST
        datetime(1999, 10, 30, 16,  0,  0), #  36000     0 SAKT
        datetime(2000,  3, 25, 16,  0,  0), #  39600  3600 SAKST
        datetime(2000, 10, 28, 16,  0,  0), #  36000     0 SAKT
        datetime(2001,  3, 24, 16,  0,  0), #  39600  3600 SAKST
        datetime(2001, 10, 27, 16,  0,  0), #  36000     0 SAKT
        datetime(2002,  3, 30, 16,  0,  0), #  39600  3600 SAKST
        datetime(2002, 10, 26, 16,  0,  0), #  36000     0 SAKT
        datetime(2003,  3, 29, 16,  0,  0), #  39600  3600 SAKST
        datetime(2003, 10, 25, 16,  0,  0), #  36000     0 SAKT
        datetime(2004,  3, 27, 16,  0,  0), #  39600  3600 SAKST
        datetime(2004, 10, 30, 16,  0,  0), #  36000     0 SAKT
        datetime(2005,  3, 26, 16,  0,  0), #  39600  3600 SAKST
        datetime(2005, 10, 29, 16,  0,  0), #  36000     0 SAKT
        datetime(2006,  3, 25, 16,  0,  0), #  39600  3600 SAKST
        datetime(2006, 10, 28, 16,  0,  0), #  36000     0 SAKT
        datetime(2007,  3, 24, 16,  0,  0), #  39600  3600 SAKST
        datetime(2007, 10, 27, 16,  0,  0), #  36000     0 SAKT
        datetime(2008,  3, 29, 16,  0,  0), #  39600  3600 SAKST
        datetime(2008, 10, 25, 16,  0,  0), #  36000     0 SAKT
        datetime(2009,  3, 28, 16,  0,  0), #  39600  3600 SAKST
        datetime(2009, 10, 24, 16,  0,  0), #  36000     0 SAKT
        datetime(2010,  3, 27, 16,  0,  0), #  39600  3600 SAKST
        datetime(2010, 10, 30, 16,  0,  0), #  36000     0 SAKT
        datetime(2011,  3, 26, 16,  0,  0), #  39600  3600 SAKST
        datetime(2011, 10, 29, 16,  0,  0), #  36000     0 SAKT
        datetime(2012,  3, 24, 16,  0,  0), #  39600  3600 SAKST
        datetime(2012, 10, 27, 16,  0,  0), #  36000     0 SAKT
        datetime(2013,  3, 30, 16,  0,  0), #  39600  3600 SAKST
        datetime(2013, 10, 26, 16,  0,  0), #  36000     0 SAKT
        datetime(2014,  3, 29, 16,  0,  0), #  39600  3600 SAKST
        datetime(2014, 10, 25, 16,  0,  0), #  36000     0 SAKT
        datetime(2015,  3, 28, 16,  0,  0), #  39600  3600 SAKST
        datetime(2015, 10, 24, 16,  0,  0), #  36000     0 SAKT
        datetime(2016,  3, 26, 16,  0,  0), #  39600  3600 SAKST
        datetime(2016, 10, 29, 16,  0,  0), #  36000     0 SAKT
        datetime(2017,  3, 25, 16,  0,  0), #  39600  3600 SAKST
        datetime(2017, 10, 28, 16,  0,  0), #  36000     0 SAKT
        datetime(2018,  3, 24, 16,  0,  0), #  39600  3600 SAKST
        datetime(2018, 10, 27, 16,  0,  0), #  36000     0 SAKT
        datetime(2019,  3, 30, 16,  0,  0), #  39600  3600 SAKST
        datetime(2019, 10, 26, 16,  0,  0), #  36000     0 SAKT
        datetime(2020,  3, 28, 16,  0,  0), #  39600  3600 SAKST
        datetime(2020, 10, 24, 16,  0,  0), #  36000     0 SAKT
        datetime(2021,  3, 27, 16,  0,  0), #  39600  3600 SAKST
        datetime(2021, 10, 30, 16,  0,  0), #  36000     0 SAKT
        datetime(2022,  3, 26, 16,  0,  0), #  39600  3600 SAKST
        datetime(2022, 10, 29, 16,  0,  0), #  36000     0 SAKT
        datetime(2023,  3, 25, 16,  0,  0), #  39600  3600 SAKST
        datetime(2023, 10, 28, 16,  0,  0), #  36000     0 SAKT
        datetime(2024,  3, 30, 16,  0,  0), #  39600  3600 SAKST
        datetime(2024, 10, 26, 16,  0,  0), #  36000     0 SAKT
        datetime(2025,  3, 29, 16,  0,  0), #  39600  3600 SAKST
        datetime(2025, 10, 25, 16,  0,  0), #  36000     0 SAKT
        datetime(2026,  3, 28, 16,  0,  0), #  39600  3600 SAKST
        datetime(2026, 10, 24, 16,  0,  0), #  36000     0 SAKT
        datetime(2027,  3, 27, 16,  0,  0), #  39600  3600 SAKST
        datetime(2027, 10, 30, 16,  0,  0), #  36000     0 SAKT
        datetime(2028,  3, 25, 16,  0,  0), #  39600  3600 SAKST
        datetime(2028, 10, 28, 16,  0,  0), #  36000     0 SAKT
        datetime(2029,  3, 24, 16,  0,  0), #  39600  3600 SAKST
        datetime(2029, 10, 27, 16,  0,  0), #  36000     0 SAKT
        datetime(2030,  3, 30, 16,  0,  0), #  39600  3600 SAKST
        datetime(2030, 10, 26, 16,  0,  0), #  36000     0 SAKT
        datetime(2031,  3, 29, 16,  0,  0), #  39600  3600 SAKST
        datetime(2031, 10, 25, 16,  0,  0), #  36000     0 SAKT
        datetime(2032,  3, 27, 16,  0,  0), #  39600  3600 SAKST
        datetime(2032, 10, 30, 16,  0,  0), #  36000     0 SAKT
        datetime(2033,  3, 26, 16,  0,  0), #  39600  3600 SAKST
        datetime(2033, 10, 29, 16,  0,  0), #  36000     0 SAKT
        datetime(2034,  3, 25, 16,  0,  0), #  39600  3600 SAKST
        datetime(2034, 10, 28, 16,  0,  0), #  36000     0 SAKT
        datetime(2035,  3, 24, 16,  0,  0), #  39600  3600 SAKST
        datetime(2035, 10, 27, 16,  0,  0), #  36000     0 SAKT
        datetime(2036,  3, 29, 16,  0,  0), #  39600  3600 SAKST
        datetime(2036, 10, 25, 16,  0,  0), #  36000     0 SAKT
        datetime(2037,  3, 28, 16,  0,  0), #  39600  3600 SAKST
        datetime(2037, 10, 24, 16,  0,  0), #  36000     0 SAKT
        ]

    _transition_info = [
        ttinfo( 34248,      0,  'LMT'),
        ttinfo( 32400,      0,  'CJT'),
        ttinfo( 32400,      0,  'JST'),
        ttinfo( 39600,      0, 'SAKT'),
        ttinfo( 43200,   3600, 'SAKST'),
        ttinfo( 39600,      0, 'SAKT'),
        ttinfo( 43200,   3600, 'SAKST'),
        ttinfo( 39600,      0, 'SAKT'),
        ttinfo( 43200,   3600, 'SAKST'),
        ttinfo( 39600,      0, 'SAKT'),
        ttinfo( 43200,   3600, 'SAKST'),
        ttinfo( 39600,      0, 'SAKT'),
        ttinfo( 43200,   3600, 'SAKST'),
        ttinfo( 39600,      0, 'SAKT'),
        ttinfo( 43200,   3600, 'SAKST'),
        ttinfo( 39600,      0, 'SAKT'),
        ttinfo( 43200,   3600, 'SAKST'),
        ttinfo( 39600,      0, 'SAKT'),
        ttinfo( 43200,   3600, 'SAKST'),
        ttinfo( 39600,      0, 'SAKT'),
        ttinfo( 43200,   3600, 'SAKST'),
        ttinfo( 39600,      0, 'SAKT'),
        ttinfo( 43200,   3600, 'SAKST'),
        ttinfo( 39600,      0, 'SAKT'),
        ttinfo( 39600,      0, 'SAKST'),
        ttinfo( 36000,      0, 'SAKT'),
        ttinfo( 39600,      0, 'SAKT'),
        ttinfo( 43200,   3600, 'SAKST'),
        ttinfo( 39600,      0, 'SAKT'),
        ttinfo( 43200,   3600, 'SAKST'),
        ttinfo( 39600,      0, 'SAKT'),
        ttinfo( 43200,   3600, 'SAKST'),
        ttinfo( 39600,      0, 'SAKT'),
        ttinfo( 43200,   3600, 'SAKST'),
        ttinfo( 39600,      0, 'SAKT'),
        ttinfo( 43200,   3600, 'SAKST'),
        ttinfo( 39600,      0, 'SAKT'),
        ttinfo( 39600,      0, 'SAKST'),
        ttinfo( 36000,      0, 'SAKT'),
        ttinfo( 39600,   3600, 'SAKST'),
        ttinfo( 36000,      0, 'SAKT'),
        ttinfo( 39600,   3600, 'SAKST'),
        ttinfo( 36000,      0, 'SAKT'),
        ttinfo( 39600,   3600, 'SAKST'),
        ttinfo( 36000,      0, 'SAKT'),
        ttinfo( 39600,   3600, 'SAKST'),
        ttinfo( 36000,      0, 'SAKT'),
        ttinfo( 39600,   3600, 'SAKST'),
        ttinfo( 36000,      0, 'SAKT'),
        ttinfo( 39600,   3600, 'SAKST'),
        ttinfo( 36000,      0, 'SAKT'),
        ttinfo( 39600,   3600, 'SAKST'),
        ttinfo( 36000,      0, 'SAKT'),
        ttinfo( 39600,   3600, 'SAKST'),
        ttinfo( 36000,      0, 'SAKT'),
        ttinfo( 39600,   3600, 'SAKST'),
        ttinfo( 36000,      0, 'SAKT'),
        ttinfo( 39600,   3600, 'SAKST'),
        ttinfo( 36000,      0, 'SAKT'),
        ttinfo( 39600,   3600, 'SAKST'),
        ttinfo( 36000,      0, 'SAKT'),
        ttinfo( 39600,   3600, 'SAKST'),
        ttinfo( 36000,      0, 'SAKT'),
        ttinfo( 39600,   3600, 'SAKST'),
        ttinfo( 36000,      0, 'SAKT'),
        ttinfo( 39600,   3600, 'SAKST'),
        ttinfo( 36000,      0, 'SAKT'),
        ttinfo( 39600,   3600, 'SAKST'),
        ttinfo( 36000,      0, 'SAKT'),
        ttinfo( 39600,   3600, 'SAKST'),
        ttinfo( 36000,      0, 'SAKT'),
        ttinfo( 39600,   3600, 'SAKST'),
        ttinfo( 36000,      0, 'SAKT'),
        ttinfo( 39600,   3600, 'SAKST'),
        ttinfo( 36000,      0, 'SAKT'),
        ttinfo( 39600,   3600, 'SAKST'),
        ttinfo( 36000,      0, 'SAKT'),
        ttinfo( 39600,   3600, 'SAKST'),
        ttinfo( 36000,      0, 'SAKT'),
        ttinfo( 39600,   3600, 'SAKST'),
        ttinfo( 36000,      0, 'SAKT'),
        ttinfo( 39600,   3600, 'SAKST'),
        ttinfo( 36000,      0, 'SAKT'),
        ttinfo( 39600,   3600, 'SAKST'),
        ttinfo( 36000,      0, 'SAKT'),
        ttinfo( 39600,   3600, 'SAKST'),
        ttinfo( 36000,      0, 'SAKT'),
        ttinfo( 39600,   3600, 'SAKST'),
        ttinfo( 36000,      0, 'SAKT'),
        ttinfo( 39600,   3600, 'SAKST'),
        ttinfo( 36000,      0, 'SAKT'),
        ttinfo( 39600,   3600, 'SAKST'),
        ttinfo( 36000,      0, 'SAKT'),
        ttinfo( 39600,   3600, 'SAKST'),
        ttinfo( 36000,      0, 'SAKT'),
        ttinfo( 39600,   3600, 'SAKST'),
        ttinfo( 36000,      0, 'SAKT'),
        ttinfo( 39600,   3600, 'SAKST'),
        ttinfo( 36000,      0, 'SAKT'),
        ttinfo( 39600,   3600, 'SAKST'),
        ttinfo( 36000,      0, 'SAKT'),
        ttinfo( 39600,   3600, 'SAKST'),
        ttinfo( 36000,      0, 'SAKT'),
        ttinfo( 39600,   3600, 'SAKST'),
        ttinfo( 36000,      0, 'SAKT'),
        ttinfo( 39600,   3600, 'SAKST'),
        ttinfo( 36000,      0, 'SAKT'),
        ttinfo( 39600,   3600, 'SAKST'),
        ttinfo( 36000,      0, 'SAKT'),
        ttinfo( 39600,   3600, 'SAKST'),
        ttinfo( 36000,      0, 'SAKT'),
        ttinfo( 39600,   3600, 'SAKST'),
        ttinfo( 36000,      0, 'SAKT'),
        ttinfo( 39600,   3600, 'SAKST'),
        ttinfo( 36000,      0, 'SAKT'),
        ttinfo( 39600,   3600, 'SAKST'),
        ttinfo( 36000,      0, 'SAKT'),
        ttinfo( 39600,   3600, 'SAKST'),
        ttinfo( 36000,      0, 'SAKT'),
        ]

Sakhalin = Sakhalin() # Singleton

