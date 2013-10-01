'''
tzinfo timezone information for Brazil/East.

Generated from the Olson timezone database:
    ftp://elsie.nci.nih.gov/pub/tz*.tar.gz
'''

from pytz.tzinfo import DstTzInfo
from pytz.tzinfo import memorized_datetime as datetime
from pytz.tzinfo import memorized_ttinfo as ttinfo

class East(DstTzInfo):
    '''Brazil/East timezone definition. See datetime.tzinfo for details'''

    _zone = 'Brazil/East'

    _utc_transition_times = [
        datetime(   1,  1,  1,  0,  0,  0), # -11188     0 LMT
        datetime(1914,  1,  1,  3,  6, 28), # -10800     0 BRT
        datetime(1931, 10,  3, 14,  0,  0), #  -7200  3600 BRST
        datetime(1932,  4,  1,  2,  0,  0), # -10800     0 BRT
        datetime(1932, 10,  3,  3,  0,  0), #  -7200  3600 BRST
        datetime(1933,  4,  1,  2,  0,  0), # -10800     0 BRT
        datetime(1949, 12,  1,  3,  0,  0), #  -7200  3600 BRST
        datetime(1950,  4, 16,  3,  0,  0), # -10800     0 BRT
        datetime(1950, 12,  1,  3,  0,  0), #  -7200  3600 BRST
        datetime(1951,  4,  1,  2,  0,  0), # -10800     0 BRT
        datetime(1951, 12,  1,  3,  0,  0), #  -7200  3600 BRST
        datetime(1952,  4,  1,  2,  0,  0), # -10800     0 BRT
        datetime(1952, 12,  1,  3,  0,  0), #  -7200  3600 BRST
        datetime(1953,  3,  1,  2,  0,  0), # -10800     0 BRT
        datetime(1963, 10, 23,  3,  0,  0), #  -7200  3600 BRST
        datetime(1964,  3,  1,  2,  0,  0), # -10800     0 BRT
        datetime(1965,  1, 31,  3,  0,  0), #  -7200  3600 BRST
        datetime(1965,  3, 31,  2,  0,  0), # -10800     0 BRT
        datetime(1965, 12,  1,  3,  0,  0), #  -7200  3600 BRST
        datetime(1966,  3,  1,  2,  0,  0), # -10800     0 BRT
        datetime(1966, 11,  1,  3,  0,  0), #  -7200  3600 BRST
        datetime(1967,  3,  1,  2,  0,  0), # -10800     0 BRT
        datetime(1967, 11,  1,  3,  0,  0), #  -7200  3600 BRST
        datetime(1968,  3,  1,  2,  0,  0), # -10800     0 BRT
        datetime(1985, 11,  2,  3,  0,  0), #  -7200  3600 BRST
        datetime(1986,  3, 15,  2,  0,  0), # -10800     0 BRT
        datetime(1986, 10, 25,  3,  0,  0), #  -7200  3600 BRST
        datetime(1987,  2, 14,  2,  0,  0), # -10800     0 BRT
        datetime(1987, 10, 25,  3,  0,  0), #  -7200  3600 BRST
        datetime(1988,  2,  7,  2,  0,  0), # -10800     0 BRT
        datetime(1988, 10, 16,  3,  0,  0), #  -7200  3600 BRST
        datetime(1989,  1, 29,  2,  0,  0), # -10800     0 BRT
        datetime(1989, 10, 15,  3,  0,  0), #  -7200  3600 BRST
        datetime(1990,  2, 11,  2,  0,  0), # -10800     0 BRT
        datetime(1990, 10, 21,  3,  0,  0), #  -7200  3600 BRST
        datetime(1991,  2, 17,  2,  0,  0), # -10800     0 BRT
        datetime(1991, 10, 20,  3,  0,  0), #  -7200  3600 BRST
        datetime(1992,  2,  9,  2,  0,  0), # -10800     0 BRT
        datetime(1992, 10, 25,  3,  0,  0), #  -7200  3600 BRST
        datetime(1993,  1, 31,  2,  0,  0), # -10800     0 BRT
        datetime(1993, 10, 17,  3,  0,  0), #  -7200  3600 BRST
        datetime(1994,  2, 20,  2,  0,  0), # -10800     0 BRT
        datetime(1994, 10, 16,  3,  0,  0), #  -7200  3600 BRST
        datetime(1995,  2, 19,  2,  0,  0), # -10800     0 BRT
        datetime(1995, 10, 15,  3,  0,  0), #  -7200  3600 BRST
        datetime(1996,  2, 11,  2,  0,  0), # -10800     0 BRT
        datetime(1996, 10,  6,  3,  0,  0), #  -7200  3600 BRST
        datetime(1997,  2, 16,  2,  0,  0), # -10800     0 BRT
        datetime(1997, 10,  6,  3,  0,  0), #  -7200  3600 BRST
        datetime(1998,  3,  1,  2,  0,  0), # -10800     0 BRT
        datetime(1998, 10, 11,  3,  0,  0), #  -7200  3600 BRST
        datetime(1999,  2, 21,  2,  0,  0), # -10800     0 BRT
        datetime(1999, 10,  3,  3,  0,  0), #  -7200  3600 BRST
        datetime(2000,  2, 27,  2,  0,  0), # -10800     0 BRT
        datetime(2000, 10,  8,  3,  0,  0), #  -7200  3600 BRST
        datetime(2001,  2, 18,  2,  0,  0), # -10800     0 BRT
        datetime(2001, 10, 14,  3,  0,  0), #  -7200  3600 BRST
        datetime(2002,  2, 17,  2,  0,  0), # -10800     0 BRT
        datetime(2002, 11,  3,  3,  0,  0), #  -7200  3600 BRST
        datetime(2003,  2, 16,  2,  0,  0), # -10800     0 BRT
        datetime(2003, 10, 19,  3,  0,  0), #  -7200  3600 BRST
        datetime(2004,  2, 15,  2,  0,  0), # -10800     0 BRT
        datetime(2004, 10, 17,  3,  0,  0), #  -7200  3600 BRST
        datetime(2005,  2, 20,  2,  0,  0), # -10800     0 BRT
        datetime(2005, 10, 16,  3,  0,  0), #  -7200  3600 BRST
        datetime(2006,  2, 19,  2,  0,  0), # -10800     0 BRT
        datetime(2006, 10, 15,  3,  0,  0), #  -7200  3600 BRST
        datetime(2007,  2, 18,  2,  0,  0), # -10800     0 BRT
        datetime(2007, 10, 21,  3,  0,  0), #  -7200  3600 BRST
        datetime(2008,  2, 17,  2,  0,  0), # -10800     0 BRT
        datetime(2008, 10, 19,  3,  0,  0), #  -7200  3600 BRST
        datetime(2009,  2, 15,  2,  0,  0), # -10800     0 BRT
        datetime(2009, 10, 18,  3,  0,  0), #  -7200  3600 BRST
        datetime(2010,  2, 21,  2,  0,  0), # -10800     0 BRT
        datetime(2010, 10, 17,  3,  0,  0), #  -7200  3600 BRST
        datetime(2011,  2, 20,  2,  0,  0), # -10800     0 BRT
        datetime(2011, 10, 16,  3,  0,  0), #  -7200  3600 BRST
        datetime(2012,  2, 19,  2,  0,  0), # -10800     0 BRT
        datetime(2012, 10, 21,  3,  0,  0), #  -7200  3600 BRST
        datetime(2013,  2, 17,  2,  0,  0), # -10800     0 BRT
        datetime(2013, 10, 20,  3,  0,  0), #  -7200  3600 BRST
        datetime(2014,  2, 16,  2,  0,  0), # -10800     0 BRT
        datetime(2014, 10, 19,  3,  0,  0), #  -7200  3600 BRST
        datetime(2015,  2, 15,  2,  0,  0), # -10800     0 BRT
        datetime(2015, 10, 18,  3,  0,  0), #  -7200  3600 BRST
        datetime(2016,  2, 21,  2,  0,  0), # -10800     0 BRT
        datetime(2016, 10, 16,  3,  0,  0), #  -7200  3600 BRST
        datetime(2017,  2, 19,  2,  0,  0), # -10800     0 BRT
        datetime(2017, 10, 15,  3,  0,  0), #  -7200  3600 BRST
        datetime(2018,  2, 18,  2,  0,  0), # -10800     0 BRT
        datetime(2018, 10, 21,  3,  0,  0), #  -7200  3600 BRST
        datetime(2019,  2, 17,  2,  0,  0), # -10800     0 BRT
        datetime(2019, 10, 20,  3,  0,  0), #  -7200  3600 BRST
        datetime(2020,  2, 16,  2,  0,  0), # -10800     0 BRT
        datetime(2020, 10, 18,  3,  0,  0), #  -7200  3600 BRST
        datetime(2021,  2, 21,  2,  0,  0), # -10800     0 BRT
        datetime(2021, 10, 17,  3,  0,  0), #  -7200  3600 BRST
        datetime(2022,  2, 20,  2,  0,  0), # -10800     0 BRT
        datetime(2022, 10, 16,  3,  0,  0), #  -7200  3600 BRST
        datetime(2023,  2, 19,  2,  0,  0), # -10800     0 BRT
        datetime(2023, 10, 15,  3,  0,  0), #  -7200  3600 BRST
        datetime(2024,  2, 18,  2,  0,  0), # -10800     0 BRT
        datetime(2024, 10, 20,  3,  0,  0), #  -7200  3600 BRST
        datetime(2025,  2, 16,  2,  0,  0), # -10800     0 BRT
        datetime(2025, 10, 19,  3,  0,  0), #  -7200  3600 BRST
        datetime(2026,  2, 15,  2,  0,  0), # -10800     0 BRT
        datetime(2026, 10, 18,  3,  0,  0), #  -7200  3600 BRST
        datetime(2027,  2, 21,  2,  0,  0), # -10800     0 BRT
        datetime(2027, 10, 17,  3,  0,  0), #  -7200  3600 BRST
        datetime(2028,  2, 20,  2,  0,  0), # -10800     0 BRT
        datetime(2028, 10, 15,  3,  0,  0), #  -7200  3600 BRST
        datetime(2029,  2, 18,  2,  0,  0), # -10800     0 BRT
        datetime(2029, 10, 21,  3,  0,  0), #  -7200  3600 BRST
        datetime(2030,  2, 17,  2,  0,  0), # -10800     0 BRT
        datetime(2030, 10, 20,  3,  0,  0), #  -7200  3600 BRST
        datetime(2031,  2, 16,  2,  0,  0), # -10800     0 BRT
        datetime(2031, 10, 19,  3,  0,  0), #  -7200  3600 BRST
        datetime(2032,  2, 15,  2,  0,  0), # -10800     0 BRT
        datetime(2032, 10, 17,  3,  0,  0), #  -7200  3600 BRST
        datetime(2033,  2, 20,  2,  0,  0), # -10800     0 BRT
        datetime(2033, 10, 16,  3,  0,  0), #  -7200  3600 BRST
        datetime(2034,  2, 19,  2,  0,  0), # -10800     0 BRT
        datetime(2034, 10, 15,  3,  0,  0), #  -7200  3600 BRST
        datetime(2035,  2, 18,  2,  0,  0), # -10800     0 BRT
        datetime(2035, 10, 21,  3,  0,  0), #  -7200  3600 BRST
        datetime(2036,  2, 17,  2,  0,  0), # -10800     0 BRT
        datetime(2036, 10, 19,  3,  0,  0), #  -7200  3600 BRST
        datetime(2037,  2, 15,  2,  0,  0), # -10800     0 BRT
        datetime(2037, 10, 18,  3,  0,  0), #  -7200  3600 BRST
        ]

    _transition_info = [
        ttinfo(-11188,      0,  'LMT'),
        ttinfo(-10800,      0,  'BRT'),
        ttinfo( -7200,   3600, 'BRST'),
        ttinfo(-10800,      0,  'BRT'),
        ttinfo( -7200,   3600, 'BRST'),
        ttinfo(-10800,      0,  'BRT'),
        ttinfo( -7200,   3600, 'BRST'),
        ttinfo(-10800,      0,  'BRT'),
        ttinfo( -7200,   3600, 'BRST'),
        ttinfo(-10800,      0,  'BRT'),
        ttinfo( -7200,   3600, 'BRST'),
        ttinfo(-10800,      0,  'BRT'),
        ttinfo( -7200,   3600, 'BRST'),
        ttinfo(-10800,      0,  'BRT'),
        ttinfo( -7200,   3600, 'BRST'),
        ttinfo(-10800,      0,  'BRT'),
        ttinfo( -7200,   3600, 'BRST'),
        ttinfo(-10800,      0,  'BRT'),
        ttinfo( -7200,   3600, 'BRST'),
        ttinfo(-10800,      0,  'BRT'),
        ttinfo( -7200,   3600, 'BRST'),
        ttinfo(-10800,      0,  'BRT'),
        ttinfo( -7200,   3600, 'BRST'),
        ttinfo(-10800,      0,  'BRT'),
        ttinfo( -7200,   3600, 'BRST'),
        ttinfo(-10800,      0,  'BRT'),
        ttinfo( -7200,   3600, 'BRST'),
        ttinfo(-10800,      0,  'BRT'),
        ttinfo( -7200,   3600, 'BRST'),
        ttinfo(-10800,      0,  'BRT'),
        ttinfo( -7200,   3600, 'BRST'),
        ttinfo(-10800,      0,  'BRT'),
        ttinfo( -7200,   3600, 'BRST'),
        ttinfo(-10800,      0,  'BRT'),
        ttinfo( -7200,   3600, 'BRST'),
        ttinfo(-10800,      0,  'BRT'),
        ttinfo( -7200,   3600, 'BRST'),
        ttinfo(-10800,      0,  'BRT'),
        ttinfo( -7200,   3600, 'BRST'),
        ttinfo(-10800,      0,  'BRT'),
        ttinfo( -7200,   3600, 'BRST'),
        ttinfo(-10800,      0,  'BRT'),
        ttinfo( -7200,   3600, 'BRST'),
        ttinfo(-10800,      0,  'BRT'),
        ttinfo( -7200,   3600, 'BRST'),
        ttinfo(-10800,      0,  'BRT'),
        ttinfo( -7200,   3600, 'BRST'),
        ttinfo(-10800,      0,  'BRT'),
        ttinfo( -7200,   3600, 'BRST'),
        ttinfo(-10800,      0,  'BRT'),
        ttinfo( -7200,   3600, 'BRST'),
        ttinfo(-10800,      0,  'BRT'),
        ttinfo( -7200,   3600, 'BRST'),
        ttinfo(-10800,      0,  'BRT'),
        ttinfo( -7200,   3600, 'BRST'),
        ttinfo(-10800,      0,  'BRT'),
        ttinfo( -7200,   3600, 'BRST'),
        ttinfo(-10800,      0,  'BRT'),
        ttinfo( -7200,   3600, 'BRST'),
        ttinfo(-10800,      0,  'BRT'),
        ttinfo( -7200,   3600, 'BRST'),
        ttinfo(-10800,      0,  'BRT'),
        ttinfo( -7200,   3600, 'BRST'),
        ttinfo(-10800,      0,  'BRT'),
        ttinfo( -7200,   3600, 'BRST'),
        ttinfo(-10800,      0,  'BRT'),
        ttinfo( -7200,   3600, 'BRST'),
        ttinfo(-10800,      0,  'BRT'),
        ttinfo( -7200,   3600, 'BRST'),
        ttinfo(-10800,      0,  'BRT'),
        ttinfo( -7200,   3600, 'BRST'),
        ttinfo(-10800,      0,  'BRT'),
        ttinfo( -7200,   3600, 'BRST'),
        ttinfo(-10800,      0,  'BRT'),
        ttinfo( -7200,   3600, 'BRST'),
        ttinfo(-10800,      0,  'BRT'),
        ttinfo( -7200,   3600, 'BRST'),
        ttinfo(-10800,      0,  'BRT'),
        ttinfo( -7200,   3600, 'BRST'),
        ttinfo(-10800,      0,  'BRT'),
        ttinfo( -7200,   3600, 'BRST'),
        ttinfo(-10800,      0,  'BRT'),
        ttinfo( -7200,   3600, 'BRST'),
        ttinfo(-10800,      0,  'BRT'),
        ttinfo( -7200,   3600, 'BRST'),
        ttinfo(-10800,      0,  'BRT'),
        ttinfo( -7200,   3600, 'BRST'),
        ttinfo(-10800,      0,  'BRT'),
        ttinfo( -7200,   3600, 'BRST'),
        ttinfo(-10800,      0,  'BRT'),
        ttinfo( -7200,   3600, 'BRST'),
        ttinfo(-10800,      0,  'BRT'),
        ttinfo( -7200,   3600, 'BRST'),
        ttinfo(-10800,      0,  'BRT'),
        ttinfo( -7200,   3600, 'BRST'),
        ttinfo(-10800,      0,  'BRT'),
        ttinfo( -7200,   3600, 'BRST'),
        ttinfo(-10800,      0,  'BRT'),
        ttinfo( -7200,   3600, 'BRST'),
        ttinfo(-10800,      0,  'BRT'),
        ttinfo( -7200,   3600, 'BRST'),
        ttinfo(-10800,      0,  'BRT'),
        ttinfo( -7200,   3600, 'BRST'),
        ttinfo(-10800,      0,  'BRT'),
        ttinfo( -7200,   3600, 'BRST'),
        ttinfo(-10800,      0,  'BRT'),
        ttinfo( -7200,   3600, 'BRST'),
        ttinfo(-10800,      0,  'BRT'),
        ttinfo( -7200,   3600, 'BRST'),
        ttinfo(-10800,      0,  'BRT'),
        ttinfo( -7200,   3600, 'BRST'),
        ttinfo(-10800,      0,  'BRT'),
        ttinfo( -7200,   3600, 'BRST'),
        ttinfo(-10800,      0,  'BRT'),
        ttinfo( -7200,   3600, 'BRST'),
        ttinfo(-10800,      0,  'BRT'),
        ttinfo( -7200,   3600, 'BRST'),
        ttinfo(-10800,      0,  'BRT'),
        ttinfo( -7200,   3600, 'BRST'),
        ttinfo(-10800,      0,  'BRT'),
        ttinfo( -7200,   3600, 'BRST'),
        ttinfo(-10800,      0,  'BRT'),
        ttinfo( -7200,   3600, 'BRST'),
        ttinfo(-10800,      0,  'BRT'),
        ttinfo( -7200,   3600, 'BRST'),
        ttinfo(-10800,      0,  'BRT'),
        ttinfo( -7200,   3600, 'BRST'),
        ttinfo(-10800,      0,  'BRT'),
        ttinfo( -7200,   3600, 'BRST'),
        ]

East = East() # Singleton

