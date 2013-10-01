'''
tzinfo timezone information for Europe/Kaliningrad.

Generated from the Olson timezone database:
    ftp://elsie.nci.nih.gov/pub/tz*.tar.gz
'''

from pytz.tzinfo import DstTzInfo
from pytz.tzinfo import memorized_datetime as datetime
from pytz.tzinfo import memorized_ttinfo as ttinfo

class Kaliningrad(DstTzInfo):
    '''Europe/Kaliningrad timezone definition. See datetime.tzinfo for details'''

    _zone = 'Europe/Kaliningrad'

    _utc_transition_times = [
        datetime(   1,  1,  1,  0,  0,  0), #   3600     0 CET
        datetime(1916,  4, 30, 22,  0,  0), #   7200  3600 CEST
        datetime(1916,  9, 30, 23,  0,  0), #   3600     0 CET
        datetime(1917,  4, 16,  1,  0,  0), #   7200  3600 CEST
        datetime(1917,  9, 17,  1,  0,  0), #   3600     0 CET
        datetime(1918,  4, 15,  1,  0,  0), #   7200  3600 CEST
        datetime(1918,  9, 16,  1,  0,  0), #   3600     0 CET
        datetime(1940,  4,  1,  1,  0,  0), #   7200  3600 CEST
        datetime(1942, 11,  2,  1,  0,  0), #   3600     0 CET
        datetime(1943,  3, 29,  1,  0,  0), #   7200  3600 CEST
        datetime(1943, 10,  4,  1,  0,  0), #   3600     0 CET
        datetime(1944,  4,  3,  1,  0,  0), #   7200  3600 CEST
        datetime(1944, 10,  2,  1,  0,  0), #   3600     0 CET
        datetime(1944, 12, 31, 23,  0,  0), #   7200     0 CET
        datetime(1945,  4, 28, 22,  0,  0), #  10800  3600 CEST
        datetime(1945, 10, 31, 21,  0,  0), #   7200     0 CET
        datetime(1945, 12, 31, 22,  0,  0), #  10800     0 MSK
        datetime(1981,  3, 31, 21,  0,  0), #  14400  3600 MSD
        datetime(1981,  9, 30, 20,  0,  0), #  10800     0 MSK
        datetime(1982,  3, 31, 21,  0,  0), #  14400  3600 MSD
        datetime(1982,  9, 30, 20,  0,  0), #  10800     0 MSK
        datetime(1983,  3, 31, 21,  0,  0), #  14400  3600 MSD
        datetime(1983,  9, 30, 20,  0,  0), #  10800     0 MSK
        datetime(1984,  3, 31, 21,  0,  0), #  14400  3600 MSD
        datetime(1984,  9, 29, 23,  0,  0), #  10800     0 MSK
        datetime(1985,  3, 30, 23,  0,  0), #  14400  3600 MSD
        datetime(1985,  9, 28, 23,  0,  0), #  10800     0 MSK
        datetime(1986,  3, 29, 23,  0,  0), #  14400  3600 MSD
        datetime(1986,  9, 27, 23,  0,  0), #  10800     0 MSK
        datetime(1987,  3, 28, 23,  0,  0), #  14400  3600 MSD
        datetime(1987,  9, 26, 23,  0,  0), #  10800     0 MSK
        datetime(1988,  3, 26, 23,  0,  0), #  14400  3600 MSD
        datetime(1988,  9, 24, 23,  0,  0), #  10800     0 MSK
        datetime(1989,  3, 25, 23,  0,  0), #  14400  3600 MSD
        datetime(1989,  9, 23, 23,  0,  0), #  10800     0 MSK
        datetime(1990,  3, 24, 23,  0,  0), #  14400  3600 MSD
        datetime(1990,  9, 29, 23,  0,  0), #  10800     0 MSK
        datetime(1991,  3, 30, 23,  0,  0), #  10800     0 EEST
        datetime(1991,  9, 29,  0,  0,  0), #   7200     0 EET
        datetime(1992,  3, 28, 21,  0,  0), #  10800  3600 EEST
        datetime(1992,  9, 26, 20,  0,  0), #   7200     0 EET
        datetime(1993,  3, 28,  0,  0,  0), #  10800  3600 EEST
        datetime(1993,  9, 26,  0,  0,  0), #   7200     0 EET
        datetime(1994,  3, 27,  0,  0,  0), #  10800  3600 EEST
        datetime(1994,  9, 25,  0,  0,  0), #   7200     0 EET
        datetime(1995,  3, 26,  0,  0,  0), #  10800  3600 EEST
        datetime(1995,  9, 24,  0,  0,  0), #   7200     0 EET
        datetime(1996,  3, 31,  0,  0,  0), #  10800  3600 EEST
        datetime(1996, 10, 27,  0,  0,  0), #   7200     0 EET
        datetime(1997,  3, 30,  0,  0,  0), #  10800  3600 EEST
        datetime(1997, 10, 26,  0,  0,  0), #   7200     0 EET
        datetime(1998,  3, 29,  0,  0,  0), #  10800  3600 EEST
        datetime(1998, 10, 25,  0,  0,  0), #   7200     0 EET
        datetime(1999,  3, 28,  0,  0,  0), #  10800  3600 EEST
        datetime(1999, 10, 31,  0,  0,  0), #   7200     0 EET
        datetime(2000,  3, 26,  0,  0,  0), #  10800  3600 EEST
        datetime(2000, 10, 29,  0,  0,  0), #   7200     0 EET
        datetime(2001,  3, 25,  0,  0,  0), #  10800  3600 EEST
        datetime(2001, 10, 28,  0,  0,  0), #   7200     0 EET
        datetime(2002,  3, 31,  0,  0,  0), #  10800  3600 EEST
        datetime(2002, 10, 27,  0,  0,  0), #   7200     0 EET
        datetime(2003,  3, 30,  0,  0,  0), #  10800  3600 EEST
        datetime(2003, 10, 26,  0,  0,  0), #   7200     0 EET
        datetime(2004,  3, 28,  0,  0,  0), #  10800  3600 EEST
        datetime(2004, 10, 31,  0,  0,  0), #   7200     0 EET
        datetime(2005,  3, 27,  0,  0,  0), #  10800  3600 EEST
        datetime(2005, 10, 30,  0,  0,  0), #   7200     0 EET
        datetime(2006,  3, 26,  0,  0,  0), #  10800  3600 EEST
        datetime(2006, 10, 29,  0,  0,  0), #   7200     0 EET
        datetime(2007,  3, 25,  0,  0,  0), #  10800  3600 EEST
        datetime(2007, 10, 28,  0,  0,  0), #   7200     0 EET
        datetime(2008,  3, 30,  0,  0,  0), #  10800  3600 EEST
        datetime(2008, 10, 26,  0,  0,  0), #   7200     0 EET
        datetime(2009,  3, 29,  0,  0,  0), #  10800  3600 EEST
        datetime(2009, 10, 25,  0,  0,  0), #   7200     0 EET
        datetime(2010,  3, 28,  0,  0,  0), #  10800  3600 EEST
        datetime(2010, 10, 31,  0,  0,  0), #   7200     0 EET
        datetime(2011,  3, 27,  0,  0,  0), #  10800  3600 EEST
        datetime(2011, 10, 30,  0,  0,  0), #   7200     0 EET
        datetime(2012,  3, 25,  0,  0,  0), #  10800  3600 EEST
        datetime(2012, 10, 28,  0,  0,  0), #   7200     0 EET
        datetime(2013,  3, 31,  0,  0,  0), #  10800  3600 EEST
        datetime(2013, 10, 27,  0,  0,  0), #   7200     0 EET
        datetime(2014,  3, 30,  0,  0,  0), #  10800  3600 EEST
        datetime(2014, 10, 26,  0,  0,  0), #   7200     0 EET
        datetime(2015,  3, 29,  0,  0,  0), #  10800  3600 EEST
        datetime(2015, 10, 25,  0,  0,  0), #   7200     0 EET
        datetime(2016,  3, 27,  0,  0,  0), #  10800  3600 EEST
        datetime(2016, 10, 30,  0,  0,  0), #   7200     0 EET
        datetime(2017,  3, 26,  0,  0,  0), #  10800  3600 EEST
        datetime(2017, 10, 29,  0,  0,  0), #   7200     0 EET
        datetime(2018,  3, 25,  0,  0,  0), #  10800  3600 EEST
        datetime(2018, 10, 28,  0,  0,  0), #   7200     0 EET
        datetime(2019,  3, 31,  0,  0,  0), #  10800  3600 EEST
        datetime(2019, 10, 27,  0,  0,  0), #   7200     0 EET
        datetime(2020,  3, 29,  0,  0,  0), #  10800  3600 EEST
        datetime(2020, 10, 25,  0,  0,  0), #   7200     0 EET
        datetime(2021,  3, 28,  0,  0,  0), #  10800  3600 EEST
        datetime(2021, 10, 31,  0,  0,  0), #   7200     0 EET
        datetime(2022,  3, 27,  0,  0,  0), #  10800  3600 EEST
        datetime(2022, 10, 30,  0,  0,  0), #   7200     0 EET
        datetime(2023,  3, 26,  0,  0,  0), #  10800  3600 EEST
        datetime(2023, 10, 29,  0,  0,  0), #   7200     0 EET
        datetime(2024,  3, 31,  0,  0,  0), #  10800  3600 EEST
        datetime(2024, 10, 27,  0,  0,  0), #   7200     0 EET
        datetime(2025,  3, 30,  0,  0,  0), #  10800  3600 EEST
        datetime(2025, 10, 26,  0,  0,  0), #   7200     0 EET
        datetime(2026,  3, 29,  0,  0,  0), #  10800  3600 EEST
        datetime(2026, 10, 25,  0,  0,  0), #   7200     0 EET
        datetime(2027,  3, 28,  0,  0,  0), #  10800  3600 EEST
        datetime(2027, 10, 31,  0,  0,  0), #   7200     0 EET
        datetime(2028,  3, 26,  0,  0,  0), #  10800  3600 EEST
        datetime(2028, 10, 29,  0,  0,  0), #   7200     0 EET
        datetime(2029,  3, 25,  0,  0,  0), #  10800  3600 EEST
        datetime(2029, 10, 28,  0,  0,  0), #   7200     0 EET
        datetime(2030,  3, 31,  0,  0,  0), #  10800  3600 EEST
        datetime(2030, 10, 27,  0,  0,  0), #   7200     0 EET
        datetime(2031,  3, 30,  0,  0,  0), #  10800  3600 EEST
        datetime(2031, 10, 26,  0,  0,  0), #   7200     0 EET
        datetime(2032,  3, 28,  0,  0,  0), #  10800  3600 EEST
        datetime(2032, 10, 31,  0,  0,  0), #   7200     0 EET
        datetime(2033,  3, 27,  0,  0,  0), #  10800  3600 EEST
        datetime(2033, 10, 30,  0,  0,  0), #   7200     0 EET
        datetime(2034,  3, 26,  0,  0,  0), #  10800  3600 EEST
        datetime(2034, 10, 29,  0,  0,  0), #   7200     0 EET
        datetime(2035,  3, 25,  0,  0,  0), #  10800  3600 EEST
        datetime(2035, 10, 28,  0,  0,  0), #   7200     0 EET
        datetime(2036,  3, 30,  0,  0,  0), #  10800  3600 EEST
        datetime(2036, 10, 26,  0,  0,  0), #   7200     0 EET
        datetime(2037,  3, 29,  0,  0,  0), #  10800  3600 EEST
        datetime(2037, 10, 25,  0,  0,  0), #   7200     0 EET
        ]

    _transition_info = [
        ttinfo(  3600,      0,  'CET'),
        ttinfo(  7200,   3600, 'CEST'),
        ttinfo(  3600,      0,  'CET'),
        ttinfo(  7200,   3600, 'CEST'),
        ttinfo(  3600,      0,  'CET'),
        ttinfo(  7200,   3600, 'CEST'),
        ttinfo(  3600,      0,  'CET'),
        ttinfo(  7200,   3600, 'CEST'),
        ttinfo(  3600,      0,  'CET'),
        ttinfo(  7200,   3600, 'CEST'),
        ttinfo(  3600,      0,  'CET'),
        ttinfo(  7200,   3600, 'CEST'),
        ttinfo(  3600,      0,  'CET'),
        ttinfo(  7200,      0,  'CET'),
        ttinfo( 10800,   3600, 'CEST'),
        ttinfo(  7200,      0,  'CET'),
        ttinfo( 10800,      0,  'MSK'),
        ttinfo( 14400,   3600,  'MSD'),
        ttinfo( 10800,      0,  'MSK'),
        ttinfo( 14400,   3600,  'MSD'),
        ttinfo( 10800,      0,  'MSK'),
        ttinfo( 14400,   3600,  'MSD'),
        ttinfo( 10800,      0,  'MSK'),
        ttinfo( 14400,   3600,  'MSD'),
        ttinfo( 10800,      0,  'MSK'),
        ttinfo( 14400,   3600,  'MSD'),
        ttinfo( 10800,      0,  'MSK'),
        ttinfo( 14400,   3600,  'MSD'),
        ttinfo( 10800,      0,  'MSK'),
        ttinfo( 14400,   3600,  'MSD'),
        ttinfo( 10800,      0,  'MSK'),
        ttinfo( 14400,   3600,  'MSD'),
        ttinfo( 10800,      0,  'MSK'),
        ttinfo( 14400,   3600,  'MSD'),
        ttinfo( 10800,      0,  'MSK'),
        ttinfo( 14400,   3600,  'MSD'),
        ttinfo( 10800,      0,  'MSK'),
        ttinfo( 10800,      0, 'EEST'),
        ttinfo(  7200,      0,  'EET'),
        ttinfo( 10800,   3600, 'EEST'),
        ttinfo(  7200,      0,  'EET'),
        ttinfo( 10800,   3600, 'EEST'),
        ttinfo(  7200,      0,  'EET'),
        ttinfo( 10800,   3600, 'EEST'),
        ttinfo(  7200,      0,  'EET'),
        ttinfo( 10800,   3600, 'EEST'),
        ttinfo(  7200,      0,  'EET'),
        ttinfo( 10800,   3600, 'EEST'),
        ttinfo(  7200,      0,  'EET'),
        ttinfo( 10800,   3600, 'EEST'),
        ttinfo(  7200,      0,  'EET'),
        ttinfo( 10800,   3600, 'EEST'),
        ttinfo(  7200,      0,  'EET'),
        ttinfo( 10800,   3600, 'EEST'),
        ttinfo(  7200,      0,  'EET'),
        ttinfo( 10800,   3600, 'EEST'),
        ttinfo(  7200,      0,  'EET'),
        ttinfo( 10800,   3600, 'EEST'),
        ttinfo(  7200,      0,  'EET'),
        ttinfo( 10800,   3600, 'EEST'),
        ttinfo(  7200,      0,  'EET'),
        ttinfo( 10800,   3600, 'EEST'),
        ttinfo(  7200,      0,  'EET'),
        ttinfo( 10800,   3600, 'EEST'),
        ttinfo(  7200,      0,  'EET'),
        ttinfo( 10800,   3600, 'EEST'),
        ttinfo(  7200,      0,  'EET'),
        ttinfo( 10800,   3600, 'EEST'),
        ttinfo(  7200,      0,  'EET'),
        ttinfo( 10800,   3600, 'EEST'),
        ttinfo(  7200,      0,  'EET'),
        ttinfo( 10800,   3600, 'EEST'),
        ttinfo(  7200,      0,  'EET'),
        ttinfo( 10800,   3600, 'EEST'),
        ttinfo(  7200,      0,  'EET'),
        ttinfo( 10800,   3600, 'EEST'),
        ttinfo(  7200,      0,  'EET'),
        ttinfo( 10800,   3600, 'EEST'),
        ttinfo(  7200,      0,  'EET'),
        ttinfo( 10800,   3600, 'EEST'),
        ttinfo(  7200,      0,  'EET'),
        ttinfo( 10800,   3600, 'EEST'),
        ttinfo(  7200,      0,  'EET'),
        ttinfo( 10800,   3600, 'EEST'),
        ttinfo(  7200,      0,  'EET'),
        ttinfo( 10800,   3600, 'EEST'),
        ttinfo(  7200,      0,  'EET'),
        ttinfo( 10800,   3600, 'EEST'),
        ttinfo(  7200,      0,  'EET'),
        ttinfo( 10800,   3600, 'EEST'),
        ttinfo(  7200,      0,  'EET'),
        ttinfo( 10800,   3600, 'EEST'),
        ttinfo(  7200,      0,  'EET'),
        ttinfo( 10800,   3600, 'EEST'),
        ttinfo(  7200,      0,  'EET'),
        ttinfo( 10800,   3600, 'EEST'),
        ttinfo(  7200,      0,  'EET'),
        ttinfo( 10800,   3600, 'EEST'),
        ttinfo(  7200,      0,  'EET'),
        ttinfo( 10800,   3600, 'EEST'),
        ttinfo(  7200,      0,  'EET'),
        ttinfo( 10800,   3600, 'EEST'),
        ttinfo(  7200,      0,  'EET'),
        ttinfo( 10800,   3600, 'EEST'),
        ttinfo(  7200,      0,  'EET'),
        ttinfo( 10800,   3600, 'EEST'),
        ttinfo(  7200,      0,  'EET'),
        ttinfo( 10800,   3600, 'EEST'),
        ttinfo(  7200,      0,  'EET'),
        ttinfo( 10800,   3600, 'EEST'),
        ttinfo(  7200,      0,  'EET'),
        ttinfo( 10800,   3600, 'EEST'),
        ttinfo(  7200,      0,  'EET'),
        ttinfo( 10800,   3600, 'EEST'),
        ttinfo(  7200,      0,  'EET'),
        ttinfo( 10800,   3600, 'EEST'),
        ttinfo(  7200,      0,  'EET'),
        ttinfo( 10800,   3600, 'EEST'),
        ttinfo(  7200,      0,  'EET'),
        ttinfo( 10800,   3600, 'EEST'),
        ttinfo(  7200,      0,  'EET'),
        ttinfo( 10800,   3600, 'EEST'),
        ttinfo(  7200,      0,  'EET'),
        ttinfo( 10800,   3600, 'EEST'),
        ttinfo(  7200,      0,  'EET'),
        ttinfo( 10800,   3600, 'EEST'),
        ttinfo(  7200,      0,  'EET'),
        ttinfo( 10800,   3600, 'EEST'),
        ttinfo(  7200,      0,  'EET'),
        ttinfo( 10800,   3600, 'EEST'),
        ttinfo(  7200,      0,  'EET'),
        ]

Kaliningrad = Kaliningrad() # Singleton

