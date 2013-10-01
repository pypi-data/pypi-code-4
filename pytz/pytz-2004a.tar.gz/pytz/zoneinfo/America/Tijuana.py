'''
tzinfo timezone information for America/Tijuana.

Generated from the Olson timezone database:
    ftp://elsie.nci.nih.gov/pub/tz*.tar.gz
'''

from pytz.tzinfo import DstTzInfo
from pytz.tzinfo import memorized_datetime as datetime
from pytz.tzinfo import memorized_ttinfo as ttinfo

class Tijuana(DstTzInfo):
    '''America/Tijuana timezone definition. See datetime.tzinfo for details'''

    _zone = 'America/Tijuana'

    _utc_transition_times = [
        datetime(   1,  1,  1,  0,  0,  0), # -28084     0 LMT
        datetime(1922,  1,  1,  8,  0,  0), # -25200     0 MST
        datetime(1924,  1,  1,  7,  0,  0), # -28800     0 PST
        datetime(1927,  6, 11,  7,  0,  0), # -25200     0 MST
        datetime(1930, 11, 15,  7,  0,  0), # -28800     0 PST
        datetime(1931,  4,  1,  8,  0,  0), # -25200  3600 PDT
        datetime(1931,  9, 30,  7,  0,  0), # -28800     0 PST
        datetime(1942,  4, 24,  8,  0,  0), # -25200  3600 PWT
        datetime(1945, 11, 12,  7,  0,  0), # -28800     0 PST
        datetime(1948,  4,  5,  8,  0,  0), # -25200  3600 PDT
        datetime(1949,  1, 14,  7,  0,  0), # -28800     0 PST
        datetime(1954,  4, 25, 10,  0,  0), # -25200  3600 PDT
        datetime(1954,  9, 26,  9,  0,  0), # -28800     0 PST
        datetime(1955,  4, 24, 10,  0,  0), # -25200  3600 PDT
        datetime(1955,  9, 25,  9,  0,  0), # -28800     0 PST
        datetime(1956,  4, 29, 10,  0,  0), # -25200  3600 PDT
        datetime(1956,  9, 30,  9,  0,  0), # -28800     0 PST
        datetime(1957,  4, 28, 10,  0,  0), # -25200  3600 PDT
        datetime(1957,  9, 29,  9,  0,  0), # -28800     0 PST
        datetime(1958,  4, 27, 10,  0,  0), # -25200  3600 PDT
        datetime(1958,  9, 28,  9,  0,  0), # -28800     0 PST
        datetime(1959,  4, 26, 10,  0,  0), # -25200  3600 PDT
        datetime(1959,  9, 27,  9,  0,  0), # -28800     0 PST
        datetime(1960,  4, 24, 10,  0,  0), # -25200  3600 PDT
        datetime(1960,  9, 25,  9,  0,  0), # -28800     0 PST
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
        datetime(1983, 10, 30,  9,  0,  0), # -28800     0 PST
        datetime(1984,  4, 29, 10,  0,  0), # -25200  3600 PDT
        datetime(1984, 10, 28,  9,  0,  0), # -28800     0 PST
        datetime(1985,  4, 28, 10,  0,  0), # -25200  3600 PDT
        datetime(1985, 10, 27,  9,  0,  0), # -28800     0 PST
        datetime(1986,  4, 27, 10,  0,  0), # -25200  3600 PDT
        datetime(1986, 10, 26,  9,  0,  0), # -28800     0 PST
        datetime(1987,  4,  5, 10,  0,  0), # -25200  3600 PDT
        datetime(1987, 10, 25,  9,  0,  0), # -28800     0 PST
        datetime(1988,  4,  3, 10,  0,  0), # -25200  3600 PDT
        datetime(1988, 10, 30,  9,  0,  0), # -28800     0 PST
        datetime(1989,  4,  2, 10,  0,  0), # -25200  3600 PDT
        datetime(1989, 10, 29,  9,  0,  0), # -28800     0 PST
        datetime(1990,  4,  1, 10,  0,  0), # -25200  3600 PDT
        datetime(1990, 10, 28,  9,  0,  0), # -28800     0 PST
        datetime(1991,  4,  7, 10,  0,  0), # -25200  3600 PDT
        datetime(1991, 10, 27,  9,  0,  0), # -28800     0 PST
        datetime(1992,  4,  5, 10,  0,  0), # -25200  3600 PDT
        datetime(1992, 10, 25,  9,  0,  0), # -28800     0 PST
        datetime(1993,  4,  4, 10,  0,  0), # -25200  3600 PDT
        datetime(1993, 10, 31,  9,  0,  0), # -28800     0 PST
        datetime(1994,  4,  3, 10,  0,  0), # -25200  3600 PDT
        datetime(1994, 10, 30,  9,  0,  0), # -28800     0 PST
        datetime(1995,  4,  2, 10,  0,  0), # -25200  3600 PDT
        datetime(1995, 10, 29,  9,  0,  0), # -28800     0 PST
        datetime(1996,  4,  7, 10,  0,  0), # -25200  3600 PDT
        datetime(1996, 10, 27,  9,  0,  0), # -28800     0 PST
        datetime(1997,  4,  6, 10,  0,  0), # -25200  3600 PDT
        datetime(1997, 10, 26,  9,  0,  0), # -28800     0 PST
        datetime(1998,  4,  5, 10,  0,  0), # -25200  3600 PDT
        datetime(1998, 10, 25,  9,  0,  0), # -28800     0 PST
        datetime(1999,  4,  4, 10,  0,  0), # -25200  3600 PDT
        datetime(1999, 10, 31,  9,  0,  0), # -28800     0 PST
        datetime(2000,  4,  2, 10,  0,  0), # -25200  3600 PDT
        datetime(2000, 10, 29,  9,  0,  0), # -28800     0 PST
        datetime(2001,  4,  1, 10,  0,  0), # -25200  3600 PDT
        datetime(2001, 10, 28,  9,  0,  0), # -28800     0 PST
        datetime(2002,  4,  7, 10,  0,  0), # -25200  3600 PDT
        datetime(2002, 10, 27,  9,  0,  0), # -28800     0 PST
        datetime(2003,  4,  6, 10,  0,  0), # -25200  3600 PDT
        datetime(2003, 10, 26,  9,  0,  0), # -28800     0 PST
        datetime(2004,  4,  4, 10,  0,  0), # -25200  3600 PDT
        datetime(2004, 10, 31,  9,  0,  0), # -28800     0 PST
        datetime(2005,  4,  3, 10,  0,  0), # -25200  3600 PDT
        datetime(2005, 10, 30,  9,  0,  0), # -28800     0 PST
        datetime(2006,  4,  2, 10,  0,  0), # -25200  3600 PDT
        datetime(2006, 10, 29,  9,  0,  0), # -28800     0 PST
        datetime(2007,  4,  1, 10,  0,  0), # -25200  3600 PDT
        datetime(2007, 10, 28,  9,  0,  0), # -28800     0 PST
        datetime(2008,  4,  6, 10,  0,  0), # -25200  3600 PDT
        datetime(2008, 10, 26,  9,  0,  0), # -28800     0 PST
        datetime(2009,  4,  5, 10,  0,  0), # -25200  3600 PDT
        datetime(2009, 10, 25,  9,  0,  0), # -28800     0 PST
        datetime(2010,  4,  4, 10,  0,  0), # -25200  3600 PDT
        datetime(2010, 10, 31,  9,  0,  0), # -28800     0 PST
        datetime(2011,  4,  3, 10,  0,  0), # -25200  3600 PDT
        datetime(2011, 10, 30,  9,  0,  0), # -28800     0 PST
        datetime(2012,  4,  1, 10,  0,  0), # -25200  3600 PDT
        datetime(2012, 10, 28,  9,  0,  0), # -28800     0 PST
        datetime(2013,  4,  7, 10,  0,  0), # -25200  3600 PDT
        datetime(2013, 10, 27,  9,  0,  0), # -28800     0 PST
        datetime(2014,  4,  6, 10,  0,  0), # -25200  3600 PDT
        datetime(2014, 10, 26,  9,  0,  0), # -28800     0 PST
        datetime(2015,  4,  5, 10,  0,  0), # -25200  3600 PDT
        datetime(2015, 10, 25,  9,  0,  0), # -28800     0 PST
        datetime(2016,  4,  3, 10,  0,  0), # -25200  3600 PDT
        datetime(2016, 10, 30,  9,  0,  0), # -28800     0 PST
        datetime(2017,  4,  2, 10,  0,  0), # -25200  3600 PDT
        datetime(2017, 10, 29,  9,  0,  0), # -28800     0 PST
        datetime(2018,  4,  1, 10,  0,  0), # -25200  3600 PDT
        datetime(2018, 10, 28,  9,  0,  0), # -28800     0 PST
        datetime(2019,  4,  7, 10,  0,  0), # -25200  3600 PDT
        datetime(2019, 10, 27,  9,  0,  0), # -28800     0 PST
        datetime(2020,  4,  5, 10,  0,  0), # -25200  3600 PDT
        datetime(2020, 10, 25,  9,  0,  0), # -28800     0 PST
        datetime(2021,  4,  4, 10,  0,  0), # -25200  3600 PDT
        datetime(2021, 10, 31,  9,  0,  0), # -28800     0 PST
        datetime(2022,  4,  3, 10,  0,  0), # -25200  3600 PDT
        datetime(2022, 10, 30,  9,  0,  0), # -28800     0 PST
        datetime(2023,  4,  2, 10,  0,  0), # -25200  3600 PDT
        datetime(2023, 10, 29,  9,  0,  0), # -28800     0 PST
        datetime(2024,  4,  7, 10,  0,  0), # -25200  3600 PDT
        datetime(2024, 10, 27,  9,  0,  0), # -28800     0 PST
        datetime(2025,  4,  6, 10,  0,  0), # -25200  3600 PDT
        datetime(2025, 10, 26,  9,  0,  0), # -28800     0 PST
        datetime(2026,  4,  5, 10,  0,  0), # -25200  3600 PDT
        datetime(2026, 10, 25,  9,  0,  0), # -28800     0 PST
        datetime(2027,  4,  4, 10,  0,  0), # -25200  3600 PDT
        datetime(2027, 10, 31,  9,  0,  0), # -28800     0 PST
        datetime(2028,  4,  2, 10,  0,  0), # -25200  3600 PDT
        datetime(2028, 10, 29,  9,  0,  0), # -28800     0 PST
        datetime(2029,  4,  1, 10,  0,  0), # -25200  3600 PDT
        datetime(2029, 10, 28,  9,  0,  0), # -28800     0 PST
        datetime(2030,  4,  7, 10,  0,  0), # -25200  3600 PDT
        datetime(2030, 10, 27,  9,  0,  0), # -28800     0 PST
        datetime(2031,  4,  6, 10,  0,  0), # -25200  3600 PDT
        datetime(2031, 10, 26,  9,  0,  0), # -28800     0 PST
        datetime(2032,  4,  4, 10,  0,  0), # -25200  3600 PDT
        datetime(2032, 10, 31,  9,  0,  0), # -28800     0 PST
        datetime(2033,  4,  3, 10,  0,  0), # -25200  3600 PDT
        datetime(2033, 10, 30,  9,  0,  0), # -28800     0 PST
        datetime(2034,  4,  2, 10,  0,  0), # -25200  3600 PDT
        datetime(2034, 10, 29,  9,  0,  0), # -28800     0 PST
        datetime(2035,  4,  1, 10,  0,  0), # -25200  3600 PDT
        datetime(2035, 10, 28,  9,  0,  0), # -28800     0 PST
        datetime(2036,  4,  6, 10,  0,  0), # -25200  3600 PDT
        datetime(2036, 10, 26,  9,  0,  0), # -28800     0 PST
        datetime(2037,  4,  5, 10,  0,  0), # -25200  3600 PDT
        datetime(2037, 10, 25,  9,  0,  0), # -28800     0 PST
        ]

    _transition_info = [
        ttinfo(-28084,      0,  'LMT'),
        ttinfo(-25200,      0,  'MST'),
        ttinfo(-28800,      0,  'PST'),
        ttinfo(-25200,      0,  'MST'),
        ttinfo(-28800,      0,  'PST'),
        ttinfo(-25200,   3600,  'PDT'),
        ttinfo(-28800,      0,  'PST'),
        ttinfo(-25200,   3600,  'PWT'),
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
        ]

Tijuana = Tijuana() # Singleton

