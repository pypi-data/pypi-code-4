'''
tzinfo timezone information for MET.

Generated from the Olson timezone database:
    ftp://elsie.nci.nih.gov/pub/tz*.tar.gz
'''

from pytz.tzinfo import DstTzInfo
from pytz.tzinfo import memorized_datetime as datetime
from pytz.tzinfo import memorized_ttinfo as ttinfo

class MET(DstTzInfo):
    '''MET timezone definition. See datetime.tzinfo for details'''

    _zone = 'MET'

    _utc_transition_times = [
        datetime(   1,  1,  1,  0,  0,  0), #   3600     0 MET
        datetime(1916,  4, 30, 22,  0,  0), #   7200  3600 MEST
        datetime(1916,  9, 30, 23,  0,  0), #   3600     0 MET
        datetime(1917,  4, 16,  1,  0,  0), #   7200  3600 MEST
        datetime(1917,  9, 17,  1,  0,  0), #   3600     0 MET
        datetime(1918,  4, 15,  1,  0,  0), #   7200  3600 MEST
        datetime(1918,  9, 16,  1,  0,  0), #   3600     0 MET
        datetime(1940,  4,  1,  1,  0,  0), #   7200  3600 MEST
        datetime(1942, 11,  2,  1,  0,  0), #   3600     0 MET
        datetime(1943,  3, 29,  1,  0,  0), #   7200  3600 MEST
        datetime(1943, 10,  4,  1,  0,  0), #   3600     0 MET
        datetime(1944,  4,  3,  1,  0,  0), #   7200  3600 MEST
        datetime(1944, 10,  2,  1,  0,  0), #   3600     0 MET
        datetime(1977,  4,  3,  1,  0,  0), #   7200  3600 MEST
        datetime(1977,  9, 25,  1,  0,  0), #   3600     0 MET
        datetime(1978,  4,  2,  1,  0,  0), #   7200  3600 MEST
        datetime(1978, 10,  1,  1,  0,  0), #   3600     0 MET
        datetime(1979,  4,  1,  1,  0,  0), #   7200  3600 MEST
        datetime(1979,  9, 30,  1,  0,  0), #   3600     0 MET
        datetime(1980,  4,  6,  1,  0,  0), #   7200  3600 MEST
        datetime(1980,  9, 28,  1,  0,  0), #   3600     0 MET
        datetime(1981,  3, 29,  1,  0,  0), #   7200  3600 MEST
        datetime(1981,  9, 27,  1,  0,  0), #   3600     0 MET
        datetime(1982,  3, 28,  1,  0,  0), #   7200  3600 MEST
        datetime(1982,  9, 26,  1,  0,  0), #   3600     0 MET
        datetime(1983,  3, 27,  1,  0,  0), #   7200  3600 MEST
        datetime(1983,  9, 25,  1,  0,  0), #   3600     0 MET
        datetime(1984,  3, 25,  1,  0,  0), #   7200  3600 MEST
        datetime(1984,  9, 30,  1,  0,  0), #   3600     0 MET
        datetime(1985,  3, 31,  1,  0,  0), #   7200  3600 MEST
        datetime(1985,  9, 29,  1,  0,  0), #   3600     0 MET
        datetime(1986,  3, 30,  1,  0,  0), #   7200  3600 MEST
        datetime(1986,  9, 28,  1,  0,  0), #   3600     0 MET
        datetime(1987,  3, 29,  1,  0,  0), #   7200  3600 MEST
        datetime(1987,  9, 27,  1,  0,  0), #   3600     0 MET
        datetime(1988,  3, 27,  1,  0,  0), #   7200  3600 MEST
        datetime(1988,  9, 25,  1,  0,  0), #   3600     0 MET
        datetime(1989,  3, 26,  1,  0,  0), #   7200  3600 MEST
        datetime(1989,  9, 24,  1,  0,  0), #   3600     0 MET
        datetime(1990,  3, 25,  1,  0,  0), #   7200  3600 MEST
        datetime(1990,  9, 30,  1,  0,  0), #   3600     0 MET
        datetime(1991,  3, 31,  1,  0,  0), #   7200  3600 MEST
        datetime(1991,  9, 29,  1,  0,  0), #   3600     0 MET
        datetime(1992,  3, 29,  1,  0,  0), #   7200  3600 MEST
        datetime(1992,  9, 27,  1,  0,  0), #   3600     0 MET
        datetime(1993,  3, 28,  1,  0,  0), #   7200  3600 MEST
        datetime(1993,  9, 26,  1,  0,  0), #   3600     0 MET
        datetime(1994,  3, 27,  1,  0,  0), #   7200  3600 MEST
        datetime(1994,  9, 25,  1,  0,  0), #   3600     0 MET
        datetime(1995,  3, 26,  1,  0,  0), #   7200  3600 MEST
        datetime(1995,  9, 24,  1,  0,  0), #   3600     0 MET
        datetime(1996,  3, 31,  1,  0,  0), #   7200  3600 MEST
        datetime(1996, 10, 27,  1,  0,  0), #   3600     0 MET
        datetime(1997,  3, 30,  1,  0,  0), #   7200  3600 MEST
        datetime(1997, 10, 26,  1,  0,  0), #   3600     0 MET
        datetime(1998,  3, 29,  1,  0,  0), #   7200  3600 MEST
        datetime(1998, 10, 25,  1,  0,  0), #   3600     0 MET
        datetime(1999,  3, 28,  1,  0,  0), #   7200  3600 MEST
        datetime(1999, 10, 31,  1,  0,  0), #   3600     0 MET
        datetime(2000,  3, 26,  1,  0,  0), #   7200  3600 MEST
        datetime(2000, 10, 29,  1,  0,  0), #   3600     0 MET
        datetime(2001,  3, 25,  1,  0,  0), #   7200  3600 MEST
        datetime(2001, 10, 28,  1,  0,  0), #   3600     0 MET
        datetime(2002,  3, 31,  1,  0,  0), #   7200  3600 MEST
        datetime(2002, 10, 27,  1,  0,  0), #   3600     0 MET
        datetime(2003,  3, 30,  1,  0,  0), #   7200  3600 MEST
        datetime(2003, 10, 26,  1,  0,  0), #   3600     0 MET
        datetime(2004,  3, 28,  1,  0,  0), #   7200  3600 MEST
        datetime(2004, 10, 31,  1,  0,  0), #   3600     0 MET
        datetime(2005,  3, 27,  1,  0,  0), #   7200  3600 MEST
        datetime(2005, 10, 30,  1,  0,  0), #   3600     0 MET
        datetime(2006,  3, 26,  1,  0,  0), #   7200  3600 MEST
        datetime(2006, 10, 29,  1,  0,  0), #   3600     0 MET
        datetime(2007,  3, 25,  1,  0,  0), #   7200  3600 MEST
        datetime(2007, 10, 28,  1,  0,  0), #   3600     0 MET
        datetime(2008,  3, 30,  1,  0,  0), #   7200  3600 MEST
        datetime(2008, 10, 26,  1,  0,  0), #   3600     0 MET
        datetime(2009,  3, 29,  1,  0,  0), #   7200  3600 MEST
        datetime(2009, 10, 25,  1,  0,  0), #   3600     0 MET
        datetime(2010,  3, 28,  1,  0,  0), #   7200  3600 MEST
        datetime(2010, 10, 31,  1,  0,  0), #   3600     0 MET
        datetime(2011,  3, 27,  1,  0,  0), #   7200  3600 MEST
        datetime(2011, 10, 30,  1,  0,  0), #   3600     0 MET
        datetime(2012,  3, 25,  1,  0,  0), #   7200  3600 MEST
        datetime(2012, 10, 28,  1,  0,  0), #   3600     0 MET
        datetime(2013,  3, 31,  1,  0,  0), #   7200  3600 MEST
        datetime(2013, 10, 27,  1,  0,  0), #   3600     0 MET
        datetime(2014,  3, 30,  1,  0,  0), #   7200  3600 MEST
        datetime(2014, 10, 26,  1,  0,  0), #   3600     0 MET
        datetime(2015,  3, 29,  1,  0,  0), #   7200  3600 MEST
        datetime(2015, 10, 25,  1,  0,  0), #   3600     0 MET
        datetime(2016,  3, 27,  1,  0,  0), #   7200  3600 MEST
        datetime(2016, 10, 30,  1,  0,  0), #   3600     0 MET
        datetime(2017,  3, 26,  1,  0,  0), #   7200  3600 MEST
        datetime(2017, 10, 29,  1,  0,  0), #   3600     0 MET
        datetime(2018,  3, 25,  1,  0,  0), #   7200  3600 MEST
        datetime(2018, 10, 28,  1,  0,  0), #   3600     0 MET
        datetime(2019,  3, 31,  1,  0,  0), #   7200  3600 MEST
        datetime(2019, 10, 27,  1,  0,  0), #   3600     0 MET
        datetime(2020,  3, 29,  1,  0,  0), #   7200  3600 MEST
        datetime(2020, 10, 25,  1,  0,  0), #   3600     0 MET
        datetime(2021,  3, 28,  1,  0,  0), #   7200  3600 MEST
        datetime(2021, 10, 31,  1,  0,  0), #   3600     0 MET
        datetime(2022,  3, 27,  1,  0,  0), #   7200  3600 MEST
        datetime(2022, 10, 30,  1,  0,  0), #   3600     0 MET
        datetime(2023,  3, 26,  1,  0,  0), #   7200  3600 MEST
        datetime(2023, 10, 29,  1,  0,  0), #   3600     0 MET
        datetime(2024,  3, 31,  1,  0,  0), #   7200  3600 MEST
        datetime(2024, 10, 27,  1,  0,  0), #   3600     0 MET
        datetime(2025,  3, 30,  1,  0,  0), #   7200  3600 MEST
        datetime(2025, 10, 26,  1,  0,  0), #   3600     0 MET
        datetime(2026,  3, 29,  1,  0,  0), #   7200  3600 MEST
        datetime(2026, 10, 25,  1,  0,  0), #   3600     0 MET
        datetime(2027,  3, 28,  1,  0,  0), #   7200  3600 MEST
        datetime(2027, 10, 31,  1,  0,  0), #   3600     0 MET
        datetime(2028,  3, 26,  1,  0,  0), #   7200  3600 MEST
        datetime(2028, 10, 29,  1,  0,  0), #   3600     0 MET
        datetime(2029,  3, 25,  1,  0,  0), #   7200  3600 MEST
        datetime(2029, 10, 28,  1,  0,  0), #   3600     0 MET
        datetime(2030,  3, 31,  1,  0,  0), #   7200  3600 MEST
        datetime(2030, 10, 27,  1,  0,  0), #   3600     0 MET
        datetime(2031,  3, 30,  1,  0,  0), #   7200  3600 MEST
        datetime(2031, 10, 26,  1,  0,  0), #   3600     0 MET
        datetime(2032,  3, 28,  1,  0,  0), #   7200  3600 MEST
        datetime(2032, 10, 31,  1,  0,  0), #   3600     0 MET
        datetime(2033,  3, 27,  1,  0,  0), #   7200  3600 MEST
        datetime(2033, 10, 30,  1,  0,  0), #   3600     0 MET
        datetime(2034,  3, 26,  1,  0,  0), #   7200  3600 MEST
        datetime(2034, 10, 29,  1,  0,  0), #   3600     0 MET
        datetime(2035,  3, 25,  1,  0,  0), #   7200  3600 MEST
        datetime(2035, 10, 28,  1,  0,  0), #   3600     0 MET
        datetime(2036,  3, 30,  1,  0,  0), #   7200  3600 MEST
        datetime(2036, 10, 26,  1,  0,  0), #   3600     0 MET
        datetime(2037,  3, 29,  1,  0,  0), #   7200  3600 MEST
        datetime(2037, 10, 25,  1,  0,  0), #   3600     0 MET
        ]

    _transition_info = [
        ttinfo(  3600,      0,  'MET'),
        ttinfo(  7200,   3600, 'MEST'),
        ttinfo(  3600,      0,  'MET'),
        ttinfo(  7200,   3600, 'MEST'),
        ttinfo(  3600,      0,  'MET'),
        ttinfo(  7200,   3600, 'MEST'),
        ttinfo(  3600,      0,  'MET'),
        ttinfo(  7200,   3600, 'MEST'),
        ttinfo(  3600,      0,  'MET'),
        ttinfo(  7200,   3600, 'MEST'),
        ttinfo(  3600,      0,  'MET'),
        ttinfo(  7200,   3600, 'MEST'),
        ttinfo(  3600,      0,  'MET'),
        ttinfo(  7200,   3600, 'MEST'),
        ttinfo(  3600,      0,  'MET'),
        ttinfo(  7200,   3600, 'MEST'),
        ttinfo(  3600,      0,  'MET'),
        ttinfo(  7200,   3600, 'MEST'),
        ttinfo(  3600,      0,  'MET'),
        ttinfo(  7200,   3600, 'MEST'),
        ttinfo(  3600,      0,  'MET'),
        ttinfo(  7200,   3600, 'MEST'),
        ttinfo(  3600,      0,  'MET'),
        ttinfo(  7200,   3600, 'MEST'),
        ttinfo(  3600,      0,  'MET'),
        ttinfo(  7200,   3600, 'MEST'),
        ttinfo(  3600,      0,  'MET'),
        ttinfo(  7200,   3600, 'MEST'),
        ttinfo(  3600,      0,  'MET'),
        ttinfo(  7200,   3600, 'MEST'),
        ttinfo(  3600,      0,  'MET'),
        ttinfo(  7200,   3600, 'MEST'),
        ttinfo(  3600,      0,  'MET'),
        ttinfo(  7200,   3600, 'MEST'),
        ttinfo(  3600,      0,  'MET'),
        ttinfo(  7200,   3600, 'MEST'),
        ttinfo(  3600,      0,  'MET'),
        ttinfo(  7200,   3600, 'MEST'),
        ttinfo(  3600,      0,  'MET'),
        ttinfo(  7200,   3600, 'MEST'),
        ttinfo(  3600,      0,  'MET'),
        ttinfo(  7200,   3600, 'MEST'),
        ttinfo(  3600,      0,  'MET'),
        ttinfo(  7200,   3600, 'MEST'),
        ttinfo(  3600,      0,  'MET'),
        ttinfo(  7200,   3600, 'MEST'),
        ttinfo(  3600,      0,  'MET'),
        ttinfo(  7200,   3600, 'MEST'),
        ttinfo(  3600,      0,  'MET'),
        ttinfo(  7200,   3600, 'MEST'),
        ttinfo(  3600,      0,  'MET'),
        ttinfo(  7200,   3600, 'MEST'),
        ttinfo(  3600,      0,  'MET'),
        ttinfo(  7200,   3600, 'MEST'),
        ttinfo(  3600,      0,  'MET'),
        ttinfo(  7200,   3600, 'MEST'),
        ttinfo(  3600,      0,  'MET'),
        ttinfo(  7200,   3600, 'MEST'),
        ttinfo(  3600,      0,  'MET'),
        ttinfo(  7200,   3600, 'MEST'),
        ttinfo(  3600,      0,  'MET'),
        ttinfo(  7200,   3600, 'MEST'),
        ttinfo(  3600,      0,  'MET'),
        ttinfo(  7200,   3600, 'MEST'),
        ttinfo(  3600,      0,  'MET'),
        ttinfo(  7200,   3600, 'MEST'),
        ttinfo(  3600,      0,  'MET'),
        ttinfo(  7200,   3600, 'MEST'),
        ttinfo(  3600,      0,  'MET'),
        ttinfo(  7200,   3600, 'MEST'),
        ttinfo(  3600,      0,  'MET'),
        ttinfo(  7200,   3600, 'MEST'),
        ttinfo(  3600,      0,  'MET'),
        ttinfo(  7200,   3600, 'MEST'),
        ttinfo(  3600,      0,  'MET'),
        ttinfo(  7200,   3600, 'MEST'),
        ttinfo(  3600,      0,  'MET'),
        ttinfo(  7200,   3600, 'MEST'),
        ttinfo(  3600,      0,  'MET'),
        ttinfo(  7200,   3600, 'MEST'),
        ttinfo(  3600,      0,  'MET'),
        ttinfo(  7200,   3600, 'MEST'),
        ttinfo(  3600,      0,  'MET'),
        ttinfo(  7200,   3600, 'MEST'),
        ttinfo(  3600,      0,  'MET'),
        ttinfo(  7200,   3600, 'MEST'),
        ttinfo(  3600,      0,  'MET'),
        ttinfo(  7200,   3600, 'MEST'),
        ttinfo(  3600,      0,  'MET'),
        ttinfo(  7200,   3600, 'MEST'),
        ttinfo(  3600,      0,  'MET'),
        ttinfo(  7200,   3600, 'MEST'),
        ttinfo(  3600,      0,  'MET'),
        ttinfo(  7200,   3600, 'MEST'),
        ttinfo(  3600,      0,  'MET'),
        ttinfo(  7200,   3600, 'MEST'),
        ttinfo(  3600,      0,  'MET'),
        ttinfo(  7200,   3600, 'MEST'),
        ttinfo(  3600,      0,  'MET'),
        ttinfo(  7200,   3600, 'MEST'),
        ttinfo(  3600,      0,  'MET'),
        ttinfo(  7200,   3600, 'MEST'),
        ttinfo(  3600,      0,  'MET'),
        ttinfo(  7200,   3600, 'MEST'),
        ttinfo(  3600,      0,  'MET'),
        ttinfo(  7200,   3600, 'MEST'),
        ttinfo(  3600,      0,  'MET'),
        ttinfo(  7200,   3600, 'MEST'),
        ttinfo(  3600,      0,  'MET'),
        ttinfo(  7200,   3600, 'MEST'),
        ttinfo(  3600,      0,  'MET'),
        ttinfo(  7200,   3600, 'MEST'),
        ttinfo(  3600,      0,  'MET'),
        ttinfo(  7200,   3600, 'MEST'),
        ttinfo(  3600,      0,  'MET'),
        ttinfo(  7200,   3600, 'MEST'),
        ttinfo(  3600,      0,  'MET'),
        ttinfo(  7200,   3600, 'MEST'),
        ttinfo(  3600,      0,  'MET'),
        ttinfo(  7200,   3600, 'MEST'),
        ttinfo(  3600,      0,  'MET'),
        ttinfo(  7200,   3600, 'MEST'),
        ttinfo(  3600,      0,  'MET'),
        ttinfo(  7200,   3600, 'MEST'),
        ttinfo(  3600,      0,  'MET'),
        ttinfo(  7200,   3600, 'MEST'),
        ttinfo(  3600,      0,  'MET'),
        ttinfo(  7200,   3600, 'MEST'),
        ttinfo(  3600,      0,  'MET'),
        ttinfo(  7200,   3600, 'MEST'),
        ttinfo(  3600,      0,  'MET'),
        ttinfo(  7200,   3600, 'MEST'),
        ttinfo(  3600,      0,  'MET'),
        ttinfo(  7200,   3600, 'MEST'),
        ttinfo(  3600,      0,  'MET'),
        ]

MET = MET() # Singleton

