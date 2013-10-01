'''
tzinfo timezone information for America/Juneau.

Generated from the Olson timezone database:
    ftp://elsie.nci.nih.gov/pub/tz*.tar.gz
'''

from pytz.tzinfo import DstTzInfo
from pytz.tzinfo import memorized_datetime as datetime
from pytz.tzinfo import memorized_ttinfo as ttinfo

class Juneau(DstTzInfo):
    '''America/Juneau timezone definition. See datetime.tzinfo for details'''

    _zone = 'America/Juneau'

    _utc_transition_times = [
        datetime(   1,  1,  1,  0,  0,  0), # -28800     0 PST
        datetime(1942,  2,  9, 10,  0,  0), # -25200  3600 PWT
        datetime(1945,  8, 14, 23,  0,  0), # -25200     0 PPT
        datetime(1945,  9, 30,  9,  0,  0), # -28800     0 PST
        datetime(1969,  4, 27, 10,  0,  0), # -25200  3600 PDT
        datetime(1969, 10, 26,  9,  0,  0), # -28800     0 PST
        datetime(1970,  4, 26, 10,  0,  0), # -25200  3600 PDT
        datetime(1970, 10, 25,  9,  0,  0), # -28800     0 PST
        datetime(1971,  4, 25, 10,  0,  0), # -25200  3600 PDT
        datetime(1971, 10, 31,  9,  0,  0), # -28800     0 PST
        datetime(1972,  4, 30, 10,  0,  0), # -25200  3600 PDT
        datetime(1972, 10, 29,  9,  0,  0), # -28800     0 PST
        datetime(1973,  4, 29, 10,  0,  0), # -25200  3600 PDT
        datetime(1973, 10, 28,  9,  0,  0), # -28800     0 PST
        datetime(1974,  1,  6, 10,  0,  0), # -25200  3600 PDT
        datetime(1974, 10, 27,  9,  0,  0), # -28800     0 PST
        datetime(1975,  2, 23, 10,  0,  0), # -25200  3600 PDT
        datetime(1975, 10, 26,  9,  0,  0), # -28800     0 PST
        datetime(1976,  4, 25, 10,  0,  0), # -25200  3600 PDT
        datetime(1976, 10, 31,  9,  0,  0), # -28800     0 PST
        datetime(1977,  4, 24, 10,  0,  0), # -25200  3600 PDT
        datetime(1977, 10, 30,  9,  0,  0), # -28800     0 PST
        datetime(1978,  4, 30, 10,  0,  0), # -25200  3600 PDT
        datetime(1978, 10, 29,  9,  0,  0), # -28800     0 PST
        datetime(1979,  4, 29, 10,  0,  0), # -25200  3600 PDT
        datetime(1979, 10, 28,  9,  0,  0), # -28800     0 PST
        datetime(1980,  4, 27, 10,  0,  0), # -25200  3600 PDT
        datetime(1980, 10, 26,  9,  0,  0), # -28800     0 PST
        datetime(1981,  4, 26, 10,  0,  0), # -25200  3600 PDT
        datetime(1981, 10, 25,  9,  0,  0), # -28800     0 PST
        datetime(1982,  4, 25, 10,  0,  0), # -25200  3600 PDT
        datetime(1982, 10, 31,  9,  0,  0), # -28800     0 PST
        datetime(1983,  4, 24, 10,  0,  0), # -25200  3600 PDT
        datetime(1983, 10, 30,  9,  0,  0), # -32400     0 YST
        datetime(1983, 11, 30,  9,  0,  0), # -32400     0 AKST
        datetime(1984,  4, 29, 11,  0,  0), # -28800  3600 AKDT
        datetime(1984, 10, 28, 10,  0,  0), # -32400     0 AKST
        datetime(1985,  4, 28, 11,  0,  0), # -28800  3600 AKDT
        datetime(1985, 10, 27, 10,  0,  0), # -32400     0 AKST
        datetime(1986,  4, 27, 11,  0,  0), # -28800  3600 AKDT
        datetime(1986, 10, 26, 10,  0,  0), # -32400     0 AKST
        datetime(1987,  4,  5, 11,  0,  0), # -28800  3600 AKDT
        datetime(1987, 10, 25, 10,  0,  0), # -32400     0 AKST
        datetime(1988,  4,  3, 11,  0,  0), # -28800  3600 AKDT
        datetime(1988, 10, 30, 10,  0,  0), # -32400     0 AKST
        datetime(1989,  4,  2, 11,  0,  0), # -28800  3600 AKDT
        datetime(1989, 10, 29, 10,  0,  0), # -32400     0 AKST
        datetime(1990,  4,  1, 11,  0,  0), # -28800  3600 AKDT
        datetime(1990, 10, 28, 10,  0,  0), # -32400     0 AKST
        datetime(1991,  4,  7, 11,  0,  0), # -28800  3600 AKDT
        datetime(1991, 10, 27, 10,  0,  0), # -32400     0 AKST
        datetime(1992,  4,  5, 11,  0,  0), # -28800  3600 AKDT
        datetime(1992, 10, 25, 10,  0,  0), # -32400     0 AKST
        datetime(1993,  4,  4, 11,  0,  0), # -28800  3600 AKDT
        datetime(1993, 10, 31, 10,  0,  0), # -32400     0 AKST
        datetime(1994,  4,  3, 11,  0,  0), # -28800  3600 AKDT
        datetime(1994, 10, 30, 10,  0,  0), # -32400     0 AKST
        datetime(1995,  4,  2, 11,  0,  0), # -28800  3600 AKDT
        datetime(1995, 10, 29, 10,  0,  0), # -32400     0 AKST
        datetime(1996,  4,  7, 11,  0,  0), # -28800  3600 AKDT
        datetime(1996, 10, 27, 10,  0,  0), # -32400     0 AKST
        datetime(1997,  4,  6, 11,  0,  0), # -28800  3600 AKDT
        datetime(1997, 10, 26, 10,  0,  0), # -32400     0 AKST
        datetime(1998,  4,  5, 11,  0,  0), # -28800  3600 AKDT
        datetime(1998, 10, 25, 10,  0,  0), # -32400     0 AKST
        datetime(1999,  4,  4, 11,  0,  0), # -28800  3600 AKDT
        datetime(1999, 10, 31, 10,  0,  0), # -32400     0 AKST
        datetime(2000,  4,  2, 11,  0,  0), # -28800  3600 AKDT
        datetime(2000, 10, 29, 10,  0,  0), # -32400     0 AKST
        datetime(2001,  4,  1, 11,  0,  0), # -28800  3600 AKDT
        datetime(2001, 10, 28, 10,  0,  0), # -32400     0 AKST
        datetime(2002,  4,  7, 11,  0,  0), # -28800  3600 AKDT
        datetime(2002, 10, 27, 10,  0,  0), # -32400     0 AKST
        datetime(2003,  4,  6, 11,  0,  0), # -28800  3600 AKDT
        datetime(2003, 10, 26, 10,  0,  0), # -32400     0 AKST
        datetime(2004,  4,  4, 11,  0,  0), # -28800  3600 AKDT
        datetime(2004, 10, 31, 10,  0,  0), # -32400     0 AKST
        datetime(2005,  4,  3, 11,  0,  0), # -28800  3600 AKDT
        datetime(2005, 10, 30, 10,  0,  0), # -32400     0 AKST
        datetime(2006,  4,  2, 11,  0,  0), # -28800  3600 AKDT
        datetime(2006, 10, 29, 10,  0,  0), # -32400     0 AKST
        datetime(2007,  4,  1, 11,  0,  0), # -28800  3600 AKDT
        datetime(2007, 10, 28, 10,  0,  0), # -32400     0 AKST
        datetime(2008,  4,  6, 11,  0,  0), # -28800  3600 AKDT
        datetime(2008, 10, 26, 10,  0,  0), # -32400     0 AKST
        datetime(2009,  4,  5, 11,  0,  0), # -28800  3600 AKDT
        datetime(2009, 10, 25, 10,  0,  0), # -32400     0 AKST
        datetime(2010,  4,  4, 11,  0,  0), # -28800  3600 AKDT
        datetime(2010, 10, 31, 10,  0,  0), # -32400     0 AKST
        datetime(2011,  4,  3, 11,  0,  0), # -28800  3600 AKDT
        datetime(2011, 10, 30, 10,  0,  0), # -32400     0 AKST
        datetime(2012,  4,  1, 11,  0,  0), # -28800  3600 AKDT
        datetime(2012, 10, 28, 10,  0,  0), # -32400     0 AKST
        datetime(2013,  4,  7, 11,  0,  0), # -28800  3600 AKDT
        datetime(2013, 10, 27, 10,  0,  0), # -32400     0 AKST
        datetime(2014,  4,  6, 11,  0,  0), # -28800  3600 AKDT
        datetime(2014, 10, 26, 10,  0,  0), # -32400     0 AKST
        datetime(2015,  4,  5, 11,  0,  0), # -28800  3600 AKDT
        datetime(2015, 10, 25, 10,  0,  0), # -32400     0 AKST
        datetime(2016,  4,  3, 11,  0,  0), # -28800  3600 AKDT
        datetime(2016, 10, 30, 10,  0,  0), # -32400     0 AKST
        datetime(2017,  4,  2, 11,  0,  0), # -28800  3600 AKDT
        datetime(2017, 10, 29, 10,  0,  0), # -32400     0 AKST
        datetime(2018,  4,  1, 11,  0,  0), # -28800  3600 AKDT
        datetime(2018, 10, 28, 10,  0,  0), # -32400     0 AKST
        datetime(2019,  4,  7, 11,  0,  0), # -28800  3600 AKDT
        datetime(2019, 10, 27, 10,  0,  0), # -32400     0 AKST
        datetime(2020,  4,  5, 11,  0,  0), # -28800  3600 AKDT
        datetime(2020, 10, 25, 10,  0,  0), # -32400     0 AKST
        datetime(2021,  4,  4, 11,  0,  0), # -28800  3600 AKDT
        datetime(2021, 10, 31, 10,  0,  0), # -32400     0 AKST
        datetime(2022,  4,  3, 11,  0,  0), # -28800  3600 AKDT
        datetime(2022, 10, 30, 10,  0,  0), # -32400     0 AKST
        datetime(2023,  4,  2, 11,  0,  0), # -28800  3600 AKDT
        datetime(2023, 10, 29, 10,  0,  0), # -32400     0 AKST
        datetime(2024,  4,  7, 11,  0,  0), # -28800  3600 AKDT
        datetime(2024, 10, 27, 10,  0,  0), # -32400     0 AKST
        datetime(2025,  4,  6, 11,  0,  0), # -28800  3600 AKDT
        datetime(2025, 10, 26, 10,  0,  0), # -32400     0 AKST
        datetime(2026,  4,  5, 11,  0,  0), # -28800  3600 AKDT
        datetime(2026, 10, 25, 10,  0,  0), # -32400     0 AKST
        datetime(2027,  4,  4, 11,  0,  0), # -28800  3600 AKDT
        datetime(2027, 10, 31, 10,  0,  0), # -32400     0 AKST
        datetime(2028,  4,  2, 11,  0,  0), # -28800  3600 AKDT
        datetime(2028, 10, 29, 10,  0,  0), # -32400     0 AKST
        datetime(2029,  4,  1, 11,  0,  0), # -28800  3600 AKDT
        datetime(2029, 10, 28, 10,  0,  0), # -32400     0 AKST
        datetime(2030,  4,  7, 11,  0,  0), # -28800  3600 AKDT
        datetime(2030, 10, 27, 10,  0,  0), # -32400     0 AKST
        datetime(2031,  4,  6, 11,  0,  0), # -28800  3600 AKDT
        datetime(2031, 10, 26, 10,  0,  0), # -32400     0 AKST
        datetime(2032,  4,  4, 11,  0,  0), # -28800  3600 AKDT
        datetime(2032, 10, 31, 10,  0,  0), # -32400     0 AKST
        datetime(2033,  4,  3, 11,  0,  0), # -28800  3600 AKDT
        datetime(2033, 10, 30, 10,  0,  0), # -32400     0 AKST
        datetime(2034,  4,  2, 11,  0,  0), # -28800  3600 AKDT
        datetime(2034, 10, 29, 10,  0,  0), # -32400     0 AKST
        datetime(2035,  4,  1, 11,  0,  0), # -28800  3600 AKDT
        datetime(2035, 10, 28, 10,  0,  0), # -32400     0 AKST
        datetime(2036,  4,  6, 11,  0,  0), # -28800  3600 AKDT
        datetime(2036, 10, 26, 10,  0,  0), # -32400     0 AKST
        datetime(2037,  4,  5, 11,  0,  0), # -28800  3600 AKDT
        datetime(2037, 10, 25, 10,  0,  0), # -32400     0 AKST
        ]

    _transition_info = [
        ttinfo(-28800,      0,  'PST'),
        ttinfo(-25200,   3600,  'PWT'),
        ttinfo(-25200,      0,  'PPT'),
        ttinfo(-28800,      0,  'PST'),
        ttinfo(-25200,   3600,  'PDT'),
        ttinfo(-28800,      0,  'PST'),
        ttinfo(-25200,   3600,  'PDT'),
        ttinfo(-28800,      0,  'PST'),
        ttinfo(-25200,   3600,  'PDT'),
        ttinfo(-28800,      0,  'PST'),
        ttinfo(-25200,   3600,  'PDT'),
        ttinfo(-28800,      0,  'PST'),
        ttinfo(-25200,   3600,  'PDT'),
        ttinfo(-28800,      0,  'PST'),
        ttinfo(-25200,   3600,  'PDT'),
        ttinfo(-28800,      0,  'PST'),
        ttinfo(-25200,   3600,  'PDT'),
        ttinfo(-28800,      0,  'PST'),
        ttinfo(-25200,   3600,  'PDT'),
        ttinfo(-28800,      0,  'PST'),
        ttinfo(-25200,   3600,  'PDT'),
        ttinfo(-28800,      0,  'PST'),
        ttinfo(-25200,   3600,  'PDT'),
        ttinfo(-28800,      0,  'PST'),
        ttinfo(-25200,   3600,  'PDT'),
        ttinfo(-28800,      0,  'PST'),
        ttinfo(-25200,   3600,  'PDT'),
        ttinfo(-28800,      0,  'PST'),
        ttinfo(-25200,   3600,  'PDT'),
        ttinfo(-28800,      0,  'PST'),
        ttinfo(-25200,   3600,  'PDT'),
        ttinfo(-28800,      0,  'PST'),
        ttinfo(-25200,   3600,  'PDT'),
        ttinfo(-32400,      0,  'YST'),
        ttinfo(-32400,      0, 'AKST'),
        ttinfo(-28800,   3600, 'AKDT'),
        ttinfo(-32400,      0, 'AKST'),
        ttinfo(-28800,   3600, 'AKDT'),
        ttinfo(-32400,      0, 'AKST'),
        ttinfo(-28800,   3600, 'AKDT'),
        ttinfo(-32400,      0, 'AKST'),
        ttinfo(-28800,   3600, 'AKDT'),
        ttinfo(-32400,      0, 'AKST'),
        ttinfo(-28800,   3600, 'AKDT'),
        ttinfo(-32400,      0, 'AKST'),
        ttinfo(-28800,   3600, 'AKDT'),
        ttinfo(-32400,      0, 'AKST'),
        ttinfo(-28800,   3600, 'AKDT'),
        ttinfo(-32400,      0, 'AKST'),
        ttinfo(-28800,   3600, 'AKDT'),
        ttinfo(-32400,      0, 'AKST'),
        ttinfo(-28800,   3600, 'AKDT'),
        ttinfo(-32400,      0, 'AKST'),
        ttinfo(-28800,   3600, 'AKDT'),
        ttinfo(-32400,      0, 'AKST'),
        ttinfo(-28800,   3600, 'AKDT'),
        ttinfo(-32400,      0, 'AKST'),
        ttinfo(-28800,   3600, 'AKDT'),
        ttinfo(-32400,      0, 'AKST'),
        ttinfo(-28800,   3600, 'AKDT'),
        ttinfo(-32400,      0, 'AKST'),
        ttinfo(-28800,   3600, 'AKDT'),
        ttinfo(-32400,      0, 'AKST'),
        ttinfo(-28800,   3600, 'AKDT'),
        ttinfo(-32400,      0, 'AKST'),
        ttinfo(-28800,   3600, 'AKDT'),
        ttinfo(-32400,      0, 'AKST'),
        ttinfo(-28800,   3600, 'AKDT'),
        ttinfo(-32400,      0, 'AKST'),
        ttinfo(-28800,   3600, 'AKDT'),
        ttinfo(-32400,      0, 'AKST'),
        ttinfo(-28800,   3600, 'AKDT'),
        ttinfo(-32400,      0, 'AKST'),
        ttinfo(-28800,   3600, 'AKDT'),
        ttinfo(-32400,      0, 'AKST'),
        ttinfo(-28800,   3600, 'AKDT'),
        ttinfo(-32400,      0, 'AKST'),
        ttinfo(-28800,   3600, 'AKDT'),
        ttinfo(-32400,      0, 'AKST'),
        ttinfo(-28800,   3600, 'AKDT'),
        ttinfo(-32400,      0, 'AKST'),
        ttinfo(-28800,   3600, 'AKDT'),
        ttinfo(-32400,      0, 'AKST'),
        ttinfo(-28800,   3600, 'AKDT'),
        ttinfo(-32400,      0, 'AKST'),
        ttinfo(-28800,   3600, 'AKDT'),
        ttinfo(-32400,      0, 'AKST'),
        ttinfo(-28800,   3600, 'AKDT'),
        ttinfo(-32400,      0, 'AKST'),
        ttinfo(-28800,   3600, 'AKDT'),
        ttinfo(-32400,      0, 'AKST'),
        ttinfo(-28800,   3600, 'AKDT'),
        ttinfo(-32400,      0, 'AKST'),
        ttinfo(-28800,   3600, 'AKDT'),
        ttinfo(-32400,      0, 'AKST'),
        ttinfo(-28800,   3600, 'AKDT'),
        ttinfo(-32400,      0, 'AKST'),
        ttinfo(-28800,   3600, 'AKDT'),
        ttinfo(-32400,      0, 'AKST'),
        ttinfo(-28800,   3600, 'AKDT'),
        ttinfo(-32400,      0, 'AKST'),
        ttinfo(-28800,   3600, 'AKDT'),
        ttinfo(-32400,      0, 'AKST'),
        ttinfo(-28800,   3600, 'AKDT'),
        ttinfo(-32400,      0, 'AKST'),
        ttinfo(-28800,   3600, 'AKDT'),
        ttinfo(-32400,      0, 'AKST'),
        ttinfo(-28800,   3600, 'AKDT'),
        ttinfo(-32400,      0, 'AKST'),
        ttinfo(-28800,   3600, 'AKDT'),
        ttinfo(-32400,      0, 'AKST'),
        ttinfo(-28800,   3600, 'AKDT'),
        ttinfo(-32400,      0, 'AKST'),
        ttinfo(-28800,   3600, 'AKDT'),
        ttinfo(-32400,      0, 'AKST'),
        ttinfo(-28800,   3600, 'AKDT'),
        ttinfo(-32400,      0, 'AKST'),
        ttinfo(-28800,   3600, 'AKDT'),
        ttinfo(-32400,      0, 'AKST'),
        ttinfo(-28800,   3600, 'AKDT'),
        ttinfo(-32400,      0, 'AKST'),
        ttinfo(-28800,   3600, 'AKDT'),
        ttinfo(-32400,      0, 'AKST'),
        ttinfo(-28800,   3600, 'AKDT'),
        ttinfo(-32400,      0, 'AKST'),
        ttinfo(-28800,   3600, 'AKDT'),
        ttinfo(-32400,      0, 'AKST'),
        ttinfo(-28800,   3600, 'AKDT'),
        ttinfo(-32400,      0, 'AKST'),
        ttinfo(-28800,   3600, 'AKDT'),
        ttinfo(-32400,      0, 'AKST'),
        ttinfo(-28800,   3600, 'AKDT'),
        ttinfo(-32400,      0, 'AKST'),
        ttinfo(-28800,   3600, 'AKDT'),
        ttinfo(-32400,      0, 'AKST'),
        ttinfo(-28800,   3600, 'AKDT'),
        ttinfo(-32400,      0, 'AKST'),
        ttinfo(-28800,   3600, 'AKDT'),
        ttinfo(-32400,      0, 'AKST'),
        ttinfo(-28800,   3600, 'AKDT'),
        ttinfo(-32400,      0, 'AKST'),
        ttinfo(-28800,   3600, 'AKDT'),
        ttinfo(-32400,      0, 'AKST'),
        ]

Juneau = Juneau() # Singleton

