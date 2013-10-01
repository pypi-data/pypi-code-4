'''
tzinfo timezone information for America/Monterrey.

Generated from the Olson timezone database:
    ftp://elsie.nci.nih.gov/pub/tz*.tar.gz
'''

from pytz.tzinfo import DstTzInfo
from pytz.tzinfo import memorized_datetime as datetime
from pytz.tzinfo import memorized_ttinfo as ttinfo

class Monterrey(DstTzInfo):
    '''America/Monterrey timezone definition. See datetime.tzinfo for details'''

    _zone = 'America/Monterrey'

    _utc_transition_times = [
        datetime(   1,  1,  1,  0,  0,  0), # -24076     0 LMT
        datetime(1922,  1,  1,  6,  0,  0), # -21600     0 CST
        datetime(1988,  4,  3,  8,  0,  0), # -18000  3600 CDT
        datetime(1988, 10, 30,  7,  0,  0), # -21600     0 CST
        datetime(1996,  4,  7,  8,  0,  0), # -18000  3600 CDT
        datetime(1996, 10, 27,  7,  0,  0), # -21600     0 CST
        datetime(1997,  4,  6,  8,  0,  0), # -18000  3600 CDT
        datetime(1997, 10, 26,  7,  0,  0), # -21600     0 CST
        datetime(1998,  4,  5,  8,  0,  0), # -18000  3600 CDT
        datetime(1998, 10, 25,  7,  0,  0), # -21600     0 CST
        datetime(1999,  4,  4,  8,  0,  0), # -18000  3600 CDT
        datetime(1999, 10, 31,  7,  0,  0), # -21600     0 CST
        datetime(2000,  4,  2,  8,  0,  0), # -18000  3600 CDT
        datetime(2000, 10, 29,  7,  0,  0), # -21600     0 CST
        datetime(2001,  5,  6,  8,  0,  0), # -18000  3600 CDT
        datetime(2001,  9, 30,  7,  0,  0), # -21600     0 CST
        datetime(2002,  4,  7,  8,  0,  0), # -18000  3600 CDT
        datetime(2002, 10, 27,  7,  0,  0), # -21600     0 CST
        datetime(2003,  4,  6,  8,  0,  0), # -18000  3600 CDT
        datetime(2003, 10, 26,  7,  0,  0), # -21600     0 CST
        datetime(2004,  4,  4,  8,  0,  0), # -18000  3600 CDT
        datetime(2004, 10, 31,  7,  0,  0), # -21600     0 CST
        datetime(2005,  4,  3,  8,  0,  0), # -18000  3600 CDT
        datetime(2005, 10, 30,  7,  0,  0), # -21600     0 CST
        datetime(2006,  4,  2,  8,  0,  0), # -18000  3600 CDT
        datetime(2006, 10, 29,  7,  0,  0), # -21600     0 CST
        datetime(2007,  4,  1,  8,  0,  0), # -18000  3600 CDT
        datetime(2007, 10, 28,  7,  0,  0), # -21600     0 CST
        datetime(2008,  4,  6,  8,  0,  0), # -18000  3600 CDT
        datetime(2008, 10, 26,  7,  0,  0), # -21600     0 CST
        datetime(2009,  4,  5,  8,  0,  0), # -18000  3600 CDT
        datetime(2009, 10, 25,  7,  0,  0), # -21600     0 CST
        datetime(2010,  4,  4,  8,  0,  0), # -18000  3600 CDT
        datetime(2010, 10, 31,  7,  0,  0), # -21600     0 CST
        datetime(2011,  4,  3,  8,  0,  0), # -18000  3600 CDT
        datetime(2011, 10, 30,  7,  0,  0), # -21600     0 CST
        datetime(2012,  4,  1,  8,  0,  0), # -18000  3600 CDT
        datetime(2012, 10, 28,  7,  0,  0), # -21600     0 CST
        datetime(2013,  4,  7,  8,  0,  0), # -18000  3600 CDT
        datetime(2013, 10, 27,  7,  0,  0), # -21600     0 CST
        datetime(2014,  4,  6,  8,  0,  0), # -18000  3600 CDT
        datetime(2014, 10, 26,  7,  0,  0), # -21600     0 CST
        datetime(2015,  4,  5,  8,  0,  0), # -18000  3600 CDT
        datetime(2015, 10, 25,  7,  0,  0), # -21600     0 CST
        datetime(2016,  4,  3,  8,  0,  0), # -18000  3600 CDT
        datetime(2016, 10, 30,  7,  0,  0), # -21600     0 CST
        datetime(2017,  4,  2,  8,  0,  0), # -18000  3600 CDT
        datetime(2017, 10, 29,  7,  0,  0), # -21600     0 CST
        datetime(2018,  4,  1,  8,  0,  0), # -18000  3600 CDT
        datetime(2018, 10, 28,  7,  0,  0), # -21600     0 CST
        datetime(2019,  4,  7,  8,  0,  0), # -18000  3600 CDT
        datetime(2019, 10, 27,  7,  0,  0), # -21600     0 CST
        datetime(2020,  4,  5,  8,  0,  0), # -18000  3600 CDT
        datetime(2020, 10, 25,  7,  0,  0), # -21600     0 CST
        datetime(2021,  4,  4,  8,  0,  0), # -18000  3600 CDT
        datetime(2021, 10, 31,  7,  0,  0), # -21600     0 CST
        datetime(2022,  4,  3,  8,  0,  0), # -18000  3600 CDT
        datetime(2022, 10, 30,  7,  0,  0), # -21600     0 CST
        datetime(2023,  4,  2,  8,  0,  0), # -18000  3600 CDT
        datetime(2023, 10, 29,  7,  0,  0), # -21600     0 CST
        datetime(2024,  4,  7,  8,  0,  0), # -18000  3600 CDT
        datetime(2024, 10, 27,  7,  0,  0), # -21600     0 CST
        datetime(2025,  4,  6,  8,  0,  0), # -18000  3600 CDT
        datetime(2025, 10, 26,  7,  0,  0), # -21600     0 CST
        datetime(2026,  4,  5,  8,  0,  0), # -18000  3600 CDT
        datetime(2026, 10, 25,  7,  0,  0), # -21600     0 CST
        datetime(2027,  4,  4,  8,  0,  0), # -18000  3600 CDT
        datetime(2027, 10, 31,  7,  0,  0), # -21600     0 CST
        datetime(2028,  4,  2,  8,  0,  0), # -18000  3600 CDT
        datetime(2028, 10, 29,  7,  0,  0), # -21600     0 CST
        datetime(2029,  4,  1,  8,  0,  0), # -18000  3600 CDT
        datetime(2029, 10, 28,  7,  0,  0), # -21600     0 CST
        datetime(2030,  4,  7,  8,  0,  0), # -18000  3600 CDT
        datetime(2030, 10, 27,  7,  0,  0), # -21600     0 CST
        datetime(2031,  4,  6,  8,  0,  0), # -18000  3600 CDT
        datetime(2031, 10, 26,  7,  0,  0), # -21600     0 CST
        datetime(2032,  4,  4,  8,  0,  0), # -18000  3600 CDT
        datetime(2032, 10, 31,  7,  0,  0), # -21600     0 CST
        datetime(2033,  4,  3,  8,  0,  0), # -18000  3600 CDT
        datetime(2033, 10, 30,  7,  0,  0), # -21600     0 CST
        datetime(2034,  4,  2,  8,  0,  0), # -18000  3600 CDT
        datetime(2034, 10, 29,  7,  0,  0), # -21600     0 CST
        datetime(2035,  4,  1,  8,  0,  0), # -18000  3600 CDT
        datetime(2035, 10, 28,  7,  0,  0), # -21600     0 CST
        datetime(2036,  4,  6,  8,  0,  0), # -18000  3600 CDT
        datetime(2036, 10, 26,  7,  0,  0), # -21600     0 CST
        datetime(2037,  4,  5,  8,  0,  0), # -18000  3600 CDT
        datetime(2037, 10, 25,  7,  0,  0), # -21600     0 CST
        ]

    _transition_info = [
        ttinfo(-24076,      0,  'LMT'),
        ttinfo(-21600,      0,  'CST'),
        ttinfo(-18000,   3600,  'CDT'),
        ttinfo(-21600,      0,  'CST'),
        ttinfo(-18000,   3600,  'CDT'),
        ttinfo(-21600,      0,  'CST'),
        ttinfo(-18000,   3600,  'CDT'),
        ttinfo(-21600,      0,  'CST'),
        ttinfo(-18000,   3600,  'CDT'),
        ttinfo(-21600,      0,  'CST'),
        ttinfo(-18000,   3600,  'CDT'),
        ttinfo(-21600,      0,  'CST'),
        ttinfo(-18000,   3600,  'CDT'),
        ttinfo(-21600,      0,  'CST'),
        ttinfo(-18000,   3600,  'CDT'),
        ttinfo(-21600,      0,  'CST'),
        ttinfo(-18000,   3600,  'CDT'),
        ttinfo(-21600,      0,  'CST'),
        ttinfo(-18000,   3600,  'CDT'),
        ttinfo(-21600,      0,  'CST'),
        ttinfo(-18000,   3600,  'CDT'),
        ttinfo(-21600,      0,  'CST'),
        ttinfo(-18000,   3600,  'CDT'),
        ttinfo(-21600,      0,  'CST'),
        ttinfo(-18000,   3600,  'CDT'),
        ttinfo(-21600,      0,  'CST'),
        ttinfo(-18000,   3600,  'CDT'),
        ttinfo(-21600,      0,  'CST'),
        ttinfo(-18000,   3600,  'CDT'),
        ttinfo(-21600,      0,  'CST'),
        ttinfo(-18000,   3600,  'CDT'),
        ttinfo(-21600,      0,  'CST'),
        ttinfo(-18000,   3600,  'CDT'),
        ttinfo(-21600,      0,  'CST'),
        ttinfo(-18000,   3600,  'CDT'),
        ttinfo(-21600,      0,  'CST'),
        ttinfo(-18000,   3600,  'CDT'),
        ttinfo(-21600,      0,  'CST'),
        ttinfo(-18000,   3600,  'CDT'),
        ttinfo(-21600,      0,  'CST'),
        ttinfo(-18000,   3600,  'CDT'),
        ttinfo(-21600,      0,  'CST'),
        ttinfo(-18000,   3600,  'CDT'),
        ttinfo(-21600,      0,  'CST'),
        ttinfo(-18000,   3600,  'CDT'),
        ttinfo(-21600,      0,  'CST'),
        ttinfo(-18000,   3600,  'CDT'),
        ttinfo(-21600,      0,  'CST'),
        ttinfo(-18000,   3600,  'CDT'),
        ttinfo(-21600,      0,  'CST'),
        ttinfo(-18000,   3600,  'CDT'),
        ttinfo(-21600,      0,  'CST'),
        ttinfo(-18000,   3600,  'CDT'),
        ttinfo(-21600,      0,  'CST'),
        ttinfo(-18000,   3600,  'CDT'),
        ttinfo(-21600,      0,  'CST'),
        ttinfo(-18000,   3600,  'CDT'),
        ttinfo(-21600,      0,  'CST'),
        ttinfo(-18000,   3600,  'CDT'),
        ttinfo(-21600,      0,  'CST'),
        ttinfo(-18000,   3600,  'CDT'),
        ttinfo(-21600,      0,  'CST'),
        ttinfo(-18000,   3600,  'CDT'),
        ttinfo(-21600,      0,  'CST'),
        ttinfo(-18000,   3600,  'CDT'),
        ttinfo(-21600,      0,  'CST'),
        ttinfo(-18000,   3600,  'CDT'),
        ttinfo(-21600,      0,  'CST'),
        ttinfo(-18000,   3600,  'CDT'),
        ttinfo(-21600,      0,  'CST'),
        ttinfo(-18000,   3600,  'CDT'),
        ttinfo(-21600,      0,  'CST'),
        ttinfo(-18000,   3600,  'CDT'),
        ttinfo(-21600,      0,  'CST'),
        ttinfo(-18000,   3600,  'CDT'),
        ttinfo(-21600,      0,  'CST'),
        ttinfo(-18000,   3600,  'CDT'),
        ttinfo(-21600,      0,  'CST'),
        ttinfo(-18000,   3600,  'CDT'),
        ttinfo(-21600,      0,  'CST'),
        ttinfo(-18000,   3600,  'CDT'),
        ttinfo(-21600,      0,  'CST'),
        ttinfo(-18000,   3600,  'CDT'),
        ttinfo(-21600,      0,  'CST'),
        ttinfo(-18000,   3600,  'CDT'),
        ttinfo(-21600,      0,  'CST'),
        ttinfo(-18000,   3600,  'CDT'),
        ttinfo(-21600,      0,  'CST'),
        ]

Monterrey = Monterrey() # Singleton

