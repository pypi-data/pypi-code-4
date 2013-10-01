'''
tzinfo timezone information for Antarctica/South_Pole.

Generated from the Olson timezone database:
    ftp://elsie.nci.nih.gov/pub/tz*.tar.gz
'''

from pytz.tzinfo import DstTzInfo
from pytz.tzinfo import memorized_datetime as datetime
from pytz.tzinfo import memorized_ttinfo as ttinfo

class South_Pole(DstTzInfo):
    '''Antarctica/South_Pole timezone definition. See datetime.tzinfo for details'''

    _zone = 'Antarctica/South_Pole'

    _utc_transition_times = [
        datetime(   1,  1,  1,  0,  0,  0), #      0     0 zzz
        datetime(1956,  1,  1,  0,  0,  0), #  43200     0 NZST
        datetime(1974, 11,  2, 14,  0,  0), #  46800  3600 NZDT
        datetime(1975,  2, 22, 14,  0,  0), #  43200     0 NZST
        datetime(1975, 10, 25, 14,  0,  0), #  46800  3600 NZDT
        datetime(1976,  3,  6, 14,  0,  0), #  43200     0 NZST
        datetime(1976, 10, 30, 14,  0,  0), #  46800  3600 NZDT
        datetime(1977,  3,  5, 14,  0,  0), #  43200     0 NZST
        datetime(1977, 10, 29, 14,  0,  0), #  46800  3600 NZDT
        datetime(1978,  3,  4, 14,  0,  0), #  43200     0 NZST
        datetime(1978, 10, 28, 14,  0,  0), #  46800  3600 NZDT
        datetime(1979,  3,  3, 14,  0,  0), #  43200     0 NZST
        datetime(1979, 10, 27, 14,  0,  0), #  46800  3600 NZDT
        datetime(1980,  3,  1, 14,  0,  0), #  43200     0 NZST
        datetime(1980, 10, 25, 14,  0,  0), #  46800  3600 NZDT
        datetime(1981,  2, 28, 14,  0,  0), #  43200     0 NZST
        datetime(1981, 10, 24, 14,  0,  0), #  46800  3600 NZDT
        datetime(1982,  3,  6, 14,  0,  0), #  43200     0 NZST
        datetime(1982, 10, 30, 14,  0,  0), #  46800  3600 NZDT
        datetime(1983,  3,  5, 14,  0,  0), #  43200     0 NZST
        datetime(1983, 10, 29, 14,  0,  0), #  46800  3600 NZDT
        datetime(1984,  3,  3, 14,  0,  0), #  43200     0 NZST
        datetime(1984, 10, 27, 14,  0,  0), #  46800  3600 NZDT
        datetime(1985,  3,  2, 14,  0,  0), #  43200     0 NZST
        datetime(1985, 10, 26, 14,  0,  0), #  46800  3600 NZDT
        datetime(1986,  3,  1, 14,  0,  0), #  43200     0 NZST
        datetime(1986, 10, 25, 14,  0,  0), #  46800  3600 NZDT
        datetime(1987,  2, 28, 14,  0,  0), #  43200     0 NZST
        datetime(1987, 10, 24, 14,  0,  0), #  46800  3600 NZDT
        datetime(1988,  3,  5, 14,  0,  0), #  43200     0 NZST
        datetime(1988, 10, 29, 14,  0,  0), #  46800  3600 NZDT
        datetime(1989,  3,  4, 14,  0,  0), #  43200     0 NZST
        datetime(1989, 10,  7, 14,  0,  0), #  46800  3600 NZDT
        datetime(1990,  3, 17, 14,  0,  0), #  43200     0 NZST
        datetime(1990, 10,  6, 14,  0,  0), #  46800  3600 NZDT
        datetime(1991,  3, 16, 14,  0,  0), #  43200     0 NZST
        datetime(1991, 10,  5, 14,  0,  0), #  46800  3600 NZDT
        datetime(1992,  3, 14, 14,  0,  0), #  43200     0 NZST
        datetime(1992, 10,  3, 14,  0,  0), #  46800  3600 NZDT
        datetime(1993,  3, 20, 14,  0,  0), #  43200     0 NZST
        datetime(1993, 10,  2, 14,  0,  0), #  46800  3600 NZDT
        datetime(1994,  3, 19, 14,  0,  0), #  43200     0 NZST
        datetime(1994, 10,  1, 14,  0,  0), #  46800  3600 NZDT
        datetime(1995,  3, 18, 14,  0,  0), #  43200     0 NZST
        datetime(1995,  9, 30, 14,  0,  0), #  46800  3600 NZDT
        datetime(1996,  3, 16, 14,  0,  0), #  43200     0 NZST
        datetime(1996, 10,  5, 14,  0,  0), #  46800  3600 NZDT
        datetime(1997,  3, 15, 14,  0,  0), #  43200     0 NZST
        datetime(1997, 10,  4, 14,  0,  0), #  46800  3600 NZDT
        datetime(1998,  3, 14, 14,  0,  0), #  43200     0 NZST
        datetime(1998, 10,  3, 14,  0,  0), #  46800  3600 NZDT
        datetime(1999,  3, 20, 14,  0,  0), #  43200     0 NZST
        datetime(1999, 10,  2, 14,  0,  0), #  46800  3600 NZDT
        datetime(2000,  3, 18, 14,  0,  0), #  43200     0 NZST
        datetime(2000,  9, 30, 14,  0,  0), #  46800  3600 NZDT
        datetime(2001,  3, 17, 14,  0,  0), #  43200     0 NZST
        datetime(2001, 10,  6, 14,  0,  0), #  46800  3600 NZDT
        datetime(2002,  3, 16, 14,  0,  0), #  43200     0 NZST
        datetime(2002, 10,  5, 14,  0,  0), #  46800  3600 NZDT
        datetime(2003,  3, 15, 14,  0,  0), #  43200     0 NZST
        datetime(2003, 10,  4, 14,  0,  0), #  46800  3600 NZDT
        datetime(2004,  3, 20, 14,  0,  0), #  43200     0 NZST
        datetime(2004, 10,  2, 14,  0,  0), #  46800  3600 NZDT
        datetime(2005,  3, 19, 14,  0,  0), #  43200     0 NZST
        datetime(2005, 10,  1, 14,  0,  0), #  46800  3600 NZDT
        datetime(2006,  3, 18, 14,  0,  0), #  43200     0 NZST
        datetime(2006,  9, 30, 14,  0,  0), #  46800  3600 NZDT
        datetime(2007,  3, 17, 14,  0,  0), #  43200     0 NZST
        datetime(2007, 10,  6, 14,  0,  0), #  46800  3600 NZDT
        datetime(2008,  3, 15, 14,  0,  0), #  43200     0 NZST
        datetime(2008, 10,  4, 14,  0,  0), #  46800  3600 NZDT
        datetime(2009,  3, 14, 14,  0,  0), #  43200     0 NZST
        datetime(2009, 10,  3, 14,  0,  0), #  46800  3600 NZDT
        datetime(2010,  3, 20, 14,  0,  0), #  43200     0 NZST
        datetime(2010, 10,  2, 14,  0,  0), #  46800  3600 NZDT
        datetime(2011,  3, 19, 14,  0,  0), #  43200     0 NZST
        datetime(2011, 10,  1, 14,  0,  0), #  46800  3600 NZDT
        datetime(2012,  3, 17, 14,  0,  0), #  43200     0 NZST
        datetime(2012, 10,  6, 14,  0,  0), #  46800  3600 NZDT
        datetime(2013,  3, 16, 14,  0,  0), #  43200     0 NZST
        datetime(2013, 10,  5, 14,  0,  0), #  46800  3600 NZDT
        datetime(2014,  3, 15, 14,  0,  0), #  43200     0 NZST
        datetime(2014, 10,  4, 14,  0,  0), #  46800  3600 NZDT
        datetime(2015,  3, 14, 14,  0,  0), #  43200     0 NZST
        datetime(2015, 10,  3, 14,  0,  0), #  46800  3600 NZDT
        datetime(2016,  3, 19, 14,  0,  0), #  43200     0 NZST
        datetime(2016, 10,  1, 14,  0,  0), #  46800  3600 NZDT
        datetime(2017,  3, 18, 14,  0,  0), #  43200     0 NZST
        datetime(2017,  9, 30, 14,  0,  0), #  46800  3600 NZDT
        datetime(2018,  3, 17, 14,  0,  0), #  43200     0 NZST
        datetime(2018, 10,  6, 14,  0,  0), #  46800  3600 NZDT
        datetime(2019,  3, 16, 14,  0,  0), #  43200     0 NZST
        datetime(2019, 10,  5, 14,  0,  0), #  46800  3600 NZDT
        datetime(2020,  3, 14, 14,  0,  0), #  43200     0 NZST
        datetime(2020, 10,  3, 14,  0,  0), #  46800  3600 NZDT
        datetime(2021,  3, 20, 14,  0,  0), #  43200     0 NZST
        datetime(2021, 10,  2, 14,  0,  0), #  46800  3600 NZDT
        datetime(2022,  3, 19, 14,  0,  0), #  43200     0 NZST
        datetime(2022, 10,  1, 14,  0,  0), #  46800  3600 NZDT
        datetime(2023,  3, 18, 14,  0,  0), #  43200     0 NZST
        datetime(2023,  9, 30, 14,  0,  0), #  46800  3600 NZDT
        datetime(2024,  3, 16, 14,  0,  0), #  43200     0 NZST
        datetime(2024, 10,  5, 14,  0,  0), #  46800  3600 NZDT
        datetime(2025,  3, 15, 14,  0,  0), #  43200     0 NZST
        datetime(2025, 10,  4, 14,  0,  0), #  46800  3600 NZDT
        datetime(2026,  3, 14, 14,  0,  0), #  43200     0 NZST
        datetime(2026, 10,  3, 14,  0,  0), #  46800  3600 NZDT
        datetime(2027,  3, 20, 14,  0,  0), #  43200     0 NZST
        datetime(2027, 10,  2, 14,  0,  0), #  46800  3600 NZDT
        datetime(2028,  3, 18, 14,  0,  0), #  43200     0 NZST
        datetime(2028,  9, 30, 14,  0,  0), #  46800  3600 NZDT
        datetime(2029,  3, 17, 14,  0,  0), #  43200     0 NZST
        datetime(2029, 10,  6, 14,  0,  0), #  46800  3600 NZDT
        datetime(2030,  3, 16, 14,  0,  0), #  43200     0 NZST
        datetime(2030, 10,  5, 14,  0,  0), #  46800  3600 NZDT
        datetime(2031,  3, 15, 14,  0,  0), #  43200     0 NZST
        datetime(2031, 10,  4, 14,  0,  0), #  46800  3600 NZDT
        datetime(2032,  3, 20, 14,  0,  0), #  43200     0 NZST
        datetime(2032, 10,  2, 14,  0,  0), #  46800  3600 NZDT
        datetime(2033,  3, 19, 14,  0,  0), #  43200     0 NZST
        datetime(2033, 10,  1, 14,  0,  0), #  46800  3600 NZDT
        datetime(2034,  3, 18, 14,  0,  0), #  43200     0 NZST
        datetime(2034,  9, 30, 14,  0,  0), #  46800  3600 NZDT
        datetime(2035,  3, 17, 14,  0,  0), #  43200     0 NZST
        datetime(2035, 10,  6, 14,  0,  0), #  46800  3600 NZDT
        datetime(2036,  3, 15, 14,  0,  0), #  43200     0 NZST
        datetime(2036, 10,  4, 14,  0,  0), #  46800  3600 NZDT
        datetime(2037,  3, 14, 14,  0,  0), #  43200     0 NZST
        datetime(2037, 10,  3, 14,  0,  0), #  46800  3600 NZDT
        ]

    _transition_info = [
        ttinfo(     0,      0,  'zzz'),
        ttinfo( 43200,      0, 'NZST'),
        ttinfo( 46800,   3600, 'NZDT'),
        ttinfo( 43200,      0, 'NZST'),
        ttinfo( 46800,   3600, 'NZDT'),
        ttinfo( 43200,      0, 'NZST'),
        ttinfo( 46800,   3600, 'NZDT'),
        ttinfo( 43200,      0, 'NZST'),
        ttinfo( 46800,   3600, 'NZDT'),
        ttinfo( 43200,      0, 'NZST'),
        ttinfo( 46800,   3600, 'NZDT'),
        ttinfo( 43200,      0, 'NZST'),
        ttinfo( 46800,   3600, 'NZDT'),
        ttinfo( 43200,      0, 'NZST'),
        ttinfo( 46800,   3600, 'NZDT'),
        ttinfo( 43200,      0, 'NZST'),
        ttinfo( 46800,   3600, 'NZDT'),
        ttinfo( 43200,      0, 'NZST'),
        ttinfo( 46800,   3600, 'NZDT'),
        ttinfo( 43200,      0, 'NZST'),
        ttinfo( 46800,   3600, 'NZDT'),
        ttinfo( 43200,      0, 'NZST'),
        ttinfo( 46800,   3600, 'NZDT'),
        ttinfo( 43200,      0, 'NZST'),
        ttinfo( 46800,   3600, 'NZDT'),
        ttinfo( 43200,      0, 'NZST'),
        ttinfo( 46800,   3600, 'NZDT'),
        ttinfo( 43200,      0, 'NZST'),
        ttinfo( 46800,   3600, 'NZDT'),
        ttinfo( 43200,      0, 'NZST'),
        ttinfo( 46800,   3600, 'NZDT'),
        ttinfo( 43200,      0, 'NZST'),
        ttinfo( 46800,   3600, 'NZDT'),
        ttinfo( 43200,      0, 'NZST'),
        ttinfo( 46800,   3600, 'NZDT'),
        ttinfo( 43200,      0, 'NZST'),
        ttinfo( 46800,   3600, 'NZDT'),
        ttinfo( 43200,      0, 'NZST'),
        ttinfo( 46800,   3600, 'NZDT'),
        ttinfo( 43200,      0, 'NZST'),
        ttinfo( 46800,   3600, 'NZDT'),
        ttinfo( 43200,      0, 'NZST'),
        ttinfo( 46800,   3600, 'NZDT'),
        ttinfo( 43200,      0, 'NZST'),
        ttinfo( 46800,   3600, 'NZDT'),
        ttinfo( 43200,      0, 'NZST'),
        ttinfo( 46800,   3600, 'NZDT'),
        ttinfo( 43200,      0, 'NZST'),
        ttinfo( 46800,   3600, 'NZDT'),
        ttinfo( 43200,      0, 'NZST'),
        ttinfo( 46800,   3600, 'NZDT'),
        ttinfo( 43200,      0, 'NZST'),
        ttinfo( 46800,   3600, 'NZDT'),
        ttinfo( 43200,      0, 'NZST'),
        ttinfo( 46800,   3600, 'NZDT'),
        ttinfo( 43200,      0, 'NZST'),
        ttinfo( 46800,   3600, 'NZDT'),
        ttinfo( 43200,      0, 'NZST'),
        ttinfo( 46800,   3600, 'NZDT'),
        ttinfo( 43200,      0, 'NZST'),
        ttinfo( 46800,   3600, 'NZDT'),
        ttinfo( 43200,      0, 'NZST'),
        ttinfo( 46800,   3600, 'NZDT'),
        ttinfo( 43200,      0, 'NZST'),
        ttinfo( 46800,   3600, 'NZDT'),
        ttinfo( 43200,      0, 'NZST'),
        ttinfo( 46800,   3600, 'NZDT'),
        ttinfo( 43200,      0, 'NZST'),
        ttinfo( 46800,   3600, 'NZDT'),
        ttinfo( 43200,      0, 'NZST'),
        ttinfo( 46800,   3600, 'NZDT'),
        ttinfo( 43200,      0, 'NZST'),
        ttinfo( 46800,   3600, 'NZDT'),
        ttinfo( 43200,      0, 'NZST'),
        ttinfo( 46800,   3600, 'NZDT'),
        ttinfo( 43200,      0, 'NZST'),
        ttinfo( 46800,   3600, 'NZDT'),
        ttinfo( 43200,      0, 'NZST'),
        ttinfo( 46800,   3600, 'NZDT'),
        ttinfo( 43200,      0, 'NZST'),
        ttinfo( 46800,   3600, 'NZDT'),
        ttinfo( 43200,      0, 'NZST'),
        ttinfo( 46800,   3600, 'NZDT'),
        ttinfo( 43200,      0, 'NZST'),
        ttinfo( 46800,   3600, 'NZDT'),
        ttinfo( 43200,      0, 'NZST'),
        ttinfo( 46800,   3600, 'NZDT'),
        ttinfo( 43200,      0, 'NZST'),
        ttinfo( 46800,   3600, 'NZDT'),
        ttinfo( 43200,      0, 'NZST'),
        ttinfo( 46800,   3600, 'NZDT'),
        ttinfo( 43200,      0, 'NZST'),
        ttinfo( 46800,   3600, 'NZDT'),
        ttinfo( 43200,      0, 'NZST'),
        ttinfo( 46800,   3600, 'NZDT'),
        ttinfo( 43200,      0, 'NZST'),
        ttinfo( 46800,   3600, 'NZDT'),
        ttinfo( 43200,      0, 'NZST'),
        ttinfo( 46800,   3600, 'NZDT'),
        ttinfo( 43200,      0, 'NZST'),
        ttinfo( 46800,   3600, 'NZDT'),
        ttinfo( 43200,      0, 'NZST'),
        ttinfo( 46800,   3600, 'NZDT'),
        ttinfo( 43200,      0, 'NZST'),
        ttinfo( 46800,   3600, 'NZDT'),
        ttinfo( 43200,      0, 'NZST'),
        ttinfo( 46800,   3600, 'NZDT'),
        ttinfo( 43200,      0, 'NZST'),
        ttinfo( 46800,   3600, 'NZDT'),
        ttinfo( 43200,      0, 'NZST'),
        ttinfo( 46800,   3600, 'NZDT'),
        ttinfo( 43200,      0, 'NZST'),
        ttinfo( 46800,   3600, 'NZDT'),
        ttinfo( 43200,      0, 'NZST'),
        ttinfo( 46800,   3600, 'NZDT'),
        ttinfo( 43200,      0, 'NZST'),
        ttinfo( 46800,   3600, 'NZDT'),
        ttinfo( 43200,      0, 'NZST'),
        ttinfo( 46800,   3600, 'NZDT'),
        ttinfo( 43200,      0, 'NZST'),
        ttinfo( 46800,   3600, 'NZDT'),
        ttinfo( 43200,      0, 'NZST'),
        ttinfo( 46800,   3600, 'NZDT'),
        ttinfo( 43200,      0, 'NZST'),
        ttinfo( 46800,   3600, 'NZDT'),
        ttinfo( 43200,      0, 'NZST'),
        ttinfo( 46800,   3600, 'NZDT'),
        ttinfo( 43200,      0, 'NZST'),
        ttinfo( 46800,   3600, 'NZDT'),
        ]

South_Pole = South_Pole() # Singleton

