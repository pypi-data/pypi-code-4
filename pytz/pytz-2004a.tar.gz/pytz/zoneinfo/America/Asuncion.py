'''
tzinfo timezone information for America/Asuncion.

Generated from the Olson timezone database:
    ftp://elsie.nci.nih.gov/pub/tz*.tar.gz
'''

from pytz.tzinfo import DstTzInfo
from pytz.tzinfo import memorized_datetime as datetime
from pytz.tzinfo import memorized_ttinfo as ttinfo

class Asuncion(DstTzInfo):
    '''America/Asuncion timezone definition. See datetime.tzinfo for details'''

    _zone = 'America/Asuncion'

    _utc_transition_times = [
        datetime(   1,  1,  1,  0,  0,  0), # -13840     0 AMT
        datetime(1931, 10, 10,  3, 50, 40), # -14400     0 PYT
        datetime(1972, 10,  1,  4,  0,  0), # -10800     0 PYT
        datetime(1974,  4,  1,  3,  0,  0), # -14400     0 PYT
        datetime(1975, 10,  1,  4,  0,  0), # -10800  3600 PYST
        datetime(1976,  3,  1,  3,  0,  0), # -14400     0 PYT
        datetime(1976, 10,  1,  4,  0,  0), # -10800  3600 PYST
        datetime(1977,  3,  1,  3,  0,  0), # -14400     0 PYT
        datetime(1977, 10,  1,  4,  0,  0), # -10800  3600 PYST
        datetime(1978,  3,  1,  3,  0,  0), # -14400     0 PYT
        datetime(1978, 10,  1,  4,  0,  0), # -10800  3600 PYST
        datetime(1979,  4,  1,  3,  0,  0), # -14400     0 PYT
        datetime(1979, 10,  1,  4,  0,  0), # -10800  3600 PYST
        datetime(1980,  4,  1,  3,  0,  0), # -14400     0 PYT
        datetime(1980, 10,  1,  4,  0,  0), # -10800  3600 PYST
        datetime(1981,  4,  1,  3,  0,  0), # -14400     0 PYT
        datetime(1981, 10,  1,  4,  0,  0), # -10800  3600 PYST
        datetime(1982,  4,  1,  3,  0,  0), # -14400     0 PYT
        datetime(1982, 10,  1,  4,  0,  0), # -10800  3600 PYST
        datetime(1983,  4,  1,  3,  0,  0), # -14400     0 PYT
        datetime(1983, 10,  1,  4,  0,  0), # -10800  3600 PYST
        datetime(1984,  4,  1,  3,  0,  0), # -14400     0 PYT
        datetime(1984, 10,  1,  4,  0,  0), # -10800  3600 PYST
        datetime(1985,  4,  1,  3,  0,  0), # -14400     0 PYT
        datetime(1985, 10,  1,  4,  0,  0), # -10800  3600 PYST
        datetime(1986,  4,  1,  3,  0,  0), # -14400     0 PYT
        datetime(1986, 10,  1,  4,  0,  0), # -10800  3600 PYST
        datetime(1987,  4,  1,  3,  0,  0), # -14400     0 PYT
        datetime(1987, 10,  1,  4,  0,  0), # -10800  3600 PYST
        datetime(1988,  4,  1,  3,  0,  0), # -14400     0 PYT
        datetime(1988, 10,  1,  4,  0,  0), # -10800  3600 PYST
        datetime(1989,  4,  1,  3,  0,  0), # -14400     0 PYT
        datetime(1989, 10, 22,  4,  0,  0), # -10800  3600 PYST
        datetime(1990,  4,  1,  3,  0,  0), # -14400     0 PYT
        datetime(1990, 10,  1,  4,  0,  0), # -10800  3600 PYST
        datetime(1991,  4,  1,  3,  0,  0), # -14400     0 PYT
        datetime(1991, 10,  6,  4,  0,  0), # -10800  3600 PYST
        datetime(1992,  3,  1,  3,  0,  0), # -14400     0 PYT
        datetime(1992, 10,  5,  4,  0,  0), # -10800  3600 PYST
        datetime(1993,  3, 31,  3,  0,  0), # -14400     0 PYT
        datetime(1993, 10,  1,  4,  0,  0), # -10800  3600 PYST
        datetime(1994,  2, 27,  3,  0,  0), # -14400     0 PYT
        datetime(1994, 10,  1,  4,  0,  0), # -10800  3600 PYST
        datetime(1995,  2, 26,  3,  0,  0), # -14400     0 PYT
        datetime(1995, 10,  1,  4,  0,  0), # -10800  3600 PYST
        datetime(1996,  3,  1,  3,  0,  0), # -14400     0 PYT
        datetime(1996, 10,  6,  4,  0,  0), # -10800  3600 PYST
        datetime(1997,  2, 23,  3,  0,  0), # -14400     0 PYT
        datetime(1997, 10,  5,  4,  0,  0), # -10800  3600 PYST
        datetime(1998,  3,  1,  3,  0,  0), # -14400     0 PYT
        datetime(1998, 10,  4,  4,  0,  0), # -10800  3600 PYST
        datetime(1999,  3,  7,  3,  0,  0), # -14400     0 PYT
        datetime(1999, 10,  3,  4,  0,  0), # -10800  3600 PYST
        datetime(2000,  3,  5,  3,  0,  0), # -14400     0 PYT
        datetime(2000, 10,  1,  4,  0,  0), # -10800  3600 PYST
        datetime(2001,  3,  4,  3,  0,  0), # -14400     0 PYT
        datetime(2001, 10,  7,  4,  0,  0), # -10800  3600 PYST
        datetime(2002,  4,  7,  3,  0,  0), # -14400     0 PYT
        datetime(2002,  9,  1,  4,  0,  0), # -10800  3600 PYST
        datetime(2003,  4,  6,  3,  0,  0), # -14400     0 PYT
        datetime(2003,  9,  7,  4,  0,  0), # -10800  3600 PYST
        datetime(2004,  4,  4,  3,  0,  0), # -14400     0 PYT
        datetime(2004,  9,  5,  4,  0,  0), # -10800  3600 PYST
        datetime(2005,  4,  3,  3,  0,  0), # -14400     0 PYT
        datetime(2005,  9,  4,  4,  0,  0), # -10800  3600 PYST
        datetime(2006,  4,  2,  3,  0,  0), # -14400     0 PYT
        datetime(2006,  9,  3,  4,  0,  0), # -10800  3600 PYST
        datetime(2007,  4,  1,  3,  0,  0), # -14400     0 PYT
        datetime(2007,  9,  2,  4,  0,  0), # -10800  3600 PYST
        datetime(2008,  4,  6,  3,  0,  0), # -14400     0 PYT
        datetime(2008,  9,  7,  4,  0,  0), # -10800  3600 PYST
        datetime(2009,  4,  5,  3,  0,  0), # -14400     0 PYT
        datetime(2009,  9,  6,  4,  0,  0), # -10800  3600 PYST
        datetime(2010,  4,  4,  3,  0,  0), # -14400     0 PYT
        datetime(2010,  9,  5,  4,  0,  0), # -10800  3600 PYST
        datetime(2011,  4,  3,  3,  0,  0), # -14400     0 PYT
        datetime(2011,  9,  4,  4,  0,  0), # -10800  3600 PYST
        datetime(2012,  4,  1,  3,  0,  0), # -14400     0 PYT
        datetime(2012,  9,  2,  4,  0,  0), # -10800  3600 PYST
        datetime(2013,  4,  7,  3,  0,  0), # -14400     0 PYT
        datetime(2013,  9,  1,  4,  0,  0), # -10800  3600 PYST
        datetime(2014,  4,  6,  3,  0,  0), # -14400     0 PYT
        datetime(2014,  9,  7,  4,  0,  0), # -10800  3600 PYST
        datetime(2015,  4,  5,  3,  0,  0), # -14400     0 PYT
        datetime(2015,  9,  6,  4,  0,  0), # -10800  3600 PYST
        datetime(2016,  4,  3,  3,  0,  0), # -14400     0 PYT
        datetime(2016,  9,  4,  4,  0,  0), # -10800  3600 PYST
        datetime(2017,  4,  2,  3,  0,  0), # -14400     0 PYT
        datetime(2017,  9,  3,  4,  0,  0), # -10800  3600 PYST
        datetime(2018,  4,  1,  3,  0,  0), # -14400     0 PYT
        datetime(2018,  9,  2,  4,  0,  0), # -10800  3600 PYST
        datetime(2019,  4,  7,  3,  0,  0), # -14400     0 PYT
        datetime(2019,  9,  1,  4,  0,  0), # -10800  3600 PYST
        datetime(2020,  4,  5,  3,  0,  0), # -14400     0 PYT
        datetime(2020,  9,  6,  4,  0,  0), # -10800  3600 PYST
        datetime(2021,  4,  4,  3,  0,  0), # -14400     0 PYT
        datetime(2021,  9,  5,  4,  0,  0), # -10800  3600 PYST
        datetime(2022,  4,  3,  3,  0,  0), # -14400     0 PYT
        datetime(2022,  9,  4,  4,  0,  0), # -10800  3600 PYST
        datetime(2023,  4,  2,  3,  0,  0), # -14400     0 PYT
        datetime(2023,  9,  3,  4,  0,  0), # -10800  3600 PYST
        datetime(2024,  4,  7,  3,  0,  0), # -14400     0 PYT
        datetime(2024,  9,  1,  4,  0,  0), # -10800  3600 PYST
        datetime(2025,  4,  6,  3,  0,  0), # -14400     0 PYT
        datetime(2025,  9,  7,  4,  0,  0), # -10800  3600 PYST
        datetime(2026,  4,  5,  3,  0,  0), # -14400     0 PYT
        datetime(2026,  9,  6,  4,  0,  0), # -10800  3600 PYST
        datetime(2027,  4,  4,  3,  0,  0), # -14400     0 PYT
        datetime(2027,  9,  5,  4,  0,  0), # -10800  3600 PYST
        datetime(2028,  4,  2,  3,  0,  0), # -14400     0 PYT
        datetime(2028,  9,  3,  4,  0,  0), # -10800  3600 PYST
        datetime(2029,  4,  1,  3,  0,  0), # -14400     0 PYT
        datetime(2029,  9,  2,  4,  0,  0), # -10800  3600 PYST
        datetime(2030,  4,  7,  3,  0,  0), # -14400     0 PYT
        datetime(2030,  9,  1,  4,  0,  0), # -10800  3600 PYST
        datetime(2031,  4,  6,  3,  0,  0), # -14400     0 PYT
        datetime(2031,  9,  7,  4,  0,  0), # -10800  3600 PYST
        datetime(2032,  4,  4,  3,  0,  0), # -14400     0 PYT
        datetime(2032,  9,  5,  4,  0,  0), # -10800  3600 PYST
        datetime(2033,  4,  3,  3,  0,  0), # -14400     0 PYT
        datetime(2033,  9,  4,  4,  0,  0), # -10800  3600 PYST
        datetime(2034,  4,  2,  3,  0,  0), # -14400     0 PYT
        datetime(2034,  9,  3,  4,  0,  0), # -10800  3600 PYST
        datetime(2035,  4,  1,  3,  0,  0), # -14400     0 PYT
        datetime(2035,  9,  2,  4,  0,  0), # -10800  3600 PYST
        datetime(2036,  4,  6,  3,  0,  0), # -14400     0 PYT
        datetime(2036,  9,  7,  4,  0,  0), # -10800  3600 PYST
        datetime(2037,  4,  5,  3,  0,  0), # -14400     0 PYT
        datetime(2037,  9,  6,  4,  0,  0), # -10800  3600 PYST
        ]

    _transition_info = [
        ttinfo(-13840,      0,  'AMT'),
        ttinfo(-14400,      0,  'PYT'),
        ttinfo(-10800,      0,  'PYT'),
        ttinfo(-14400,      0,  'PYT'),
        ttinfo(-10800,   3600, 'PYST'),
        ttinfo(-14400,      0,  'PYT'),
        ttinfo(-10800,   3600, 'PYST'),
        ttinfo(-14400,      0,  'PYT'),
        ttinfo(-10800,   3600, 'PYST'),
        ttinfo(-14400,      0,  'PYT'),
        ttinfo(-10800,   3600, 'PYST'),
        ttinfo(-14400,      0,  'PYT'),
        ttinfo(-10800,   3600, 'PYST'),
        ttinfo(-14400,      0,  'PYT'),
        ttinfo(-10800,   3600, 'PYST'),
        ttinfo(-14400,      0,  'PYT'),
        ttinfo(-10800,   3600, 'PYST'),
        ttinfo(-14400,      0,  'PYT'),
        ttinfo(-10800,   3600, 'PYST'),
        ttinfo(-14400,      0,  'PYT'),
        ttinfo(-10800,   3600, 'PYST'),
        ttinfo(-14400,      0,  'PYT'),
        ttinfo(-10800,   3600, 'PYST'),
        ttinfo(-14400,      0,  'PYT'),
        ttinfo(-10800,   3600, 'PYST'),
        ttinfo(-14400,      0,  'PYT'),
        ttinfo(-10800,   3600, 'PYST'),
        ttinfo(-14400,      0,  'PYT'),
        ttinfo(-10800,   3600, 'PYST'),
        ttinfo(-14400,      0,  'PYT'),
        ttinfo(-10800,   3600, 'PYST'),
        ttinfo(-14400,      0,  'PYT'),
        ttinfo(-10800,   3600, 'PYST'),
        ttinfo(-14400,      0,  'PYT'),
        ttinfo(-10800,   3600, 'PYST'),
        ttinfo(-14400,      0,  'PYT'),
        ttinfo(-10800,   3600, 'PYST'),
        ttinfo(-14400,      0,  'PYT'),
        ttinfo(-10800,   3600, 'PYST'),
        ttinfo(-14400,      0,  'PYT'),
        ttinfo(-10800,   3600, 'PYST'),
        ttinfo(-14400,      0,  'PYT'),
        ttinfo(-10800,   3600, 'PYST'),
        ttinfo(-14400,      0,  'PYT'),
        ttinfo(-10800,   3600, 'PYST'),
        ttinfo(-14400,      0,  'PYT'),
        ttinfo(-10800,   3600, 'PYST'),
        ttinfo(-14400,      0,  'PYT'),
        ttinfo(-10800,   3600, 'PYST'),
        ttinfo(-14400,      0,  'PYT'),
        ttinfo(-10800,   3600, 'PYST'),
        ttinfo(-14400,      0,  'PYT'),
        ttinfo(-10800,   3600, 'PYST'),
        ttinfo(-14400,      0,  'PYT'),
        ttinfo(-10800,   3600, 'PYST'),
        ttinfo(-14400,      0,  'PYT'),
        ttinfo(-10800,   3600, 'PYST'),
        ttinfo(-14400,      0,  'PYT'),
        ttinfo(-10800,   3600, 'PYST'),
        ttinfo(-14400,      0,  'PYT'),
        ttinfo(-10800,   3600, 'PYST'),
        ttinfo(-14400,      0,  'PYT'),
        ttinfo(-10800,   3600, 'PYST'),
        ttinfo(-14400,      0,  'PYT'),
        ttinfo(-10800,   3600, 'PYST'),
        ttinfo(-14400,      0,  'PYT'),
        ttinfo(-10800,   3600, 'PYST'),
        ttinfo(-14400,      0,  'PYT'),
        ttinfo(-10800,   3600, 'PYST'),
        ttinfo(-14400,      0,  'PYT'),
        ttinfo(-10800,   3600, 'PYST'),
        ttinfo(-14400,      0,  'PYT'),
        ttinfo(-10800,   3600, 'PYST'),
        ttinfo(-14400,      0,  'PYT'),
        ttinfo(-10800,   3600, 'PYST'),
        ttinfo(-14400,      0,  'PYT'),
        ttinfo(-10800,   3600, 'PYST'),
        ttinfo(-14400,      0,  'PYT'),
        ttinfo(-10800,   3600, 'PYST'),
        ttinfo(-14400,      0,  'PYT'),
        ttinfo(-10800,   3600, 'PYST'),
        ttinfo(-14400,      0,  'PYT'),
        ttinfo(-10800,   3600, 'PYST'),
        ttinfo(-14400,      0,  'PYT'),
        ttinfo(-10800,   3600, 'PYST'),
        ttinfo(-14400,      0,  'PYT'),
        ttinfo(-10800,   3600, 'PYST'),
        ttinfo(-14400,      0,  'PYT'),
        ttinfo(-10800,   3600, 'PYST'),
        ttinfo(-14400,      0,  'PYT'),
        ttinfo(-10800,   3600, 'PYST'),
        ttinfo(-14400,      0,  'PYT'),
        ttinfo(-10800,   3600, 'PYST'),
        ttinfo(-14400,      0,  'PYT'),
        ttinfo(-10800,   3600, 'PYST'),
        ttinfo(-14400,      0,  'PYT'),
        ttinfo(-10800,   3600, 'PYST'),
        ttinfo(-14400,      0,  'PYT'),
        ttinfo(-10800,   3600, 'PYST'),
        ttinfo(-14400,      0,  'PYT'),
        ttinfo(-10800,   3600, 'PYST'),
        ttinfo(-14400,      0,  'PYT'),
        ttinfo(-10800,   3600, 'PYST'),
        ttinfo(-14400,      0,  'PYT'),
        ttinfo(-10800,   3600, 'PYST'),
        ttinfo(-14400,      0,  'PYT'),
        ttinfo(-10800,   3600, 'PYST'),
        ttinfo(-14400,      0,  'PYT'),
        ttinfo(-10800,   3600, 'PYST'),
        ttinfo(-14400,      0,  'PYT'),
        ttinfo(-10800,   3600, 'PYST'),
        ttinfo(-14400,      0,  'PYT'),
        ttinfo(-10800,   3600, 'PYST'),
        ttinfo(-14400,      0,  'PYT'),
        ttinfo(-10800,   3600, 'PYST'),
        ttinfo(-14400,      0,  'PYT'),
        ttinfo(-10800,   3600, 'PYST'),
        ttinfo(-14400,      0,  'PYT'),
        ttinfo(-10800,   3600, 'PYST'),
        ttinfo(-14400,      0,  'PYT'),
        ttinfo(-10800,   3600, 'PYST'),
        ttinfo(-14400,      0,  'PYT'),
        ttinfo(-10800,   3600, 'PYST'),
        ttinfo(-14400,      0,  'PYT'),
        ttinfo(-10800,   3600, 'PYST'),
        ttinfo(-14400,      0,  'PYT'),
        ttinfo(-10800,   3600, 'PYST'),
        ttinfo(-14400,      0,  'PYT'),
        ttinfo(-10800,   3600, 'PYST'),
        ]

Asuncion = Asuncion() # Singleton

