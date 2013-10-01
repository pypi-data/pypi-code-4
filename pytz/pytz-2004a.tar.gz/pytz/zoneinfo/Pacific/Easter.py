'''
tzinfo timezone information for Pacific/Easter.

Generated from the Olson timezone database:
    ftp://elsie.nci.nih.gov/pub/tz*.tar.gz
'''

from pytz.tzinfo import DstTzInfo
from pytz.tzinfo import memorized_datetime as datetime
from pytz.tzinfo import memorized_ttinfo as ttinfo

class Easter(DstTzInfo):
    '''Pacific/Easter timezone definition. See datetime.tzinfo for details'''

    _zone = 'Pacific/Easter'

    _utc_transition_times = [
        datetime(   1,  1,  1,  0,  0,  0), # -26248     0 MMT
        datetime(1932,  9,  1,  7, 17, 28), # -25200     0 EAST
        datetime(1966, 10,  9,  4,  0,  0), # -21600  3600 EASST
        datetime(1967,  3, 12,  3,  0,  0), # -25200     0 EAST
        datetime(1967, 10, 15,  4,  0,  0), # -21600  3600 EASST
        datetime(1968,  3, 10,  3,  0,  0), # -25200     0 EAST
        datetime(1968, 10, 13,  4,  0,  0), # -21600  3600 EASST
        datetime(1969,  3,  9,  3,  0,  0), # -25200     0 EAST
        datetime(1969, 10, 12,  4,  0,  0), # -21600  3600 EASST
        datetime(1970,  3, 15,  3,  0,  0), # -25200     0 EAST
        datetime(1970, 10, 11,  4,  0,  0), # -21600  3600 EASST
        datetime(1971,  3, 14,  3,  0,  0), # -25200     0 EAST
        datetime(1971, 10, 10,  4,  0,  0), # -21600  3600 EASST
        datetime(1972,  3, 12,  3,  0,  0), # -25200     0 EAST
        datetime(1972, 10, 15,  4,  0,  0), # -21600  3600 EASST
        datetime(1973,  3, 11,  3,  0,  0), # -25200     0 EAST
        datetime(1973, 10, 14,  4,  0,  0), # -21600  3600 EASST
        datetime(1974,  3, 10,  3,  0,  0), # -25200     0 EAST
        datetime(1974, 10, 13,  4,  0,  0), # -21600  3600 EASST
        datetime(1975,  3,  9,  3,  0,  0), # -25200     0 EAST
        datetime(1975, 10, 12,  4,  0,  0), # -21600  3600 EASST
        datetime(1976,  3, 14,  3,  0,  0), # -25200     0 EAST
        datetime(1976, 10, 10,  4,  0,  0), # -21600  3600 EASST
        datetime(1977,  3, 13,  3,  0,  0), # -25200     0 EAST
        datetime(1977, 10,  9,  4,  0,  0), # -21600  3600 EASST
        datetime(1978,  3, 12,  3,  0,  0), # -25200     0 EAST
        datetime(1978, 10, 15,  4,  0,  0), # -21600  3600 EASST
        datetime(1979,  3, 11,  3,  0,  0), # -25200     0 EAST
        datetime(1979, 10, 14,  4,  0,  0), # -21600  3600 EASST
        datetime(1980,  3,  9,  3,  0,  0), # -25200     0 EAST
        datetime(1980, 10, 12,  4,  0,  0), # -21600  3600 EASST
        datetime(1981,  3, 15,  3,  0,  0), # -25200     0 EAST
        datetime(1981, 10, 11,  4,  0,  0), # -21600  3600 EASST
        datetime(1982,  3, 14,  3,  0,  0), # -25200     0 EAST
        datetime(1982,  3, 14,  7,  0,  0), # -21600     0 EAST
        datetime(1982, 10, 10,  4,  0,  0), # -18000  3600 EASST
        datetime(1983,  3, 13,  3,  0,  0), # -21600     0 EAST
        datetime(1983, 10,  9,  4,  0,  0), # -18000  3600 EASST
        datetime(1984,  3, 11,  3,  0,  0), # -21600     0 EAST
        datetime(1984, 10, 14,  4,  0,  0), # -18000  3600 EASST
        datetime(1985,  3, 10,  3,  0,  0), # -21600     0 EAST
        datetime(1985, 10, 13,  4,  0,  0), # -18000  3600 EASST
        datetime(1986,  3,  9,  3,  0,  0), # -21600     0 EAST
        datetime(1986, 10, 12,  4,  0,  0), # -18000  3600 EASST
        datetime(1987,  3, 15,  3,  0,  0), # -21600     0 EAST
        datetime(1987, 10, 11,  4,  0,  0), # -18000  3600 EASST
        datetime(1988,  3, 13,  3,  0,  0), # -21600     0 EAST
        datetime(1988, 10,  9,  4,  0,  0), # -18000  3600 EASST
        datetime(1989,  3, 12,  3,  0,  0), # -21600     0 EAST
        datetime(1989, 10, 15,  4,  0,  0), # -18000  3600 EASST
        datetime(1990,  3, 11,  3,  0,  0), # -21600     0 EAST
        datetime(1990, 10, 14,  4,  0,  0), # -18000  3600 EASST
        datetime(1991,  3, 10,  3,  0,  0), # -21600     0 EAST
        datetime(1991, 10, 13,  4,  0,  0), # -18000  3600 EASST
        datetime(1992,  3, 15,  3,  0,  0), # -21600     0 EAST
        datetime(1992, 10, 11,  4,  0,  0), # -18000  3600 EASST
        datetime(1993,  3, 14,  3,  0,  0), # -21600     0 EAST
        datetime(1993, 10, 10,  4,  0,  0), # -18000  3600 EASST
        datetime(1994,  3, 13,  3,  0,  0), # -21600     0 EAST
        datetime(1994, 10,  9,  4,  0,  0), # -18000  3600 EASST
        datetime(1995,  3, 12,  3,  0,  0), # -21600     0 EAST
        datetime(1995, 10, 15,  4,  0,  0), # -18000  3600 EASST
        datetime(1996,  3, 10,  3,  0,  0), # -21600     0 EAST
        datetime(1996, 10, 13,  4,  0,  0), # -18000  3600 EASST
        datetime(1997,  3,  9,  3,  0,  0), # -21600     0 EAST
        datetime(1997, 10, 12,  4,  0,  0), # -18000  3600 EASST
        datetime(1998,  3, 15,  3,  0,  0), # -21600     0 EAST
        datetime(1998,  9, 27,  4,  0,  0), # -18000  3600 EASST
        datetime(1999,  4,  4,  3,  0,  0), # -21600     0 EAST
        datetime(1999, 10, 10,  4,  0,  0), # -18000  3600 EASST
        datetime(2000,  3, 12,  3,  0,  0), # -21600     0 EAST
        datetime(2000, 10, 15,  4,  0,  0), # -18000  3600 EASST
        datetime(2001,  3, 11,  3,  0,  0), # -21600     0 EAST
        datetime(2001, 10, 14,  4,  0,  0), # -18000  3600 EASST
        datetime(2002,  3, 10,  3,  0,  0), # -21600     0 EAST
        datetime(2002, 10, 13,  4,  0,  0), # -18000  3600 EASST
        datetime(2003,  3,  9,  3,  0,  0), # -21600     0 EAST
        datetime(2003, 10, 12,  4,  0,  0), # -18000  3600 EASST
        datetime(2004,  3, 14,  3,  0,  0), # -21600     0 EAST
        datetime(2004, 10, 10,  4,  0,  0), # -18000  3600 EASST
        datetime(2005,  3, 13,  3,  0,  0), # -21600     0 EAST
        datetime(2005, 10,  9,  4,  0,  0), # -18000  3600 EASST
        datetime(2006,  3, 12,  3,  0,  0), # -21600     0 EAST
        datetime(2006, 10, 15,  4,  0,  0), # -18000  3600 EASST
        datetime(2007,  3, 11,  3,  0,  0), # -21600     0 EAST
        datetime(2007, 10, 14,  4,  0,  0), # -18000  3600 EASST
        datetime(2008,  3,  9,  3,  0,  0), # -21600     0 EAST
        datetime(2008, 10, 12,  4,  0,  0), # -18000  3600 EASST
        datetime(2009,  3, 15,  3,  0,  0), # -21600     0 EAST
        datetime(2009, 10, 11,  4,  0,  0), # -18000  3600 EASST
        datetime(2010,  3, 14,  3,  0,  0), # -21600     0 EAST
        datetime(2010, 10, 10,  4,  0,  0), # -18000  3600 EASST
        datetime(2011,  3, 13,  3,  0,  0), # -21600     0 EAST
        datetime(2011, 10,  9,  4,  0,  0), # -18000  3600 EASST
        datetime(2012,  3, 11,  3,  0,  0), # -21600     0 EAST
        datetime(2012, 10, 14,  4,  0,  0), # -18000  3600 EASST
        datetime(2013,  3, 10,  3,  0,  0), # -21600     0 EAST
        datetime(2013, 10, 13,  4,  0,  0), # -18000  3600 EASST
        datetime(2014,  3,  9,  3,  0,  0), # -21600     0 EAST
        datetime(2014, 10, 12,  4,  0,  0), # -18000  3600 EASST
        datetime(2015,  3, 15,  3,  0,  0), # -21600     0 EAST
        datetime(2015, 10, 11,  4,  0,  0), # -18000  3600 EASST
        datetime(2016,  3, 13,  3,  0,  0), # -21600     0 EAST
        datetime(2016, 10,  9,  4,  0,  0), # -18000  3600 EASST
        datetime(2017,  3, 12,  3,  0,  0), # -21600     0 EAST
        datetime(2017, 10, 15,  4,  0,  0), # -18000  3600 EASST
        datetime(2018,  3, 11,  3,  0,  0), # -21600     0 EAST
        datetime(2018, 10, 14,  4,  0,  0), # -18000  3600 EASST
        datetime(2019,  3, 10,  3,  0,  0), # -21600     0 EAST
        datetime(2019, 10, 13,  4,  0,  0), # -18000  3600 EASST
        datetime(2020,  3, 15,  3,  0,  0), # -21600     0 EAST
        datetime(2020, 10, 11,  4,  0,  0), # -18000  3600 EASST
        datetime(2021,  3, 14,  3,  0,  0), # -21600     0 EAST
        datetime(2021, 10, 10,  4,  0,  0), # -18000  3600 EASST
        datetime(2022,  3, 13,  3,  0,  0), # -21600     0 EAST
        datetime(2022, 10,  9,  4,  0,  0), # -18000  3600 EASST
        datetime(2023,  3, 12,  3,  0,  0), # -21600     0 EAST
        datetime(2023, 10, 15,  4,  0,  0), # -18000  3600 EASST
        datetime(2024,  3, 10,  3,  0,  0), # -21600     0 EAST
        datetime(2024, 10, 13,  4,  0,  0), # -18000  3600 EASST
        datetime(2025,  3,  9,  3,  0,  0), # -21600     0 EAST
        datetime(2025, 10, 12,  4,  0,  0), # -18000  3600 EASST
        datetime(2026,  3, 15,  3,  0,  0), # -21600     0 EAST
        datetime(2026, 10, 11,  4,  0,  0), # -18000  3600 EASST
        datetime(2027,  3, 14,  3,  0,  0), # -21600     0 EAST
        datetime(2027, 10, 10,  4,  0,  0), # -18000  3600 EASST
        datetime(2028,  3, 12,  3,  0,  0), # -21600     0 EAST
        datetime(2028, 10, 15,  4,  0,  0), # -18000  3600 EASST
        datetime(2029,  3, 11,  3,  0,  0), # -21600     0 EAST
        datetime(2029, 10, 14,  4,  0,  0), # -18000  3600 EASST
        datetime(2030,  3, 10,  3,  0,  0), # -21600     0 EAST
        datetime(2030, 10, 13,  4,  0,  0), # -18000  3600 EASST
        datetime(2031,  3,  9,  3,  0,  0), # -21600     0 EAST
        datetime(2031, 10, 12,  4,  0,  0), # -18000  3600 EASST
        datetime(2032,  3, 14,  3,  0,  0), # -21600     0 EAST
        datetime(2032, 10, 10,  4,  0,  0), # -18000  3600 EASST
        datetime(2033,  3, 13,  3,  0,  0), # -21600     0 EAST
        datetime(2033, 10,  9,  4,  0,  0), # -18000  3600 EASST
        datetime(2034,  3, 12,  3,  0,  0), # -21600     0 EAST
        datetime(2034, 10, 15,  4,  0,  0), # -18000  3600 EASST
        datetime(2035,  3, 11,  3,  0,  0), # -21600     0 EAST
        datetime(2035, 10, 14,  4,  0,  0), # -18000  3600 EASST
        datetime(2036,  3,  9,  3,  0,  0), # -21600     0 EAST
        datetime(2036, 10, 12,  4,  0,  0), # -18000  3600 EASST
        datetime(2037,  3, 15,  3,  0,  0), # -21600     0 EAST
        datetime(2037, 10, 11,  4,  0,  0), # -18000  3600 EASST
        ]

    _transition_info = [
        ttinfo(-26248,      0,  'MMT'),
        ttinfo(-25200,      0, 'EAST'),
        ttinfo(-21600,   3600, 'EASST'),
        ttinfo(-25200,      0, 'EAST'),
        ttinfo(-21600,   3600, 'EASST'),
        ttinfo(-25200,      0, 'EAST'),
        ttinfo(-21600,   3600, 'EASST'),
        ttinfo(-25200,      0, 'EAST'),
        ttinfo(-21600,   3600, 'EASST'),
        ttinfo(-25200,      0, 'EAST'),
        ttinfo(-21600,   3600, 'EASST'),
        ttinfo(-25200,      0, 'EAST'),
        ttinfo(-21600,   3600, 'EASST'),
        ttinfo(-25200,      0, 'EAST'),
        ttinfo(-21600,   3600, 'EASST'),
        ttinfo(-25200,      0, 'EAST'),
        ttinfo(-21600,   3600, 'EASST'),
        ttinfo(-25200,      0, 'EAST'),
        ttinfo(-21600,   3600, 'EASST'),
        ttinfo(-25200,      0, 'EAST'),
        ttinfo(-21600,   3600, 'EASST'),
        ttinfo(-25200,      0, 'EAST'),
        ttinfo(-21600,   3600, 'EASST'),
        ttinfo(-25200,      0, 'EAST'),
        ttinfo(-21600,   3600, 'EASST'),
        ttinfo(-25200,      0, 'EAST'),
        ttinfo(-21600,   3600, 'EASST'),
        ttinfo(-25200,      0, 'EAST'),
        ttinfo(-21600,   3600, 'EASST'),
        ttinfo(-25200,      0, 'EAST'),
        ttinfo(-21600,   3600, 'EASST'),
        ttinfo(-25200,      0, 'EAST'),
        ttinfo(-21600,   3600, 'EASST'),
        ttinfo(-25200,      0, 'EAST'),
        ttinfo(-21600,      0, 'EAST'),
        ttinfo(-18000,   3600, 'EASST'),
        ttinfo(-21600,      0, 'EAST'),
        ttinfo(-18000,   3600, 'EASST'),
        ttinfo(-21600,      0, 'EAST'),
        ttinfo(-18000,   3600, 'EASST'),
        ttinfo(-21600,      0, 'EAST'),
        ttinfo(-18000,   3600, 'EASST'),
        ttinfo(-21600,      0, 'EAST'),
        ttinfo(-18000,   3600, 'EASST'),
        ttinfo(-21600,      0, 'EAST'),
        ttinfo(-18000,   3600, 'EASST'),
        ttinfo(-21600,      0, 'EAST'),
        ttinfo(-18000,   3600, 'EASST'),
        ttinfo(-21600,      0, 'EAST'),
        ttinfo(-18000,   3600, 'EASST'),
        ttinfo(-21600,      0, 'EAST'),
        ttinfo(-18000,   3600, 'EASST'),
        ttinfo(-21600,      0, 'EAST'),
        ttinfo(-18000,   3600, 'EASST'),
        ttinfo(-21600,      0, 'EAST'),
        ttinfo(-18000,   3600, 'EASST'),
        ttinfo(-21600,      0, 'EAST'),
        ttinfo(-18000,   3600, 'EASST'),
        ttinfo(-21600,      0, 'EAST'),
        ttinfo(-18000,   3600, 'EASST'),
        ttinfo(-21600,      0, 'EAST'),
        ttinfo(-18000,   3600, 'EASST'),
        ttinfo(-21600,      0, 'EAST'),
        ttinfo(-18000,   3600, 'EASST'),
        ttinfo(-21600,      0, 'EAST'),
        ttinfo(-18000,   3600, 'EASST'),
        ttinfo(-21600,      0, 'EAST'),
        ttinfo(-18000,   3600, 'EASST'),
        ttinfo(-21600,      0, 'EAST'),
        ttinfo(-18000,   3600, 'EASST'),
        ttinfo(-21600,      0, 'EAST'),
        ttinfo(-18000,   3600, 'EASST'),
        ttinfo(-21600,      0, 'EAST'),
        ttinfo(-18000,   3600, 'EASST'),
        ttinfo(-21600,      0, 'EAST'),
        ttinfo(-18000,   3600, 'EASST'),
        ttinfo(-21600,      0, 'EAST'),
        ttinfo(-18000,   3600, 'EASST'),
        ttinfo(-21600,      0, 'EAST'),
        ttinfo(-18000,   3600, 'EASST'),
        ttinfo(-21600,      0, 'EAST'),
        ttinfo(-18000,   3600, 'EASST'),
        ttinfo(-21600,      0, 'EAST'),
        ttinfo(-18000,   3600, 'EASST'),
        ttinfo(-21600,      0, 'EAST'),
        ttinfo(-18000,   3600, 'EASST'),
        ttinfo(-21600,      0, 'EAST'),
        ttinfo(-18000,   3600, 'EASST'),
        ttinfo(-21600,      0, 'EAST'),
        ttinfo(-18000,   3600, 'EASST'),
        ttinfo(-21600,      0, 'EAST'),
        ttinfo(-18000,   3600, 'EASST'),
        ttinfo(-21600,      0, 'EAST'),
        ttinfo(-18000,   3600, 'EASST'),
        ttinfo(-21600,      0, 'EAST'),
        ttinfo(-18000,   3600, 'EASST'),
        ttinfo(-21600,      0, 'EAST'),
        ttinfo(-18000,   3600, 'EASST'),
        ttinfo(-21600,      0, 'EAST'),
        ttinfo(-18000,   3600, 'EASST'),
        ttinfo(-21600,      0, 'EAST'),
        ttinfo(-18000,   3600, 'EASST'),
        ttinfo(-21600,      0, 'EAST'),
        ttinfo(-18000,   3600, 'EASST'),
        ttinfo(-21600,      0, 'EAST'),
        ttinfo(-18000,   3600, 'EASST'),
        ttinfo(-21600,      0, 'EAST'),
        ttinfo(-18000,   3600, 'EASST'),
        ttinfo(-21600,      0, 'EAST'),
        ttinfo(-18000,   3600, 'EASST'),
        ttinfo(-21600,      0, 'EAST'),
        ttinfo(-18000,   3600, 'EASST'),
        ttinfo(-21600,      0, 'EAST'),
        ttinfo(-18000,   3600, 'EASST'),
        ttinfo(-21600,      0, 'EAST'),
        ttinfo(-18000,   3600, 'EASST'),
        ttinfo(-21600,      0, 'EAST'),
        ttinfo(-18000,   3600, 'EASST'),
        ttinfo(-21600,      0, 'EAST'),
        ttinfo(-18000,   3600, 'EASST'),
        ttinfo(-21600,      0, 'EAST'),
        ttinfo(-18000,   3600, 'EASST'),
        ttinfo(-21600,      0, 'EAST'),
        ttinfo(-18000,   3600, 'EASST'),
        ttinfo(-21600,      0, 'EAST'),
        ttinfo(-18000,   3600, 'EASST'),
        ttinfo(-21600,      0, 'EAST'),
        ttinfo(-18000,   3600, 'EASST'),
        ttinfo(-21600,      0, 'EAST'),
        ttinfo(-18000,   3600, 'EASST'),
        ttinfo(-21600,      0, 'EAST'),
        ttinfo(-18000,   3600, 'EASST'),
        ttinfo(-21600,      0, 'EAST'),
        ttinfo(-18000,   3600, 'EASST'),
        ttinfo(-21600,      0, 'EAST'),
        ttinfo(-18000,   3600, 'EASST'),
        ttinfo(-21600,      0, 'EAST'),
        ttinfo(-18000,   3600, 'EASST'),
        ttinfo(-21600,      0, 'EAST'),
        ttinfo(-18000,   3600, 'EASST'),
        ttinfo(-21600,      0, 'EAST'),
        ttinfo(-18000,   3600, 'EASST'),
        ttinfo(-21600,      0, 'EAST'),
        ttinfo(-18000,   3600, 'EASST'),
        ttinfo(-21600,      0, 'EAST'),
        ttinfo(-18000,   3600, 'EASST'),
        ]

Easter = Easter() # Singleton

