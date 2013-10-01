'''
tzinfo timezone information for Australia/Lord_Howe.

Generated from the Olson timezone database:
    ftp://elsie.nci.nih.gov/pub/tz*.tar.gz
'''

from pytz.tzinfo import DstTzInfo
from pytz.tzinfo import memorized_datetime as datetime
from pytz.tzinfo import memorized_ttinfo as ttinfo

class Lord_Howe(DstTzInfo):
    '''Australia/Lord_Howe timezone definition. See datetime.tzinfo for details'''

    _zone = 'Australia/Lord_Howe'

    _utc_transition_times = [
        datetime(   1,  1,  1,  0,  0,  0), #  36000     0 EST
        datetime(1981,  2, 28, 14,  0,  0), #  37800     0 LHST
        datetime(1981, 10, 24, 15, 30,  0), #  41400  3600 LHST
        datetime(1982,  3,  6, 14, 30,  0), #  37800     0 LHST
        datetime(1982, 10, 30, 15, 30,  0), #  41400  3600 LHST
        datetime(1983,  3,  5, 14, 30,  0), #  37800     0 LHST
        datetime(1983, 10, 29, 15, 30,  0), #  41400  3600 LHST
        datetime(1984,  3,  3, 14, 30,  0), #  37800     0 LHST
        datetime(1984, 10, 27, 15, 30,  0), #  41400  3600 LHST
        datetime(1985,  3,  2, 14, 30,  0), #  37800     0 LHST
        datetime(1985, 10, 26, 15, 30,  0), #  39600  1800 LHST
        datetime(1986,  3, 15, 15,  0,  0), #  37800     0 LHST
        datetime(1986, 10, 18, 15, 30,  0), #  39600  1800 LHST
        datetime(1987,  3, 14, 15,  0,  0), #  37800     0 LHST
        datetime(1987, 10, 24, 15, 30,  0), #  39600  1800 LHST
        datetime(1988,  3, 19, 15,  0,  0), #  37800     0 LHST
        datetime(1988, 10, 29, 15, 30,  0), #  39600  1800 LHST
        datetime(1989,  3, 18, 15,  0,  0), #  37800     0 LHST
        datetime(1989, 10, 28, 15, 30,  0), #  39600  1800 LHST
        datetime(1990,  3,  3, 15,  0,  0), #  37800     0 LHST
        datetime(1990, 10, 27, 15, 30,  0), #  39600  1800 LHST
        datetime(1991,  3,  2, 15,  0,  0), #  37800     0 LHST
        datetime(1991, 10, 26, 15, 30,  0), #  39600  1800 LHST
        datetime(1992,  2, 29, 15,  0,  0), #  37800     0 LHST
        datetime(1992, 10, 24, 15, 30,  0), #  39600  1800 LHST
        datetime(1993,  3,  6, 15,  0,  0), #  37800     0 LHST
        datetime(1993, 10, 30, 15, 30,  0), #  39600  1800 LHST
        datetime(1994,  3,  5, 15,  0,  0), #  37800     0 LHST
        datetime(1994, 10, 29, 15, 30,  0), #  39600  1800 LHST
        datetime(1995,  3,  4, 15,  0,  0), #  37800     0 LHST
        datetime(1995, 10, 28, 15, 30,  0), #  39600  1800 LHST
        datetime(1996,  3, 30, 15,  0,  0), #  37800     0 LHST
        datetime(1996, 10, 26, 15, 30,  0), #  39600  1800 LHST
        datetime(1997,  3, 29, 15,  0,  0), #  37800     0 LHST
        datetime(1997, 10, 25, 15, 30,  0), #  39600  1800 LHST
        datetime(1998,  3, 28, 15,  0,  0), #  37800     0 LHST
        datetime(1998, 10, 24, 15, 30,  0), #  39600  1800 LHST
        datetime(1999,  3, 27, 15,  0,  0), #  37800     0 LHST
        datetime(1999, 10, 30, 15, 30,  0), #  39600  1800 LHST
        datetime(2000,  3, 25, 15,  0,  0), #  37800     0 LHST
        datetime(2000,  8, 26, 15, 30,  0), #  39600  1800 LHST
        datetime(2001,  3, 24, 15,  0,  0), #  37800     0 LHST
        datetime(2001, 10, 27, 15, 30,  0), #  39600  1800 LHST
        datetime(2002,  3, 30, 15,  0,  0), #  37800     0 LHST
        datetime(2002, 10, 26, 15, 30,  0), #  39600  1800 LHST
        datetime(2003,  3, 29, 15,  0,  0), #  37800     0 LHST
        datetime(2003, 10, 25, 15, 30,  0), #  39600  1800 LHST
        datetime(2004,  3, 27, 15,  0,  0), #  37800     0 LHST
        datetime(2004, 10, 30, 15, 30,  0), #  39600  1800 LHST
        datetime(2005,  3, 26, 15,  0,  0), #  37800     0 LHST
        datetime(2005, 10, 29, 15, 30,  0), #  39600  1800 LHST
        datetime(2006,  3, 25, 15,  0,  0), #  37800     0 LHST
        datetime(2006, 10, 28, 15, 30,  0), #  39600  1800 LHST
        datetime(2007,  3, 24, 15,  0,  0), #  37800     0 LHST
        datetime(2007, 10, 27, 15, 30,  0), #  39600  1800 LHST
        datetime(2008,  3, 29, 15,  0,  0), #  37800     0 LHST
        datetime(2008, 10, 25, 15, 30,  0), #  39600  1800 LHST
        datetime(2009,  3, 28, 15,  0,  0), #  37800     0 LHST
        datetime(2009, 10, 24, 15, 30,  0), #  39600  1800 LHST
        datetime(2010,  3, 27, 15,  0,  0), #  37800     0 LHST
        datetime(2010, 10, 30, 15, 30,  0), #  39600  1800 LHST
        datetime(2011,  3, 26, 15,  0,  0), #  37800     0 LHST
        datetime(2011, 10, 29, 15, 30,  0), #  39600  1800 LHST
        datetime(2012,  3, 24, 15,  0,  0), #  37800     0 LHST
        datetime(2012, 10, 27, 15, 30,  0), #  39600  1800 LHST
        datetime(2013,  3, 30, 15,  0,  0), #  37800     0 LHST
        datetime(2013, 10, 26, 15, 30,  0), #  39600  1800 LHST
        datetime(2014,  3, 29, 15,  0,  0), #  37800     0 LHST
        datetime(2014, 10, 25, 15, 30,  0), #  39600  1800 LHST
        datetime(2015,  3, 28, 15,  0,  0), #  37800     0 LHST
        datetime(2015, 10, 24, 15, 30,  0), #  39600  1800 LHST
        datetime(2016,  3, 26, 15,  0,  0), #  37800     0 LHST
        datetime(2016, 10, 29, 15, 30,  0), #  39600  1800 LHST
        datetime(2017,  3, 25, 15,  0,  0), #  37800     0 LHST
        datetime(2017, 10, 28, 15, 30,  0), #  39600  1800 LHST
        datetime(2018,  3, 24, 15,  0,  0), #  37800     0 LHST
        datetime(2018, 10, 27, 15, 30,  0), #  39600  1800 LHST
        datetime(2019,  3, 30, 15,  0,  0), #  37800     0 LHST
        datetime(2019, 10, 26, 15, 30,  0), #  39600  1800 LHST
        datetime(2020,  3, 28, 15,  0,  0), #  37800     0 LHST
        datetime(2020, 10, 24, 15, 30,  0), #  39600  1800 LHST
        datetime(2021,  3, 27, 15,  0,  0), #  37800     0 LHST
        datetime(2021, 10, 30, 15, 30,  0), #  39600  1800 LHST
        datetime(2022,  3, 26, 15,  0,  0), #  37800     0 LHST
        datetime(2022, 10, 29, 15, 30,  0), #  39600  1800 LHST
        datetime(2023,  3, 25, 15,  0,  0), #  37800     0 LHST
        datetime(2023, 10, 28, 15, 30,  0), #  39600  1800 LHST
        datetime(2024,  3, 30, 15,  0,  0), #  37800     0 LHST
        datetime(2024, 10, 26, 15, 30,  0), #  39600  1800 LHST
        datetime(2025,  3, 29, 15,  0,  0), #  37800     0 LHST
        datetime(2025, 10, 25, 15, 30,  0), #  39600  1800 LHST
        datetime(2026,  3, 28, 15,  0,  0), #  37800     0 LHST
        datetime(2026, 10, 24, 15, 30,  0), #  39600  1800 LHST
        datetime(2027,  3, 27, 15,  0,  0), #  37800     0 LHST
        datetime(2027, 10, 30, 15, 30,  0), #  39600  1800 LHST
        datetime(2028,  3, 25, 15,  0,  0), #  37800     0 LHST
        datetime(2028, 10, 28, 15, 30,  0), #  39600  1800 LHST
        datetime(2029,  3, 24, 15,  0,  0), #  37800     0 LHST
        datetime(2029, 10, 27, 15, 30,  0), #  39600  1800 LHST
        datetime(2030,  3, 30, 15,  0,  0), #  37800     0 LHST
        datetime(2030, 10, 26, 15, 30,  0), #  39600  1800 LHST
        datetime(2031,  3, 29, 15,  0,  0), #  37800     0 LHST
        datetime(2031, 10, 25, 15, 30,  0), #  39600  1800 LHST
        datetime(2032,  3, 27, 15,  0,  0), #  37800     0 LHST
        datetime(2032, 10, 30, 15, 30,  0), #  39600  1800 LHST
        datetime(2033,  3, 26, 15,  0,  0), #  37800     0 LHST
        datetime(2033, 10, 29, 15, 30,  0), #  39600  1800 LHST
        datetime(2034,  3, 25, 15,  0,  0), #  37800     0 LHST
        datetime(2034, 10, 28, 15, 30,  0), #  39600  1800 LHST
        datetime(2035,  3, 24, 15,  0,  0), #  37800     0 LHST
        datetime(2035, 10, 27, 15, 30,  0), #  39600  1800 LHST
        datetime(2036,  3, 29, 15,  0,  0), #  37800     0 LHST
        datetime(2036, 10, 25, 15, 30,  0), #  39600  1800 LHST
        datetime(2037,  3, 28, 15,  0,  0), #  37800     0 LHST
        datetime(2037, 10, 24, 15, 30,  0), #  39600  1800 LHST
        ]

    _transition_info = [
        ttinfo( 36000,      0,  'EST'),
        ttinfo( 37800,      0, 'LHST'),
        ttinfo( 41400,   3600, 'LHST'),
        ttinfo( 37800,      0, 'LHST'),
        ttinfo( 41400,   3600, 'LHST'),
        ttinfo( 37800,      0, 'LHST'),
        ttinfo( 41400,   3600, 'LHST'),
        ttinfo( 37800,      0, 'LHST'),
        ttinfo( 41400,   3600, 'LHST'),
        ttinfo( 37800,      0, 'LHST'),
        ttinfo( 39600,   1800, 'LHST'),
        ttinfo( 37800,      0, 'LHST'),
        ttinfo( 39600,   1800, 'LHST'),
        ttinfo( 37800,      0, 'LHST'),
        ttinfo( 39600,   1800, 'LHST'),
        ttinfo( 37800,      0, 'LHST'),
        ttinfo( 39600,   1800, 'LHST'),
        ttinfo( 37800,      0, 'LHST'),
        ttinfo( 39600,   1800, 'LHST'),
        ttinfo( 37800,      0, 'LHST'),
        ttinfo( 39600,   1800, 'LHST'),
        ttinfo( 37800,      0, 'LHST'),
        ttinfo( 39600,   1800, 'LHST'),
        ttinfo( 37800,      0, 'LHST'),
        ttinfo( 39600,   1800, 'LHST'),
        ttinfo( 37800,      0, 'LHST'),
        ttinfo( 39600,   1800, 'LHST'),
        ttinfo( 37800,      0, 'LHST'),
        ttinfo( 39600,   1800, 'LHST'),
        ttinfo( 37800,      0, 'LHST'),
        ttinfo( 39600,   1800, 'LHST'),
        ttinfo( 37800,      0, 'LHST'),
        ttinfo( 39600,   1800, 'LHST'),
        ttinfo( 37800,      0, 'LHST'),
        ttinfo( 39600,   1800, 'LHST'),
        ttinfo( 37800,      0, 'LHST'),
        ttinfo( 39600,   1800, 'LHST'),
        ttinfo( 37800,      0, 'LHST'),
        ttinfo( 39600,   1800, 'LHST'),
        ttinfo( 37800,      0, 'LHST'),
        ttinfo( 39600,   1800, 'LHST'),
        ttinfo( 37800,      0, 'LHST'),
        ttinfo( 39600,   1800, 'LHST'),
        ttinfo( 37800,      0, 'LHST'),
        ttinfo( 39600,   1800, 'LHST'),
        ttinfo( 37800,      0, 'LHST'),
        ttinfo( 39600,   1800, 'LHST'),
        ttinfo( 37800,      0, 'LHST'),
        ttinfo( 39600,   1800, 'LHST'),
        ttinfo( 37800,      0, 'LHST'),
        ttinfo( 39600,   1800, 'LHST'),
        ttinfo( 37800,      0, 'LHST'),
        ttinfo( 39600,   1800, 'LHST'),
        ttinfo( 37800,      0, 'LHST'),
        ttinfo( 39600,   1800, 'LHST'),
        ttinfo( 37800,      0, 'LHST'),
        ttinfo( 39600,   1800, 'LHST'),
        ttinfo( 37800,      0, 'LHST'),
        ttinfo( 39600,   1800, 'LHST'),
        ttinfo( 37800,      0, 'LHST'),
        ttinfo( 39600,   1800, 'LHST'),
        ttinfo( 37800,      0, 'LHST'),
        ttinfo( 39600,   1800, 'LHST'),
        ttinfo( 37800,      0, 'LHST'),
        ttinfo( 39600,   1800, 'LHST'),
        ttinfo( 37800,      0, 'LHST'),
        ttinfo( 39600,   1800, 'LHST'),
        ttinfo( 37800,      0, 'LHST'),
        ttinfo( 39600,   1800, 'LHST'),
        ttinfo( 37800,      0, 'LHST'),
        ttinfo( 39600,   1800, 'LHST'),
        ttinfo( 37800,      0, 'LHST'),
        ttinfo( 39600,   1800, 'LHST'),
        ttinfo( 37800,      0, 'LHST'),
        ttinfo( 39600,   1800, 'LHST'),
        ttinfo( 37800,      0, 'LHST'),
        ttinfo( 39600,   1800, 'LHST'),
        ttinfo( 37800,      0, 'LHST'),
        ttinfo( 39600,   1800, 'LHST'),
        ttinfo( 37800,      0, 'LHST'),
        ttinfo( 39600,   1800, 'LHST'),
        ttinfo( 37800,      0, 'LHST'),
        ttinfo( 39600,   1800, 'LHST'),
        ttinfo( 37800,      0, 'LHST'),
        ttinfo( 39600,   1800, 'LHST'),
        ttinfo( 37800,      0, 'LHST'),
        ttinfo( 39600,   1800, 'LHST'),
        ttinfo( 37800,      0, 'LHST'),
        ttinfo( 39600,   1800, 'LHST'),
        ttinfo( 37800,      0, 'LHST'),
        ttinfo( 39600,   1800, 'LHST'),
        ttinfo( 37800,      0, 'LHST'),
        ttinfo( 39600,   1800, 'LHST'),
        ttinfo( 37800,      0, 'LHST'),
        ttinfo( 39600,   1800, 'LHST'),
        ttinfo( 37800,      0, 'LHST'),
        ttinfo( 39600,   1800, 'LHST'),
        ttinfo( 37800,      0, 'LHST'),
        ttinfo( 39600,   1800, 'LHST'),
        ttinfo( 37800,      0, 'LHST'),
        ttinfo( 39600,   1800, 'LHST'),
        ttinfo( 37800,      0, 'LHST'),
        ttinfo( 39600,   1800, 'LHST'),
        ttinfo( 37800,      0, 'LHST'),
        ttinfo( 39600,   1800, 'LHST'),
        ttinfo( 37800,      0, 'LHST'),
        ttinfo( 39600,   1800, 'LHST'),
        ttinfo( 37800,      0, 'LHST'),
        ttinfo( 39600,   1800, 'LHST'),
        ttinfo( 37800,      0, 'LHST'),
        ttinfo( 39600,   1800, 'LHST'),
        ttinfo( 37800,      0, 'LHST'),
        ttinfo( 39600,   1800, 'LHST'),
        ttinfo( 37800,      0, 'LHST'),
        ttinfo( 39600,   1800, 'LHST'),
        ]

Lord_Howe = Lord_Howe() # Singleton

