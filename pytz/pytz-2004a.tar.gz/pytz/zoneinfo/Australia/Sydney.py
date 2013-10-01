'''
tzinfo timezone information for Australia/Sydney.

Generated from the Olson timezone database:
    ftp://elsie.nci.nih.gov/pub/tz*.tar.gz
'''

from pytz.tzinfo import DstTzInfo
from pytz.tzinfo import memorized_datetime as datetime
from pytz.tzinfo import memorized_ttinfo as ttinfo

class Sydney(DstTzInfo):
    '''Australia/Sydney timezone definition. See datetime.tzinfo for details'''

    _zone = 'Australia/Sydney'

    _utc_transition_times = [
        datetime(   1,  1,  1,  0,  0,  0), #  36000     0 EST
        datetime(1916, 12, 31, 14,  1,  0), #  39600  3600 EST
        datetime(1917,  3, 24, 15,  0,  0), #  36000     0 EST
        datetime(1941, 12, 31, 16,  0,  0), #  39600  3600 EST
        datetime(1942,  3, 28, 15,  0,  0), #  36000     0 EST
        datetime(1942,  9, 26, 16,  0,  0), #  39600  3600 EST
        datetime(1943,  3, 27, 15,  0,  0), #  36000     0 EST
        datetime(1943, 10,  2, 16,  0,  0), #  39600  3600 EST
        datetime(1944,  3, 25, 15,  0,  0), #  36000     0 EST
        datetime(1971, 10, 30, 16,  0,  0), #  39600  3600 EST
        datetime(1972,  2, 26, 16,  0,  0), #  36000     0 EST
        datetime(1972, 10, 28, 16,  0,  0), #  39600  3600 EST
        datetime(1973,  3,  3, 16,  0,  0), #  36000     0 EST
        datetime(1973, 10, 27, 16,  0,  0), #  39600  3600 EST
        datetime(1974,  3,  2, 16,  0,  0), #  36000     0 EST
        datetime(1974, 10, 26, 16,  0,  0), #  39600  3600 EST
        datetime(1975,  3,  1, 16,  0,  0), #  36000     0 EST
        datetime(1975, 10, 25, 16,  0,  0), #  39600  3600 EST
        datetime(1976,  3,  6, 16,  0,  0), #  36000     0 EST
        datetime(1976, 10, 30, 16,  0,  0), #  39600  3600 EST
        datetime(1977,  3,  5, 16,  0,  0), #  36000     0 EST
        datetime(1977, 10, 29, 16,  0,  0), #  39600  3600 EST
        datetime(1978,  3,  4, 16,  0,  0), #  36000     0 EST
        datetime(1978, 10, 28, 16,  0,  0), #  39600  3600 EST
        datetime(1979,  3,  3, 16,  0,  0), #  36000     0 EST
        datetime(1979, 10, 27, 16,  0,  0), #  39600  3600 EST
        datetime(1980,  3,  1, 16,  0,  0), #  36000     0 EST
        datetime(1980, 10, 25, 16,  0,  0), #  39600  3600 EST
        datetime(1981,  2, 28, 16,  0,  0), #  36000     0 EST
        datetime(1981, 10, 24, 16,  0,  0), #  39600  3600 EST
        datetime(1982,  4,  3, 16,  0,  0), #  36000     0 EST
        datetime(1982, 10, 30, 16,  0,  0), #  39600  3600 EST
        datetime(1983,  3,  5, 16,  0,  0), #  36000     0 EST
        datetime(1983, 10, 29, 16,  0,  0), #  39600  3600 EST
        datetime(1984,  3,  3, 16,  0,  0), #  36000     0 EST
        datetime(1984, 10, 27, 16,  0,  0), #  39600  3600 EST
        datetime(1985,  3,  2, 16,  0,  0), #  36000     0 EST
        datetime(1985, 10, 26, 16,  0,  0), #  39600  3600 EST
        datetime(1986,  3, 15, 16,  0,  0), #  36000     0 EST
        datetime(1986, 10, 18, 16,  0,  0), #  39600  3600 EST
        datetime(1987,  3, 14, 16,  0,  0), #  36000     0 EST
        datetime(1987, 10, 24, 16,  0,  0), #  39600  3600 EST
        datetime(1988,  3, 19, 16,  0,  0), #  36000     0 EST
        datetime(1988, 10, 29, 16,  0,  0), #  39600  3600 EST
        datetime(1989,  3, 18, 16,  0,  0), #  36000     0 EST
        datetime(1989, 10, 28, 16,  0,  0), #  39600  3600 EST
        datetime(1990,  3,  3, 16,  0,  0), #  36000     0 EST
        datetime(1990, 10, 27, 16,  0,  0), #  39600  3600 EST
        datetime(1991,  3,  2, 16,  0,  0), #  36000     0 EST
        datetime(1991, 10, 26, 16,  0,  0), #  39600  3600 EST
        datetime(1992,  2, 29, 16,  0,  0), #  36000     0 EST
        datetime(1992, 10, 24, 16,  0,  0), #  39600  3600 EST
        datetime(1993,  3,  6, 16,  0,  0), #  36000     0 EST
        datetime(1993, 10, 30, 16,  0,  0), #  39600  3600 EST
        datetime(1994,  3,  5, 16,  0,  0), #  36000     0 EST
        datetime(1994, 10, 29, 16,  0,  0), #  39600  3600 EST
        datetime(1995,  3,  4, 16,  0,  0), #  36000     0 EST
        datetime(1995, 10, 28, 16,  0,  0), #  39600  3600 EST
        datetime(1996,  3, 30, 16,  0,  0), #  36000     0 EST
        datetime(1996, 10, 26, 16,  0,  0), #  39600  3600 EST
        datetime(1997,  3, 29, 16,  0,  0), #  36000     0 EST
        datetime(1997, 10, 25, 16,  0,  0), #  39600  3600 EST
        datetime(1998,  3, 28, 16,  0,  0), #  36000     0 EST
        datetime(1998, 10, 24, 16,  0,  0), #  39600  3600 EST
        datetime(1999,  3, 27, 16,  0,  0), #  36000     0 EST
        datetime(1999, 10, 30, 16,  0,  0), #  39600  3600 EST
        datetime(2000,  3, 25, 16,  0,  0), #  36000     0 EST
        datetime(2000,  8, 26, 16,  0,  0), #  39600  3600 EST
        datetime(2001,  3, 24, 16,  0,  0), #  36000     0 EST
        datetime(2001, 10, 27, 16,  0,  0), #  39600  3600 EST
        datetime(2002,  3, 30, 16,  0,  0), #  36000     0 EST
        datetime(2002, 10, 26, 16,  0,  0), #  39600  3600 EST
        datetime(2003,  3, 29, 16,  0,  0), #  36000     0 EST
        datetime(2003, 10, 25, 16,  0,  0), #  39600  3600 EST
        datetime(2004,  3, 27, 16,  0,  0), #  36000     0 EST
        datetime(2004, 10, 30, 16,  0,  0), #  39600  3600 EST
        datetime(2005,  3, 26, 16,  0,  0), #  36000     0 EST
        datetime(2005, 10, 29, 16,  0,  0), #  39600  3600 EST
        datetime(2006,  3, 25, 16,  0,  0), #  36000     0 EST
        datetime(2006, 10, 28, 16,  0,  0), #  39600  3600 EST
        datetime(2007,  3, 24, 16,  0,  0), #  36000     0 EST
        datetime(2007, 10, 27, 16,  0,  0), #  39600  3600 EST
        datetime(2008,  3, 29, 16,  0,  0), #  36000     0 EST
        datetime(2008, 10, 25, 16,  0,  0), #  39600  3600 EST
        datetime(2009,  3, 28, 16,  0,  0), #  36000     0 EST
        datetime(2009, 10, 24, 16,  0,  0), #  39600  3600 EST
        datetime(2010,  3, 27, 16,  0,  0), #  36000     0 EST
        datetime(2010, 10, 30, 16,  0,  0), #  39600  3600 EST
        datetime(2011,  3, 26, 16,  0,  0), #  36000     0 EST
        datetime(2011, 10, 29, 16,  0,  0), #  39600  3600 EST
        datetime(2012,  3, 24, 16,  0,  0), #  36000     0 EST
        datetime(2012, 10, 27, 16,  0,  0), #  39600  3600 EST
        datetime(2013,  3, 30, 16,  0,  0), #  36000     0 EST
        datetime(2013, 10, 26, 16,  0,  0), #  39600  3600 EST
        datetime(2014,  3, 29, 16,  0,  0), #  36000     0 EST
        datetime(2014, 10, 25, 16,  0,  0), #  39600  3600 EST
        datetime(2015,  3, 28, 16,  0,  0), #  36000     0 EST
        datetime(2015, 10, 24, 16,  0,  0), #  39600  3600 EST
        datetime(2016,  3, 26, 16,  0,  0), #  36000     0 EST
        datetime(2016, 10, 29, 16,  0,  0), #  39600  3600 EST
        datetime(2017,  3, 25, 16,  0,  0), #  36000     0 EST
        datetime(2017, 10, 28, 16,  0,  0), #  39600  3600 EST
        datetime(2018,  3, 24, 16,  0,  0), #  36000     0 EST
        datetime(2018, 10, 27, 16,  0,  0), #  39600  3600 EST
        datetime(2019,  3, 30, 16,  0,  0), #  36000     0 EST
        datetime(2019, 10, 26, 16,  0,  0), #  39600  3600 EST
        datetime(2020,  3, 28, 16,  0,  0), #  36000     0 EST
        datetime(2020, 10, 24, 16,  0,  0), #  39600  3600 EST
        datetime(2021,  3, 27, 16,  0,  0), #  36000     0 EST
        datetime(2021, 10, 30, 16,  0,  0), #  39600  3600 EST
        datetime(2022,  3, 26, 16,  0,  0), #  36000     0 EST
        datetime(2022, 10, 29, 16,  0,  0), #  39600  3600 EST
        datetime(2023,  3, 25, 16,  0,  0), #  36000     0 EST
        datetime(2023, 10, 28, 16,  0,  0), #  39600  3600 EST
        datetime(2024,  3, 30, 16,  0,  0), #  36000     0 EST
        datetime(2024, 10, 26, 16,  0,  0), #  39600  3600 EST
        datetime(2025,  3, 29, 16,  0,  0), #  36000     0 EST
        datetime(2025, 10, 25, 16,  0,  0), #  39600  3600 EST
        datetime(2026,  3, 28, 16,  0,  0), #  36000     0 EST
        datetime(2026, 10, 24, 16,  0,  0), #  39600  3600 EST
        datetime(2027,  3, 27, 16,  0,  0), #  36000     0 EST
        datetime(2027, 10, 30, 16,  0,  0), #  39600  3600 EST
        datetime(2028,  3, 25, 16,  0,  0), #  36000     0 EST
        datetime(2028, 10, 28, 16,  0,  0), #  39600  3600 EST
        datetime(2029,  3, 24, 16,  0,  0), #  36000     0 EST
        datetime(2029, 10, 27, 16,  0,  0), #  39600  3600 EST
        datetime(2030,  3, 30, 16,  0,  0), #  36000     0 EST
        datetime(2030, 10, 26, 16,  0,  0), #  39600  3600 EST
        datetime(2031,  3, 29, 16,  0,  0), #  36000     0 EST
        datetime(2031, 10, 25, 16,  0,  0), #  39600  3600 EST
        datetime(2032,  3, 27, 16,  0,  0), #  36000     0 EST
        datetime(2032, 10, 30, 16,  0,  0), #  39600  3600 EST
        datetime(2033,  3, 26, 16,  0,  0), #  36000     0 EST
        datetime(2033, 10, 29, 16,  0,  0), #  39600  3600 EST
        datetime(2034,  3, 25, 16,  0,  0), #  36000     0 EST
        datetime(2034, 10, 28, 16,  0,  0), #  39600  3600 EST
        datetime(2035,  3, 24, 16,  0,  0), #  36000     0 EST
        datetime(2035, 10, 27, 16,  0,  0), #  39600  3600 EST
        datetime(2036,  3, 29, 16,  0,  0), #  36000     0 EST
        datetime(2036, 10, 25, 16,  0,  0), #  39600  3600 EST
        datetime(2037,  3, 28, 16,  0,  0), #  36000     0 EST
        datetime(2037, 10, 24, 16,  0,  0), #  39600  3600 EST
        ]

    _transition_info = [
        ttinfo( 36000,      0,  'EST'),
        ttinfo( 39600,   3600,  'EST'),
        ttinfo( 36000,      0,  'EST'),
        ttinfo( 39600,   3600,  'EST'),
        ttinfo( 36000,      0,  'EST'),
        ttinfo( 39600,   3600,  'EST'),
        ttinfo( 36000,      0,  'EST'),
        ttinfo( 39600,   3600,  'EST'),
        ttinfo( 36000,      0,  'EST'),
        ttinfo( 39600,   3600,  'EST'),
        ttinfo( 36000,      0,  'EST'),
        ttinfo( 39600,   3600,  'EST'),
        ttinfo( 36000,      0,  'EST'),
        ttinfo( 39600,   3600,  'EST'),
        ttinfo( 36000,      0,  'EST'),
        ttinfo( 39600,   3600,  'EST'),
        ttinfo( 36000,      0,  'EST'),
        ttinfo( 39600,   3600,  'EST'),
        ttinfo( 36000,      0,  'EST'),
        ttinfo( 39600,   3600,  'EST'),
        ttinfo( 36000,      0,  'EST'),
        ttinfo( 39600,   3600,  'EST'),
        ttinfo( 36000,      0,  'EST'),
        ttinfo( 39600,   3600,  'EST'),
        ttinfo( 36000,      0,  'EST'),
        ttinfo( 39600,   3600,  'EST'),
        ttinfo( 36000,      0,  'EST'),
        ttinfo( 39600,   3600,  'EST'),
        ttinfo( 36000,      0,  'EST'),
        ttinfo( 39600,   3600,  'EST'),
        ttinfo( 36000,      0,  'EST'),
        ttinfo( 39600,   3600,  'EST'),
        ttinfo( 36000,      0,  'EST'),
        ttinfo( 39600,   3600,  'EST'),
        ttinfo( 36000,      0,  'EST'),
        ttinfo( 39600,   3600,  'EST'),
        ttinfo( 36000,      0,  'EST'),
        ttinfo( 39600,   3600,  'EST'),
        ttinfo( 36000,      0,  'EST'),
        ttinfo( 39600,   3600,  'EST'),
        ttinfo( 36000,      0,  'EST'),
        ttinfo( 39600,   3600,  'EST'),
        ttinfo( 36000,      0,  'EST'),
        ttinfo( 39600,   3600,  'EST'),
        ttinfo( 36000,      0,  'EST'),
        ttinfo( 39600,   3600,  'EST'),
        ttinfo( 36000,      0,  'EST'),
        ttinfo( 39600,   3600,  'EST'),
        ttinfo( 36000,      0,  'EST'),
        ttinfo( 39600,   3600,  'EST'),
        ttinfo( 36000,      0,  'EST'),
        ttinfo( 39600,   3600,  'EST'),
        ttinfo( 36000,      0,  'EST'),
        ttinfo( 39600,   3600,  'EST'),
        ttinfo( 36000,      0,  'EST'),
        ttinfo( 39600,   3600,  'EST'),
        ttinfo( 36000,      0,  'EST'),
        ttinfo( 39600,   3600,  'EST'),
        ttinfo( 36000,      0,  'EST'),
        ttinfo( 39600,   3600,  'EST'),
        ttinfo( 36000,      0,  'EST'),
        ttinfo( 39600,   3600,  'EST'),
        ttinfo( 36000,      0,  'EST'),
        ttinfo( 39600,   3600,  'EST'),
        ttinfo( 36000,      0,  'EST'),
        ttinfo( 39600,   3600,  'EST'),
        ttinfo( 36000,      0,  'EST'),
        ttinfo( 39600,   3600,  'EST'),
        ttinfo( 36000,      0,  'EST'),
        ttinfo( 39600,   3600,  'EST'),
        ttinfo( 36000,      0,  'EST'),
        ttinfo( 39600,   3600,  'EST'),
        ttinfo( 36000,      0,  'EST'),
        ttinfo( 39600,   3600,  'EST'),
        ttinfo( 36000,      0,  'EST'),
        ttinfo( 39600,   3600,  'EST'),
        ttinfo( 36000,      0,  'EST'),
        ttinfo( 39600,   3600,  'EST'),
        ttinfo( 36000,      0,  'EST'),
        ttinfo( 39600,   3600,  'EST'),
        ttinfo( 36000,      0,  'EST'),
        ttinfo( 39600,   3600,  'EST'),
        ttinfo( 36000,      0,  'EST'),
        ttinfo( 39600,   3600,  'EST'),
        ttinfo( 36000,      0,  'EST'),
        ttinfo( 39600,   3600,  'EST'),
        ttinfo( 36000,      0,  'EST'),
        ttinfo( 39600,   3600,  'EST'),
        ttinfo( 36000,      0,  'EST'),
        ttinfo( 39600,   3600,  'EST'),
        ttinfo( 36000,      0,  'EST'),
        ttinfo( 39600,   3600,  'EST'),
        ttinfo( 36000,      0,  'EST'),
        ttinfo( 39600,   3600,  'EST'),
        ttinfo( 36000,      0,  'EST'),
        ttinfo( 39600,   3600,  'EST'),
        ttinfo( 36000,      0,  'EST'),
        ttinfo( 39600,   3600,  'EST'),
        ttinfo( 36000,      0,  'EST'),
        ttinfo( 39600,   3600,  'EST'),
        ttinfo( 36000,      0,  'EST'),
        ttinfo( 39600,   3600,  'EST'),
        ttinfo( 36000,      0,  'EST'),
        ttinfo( 39600,   3600,  'EST'),
        ttinfo( 36000,      0,  'EST'),
        ttinfo( 39600,   3600,  'EST'),
        ttinfo( 36000,      0,  'EST'),
        ttinfo( 39600,   3600,  'EST'),
        ttinfo( 36000,      0,  'EST'),
        ttinfo( 39600,   3600,  'EST'),
        ttinfo( 36000,      0,  'EST'),
        ttinfo( 39600,   3600,  'EST'),
        ttinfo( 36000,      0,  'EST'),
        ttinfo( 39600,   3600,  'EST'),
        ttinfo( 36000,      0,  'EST'),
        ttinfo( 39600,   3600,  'EST'),
        ttinfo( 36000,      0,  'EST'),
        ttinfo( 39600,   3600,  'EST'),
        ttinfo( 36000,      0,  'EST'),
        ttinfo( 39600,   3600,  'EST'),
        ttinfo( 36000,      0,  'EST'),
        ttinfo( 39600,   3600,  'EST'),
        ttinfo( 36000,      0,  'EST'),
        ttinfo( 39600,   3600,  'EST'),
        ttinfo( 36000,      0,  'EST'),
        ttinfo( 39600,   3600,  'EST'),
        ttinfo( 36000,      0,  'EST'),
        ttinfo( 39600,   3600,  'EST'),
        ttinfo( 36000,      0,  'EST'),
        ttinfo( 39600,   3600,  'EST'),
        ttinfo( 36000,      0,  'EST'),
        ttinfo( 39600,   3600,  'EST'),
        ttinfo( 36000,      0,  'EST'),
        ttinfo( 39600,   3600,  'EST'),
        ttinfo( 36000,      0,  'EST'),
        ttinfo( 39600,   3600,  'EST'),
        ttinfo( 36000,      0,  'EST'),
        ttinfo( 39600,   3600,  'EST'),
        ttinfo( 36000,      0,  'EST'),
        ttinfo( 39600,   3600,  'EST'),
        ttinfo( 36000,      0,  'EST'),
        ttinfo( 39600,   3600,  'EST'),
        ]

Sydney = Sydney() # Singleton

