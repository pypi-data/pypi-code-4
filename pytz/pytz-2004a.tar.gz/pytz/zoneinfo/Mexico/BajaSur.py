'''
tzinfo timezone information for Mexico/BajaSur.

Generated from the Olson timezone database:
    ftp://elsie.nci.nih.gov/pub/tz*.tar.gz
'''

from pytz.tzinfo import DstTzInfo
from pytz.tzinfo import memorized_datetime as datetime
from pytz.tzinfo import memorized_ttinfo as ttinfo

class BajaSur(DstTzInfo):
    '''Mexico/BajaSur timezone definition. See datetime.tzinfo for details'''

    _zone = 'Mexico/BajaSur'

    _utc_transition_times = [
        datetime(   1,  1,  1,  0,  0,  0), # -25540     0 LMT
        datetime(1922,  1,  1,  7,  0,  0), # -25200     0 MST
        datetime(1927,  6, 11,  6,  0,  0), # -21600     0 CST
        datetime(1930, 11, 15,  6,  0,  0), # -25200     0 MST
        datetime(1931,  5,  2,  6,  0,  0), # -21600     0 CST
        datetime(1931, 10,  1,  6,  0,  0), # -25200     0 MST
        datetime(1932,  4,  1,  7,  0,  0), # -21600     0 CST
        datetime(1942,  4, 24,  6,  0,  0), # -25200     0 MST
        datetime(1949,  1, 14,  7,  0,  0), # -28800     0 PST
        datetime(1970,  1,  1,  8,  0,  0), # -25200     0 MST
        datetime(1996,  4,  7,  9,  0,  0), # -21600  3600 MDT
        datetime(1996, 10, 27,  8,  0,  0), # -25200     0 MST
        datetime(1997,  4,  6,  9,  0,  0), # -21600  3600 MDT
        datetime(1997, 10, 26,  8,  0,  0), # -25200     0 MST
        datetime(1998,  4,  5,  9,  0,  0), # -21600  3600 MDT
        datetime(1998, 10, 25,  8,  0,  0), # -25200     0 MST
        datetime(1999,  4,  4,  9,  0,  0), # -21600  3600 MDT
        datetime(1999, 10, 31,  8,  0,  0), # -25200     0 MST
        datetime(2000,  4,  2,  9,  0,  0), # -21600  3600 MDT
        datetime(2000, 10, 29,  8,  0,  0), # -25200     0 MST
        datetime(2001,  5,  6,  9,  0,  0), # -21600  3600 MDT
        datetime(2001,  9, 30,  8,  0,  0), # -25200     0 MST
        datetime(2002,  4,  7,  9,  0,  0), # -21600  3600 MDT
        datetime(2002, 10, 27,  8,  0,  0), # -25200     0 MST
        datetime(2003,  4,  6,  9,  0,  0), # -21600  3600 MDT
        datetime(2003, 10, 26,  8,  0,  0), # -25200     0 MST
        datetime(2004,  4,  4,  9,  0,  0), # -21600  3600 MDT
        datetime(2004, 10, 31,  8,  0,  0), # -25200     0 MST
        datetime(2005,  4,  3,  9,  0,  0), # -21600  3600 MDT
        datetime(2005, 10, 30,  8,  0,  0), # -25200     0 MST
        datetime(2006,  4,  2,  9,  0,  0), # -21600  3600 MDT
        datetime(2006, 10, 29,  8,  0,  0), # -25200     0 MST
        datetime(2007,  4,  1,  9,  0,  0), # -21600  3600 MDT
        datetime(2007, 10, 28,  8,  0,  0), # -25200     0 MST
        datetime(2008,  4,  6,  9,  0,  0), # -21600  3600 MDT
        datetime(2008, 10, 26,  8,  0,  0), # -25200     0 MST
        datetime(2009,  4,  5,  9,  0,  0), # -21600  3600 MDT
        datetime(2009, 10, 25,  8,  0,  0), # -25200     0 MST
        datetime(2010,  4,  4,  9,  0,  0), # -21600  3600 MDT
        datetime(2010, 10, 31,  8,  0,  0), # -25200     0 MST
        datetime(2011,  4,  3,  9,  0,  0), # -21600  3600 MDT
        datetime(2011, 10, 30,  8,  0,  0), # -25200     0 MST
        datetime(2012,  4,  1,  9,  0,  0), # -21600  3600 MDT
        datetime(2012, 10, 28,  8,  0,  0), # -25200     0 MST
        datetime(2013,  4,  7,  9,  0,  0), # -21600  3600 MDT
        datetime(2013, 10, 27,  8,  0,  0), # -25200     0 MST
        datetime(2014,  4,  6,  9,  0,  0), # -21600  3600 MDT
        datetime(2014, 10, 26,  8,  0,  0), # -25200     0 MST
        datetime(2015,  4,  5,  9,  0,  0), # -21600  3600 MDT
        datetime(2015, 10, 25,  8,  0,  0), # -25200     0 MST
        datetime(2016,  4,  3,  9,  0,  0), # -21600  3600 MDT
        datetime(2016, 10, 30,  8,  0,  0), # -25200     0 MST
        datetime(2017,  4,  2,  9,  0,  0), # -21600  3600 MDT
        datetime(2017, 10, 29,  8,  0,  0), # -25200     0 MST
        datetime(2018,  4,  1,  9,  0,  0), # -21600  3600 MDT
        datetime(2018, 10, 28,  8,  0,  0), # -25200     0 MST
        datetime(2019,  4,  7,  9,  0,  0), # -21600  3600 MDT
        datetime(2019, 10, 27,  8,  0,  0), # -25200     0 MST
        datetime(2020,  4,  5,  9,  0,  0), # -21600  3600 MDT
        datetime(2020, 10, 25,  8,  0,  0), # -25200     0 MST
        datetime(2021,  4,  4,  9,  0,  0), # -21600  3600 MDT
        datetime(2021, 10, 31,  8,  0,  0), # -25200     0 MST
        datetime(2022,  4,  3,  9,  0,  0), # -21600  3600 MDT
        datetime(2022, 10, 30,  8,  0,  0), # -25200     0 MST
        datetime(2023,  4,  2,  9,  0,  0), # -21600  3600 MDT
        datetime(2023, 10, 29,  8,  0,  0), # -25200     0 MST
        datetime(2024,  4,  7,  9,  0,  0), # -21600  3600 MDT
        datetime(2024, 10, 27,  8,  0,  0), # -25200     0 MST
        datetime(2025,  4,  6,  9,  0,  0), # -21600  3600 MDT
        datetime(2025, 10, 26,  8,  0,  0), # -25200     0 MST
        datetime(2026,  4,  5,  9,  0,  0), # -21600  3600 MDT
        datetime(2026, 10, 25,  8,  0,  0), # -25200     0 MST
        datetime(2027,  4,  4,  9,  0,  0), # -21600  3600 MDT
        datetime(2027, 10, 31,  8,  0,  0), # -25200     0 MST
        datetime(2028,  4,  2,  9,  0,  0), # -21600  3600 MDT
        datetime(2028, 10, 29,  8,  0,  0), # -25200     0 MST
        datetime(2029,  4,  1,  9,  0,  0), # -21600  3600 MDT
        datetime(2029, 10, 28,  8,  0,  0), # -25200     0 MST
        datetime(2030,  4,  7,  9,  0,  0), # -21600  3600 MDT
        datetime(2030, 10, 27,  8,  0,  0), # -25200     0 MST
        datetime(2031,  4,  6,  9,  0,  0), # -21600  3600 MDT
        datetime(2031, 10, 26,  8,  0,  0), # -25200     0 MST
        datetime(2032,  4,  4,  9,  0,  0), # -21600  3600 MDT
        datetime(2032, 10, 31,  8,  0,  0), # -25200     0 MST
        datetime(2033,  4,  3,  9,  0,  0), # -21600  3600 MDT
        datetime(2033, 10, 30,  8,  0,  0), # -25200     0 MST
        datetime(2034,  4,  2,  9,  0,  0), # -21600  3600 MDT
        datetime(2034, 10, 29,  8,  0,  0), # -25200     0 MST
        datetime(2035,  4,  1,  9,  0,  0), # -21600  3600 MDT
        datetime(2035, 10, 28,  8,  0,  0), # -25200     0 MST
        datetime(2036,  4,  6,  9,  0,  0), # -21600  3600 MDT
        datetime(2036, 10, 26,  8,  0,  0), # -25200     0 MST
        datetime(2037,  4,  5,  9,  0,  0), # -21600  3600 MDT
        datetime(2037, 10, 25,  8,  0,  0), # -25200     0 MST
        ]

    _transition_info = [
        ttinfo(-25540,      0,  'LMT'),
        ttinfo(-25200,      0,  'MST'),
        ttinfo(-21600,      0,  'CST'),
        ttinfo(-25200,      0,  'MST'),
        ttinfo(-21600,      0,  'CST'),
        ttinfo(-25200,      0,  'MST'),
        ttinfo(-21600,      0,  'CST'),
        ttinfo(-25200,      0,  'MST'),
        ttinfo(-28800,      0,  'PST'),
        ttinfo(-25200,      0,  'MST'),
        ttinfo(-21600,   3600,  'MDT'),
        ttinfo(-25200,      0,  'MST'),
        ttinfo(-21600,   3600,  'MDT'),
        ttinfo(-25200,      0,  'MST'),
        ttinfo(-21600,   3600,  'MDT'),
        ttinfo(-25200,      0,  'MST'),
        ttinfo(-21600,   3600,  'MDT'),
        ttinfo(-25200,      0,  'MST'),
        ttinfo(-21600,   3600,  'MDT'),
        ttinfo(-25200,      0,  'MST'),
        ttinfo(-21600,   3600,  'MDT'),
        ttinfo(-25200,      0,  'MST'),
        ttinfo(-21600,   3600,  'MDT'),
        ttinfo(-25200,      0,  'MST'),
        ttinfo(-21600,   3600,  'MDT'),
        ttinfo(-25200,      0,  'MST'),
        ttinfo(-21600,   3600,  'MDT'),
        ttinfo(-25200,      0,  'MST'),
        ttinfo(-21600,   3600,  'MDT'),
        ttinfo(-25200,      0,  'MST'),
        ttinfo(-21600,   3600,  'MDT'),
        ttinfo(-25200,      0,  'MST'),
        ttinfo(-21600,   3600,  'MDT'),
        ttinfo(-25200,      0,  'MST'),
        ttinfo(-21600,   3600,  'MDT'),
        ttinfo(-25200,      0,  'MST'),
        ttinfo(-21600,   3600,  'MDT'),
        ttinfo(-25200,      0,  'MST'),
        ttinfo(-21600,   3600,  'MDT'),
        ttinfo(-25200,      0,  'MST'),
        ttinfo(-21600,   3600,  'MDT'),
        ttinfo(-25200,      0,  'MST'),
        ttinfo(-21600,   3600,  'MDT'),
        ttinfo(-25200,      0,  'MST'),
        ttinfo(-21600,   3600,  'MDT'),
        ttinfo(-25200,      0,  'MST'),
        ttinfo(-21600,   3600,  'MDT'),
        ttinfo(-25200,      0,  'MST'),
        ttinfo(-21600,   3600,  'MDT'),
        ttinfo(-25200,      0,  'MST'),
        ttinfo(-21600,   3600,  'MDT'),
        ttinfo(-25200,      0,  'MST'),
        ttinfo(-21600,   3600,  'MDT'),
        ttinfo(-25200,      0,  'MST'),
        ttinfo(-21600,   3600,  'MDT'),
        ttinfo(-25200,      0,  'MST'),
        ttinfo(-21600,   3600,  'MDT'),
        ttinfo(-25200,      0,  'MST'),
        ttinfo(-21600,   3600,  'MDT'),
        ttinfo(-25200,      0,  'MST'),
        ttinfo(-21600,   3600,  'MDT'),
        ttinfo(-25200,      0,  'MST'),
        ttinfo(-21600,   3600,  'MDT'),
        ttinfo(-25200,      0,  'MST'),
        ttinfo(-21600,   3600,  'MDT'),
        ttinfo(-25200,      0,  'MST'),
        ttinfo(-21600,   3600,  'MDT'),
        ttinfo(-25200,      0,  'MST'),
        ttinfo(-21600,   3600,  'MDT'),
        ttinfo(-25200,      0,  'MST'),
        ttinfo(-21600,   3600,  'MDT'),
        ttinfo(-25200,      0,  'MST'),
        ttinfo(-21600,   3600,  'MDT'),
        ttinfo(-25200,      0,  'MST'),
        ttinfo(-21600,   3600,  'MDT'),
        ttinfo(-25200,      0,  'MST'),
        ttinfo(-21600,   3600,  'MDT'),
        ttinfo(-25200,      0,  'MST'),
        ttinfo(-21600,   3600,  'MDT'),
        ttinfo(-25200,      0,  'MST'),
        ttinfo(-21600,   3600,  'MDT'),
        ttinfo(-25200,      0,  'MST'),
        ttinfo(-21600,   3600,  'MDT'),
        ttinfo(-25200,      0,  'MST'),
        ttinfo(-21600,   3600,  'MDT'),
        ttinfo(-25200,      0,  'MST'),
        ttinfo(-21600,   3600,  'MDT'),
        ttinfo(-25200,      0,  'MST'),
        ttinfo(-21600,   3600,  'MDT'),
        ttinfo(-25200,      0,  'MST'),
        ttinfo(-21600,   3600,  'MDT'),
        ttinfo(-25200,      0,  'MST'),
        ttinfo(-21600,   3600,  'MDT'),
        ttinfo(-25200,      0,  'MST'),
        ]

BajaSur = BajaSur() # Singleton

