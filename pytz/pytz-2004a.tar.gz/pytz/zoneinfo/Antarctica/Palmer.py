'''
tzinfo timezone information for Antarctica/Palmer.

Generated from the Olson timezone database:
    ftp://elsie.nci.nih.gov/pub/tz*.tar.gz
'''

from pytz.tzinfo import DstTzInfo
from pytz.tzinfo import memorized_datetime as datetime
from pytz.tzinfo import memorized_ttinfo as ttinfo

class Palmer(DstTzInfo):
    '''Antarctica/Palmer timezone definition. See datetime.tzinfo for details'''

    _zone = 'Antarctica/Palmer'

    _utc_transition_times = [
        datetime(   1,  1,  1,  0,  0,  0), #      0     0 zzz
        datetime(1965,  1,  1,  0,  0,  0), # -10800 -10800 ARST
        datetime(1965,  3,  1,  3,  0,  0), # -14400     0 ART
        datetime(1965, 10, 15,  4,  0,  0), # -10800  3600 ARST
        datetime(1966,  3,  1,  3,  0,  0), # -14400     0 ART
        datetime(1966, 10, 15,  4,  0,  0), # -10800  3600 ARST
        datetime(1967,  4,  1,  3,  0,  0), # -14400     0 ART
        datetime(1967, 10,  1,  4,  0,  0), # -10800  3600 ARST
        datetime(1968,  4,  7,  3,  0,  0), # -14400     0 ART
        datetime(1968, 10,  6,  4,  0,  0), # -10800  3600 ARST
        datetime(1969,  4,  6,  3,  0,  0), # -14400     0 ART
        datetime(1969, 10,  5,  4,  0,  0), # -10800     0 ART
        datetime(1974,  1, 23,  3,  0,  0), #  -7200  3600 ARST
        datetime(1974,  5,  1,  2,  0,  0), # -10800     0 ART
        datetime(1974, 10,  6,  3,  0,  0), #  -7200  3600 ARST
        datetime(1975,  4,  6,  2,  0,  0), # -10800     0 ART
        datetime(1975, 10,  5,  3,  0,  0), #  -7200  3600 ARST
        datetime(1976,  4,  4,  2,  0,  0), # -10800     0 ART
        datetime(1976, 10,  3,  3,  0,  0), #  -7200  3600 ARST
        datetime(1977,  4,  3,  2,  0,  0), # -10800     0 ART
        datetime(1982,  5,  1,  3,  0,  0), # -14400     0 CLT
        datetime(1982, 10, 10,  4,  0,  0), # -10800  3600 CLST
        datetime(1983,  3, 13,  3,  0,  0), # -14400     0 CLT
        datetime(1983, 10,  9,  4,  0,  0), # -10800  3600 CLST
        datetime(1984,  3, 11,  3,  0,  0), # -14400     0 CLT
        datetime(1984, 10, 14,  4,  0,  0), # -10800  3600 CLST
        datetime(1985,  3, 10,  3,  0,  0), # -14400     0 CLT
        datetime(1985, 10, 13,  4,  0,  0), # -10800  3600 CLST
        datetime(1986,  3,  9,  3,  0,  0), # -14400     0 CLT
        datetime(1986, 10, 12,  4,  0,  0), # -10800  3600 CLST
        datetime(1987,  3, 15,  3,  0,  0), # -14400     0 CLT
        datetime(1987, 10, 11,  4,  0,  0), # -10800  3600 CLST
        datetime(1988,  3, 13,  3,  0,  0), # -14400     0 CLT
        datetime(1988, 10,  9,  4,  0,  0), # -10800  3600 CLST
        datetime(1989,  3, 12,  3,  0,  0), # -14400     0 CLT
        datetime(1989, 10, 15,  4,  0,  0), # -10800  3600 CLST
        datetime(1990,  3, 11,  3,  0,  0), # -14400     0 CLT
        datetime(1990, 10, 14,  4,  0,  0), # -10800  3600 CLST
        datetime(1991,  3, 10,  3,  0,  0), # -14400     0 CLT
        datetime(1991, 10, 13,  4,  0,  0), # -10800  3600 CLST
        datetime(1992,  3, 15,  3,  0,  0), # -14400     0 CLT
        datetime(1992, 10, 11,  4,  0,  0), # -10800  3600 CLST
        datetime(1993,  3, 14,  3,  0,  0), # -14400     0 CLT
        datetime(1993, 10, 10,  4,  0,  0), # -10800  3600 CLST
        datetime(1994,  3, 13,  3,  0,  0), # -14400     0 CLT
        datetime(1994, 10,  9,  4,  0,  0), # -10800  3600 CLST
        datetime(1995,  3, 12,  3,  0,  0), # -14400     0 CLT
        datetime(1995, 10, 15,  4,  0,  0), # -10800  3600 CLST
        datetime(1996,  3, 10,  3,  0,  0), # -14400     0 CLT
        datetime(1996, 10, 13,  4,  0,  0), # -10800  3600 CLST
        datetime(1997,  3,  9,  3,  0,  0), # -14400     0 CLT
        datetime(1997, 10, 12,  4,  0,  0), # -10800  3600 CLST
        datetime(1998,  3, 15,  3,  0,  0), # -14400     0 CLT
        datetime(1998,  9, 27,  4,  0,  0), # -10800  3600 CLST
        datetime(1999,  4,  4,  3,  0,  0), # -14400     0 CLT
        datetime(1999, 10, 10,  4,  0,  0), # -10800  3600 CLST
        datetime(2000,  3, 12,  3,  0,  0), # -14400     0 CLT
        datetime(2000, 10, 15,  4,  0,  0), # -10800  3600 CLST
        datetime(2001,  3, 11,  3,  0,  0), # -14400     0 CLT
        datetime(2001, 10, 14,  4,  0,  0), # -10800  3600 CLST
        datetime(2002,  3, 10,  3,  0,  0), # -14400     0 CLT
        datetime(2002, 10, 13,  4,  0,  0), # -10800  3600 CLST
        datetime(2003,  3,  9,  3,  0,  0), # -14400     0 CLT
        datetime(2003, 10, 12,  4,  0,  0), # -10800  3600 CLST
        datetime(2004,  3, 14,  3,  0,  0), # -14400     0 CLT
        datetime(2004, 10, 10,  4,  0,  0), # -10800  3600 CLST
        datetime(2005,  3, 13,  3,  0,  0), # -14400     0 CLT
        datetime(2005, 10,  9,  4,  0,  0), # -10800  3600 CLST
        datetime(2006,  3, 12,  3,  0,  0), # -14400     0 CLT
        datetime(2006, 10, 15,  4,  0,  0), # -10800  3600 CLST
        datetime(2007,  3, 11,  3,  0,  0), # -14400     0 CLT
        datetime(2007, 10, 14,  4,  0,  0), # -10800  3600 CLST
        datetime(2008,  3,  9,  3,  0,  0), # -14400     0 CLT
        datetime(2008, 10, 12,  4,  0,  0), # -10800  3600 CLST
        datetime(2009,  3, 15,  3,  0,  0), # -14400     0 CLT
        datetime(2009, 10, 11,  4,  0,  0), # -10800  3600 CLST
        datetime(2010,  3, 14,  3,  0,  0), # -14400     0 CLT
        datetime(2010, 10, 10,  4,  0,  0), # -10800  3600 CLST
        datetime(2011,  3, 13,  3,  0,  0), # -14400     0 CLT
        datetime(2011, 10,  9,  4,  0,  0), # -10800  3600 CLST
        datetime(2012,  3, 11,  3,  0,  0), # -14400     0 CLT
        datetime(2012, 10, 14,  4,  0,  0), # -10800  3600 CLST
        datetime(2013,  3, 10,  3,  0,  0), # -14400     0 CLT
        datetime(2013, 10, 13,  4,  0,  0), # -10800  3600 CLST
        datetime(2014,  3,  9,  3,  0,  0), # -14400     0 CLT
        datetime(2014, 10, 12,  4,  0,  0), # -10800  3600 CLST
        datetime(2015,  3, 15,  3,  0,  0), # -14400     0 CLT
        datetime(2015, 10, 11,  4,  0,  0), # -10800  3600 CLST
        datetime(2016,  3, 13,  3,  0,  0), # -14400     0 CLT
        datetime(2016, 10,  9,  4,  0,  0), # -10800  3600 CLST
        datetime(2017,  3, 12,  3,  0,  0), # -14400     0 CLT
        datetime(2017, 10, 15,  4,  0,  0), # -10800  3600 CLST
        datetime(2018,  3, 11,  3,  0,  0), # -14400     0 CLT
        datetime(2018, 10, 14,  4,  0,  0), # -10800  3600 CLST
        datetime(2019,  3, 10,  3,  0,  0), # -14400     0 CLT
        datetime(2019, 10, 13,  4,  0,  0), # -10800  3600 CLST
        datetime(2020,  3, 15,  3,  0,  0), # -14400     0 CLT
        datetime(2020, 10, 11,  4,  0,  0), # -10800  3600 CLST
        datetime(2021,  3, 14,  3,  0,  0), # -14400     0 CLT
        datetime(2021, 10, 10,  4,  0,  0), # -10800  3600 CLST
        datetime(2022,  3, 13,  3,  0,  0), # -14400     0 CLT
        datetime(2022, 10,  9,  4,  0,  0), # -10800  3600 CLST
        datetime(2023,  3, 12,  3,  0,  0), # -14400     0 CLT
        datetime(2023, 10, 15,  4,  0,  0), # -10800  3600 CLST
        datetime(2024,  3, 10,  3,  0,  0), # -14400     0 CLT
        datetime(2024, 10, 13,  4,  0,  0), # -10800  3600 CLST
        datetime(2025,  3,  9,  3,  0,  0), # -14400     0 CLT
        datetime(2025, 10, 12,  4,  0,  0), # -10800  3600 CLST
        datetime(2026,  3, 15,  3,  0,  0), # -14400     0 CLT
        datetime(2026, 10, 11,  4,  0,  0), # -10800  3600 CLST
        datetime(2027,  3, 14,  3,  0,  0), # -14400     0 CLT
        datetime(2027, 10, 10,  4,  0,  0), # -10800  3600 CLST
        datetime(2028,  3, 12,  3,  0,  0), # -14400     0 CLT
        datetime(2028, 10, 15,  4,  0,  0), # -10800  3600 CLST
        datetime(2029,  3, 11,  3,  0,  0), # -14400     0 CLT
        datetime(2029, 10, 14,  4,  0,  0), # -10800  3600 CLST
        datetime(2030,  3, 10,  3,  0,  0), # -14400     0 CLT
        datetime(2030, 10, 13,  4,  0,  0), # -10800  3600 CLST
        datetime(2031,  3,  9,  3,  0,  0), # -14400     0 CLT
        datetime(2031, 10, 12,  4,  0,  0), # -10800  3600 CLST
        datetime(2032,  3, 14,  3,  0,  0), # -14400     0 CLT
        datetime(2032, 10, 10,  4,  0,  0), # -10800  3600 CLST
        datetime(2033,  3, 13,  3,  0,  0), # -14400     0 CLT
        datetime(2033, 10,  9,  4,  0,  0), # -10800  3600 CLST
        datetime(2034,  3, 12,  3,  0,  0), # -14400     0 CLT
        datetime(2034, 10, 15,  4,  0,  0), # -10800  3600 CLST
        datetime(2035,  3, 11,  3,  0,  0), # -14400     0 CLT
        datetime(2035, 10, 14,  4,  0,  0), # -10800  3600 CLST
        datetime(2036,  3,  9,  3,  0,  0), # -14400     0 CLT
        datetime(2036, 10, 12,  4,  0,  0), # -10800  3600 CLST
        datetime(2037,  3, 15,  3,  0,  0), # -14400     0 CLT
        datetime(2037, 10, 11,  4,  0,  0), # -10800  3600 CLST
        ]

    _transition_info = [
        ttinfo(     0,      0,  'zzz'),
        ttinfo(-10800, -10800, 'ARST'),
        ttinfo(-14400,      0,  'ART'),
        ttinfo(-10800,   3600, 'ARST'),
        ttinfo(-14400,      0,  'ART'),
        ttinfo(-10800,   3600, 'ARST'),
        ttinfo(-14400,      0,  'ART'),
        ttinfo(-10800,   3600, 'ARST'),
        ttinfo(-14400,      0,  'ART'),
        ttinfo(-10800,   3600, 'ARST'),
        ttinfo(-14400,      0,  'ART'),
        ttinfo(-10800,      0,  'ART'),
        ttinfo( -7200,   3600, 'ARST'),
        ttinfo(-10800,      0,  'ART'),
        ttinfo( -7200,   3600, 'ARST'),
        ttinfo(-10800,      0,  'ART'),
        ttinfo( -7200,   3600, 'ARST'),
        ttinfo(-10800,      0,  'ART'),
        ttinfo( -7200,   3600, 'ARST'),
        ttinfo(-10800,      0,  'ART'),
        ttinfo(-14400,      0,  'CLT'),
        ttinfo(-10800,   3600, 'CLST'),
        ttinfo(-14400,      0,  'CLT'),
        ttinfo(-10800,   3600, 'CLST'),
        ttinfo(-14400,      0,  'CLT'),
        ttinfo(-10800,   3600, 'CLST'),
        ttinfo(-14400,      0,  'CLT'),
        ttinfo(-10800,   3600, 'CLST'),
        ttinfo(-14400,      0,  'CLT'),
        ttinfo(-10800,   3600, 'CLST'),
        ttinfo(-14400,      0,  'CLT'),
        ttinfo(-10800,   3600, 'CLST'),
        ttinfo(-14400,      0,  'CLT'),
        ttinfo(-10800,   3600, 'CLST'),
        ttinfo(-14400,      0,  'CLT'),
        ttinfo(-10800,   3600, 'CLST'),
        ttinfo(-14400,      0,  'CLT'),
        ttinfo(-10800,   3600, 'CLST'),
        ttinfo(-14400,      0,  'CLT'),
        ttinfo(-10800,   3600, 'CLST'),
        ttinfo(-14400,      0,  'CLT'),
        ttinfo(-10800,   3600, 'CLST'),
        ttinfo(-14400,      0,  'CLT'),
        ttinfo(-10800,   3600, 'CLST'),
        ttinfo(-14400,      0,  'CLT'),
        ttinfo(-10800,   3600, 'CLST'),
        ttinfo(-14400,      0,  'CLT'),
        ttinfo(-10800,   3600, 'CLST'),
        ttinfo(-14400,      0,  'CLT'),
        ttinfo(-10800,   3600, 'CLST'),
        ttinfo(-14400,      0,  'CLT'),
        ttinfo(-10800,   3600, 'CLST'),
        ttinfo(-14400,      0,  'CLT'),
        ttinfo(-10800,   3600, 'CLST'),
        ttinfo(-14400,      0,  'CLT'),
        ttinfo(-10800,   3600, 'CLST'),
        ttinfo(-14400,      0,  'CLT'),
        ttinfo(-10800,   3600, 'CLST'),
        ttinfo(-14400,      0,  'CLT'),
        ttinfo(-10800,   3600, 'CLST'),
        ttinfo(-14400,      0,  'CLT'),
        ttinfo(-10800,   3600, 'CLST'),
        ttinfo(-14400,      0,  'CLT'),
        ttinfo(-10800,   3600, 'CLST'),
        ttinfo(-14400,      0,  'CLT'),
        ttinfo(-10800,   3600, 'CLST'),
        ttinfo(-14400,      0,  'CLT'),
        ttinfo(-10800,   3600, 'CLST'),
        ttinfo(-14400,      0,  'CLT'),
        ttinfo(-10800,   3600, 'CLST'),
        ttinfo(-14400,      0,  'CLT'),
        ttinfo(-10800,   3600, 'CLST'),
        ttinfo(-14400,      0,  'CLT'),
        ttinfo(-10800,   3600, 'CLST'),
        ttinfo(-14400,      0,  'CLT'),
        ttinfo(-10800,   3600, 'CLST'),
        ttinfo(-14400,      0,  'CLT'),
        ttinfo(-10800,   3600, 'CLST'),
        ttinfo(-14400,      0,  'CLT'),
        ttinfo(-10800,   3600, 'CLST'),
        ttinfo(-14400,      0,  'CLT'),
        ttinfo(-10800,   3600, 'CLST'),
        ttinfo(-14400,      0,  'CLT'),
        ttinfo(-10800,   3600, 'CLST'),
        ttinfo(-14400,      0,  'CLT'),
        ttinfo(-10800,   3600, 'CLST'),
        ttinfo(-14400,      0,  'CLT'),
        ttinfo(-10800,   3600, 'CLST'),
        ttinfo(-14400,      0,  'CLT'),
        ttinfo(-10800,   3600, 'CLST'),
        ttinfo(-14400,      0,  'CLT'),
        ttinfo(-10800,   3600, 'CLST'),
        ttinfo(-14400,      0,  'CLT'),
        ttinfo(-10800,   3600, 'CLST'),
        ttinfo(-14400,      0,  'CLT'),
        ttinfo(-10800,   3600, 'CLST'),
        ttinfo(-14400,      0,  'CLT'),
        ttinfo(-10800,   3600, 'CLST'),
        ttinfo(-14400,      0,  'CLT'),
        ttinfo(-10800,   3600, 'CLST'),
        ttinfo(-14400,      0,  'CLT'),
        ttinfo(-10800,   3600, 'CLST'),
        ttinfo(-14400,      0,  'CLT'),
        ttinfo(-10800,   3600, 'CLST'),
        ttinfo(-14400,      0,  'CLT'),
        ttinfo(-10800,   3600, 'CLST'),
        ttinfo(-14400,      0,  'CLT'),
        ttinfo(-10800,   3600, 'CLST'),
        ttinfo(-14400,      0,  'CLT'),
        ttinfo(-10800,   3600, 'CLST'),
        ttinfo(-14400,      0,  'CLT'),
        ttinfo(-10800,   3600, 'CLST'),
        ttinfo(-14400,      0,  'CLT'),
        ttinfo(-10800,   3600, 'CLST'),
        ttinfo(-14400,      0,  'CLT'),
        ttinfo(-10800,   3600, 'CLST'),
        ttinfo(-14400,      0,  'CLT'),
        ttinfo(-10800,   3600, 'CLST'),
        ttinfo(-14400,      0,  'CLT'),
        ttinfo(-10800,   3600, 'CLST'),
        ttinfo(-14400,      0,  'CLT'),
        ttinfo(-10800,   3600, 'CLST'),
        ttinfo(-14400,      0,  'CLT'),
        ttinfo(-10800,   3600, 'CLST'),
        ttinfo(-14400,      0,  'CLT'),
        ttinfo(-10800,   3600, 'CLST'),
        ttinfo(-14400,      0,  'CLT'),
        ttinfo(-10800,   3600, 'CLST'),
        ttinfo(-14400,      0,  'CLT'),
        ttinfo(-10800,   3600, 'CLST'),
        ttinfo(-14400,      0,  'CLT'),
        ttinfo(-10800,   3600, 'CLST'),
        ]

Palmer = Palmer() # Singleton

