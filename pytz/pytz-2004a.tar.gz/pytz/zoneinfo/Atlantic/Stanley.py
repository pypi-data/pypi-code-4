'''
tzinfo timezone information for Atlantic/Stanley.

Generated from the Olson timezone database:
    ftp://elsie.nci.nih.gov/pub/tz*.tar.gz
'''

from pytz.tzinfo import DstTzInfo
from pytz.tzinfo import memorized_datetime as datetime
from pytz.tzinfo import memorized_ttinfo as ttinfo

class Stanley(DstTzInfo):
    '''Atlantic/Stanley timezone definition. See datetime.tzinfo for details'''

    _zone = 'Atlantic/Stanley'

    _utc_transition_times = [
        datetime(   1,  1,  1,  0,  0,  0), # -13884     0 SMT
        datetime(1912,  3, 12,  3, 51, 24), # -14400     0 FKT
        datetime(1937,  9, 26,  4,  0,  0), # -10800  3600 FKST
        datetime(1938,  3, 20,  3,  0,  0), # -14400     0 FKT
        datetime(1938,  9, 25,  4,  0,  0), # -10800  3600 FKST
        datetime(1939,  3, 19,  3,  0,  0), # -14400     0 FKT
        datetime(1939, 10,  1,  4,  0,  0), # -10800  3600 FKST
        datetime(1940,  3, 24,  3,  0,  0), # -14400     0 FKT
        datetime(1940,  9, 29,  4,  0,  0), # -10800  3600 FKST
        datetime(1941,  3, 23,  3,  0,  0), # -14400     0 FKT
        datetime(1941,  9, 28,  4,  0,  0), # -10800  3600 FKST
        datetime(1942,  3, 22,  3,  0,  0), # -14400     0 FKT
        datetime(1942,  9, 27,  4,  0,  0), # -10800  3600 FKST
        datetime(1943,  1,  1,  3,  0,  0), # -14400     0 FKT
        datetime(1983,  5,  1,  4,  0,  0), # -10800     0 FKT
        datetime(1983,  9, 25,  3,  0,  0), #  -7200  3600 FKST
        datetime(1984,  4, 29,  2,  0,  0), # -10800     0 FKT
        datetime(1984,  9, 16,  3,  0,  0), #  -7200  3600 FKST
        datetime(1985,  4, 28,  2,  0,  0), # -10800     0 FKT
        datetime(1985,  9, 15,  3,  0,  0), # -10800     0 FKST
        datetime(1986,  4, 20,  3,  0,  0), # -14400     0 FKT
        datetime(1986,  9, 14,  4,  0,  0), # -10800  3600 FKST
        datetime(1987,  4, 19,  3,  0,  0), # -14400     0 FKT
        datetime(1987,  9, 13,  4,  0,  0), # -10800  3600 FKST
        datetime(1988,  4, 17,  3,  0,  0), # -14400     0 FKT
        datetime(1988,  9, 11,  4,  0,  0), # -10800  3600 FKST
        datetime(1989,  4, 16,  3,  0,  0), # -14400     0 FKT
        datetime(1989,  9, 10,  4,  0,  0), # -10800  3600 FKST
        datetime(1990,  4, 22,  3,  0,  0), # -14400     0 FKT
        datetime(1990,  9,  9,  4,  0,  0), # -10800  3600 FKST
        datetime(1991,  4, 21,  3,  0,  0), # -14400     0 FKT
        datetime(1991,  9, 15,  4,  0,  0), # -10800  3600 FKST
        datetime(1992,  4, 19,  3,  0,  0), # -14400     0 FKT
        datetime(1992,  9, 13,  4,  0,  0), # -10800  3600 FKST
        datetime(1993,  4, 18,  3,  0,  0), # -14400     0 FKT
        datetime(1993,  9, 12,  4,  0,  0), # -10800  3600 FKST
        datetime(1994,  4, 17,  3,  0,  0), # -14400     0 FKT
        datetime(1994,  9, 11,  4,  0,  0), # -10800  3600 FKST
        datetime(1995,  4, 16,  3,  0,  0), # -14400     0 FKT
        datetime(1995,  9, 10,  4,  0,  0), # -10800  3600 FKST
        datetime(1996,  4, 21,  3,  0,  0), # -14400     0 FKT
        datetime(1996,  9, 15,  4,  0,  0), # -10800  3600 FKST
        datetime(1997,  4, 20,  3,  0,  0), # -14400     0 FKT
        datetime(1997,  9, 14,  4,  0,  0), # -10800  3600 FKST
        datetime(1998,  4, 19,  3,  0,  0), # -14400     0 FKT
        datetime(1998,  9, 13,  4,  0,  0), # -10800  3600 FKST
        datetime(1999,  4, 18,  3,  0,  0), # -14400     0 FKT
        datetime(1999,  9, 12,  4,  0,  0), # -10800  3600 FKST
        datetime(2000,  4, 16,  3,  0,  0), # -14400     0 FKT
        datetime(2000,  9, 10,  4,  0,  0), # -10800  3600 FKST
        datetime(2001,  4, 15,  5,  0,  0), # -14400     0 FKT
        datetime(2001,  9,  2,  6,  0,  0), # -10800  3600 FKST
        datetime(2002,  4, 21,  5,  0,  0), # -14400     0 FKT
        datetime(2002,  9,  1,  6,  0,  0), # -10800  3600 FKST
        datetime(2003,  4, 20,  5,  0,  0), # -14400     0 FKT
        datetime(2003,  9,  7,  6,  0,  0), # -10800  3600 FKST
        datetime(2004,  4, 18,  5,  0,  0), # -14400     0 FKT
        datetime(2004,  9,  5,  6,  0,  0), # -10800  3600 FKST
        datetime(2005,  4, 17,  5,  0,  0), # -14400     0 FKT
        datetime(2005,  9,  4,  6,  0,  0), # -10800  3600 FKST
        datetime(2006,  4, 16,  5,  0,  0), # -14400     0 FKT
        datetime(2006,  9,  3,  6,  0,  0), # -10800  3600 FKST
        datetime(2007,  4, 15,  5,  0,  0), # -14400     0 FKT
        datetime(2007,  9,  2,  6,  0,  0), # -10800  3600 FKST
        datetime(2008,  4, 20,  5,  0,  0), # -14400     0 FKT
        datetime(2008,  9,  7,  6,  0,  0), # -10800  3600 FKST
        datetime(2009,  4, 19,  5,  0,  0), # -14400     0 FKT
        datetime(2009,  9,  6,  6,  0,  0), # -10800  3600 FKST
        datetime(2010,  4, 18,  5,  0,  0), # -14400     0 FKT
        datetime(2010,  9,  5,  6,  0,  0), # -10800  3600 FKST
        datetime(2011,  4, 17,  5,  0,  0), # -14400     0 FKT
        datetime(2011,  9,  4,  6,  0,  0), # -10800  3600 FKST
        datetime(2012,  4, 15,  5,  0,  0), # -14400     0 FKT
        datetime(2012,  9,  2,  6,  0,  0), # -10800  3600 FKST
        datetime(2013,  4, 21,  5,  0,  0), # -14400     0 FKT
        datetime(2013,  9,  1,  6,  0,  0), # -10800  3600 FKST
        datetime(2014,  4, 20,  5,  0,  0), # -14400     0 FKT
        datetime(2014,  9,  7,  6,  0,  0), # -10800  3600 FKST
        datetime(2015,  4, 19,  5,  0,  0), # -14400     0 FKT
        datetime(2015,  9,  6,  6,  0,  0), # -10800  3600 FKST
        datetime(2016,  4, 17,  5,  0,  0), # -14400     0 FKT
        datetime(2016,  9,  4,  6,  0,  0), # -10800  3600 FKST
        datetime(2017,  4, 16,  5,  0,  0), # -14400     0 FKT
        datetime(2017,  9,  3,  6,  0,  0), # -10800  3600 FKST
        datetime(2018,  4, 15,  5,  0,  0), # -14400     0 FKT
        datetime(2018,  9,  2,  6,  0,  0), # -10800  3600 FKST
        datetime(2019,  4, 21,  5,  0,  0), # -14400     0 FKT
        datetime(2019,  9,  1,  6,  0,  0), # -10800  3600 FKST
        datetime(2020,  4, 19,  5,  0,  0), # -14400     0 FKT
        datetime(2020,  9,  6,  6,  0,  0), # -10800  3600 FKST
        datetime(2021,  4, 18,  5,  0,  0), # -14400     0 FKT
        datetime(2021,  9,  5,  6,  0,  0), # -10800  3600 FKST
        datetime(2022,  4, 17,  5,  0,  0), # -14400     0 FKT
        datetime(2022,  9,  4,  6,  0,  0), # -10800  3600 FKST
        datetime(2023,  4, 16,  5,  0,  0), # -14400     0 FKT
        datetime(2023,  9,  3,  6,  0,  0), # -10800  3600 FKST
        datetime(2024,  4, 21,  5,  0,  0), # -14400     0 FKT
        datetime(2024,  9,  1,  6,  0,  0), # -10800  3600 FKST
        datetime(2025,  4, 20,  5,  0,  0), # -14400     0 FKT
        datetime(2025,  9,  7,  6,  0,  0), # -10800  3600 FKST
        datetime(2026,  4, 19,  5,  0,  0), # -14400     0 FKT
        datetime(2026,  9,  6,  6,  0,  0), # -10800  3600 FKST
        datetime(2027,  4, 18,  5,  0,  0), # -14400     0 FKT
        datetime(2027,  9,  5,  6,  0,  0), # -10800  3600 FKST
        datetime(2028,  4, 16,  5,  0,  0), # -14400     0 FKT
        datetime(2028,  9,  3,  6,  0,  0), # -10800  3600 FKST
        datetime(2029,  4, 15,  5,  0,  0), # -14400     0 FKT
        datetime(2029,  9,  2,  6,  0,  0), # -10800  3600 FKST
        datetime(2030,  4, 21,  5,  0,  0), # -14400     0 FKT
        datetime(2030,  9,  1,  6,  0,  0), # -10800  3600 FKST
        datetime(2031,  4, 20,  5,  0,  0), # -14400     0 FKT
        datetime(2031,  9,  7,  6,  0,  0), # -10800  3600 FKST
        datetime(2032,  4, 18,  5,  0,  0), # -14400     0 FKT
        datetime(2032,  9,  5,  6,  0,  0), # -10800  3600 FKST
        datetime(2033,  4, 17,  5,  0,  0), # -14400     0 FKT
        datetime(2033,  9,  4,  6,  0,  0), # -10800  3600 FKST
        datetime(2034,  4, 16,  5,  0,  0), # -14400     0 FKT
        datetime(2034,  9,  3,  6,  0,  0), # -10800  3600 FKST
        datetime(2035,  4, 15,  5,  0,  0), # -14400     0 FKT
        datetime(2035,  9,  2,  6,  0,  0), # -10800  3600 FKST
        datetime(2036,  4, 20,  5,  0,  0), # -14400     0 FKT
        datetime(2036,  9,  7,  6,  0,  0), # -10800  3600 FKST
        datetime(2037,  4, 19,  5,  0,  0), # -14400     0 FKT
        datetime(2037,  9,  6,  6,  0,  0), # -10800  3600 FKST
        ]

    _transition_info = [
        ttinfo(-13884,      0,  'SMT'),
        ttinfo(-14400,      0,  'FKT'),
        ttinfo(-10800,   3600, 'FKST'),
        ttinfo(-14400,      0,  'FKT'),
        ttinfo(-10800,   3600, 'FKST'),
        ttinfo(-14400,      0,  'FKT'),
        ttinfo(-10800,   3600, 'FKST'),
        ttinfo(-14400,      0,  'FKT'),
        ttinfo(-10800,   3600, 'FKST'),
        ttinfo(-14400,      0,  'FKT'),
        ttinfo(-10800,   3600, 'FKST'),
        ttinfo(-14400,      0,  'FKT'),
        ttinfo(-10800,   3600, 'FKST'),
        ttinfo(-14400,      0,  'FKT'),
        ttinfo(-10800,      0,  'FKT'),
        ttinfo( -7200,   3600, 'FKST'),
        ttinfo(-10800,      0,  'FKT'),
        ttinfo( -7200,   3600, 'FKST'),
        ttinfo(-10800,      0,  'FKT'),
        ttinfo(-10800,      0, 'FKST'),
        ttinfo(-14400,      0,  'FKT'),
        ttinfo(-10800,   3600, 'FKST'),
        ttinfo(-14400,      0,  'FKT'),
        ttinfo(-10800,   3600, 'FKST'),
        ttinfo(-14400,      0,  'FKT'),
        ttinfo(-10800,   3600, 'FKST'),
        ttinfo(-14400,      0,  'FKT'),
        ttinfo(-10800,   3600, 'FKST'),
        ttinfo(-14400,      0,  'FKT'),
        ttinfo(-10800,   3600, 'FKST'),
        ttinfo(-14400,      0,  'FKT'),
        ttinfo(-10800,   3600, 'FKST'),
        ttinfo(-14400,      0,  'FKT'),
        ttinfo(-10800,   3600, 'FKST'),
        ttinfo(-14400,      0,  'FKT'),
        ttinfo(-10800,   3600, 'FKST'),
        ttinfo(-14400,      0,  'FKT'),
        ttinfo(-10800,   3600, 'FKST'),
        ttinfo(-14400,      0,  'FKT'),
        ttinfo(-10800,   3600, 'FKST'),
        ttinfo(-14400,      0,  'FKT'),
        ttinfo(-10800,   3600, 'FKST'),
        ttinfo(-14400,      0,  'FKT'),
        ttinfo(-10800,   3600, 'FKST'),
        ttinfo(-14400,      0,  'FKT'),
        ttinfo(-10800,   3600, 'FKST'),
        ttinfo(-14400,      0,  'FKT'),
        ttinfo(-10800,   3600, 'FKST'),
        ttinfo(-14400,      0,  'FKT'),
        ttinfo(-10800,   3600, 'FKST'),
        ttinfo(-14400,      0,  'FKT'),
        ttinfo(-10800,   3600, 'FKST'),
        ttinfo(-14400,      0,  'FKT'),
        ttinfo(-10800,   3600, 'FKST'),
        ttinfo(-14400,      0,  'FKT'),
        ttinfo(-10800,   3600, 'FKST'),
        ttinfo(-14400,      0,  'FKT'),
        ttinfo(-10800,   3600, 'FKST'),
        ttinfo(-14400,      0,  'FKT'),
        ttinfo(-10800,   3600, 'FKST'),
        ttinfo(-14400,      0,  'FKT'),
        ttinfo(-10800,   3600, 'FKST'),
        ttinfo(-14400,      0,  'FKT'),
        ttinfo(-10800,   3600, 'FKST'),
        ttinfo(-14400,      0,  'FKT'),
        ttinfo(-10800,   3600, 'FKST'),
        ttinfo(-14400,      0,  'FKT'),
        ttinfo(-10800,   3600, 'FKST'),
        ttinfo(-14400,      0,  'FKT'),
        ttinfo(-10800,   3600, 'FKST'),
        ttinfo(-14400,      0,  'FKT'),
        ttinfo(-10800,   3600, 'FKST'),
        ttinfo(-14400,      0,  'FKT'),
        ttinfo(-10800,   3600, 'FKST'),
        ttinfo(-14400,      0,  'FKT'),
        ttinfo(-10800,   3600, 'FKST'),
        ttinfo(-14400,      0,  'FKT'),
        ttinfo(-10800,   3600, 'FKST'),
        ttinfo(-14400,      0,  'FKT'),
        ttinfo(-10800,   3600, 'FKST'),
        ttinfo(-14400,      0,  'FKT'),
        ttinfo(-10800,   3600, 'FKST'),
        ttinfo(-14400,      0,  'FKT'),
        ttinfo(-10800,   3600, 'FKST'),
        ttinfo(-14400,      0,  'FKT'),
        ttinfo(-10800,   3600, 'FKST'),
        ttinfo(-14400,      0,  'FKT'),
        ttinfo(-10800,   3600, 'FKST'),
        ttinfo(-14400,      0,  'FKT'),
        ttinfo(-10800,   3600, 'FKST'),
        ttinfo(-14400,      0,  'FKT'),
        ttinfo(-10800,   3600, 'FKST'),
        ttinfo(-14400,      0,  'FKT'),
        ttinfo(-10800,   3600, 'FKST'),
        ttinfo(-14400,      0,  'FKT'),
        ttinfo(-10800,   3600, 'FKST'),
        ttinfo(-14400,      0,  'FKT'),
        ttinfo(-10800,   3600, 'FKST'),
        ttinfo(-14400,      0,  'FKT'),
        ttinfo(-10800,   3600, 'FKST'),
        ttinfo(-14400,      0,  'FKT'),
        ttinfo(-10800,   3600, 'FKST'),
        ttinfo(-14400,      0,  'FKT'),
        ttinfo(-10800,   3600, 'FKST'),
        ttinfo(-14400,      0,  'FKT'),
        ttinfo(-10800,   3600, 'FKST'),
        ttinfo(-14400,      0,  'FKT'),
        ttinfo(-10800,   3600, 'FKST'),
        ttinfo(-14400,      0,  'FKT'),
        ttinfo(-10800,   3600, 'FKST'),
        ttinfo(-14400,      0,  'FKT'),
        ttinfo(-10800,   3600, 'FKST'),
        ttinfo(-14400,      0,  'FKT'),
        ttinfo(-10800,   3600, 'FKST'),
        ttinfo(-14400,      0,  'FKT'),
        ttinfo(-10800,   3600, 'FKST'),
        ttinfo(-14400,      0,  'FKT'),
        ttinfo(-10800,   3600, 'FKST'),
        ttinfo(-14400,      0,  'FKT'),
        ttinfo(-10800,   3600, 'FKST'),
        ttinfo(-14400,      0,  'FKT'),
        ttinfo(-10800,   3600, 'FKST'),
        ttinfo(-14400,      0,  'FKT'),
        ttinfo(-10800,   3600, 'FKST'),
        ]

Stanley = Stanley() # Singleton

