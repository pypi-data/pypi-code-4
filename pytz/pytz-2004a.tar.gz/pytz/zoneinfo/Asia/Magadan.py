'''
tzinfo timezone information for Asia/Magadan.

Generated from the Olson timezone database:
    ftp://elsie.nci.nih.gov/pub/tz*.tar.gz
'''

from pytz.tzinfo import DstTzInfo
from pytz.tzinfo import memorized_datetime as datetime
from pytz.tzinfo import memorized_ttinfo as ttinfo

class Magadan(DstTzInfo):
    '''Asia/Magadan timezone definition. See datetime.tzinfo for details'''

    _zone = 'Asia/Magadan'

    _utc_transition_times = [
        datetime(   1,  1,  1,  0,  0,  0), #  36192     0 LMT
        datetime(1924,  5,  1, 13, 56, 48), #  36000     0 MAGT
        datetime(1930,  6, 20, 14,  0,  0), #  39600     0 MAGT
        datetime(1981,  3, 31, 13,  0,  0), #  43200  3600 MAGST
        datetime(1981,  9, 30, 12,  0,  0), #  39600     0 MAGT
        datetime(1982,  3, 31, 13,  0,  0), #  43200  3600 MAGST
        datetime(1982,  9, 30, 12,  0,  0), #  39600     0 MAGT
        datetime(1983,  3, 31, 13,  0,  0), #  43200  3600 MAGST
        datetime(1983,  9, 30, 12,  0,  0), #  39600     0 MAGT
        datetime(1984,  3, 31, 13,  0,  0), #  43200  3600 MAGST
        datetime(1984,  9, 29, 15,  0,  0), #  39600     0 MAGT
        datetime(1985,  3, 30, 15,  0,  0), #  43200  3600 MAGST
        datetime(1985,  9, 28, 15,  0,  0), #  39600     0 MAGT
        datetime(1986,  3, 29, 15,  0,  0), #  43200  3600 MAGST
        datetime(1986,  9, 27, 15,  0,  0), #  39600     0 MAGT
        datetime(1987,  3, 28, 15,  0,  0), #  43200  3600 MAGST
        datetime(1987,  9, 26, 15,  0,  0), #  39600     0 MAGT
        datetime(1988,  3, 26, 15,  0,  0), #  43200  3600 MAGST
        datetime(1988,  9, 24, 15,  0,  0), #  39600     0 MAGT
        datetime(1989,  3, 25, 15,  0,  0), #  43200  3600 MAGST
        datetime(1989,  9, 23, 15,  0,  0), #  39600     0 MAGT
        datetime(1990,  3, 24, 15,  0,  0), #  43200  3600 MAGST
        datetime(1990,  9, 29, 15,  0,  0), #  39600     0 MAGT
        datetime(1991,  3, 30, 15,  0,  0), #  39600     0 MAGST
        datetime(1991,  9, 28, 16,  0,  0), #  36000     0 MAGT
        datetime(1992,  1, 18, 16,  0,  0), #  39600     0 MAGT
        datetime(1992,  3, 28, 12,  0,  0), #  43200  3600 MAGST
        datetime(1992,  9, 26, 11,  0,  0), #  39600     0 MAGT
        datetime(1993,  3, 27, 15,  0,  0), #  43200  3600 MAGST
        datetime(1993,  9, 25, 15,  0,  0), #  39600     0 MAGT
        datetime(1994,  3, 26, 15,  0,  0), #  43200  3600 MAGST
        datetime(1994,  9, 24, 15,  0,  0), #  39600     0 MAGT
        datetime(1995,  3, 25, 15,  0,  0), #  43200  3600 MAGST
        datetime(1995,  9, 23, 15,  0,  0), #  39600     0 MAGT
        datetime(1996,  3, 30, 15,  0,  0), #  43200  3600 MAGST
        datetime(1996, 10, 26, 15,  0,  0), #  39600     0 MAGT
        datetime(1997,  3, 29, 15,  0,  0), #  43200  3600 MAGST
        datetime(1997, 10, 25, 15,  0,  0), #  39600     0 MAGT
        datetime(1998,  3, 28, 15,  0,  0), #  43200  3600 MAGST
        datetime(1998, 10, 24, 15,  0,  0), #  39600     0 MAGT
        datetime(1999,  3, 27, 15,  0,  0), #  43200  3600 MAGST
        datetime(1999, 10, 30, 15,  0,  0), #  39600     0 MAGT
        datetime(2000,  3, 25, 15,  0,  0), #  43200  3600 MAGST
        datetime(2000, 10, 28, 15,  0,  0), #  39600     0 MAGT
        datetime(2001,  3, 24, 15,  0,  0), #  43200  3600 MAGST
        datetime(2001, 10, 27, 15,  0,  0), #  39600     0 MAGT
        datetime(2002,  3, 30, 15,  0,  0), #  43200  3600 MAGST
        datetime(2002, 10, 26, 15,  0,  0), #  39600     0 MAGT
        datetime(2003,  3, 29, 15,  0,  0), #  43200  3600 MAGST
        datetime(2003, 10, 25, 15,  0,  0), #  39600     0 MAGT
        datetime(2004,  3, 27, 15,  0,  0), #  43200  3600 MAGST
        datetime(2004, 10, 30, 15,  0,  0), #  39600     0 MAGT
        datetime(2005,  3, 26, 15,  0,  0), #  43200  3600 MAGST
        datetime(2005, 10, 29, 15,  0,  0), #  39600     0 MAGT
        datetime(2006,  3, 25, 15,  0,  0), #  43200  3600 MAGST
        datetime(2006, 10, 28, 15,  0,  0), #  39600     0 MAGT
        datetime(2007,  3, 24, 15,  0,  0), #  43200  3600 MAGST
        datetime(2007, 10, 27, 15,  0,  0), #  39600     0 MAGT
        datetime(2008,  3, 29, 15,  0,  0), #  43200  3600 MAGST
        datetime(2008, 10, 25, 15,  0,  0), #  39600     0 MAGT
        datetime(2009,  3, 28, 15,  0,  0), #  43200  3600 MAGST
        datetime(2009, 10, 24, 15,  0,  0), #  39600     0 MAGT
        datetime(2010,  3, 27, 15,  0,  0), #  43200  3600 MAGST
        datetime(2010, 10, 30, 15,  0,  0), #  39600     0 MAGT
        datetime(2011,  3, 26, 15,  0,  0), #  43200  3600 MAGST
        datetime(2011, 10, 29, 15,  0,  0), #  39600     0 MAGT
        datetime(2012,  3, 24, 15,  0,  0), #  43200  3600 MAGST
        datetime(2012, 10, 27, 15,  0,  0), #  39600     0 MAGT
        datetime(2013,  3, 30, 15,  0,  0), #  43200  3600 MAGST
        datetime(2013, 10, 26, 15,  0,  0), #  39600     0 MAGT
        datetime(2014,  3, 29, 15,  0,  0), #  43200  3600 MAGST
        datetime(2014, 10, 25, 15,  0,  0), #  39600     0 MAGT
        datetime(2015,  3, 28, 15,  0,  0), #  43200  3600 MAGST
        datetime(2015, 10, 24, 15,  0,  0), #  39600     0 MAGT
        datetime(2016,  3, 26, 15,  0,  0), #  43200  3600 MAGST
        datetime(2016, 10, 29, 15,  0,  0), #  39600     0 MAGT
        datetime(2017,  3, 25, 15,  0,  0), #  43200  3600 MAGST
        datetime(2017, 10, 28, 15,  0,  0), #  39600     0 MAGT
        datetime(2018,  3, 24, 15,  0,  0), #  43200  3600 MAGST
        datetime(2018, 10, 27, 15,  0,  0), #  39600     0 MAGT
        datetime(2019,  3, 30, 15,  0,  0), #  43200  3600 MAGST
        datetime(2019, 10, 26, 15,  0,  0), #  39600     0 MAGT
        datetime(2020,  3, 28, 15,  0,  0), #  43200  3600 MAGST
        datetime(2020, 10, 24, 15,  0,  0), #  39600     0 MAGT
        datetime(2021,  3, 27, 15,  0,  0), #  43200  3600 MAGST
        datetime(2021, 10, 30, 15,  0,  0), #  39600     0 MAGT
        datetime(2022,  3, 26, 15,  0,  0), #  43200  3600 MAGST
        datetime(2022, 10, 29, 15,  0,  0), #  39600     0 MAGT
        datetime(2023,  3, 25, 15,  0,  0), #  43200  3600 MAGST
        datetime(2023, 10, 28, 15,  0,  0), #  39600     0 MAGT
        datetime(2024,  3, 30, 15,  0,  0), #  43200  3600 MAGST
        datetime(2024, 10, 26, 15,  0,  0), #  39600     0 MAGT
        datetime(2025,  3, 29, 15,  0,  0), #  43200  3600 MAGST
        datetime(2025, 10, 25, 15,  0,  0), #  39600     0 MAGT
        datetime(2026,  3, 28, 15,  0,  0), #  43200  3600 MAGST
        datetime(2026, 10, 24, 15,  0,  0), #  39600     0 MAGT
        datetime(2027,  3, 27, 15,  0,  0), #  43200  3600 MAGST
        datetime(2027, 10, 30, 15,  0,  0), #  39600     0 MAGT
        datetime(2028,  3, 25, 15,  0,  0), #  43200  3600 MAGST
        datetime(2028, 10, 28, 15,  0,  0), #  39600     0 MAGT
        datetime(2029,  3, 24, 15,  0,  0), #  43200  3600 MAGST
        datetime(2029, 10, 27, 15,  0,  0), #  39600     0 MAGT
        datetime(2030,  3, 30, 15,  0,  0), #  43200  3600 MAGST
        datetime(2030, 10, 26, 15,  0,  0), #  39600     0 MAGT
        datetime(2031,  3, 29, 15,  0,  0), #  43200  3600 MAGST
        datetime(2031, 10, 25, 15,  0,  0), #  39600     0 MAGT
        datetime(2032,  3, 27, 15,  0,  0), #  43200  3600 MAGST
        datetime(2032, 10, 30, 15,  0,  0), #  39600     0 MAGT
        datetime(2033,  3, 26, 15,  0,  0), #  43200  3600 MAGST
        datetime(2033, 10, 29, 15,  0,  0), #  39600     0 MAGT
        datetime(2034,  3, 25, 15,  0,  0), #  43200  3600 MAGST
        datetime(2034, 10, 28, 15,  0,  0), #  39600     0 MAGT
        datetime(2035,  3, 24, 15,  0,  0), #  43200  3600 MAGST
        datetime(2035, 10, 27, 15,  0,  0), #  39600     0 MAGT
        datetime(2036,  3, 29, 15,  0,  0), #  43200  3600 MAGST
        datetime(2036, 10, 25, 15,  0,  0), #  39600     0 MAGT
        datetime(2037,  3, 28, 15,  0,  0), #  43200  3600 MAGST
        datetime(2037, 10, 24, 15,  0,  0), #  39600     0 MAGT
        ]

    _transition_info = [
        ttinfo( 36192,      0,  'LMT'),
        ttinfo( 36000,      0, 'MAGT'),
        ttinfo( 39600,      0, 'MAGT'),
        ttinfo( 43200,   3600, 'MAGST'),
        ttinfo( 39600,      0, 'MAGT'),
        ttinfo( 43200,   3600, 'MAGST'),
        ttinfo( 39600,      0, 'MAGT'),
        ttinfo( 43200,   3600, 'MAGST'),
        ttinfo( 39600,      0, 'MAGT'),
        ttinfo( 43200,   3600, 'MAGST'),
        ttinfo( 39600,      0, 'MAGT'),
        ttinfo( 43200,   3600, 'MAGST'),
        ttinfo( 39600,      0, 'MAGT'),
        ttinfo( 43200,   3600, 'MAGST'),
        ttinfo( 39600,      0, 'MAGT'),
        ttinfo( 43200,   3600, 'MAGST'),
        ttinfo( 39600,      0, 'MAGT'),
        ttinfo( 43200,   3600, 'MAGST'),
        ttinfo( 39600,      0, 'MAGT'),
        ttinfo( 43200,   3600, 'MAGST'),
        ttinfo( 39600,      0, 'MAGT'),
        ttinfo( 43200,   3600, 'MAGST'),
        ttinfo( 39600,      0, 'MAGT'),
        ttinfo( 39600,      0, 'MAGST'),
        ttinfo( 36000,      0, 'MAGT'),
        ttinfo( 39600,      0, 'MAGT'),
        ttinfo( 43200,   3600, 'MAGST'),
        ttinfo( 39600,      0, 'MAGT'),
        ttinfo( 43200,   3600, 'MAGST'),
        ttinfo( 39600,      0, 'MAGT'),
        ttinfo( 43200,   3600, 'MAGST'),
        ttinfo( 39600,      0, 'MAGT'),
        ttinfo( 43200,   3600, 'MAGST'),
        ttinfo( 39600,      0, 'MAGT'),
        ttinfo( 43200,   3600, 'MAGST'),
        ttinfo( 39600,      0, 'MAGT'),
        ttinfo( 43200,   3600, 'MAGST'),
        ttinfo( 39600,      0, 'MAGT'),
        ttinfo( 43200,   3600, 'MAGST'),
        ttinfo( 39600,      0, 'MAGT'),
        ttinfo( 43200,   3600, 'MAGST'),
        ttinfo( 39600,      0, 'MAGT'),
        ttinfo( 43200,   3600, 'MAGST'),
        ttinfo( 39600,      0, 'MAGT'),
        ttinfo( 43200,   3600, 'MAGST'),
        ttinfo( 39600,      0, 'MAGT'),
        ttinfo( 43200,   3600, 'MAGST'),
        ttinfo( 39600,      0, 'MAGT'),
        ttinfo( 43200,   3600, 'MAGST'),
        ttinfo( 39600,      0, 'MAGT'),
        ttinfo( 43200,   3600, 'MAGST'),
        ttinfo( 39600,      0, 'MAGT'),
        ttinfo( 43200,   3600, 'MAGST'),
        ttinfo( 39600,      0, 'MAGT'),
        ttinfo( 43200,   3600, 'MAGST'),
        ttinfo( 39600,      0, 'MAGT'),
        ttinfo( 43200,   3600, 'MAGST'),
        ttinfo( 39600,      0, 'MAGT'),
        ttinfo( 43200,   3600, 'MAGST'),
        ttinfo( 39600,      0, 'MAGT'),
        ttinfo( 43200,   3600, 'MAGST'),
        ttinfo( 39600,      0, 'MAGT'),
        ttinfo( 43200,   3600, 'MAGST'),
        ttinfo( 39600,      0, 'MAGT'),
        ttinfo( 43200,   3600, 'MAGST'),
        ttinfo( 39600,      0, 'MAGT'),
        ttinfo( 43200,   3600, 'MAGST'),
        ttinfo( 39600,      0, 'MAGT'),
        ttinfo( 43200,   3600, 'MAGST'),
        ttinfo( 39600,      0, 'MAGT'),
        ttinfo( 43200,   3600, 'MAGST'),
        ttinfo( 39600,      0, 'MAGT'),
        ttinfo( 43200,   3600, 'MAGST'),
        ttinfo( 39600,      0, 'MAGT'),
        ttinfo( 43200,   3600, 'MAGST'),
        ttinfo( 39600,      0, 'MAGT'),
        ttinfo( 43200,   3600, 'MAGST'),
        ttinfo( 39600,      0, 'MAGT'),
        ttinfo( 43200,   3600, 'MAGST'),
        ttinfo( 39600,      0, 'MAGT'),
        ttinfo( 43200,   3600, 'MAGST'),
        ttinfo( 39600,      0, 'MAGT'),
        ttinfo( 43200,   3600, 'MAGST'),
        ttinfo( 39600,      0, 'MAGT'),
        ttinfo( 43200,   3600, 'MAGST'),
        ttinfo( 39600,      0, 'MAGT'),
        ttinfo( 43200,   3600, 'MAGST'),
        ttinfo( 39600,      0, 'MAGT'),
        ttinfo( 43200,   3600, 'MAGST'),
        ttinfo( 39600,      0, 'MAGT'),
        ttinfo( 43200,   3600, 'MAGST'),
        ttinfo( 39600,      0, 'MAGT'),
        ttinfo( 43200,   3600, 'MAGST'),
        ttinfo( 39600,      0, 'MAGT'),
        ttinfo( 43200,   3600, 'MAGST'),
        ttinfo( 39600,      0, 'MAGT'),
        ttinfo( 43200,   3600, 'MAGST'),
        ttinfo( 39600,      0, 'MAGT'),
        ttinfo( 43200,   3600, 'MAGST'),
        ttinfo( 39600,      0, 'MAGT'),
        ttinfo( 43200,   3600, 'MAGST'),
        ttinfo( 39600,      0, 'MAGT'),
        ttinfo( 43200,   3600, 'MAGST'),
        ttinfo( 39600,      0, 'MAGT'),
        ttinfo( 43200,   3600, 'MAGST'),
        ttinfo( 39600,      0, 'MAGT'),
        ttinfo( 43200,   3600, 'MAGST'),
        ttinfo( 39600,      0, 'MAGT'),
        ttinfo( 43200,   3600, 'MAGST'),
        ttinfo( 39600,      0, 'MAGT'),
        ttinfo( 43200,   3600, 'MAGST'),
        ttinfo( 39600,      0, 'MAGT'),
        ttinfo( 43200,   3600, 'MAGST'),
        ttinfo( 39600,      0, 'MAGT'),
        ttinfo( 43200,   3600, 'MAGST'),
        ttinfo( 39600,      0, 'MAGT'),
        ttinfo( 43200,   3600, 'MAGST'),
        ttinfo( 39600,      0, 'MAGT'),
        ]

Magadan = Magadan() # Singleton

