'''
tzinfo timezone information for Europe/Tirane.

Generated from the Olson timezone database:
    ftp://elsie.nci.nih.gov/pub/tz*.tar.gz
'''

from pytz.tzinfo import DstTzInfo
from pytz.tzinfo import memorized_datetime as datetime
from pytz.tzinfo import memorized_ttinfo as ttinfo

class Tirane(DstTzInfo):
    '''Europe/Tirane timezone definition. See datetime.tzinfo for details'''

    _zone = 'Europe/Tirane'

    _utc_transition_times = [
        datetime(   1,  1,  1,  0,  0,  0), #   4760     0 LMT
        datetime(1913, 12, 31, 22, 40, 40), #   3600     0 CET
        datetime(1940,  6, 15, 23,  0,  0), #   7200  3600 CEST
        datetime(1942, 11,  2,  1,  0,  0), #   3600     0 CET
        datetime(1943,  3, 29,  1,  0,  0), #   7200  3600 CEST
        datetime(1943,  4, 10,  1,  0,  0), #   3600     0 CET
        datetime(1974,  5,  3, 23,  0,  0), #   7200  3600 CEST
        datetime(1974, 10,  1, 22,  0,  0), #   3600     0 CET
        datetime(1975,  4, 30, 23,  0,  0), #   7200  3600 CEST
        datetime(1975, 10,  1, 22,  0,  0), #   3600     0 CET
        datetime(1976,  5,  1, 23,  0,  0), #   7200  3600 CEST
        datetime(1976, 10,  2, 22,  0,  0), #   3600     0 CET
        datetime(1977,  5,  7, 23,  0,  0), #   7200  3600 CEST
        datetime(1977, 10,  1, 22,  0,  0), #   3600     0 CET
        datetime(1978,  5,  5, 23,  0,  0), #   7200  3600 CEST
        datetime(1978,  9, 30, 22,  0,  0), #   3600     0 CET
        datetime(1979,  5,  4, 23,  0,  0), #   7200  3600 CEST
        datetime(1979,  9, 29, 22,  0,  0), #   3600     0 CET
        datetime(1980,  5,  2, 23,  0,  0), #   7200  3600 CEST
        datetime(1980, 10,  3, 22,  0,  0), #   3600     0 CET
        datetime(1981,  4, 25, 23,  0,  0), #   7200  3600 CEST
        datetime(1981,  9, 26, 22,  0,  0), #   3600     0 CET
        datetime(1982,  5,  1, 23,  0,  0), #   7200  3600 CEST
        datetime(1982, 10,  2, 22,  0,  0), #   3600     0 CET
        datetime(1983,  4, 17, 23,  0,  0), #   7200  3600 CEST
        datetime(1983,  9, 30, 22,  0,  0), #   3600     0 CET
        datetime(1984,  3, 31, 23,  0,  0), #   7200  3600 CEST
        datetime(1984,  9, 30,  1,  0,  0), #   3600     0 CET
        datetime(1985,  3, 31,  1,  0,  0), #   7200  3600 CEST
        datetime(1985,  9, 29,  1,  0,  0), #   3600     0 CET
        datetime(1986,  3, 30,  1,  0,  0), #   7200  3600 CEST
        datetime(1986,  9, 28,  1,  0,  0), #   3600     0 CET
        datetime(1987,  3, 29,  1,  0,  0), #   7200  3600 CEST
        datetime(1987,  9, 27,  1,  0,  0), #   3600     0 CET
        datetime(1988,  3, 27,  1,  0,  0), #   7200  3600 CEST
        datetime(1988,  9, 25,  1,  0,  0), #   3600     0 CET
        datetime(1989,  3, 26,  1,  0,  0), #   7200  3600 CEST
        datetime(1989,  9, 24,  1,  0,  0), #   3600     0 CET
        datetime(1990,  3, 25,  1,  0,  0), #   7200  3600 CEST
        datetime(1990,  9, 30,  1,  0,  0), #   3600     0 CET
        datetime(1991,  3, 31,  1,  0,  0), #   7200  3600 CEST
        datetime(1991,  9, 29,  1,  0,  0), #   3600     0 CET
        datetime(1992,  3, 29,  1,  0,  0), #   7200  3600 CEST
        datetime(1992,  9, 27,  1,  0,  0), #   3600     0 CET
        datetime(1993,  3, 28,  1,  0,  0), #   7200  3600 CEST
        datetime(1993,  9, 26,  1,  0,  0), #   3600     0 CET
        datetime(1994,  3, 27,  1,  0,  0), #   7200  3600 CEST
        datetime(1994,  9, 25,  1,  0,  0), #   3600     0 CET
        datetime(1995,  3, 26,  1,  0,  0), #   7200  3600 CEST
        datetime(1995,  9, 24,  1,  0,  0), #   3600     0 CET
        datetime(1996,  3, 31,  1,  0,  0), #   7200  3600 CEST
        datetime(1996, 10, 27,  1,  0,  0), #   3600     0 CET
        datetime(1997,  3, 30,  1,  0,  0), #   7200  3600 CEST
        datetime(1997, 10, 26,  1,  0,  0), #   3600     0 CET
        datetime(1998,  3, 29,  1,  0,  0), #   7200  3600 CEST
        datetime(1998, 10, 25,  1,  0,  0), #   3600     0 CET
        datetime(1999,  3, 28,  1,  0,  0), #   7200  3600 CEST
        datetime(1999, 10, 31,  1,  0,  0), #   3600     0 CET
        datetime(2000,  3, 26,  1,  0,  0), #   7200  3600 CEST
        datetime(2000, 10, 29,  1,  0,  0), #   3600     0 CET
        datetime(2001,  3, 25,  1,  0,  0), #   7200  3600 CEST
        datetime(2001, 10, 28,  1,  0,  0), #   3600     0 CET
        datetime(2002,  3, 31,  1,  0,  0), #   7200  3600 CEST
        datetime(2002, 10, 27,  1,  0,  0), #   3600     0 CET
        datetime(2003,  3, 30,  1,  0,  0), #   7200  3600 CEST
        datetime(2003, 10, 26,  1,  0,  0), #   3600     0 CET
        datetime(2004,  3, 28,  1,  0,  0), #   7200  3600 CEST
        datetime(2004, 10, 31,  1,  0,  0), #   3600     0 CET
        datetime(2005,  3, 27,  1,  0,  0), #   7200  3600 CEST
        datetime(2005, 10, 30,  1,  0,  0), #   3600     0 CET
        datetime(2006,  3, 26,  1,  0,  0), #   7200  3600 CEST
        datetime(2006, 10, 29,  1,  0,  0), #   3600     0 CET
        datetime(2007,  3, 25,  1,  0,  0), #   7200  3600 CEST
        datetime(2007, 10, 28,  1,  0,  0), #   3600     0 CET
        datetime(2008,  3, 30,  1,  0,  0), #   7200  3600 CEST
        datetime(2008, 10, 26,  1,  0,  0), #   3600     0 CET
        datetime(2009,  3, 29,  1,  0,  0), #   7200  3600 CEST
        datetime(2009, 10, 25,  1,  0,  0), #   3600     0 CET
        datetime(2010,  3, 28,  1,  0,  0), #   7200  3600 CEST
        datetime(2010, 10, 31,  1,  0,  0), #   3600     0 CET
        datetime(2011,  3, 27,  1,  0,  0), #   7200  3600 CEST
        datetime(2011, 10, 30,  1,  0,  0), #   3600     0 CET
        datetime(2012,  3, 25,  1,  0,  0), #   7200  3600 CEST
        datetime(2012, 10, 28,  1,  0,  0), #   3600     0 CET
        datetime(2013,  3, 31,  1,  0,  0), #   7200  3600 CEST
        datetime(2013, 10, 27,  1,  0,  0), #   3600     0 CET
        datetime(2014,  3, 30,  1,  0,  0), #   7200  3600 CEST
        datetime(2014, 10, 26,  1,  0,  0), #   3600     0 CET
        datetime(2015,  3, 29,  1,  0,  0), #   7200  3600 CEST
        datetime(2015, 10, 25,  1,  0,  0), #   3600     0 CET
        datetime(2016,  3, 27,  1,  0,  0), #   7200  3600 CEST
        datetime(2016, 10, 30,  1,  0,  0), #   3600     0 CET
        datetime(2017,  3, 26,  1,  0,  0), #   7200  3600 CEST
        datetime(2017, 10, 29,  1,  0,  0), #   3600     0 CET
        datetime(2018,  3, 25,  1,  0,  0), #   7200  3600 CEST
        datetime(2018, 10, 28,  1,  0,  0), #   3600     0 CET
        datetime(2019,  3, 31,  1,  0,  0), #   7200  3600 CEST
        datetime(2019, 10, 27,  1,  0,  0), #   3600     0 CET
        datetime(2020,  3, 29,  1,  0,  0), #   7200  3600 CEST
        datetime(2020, 10, 25,  1,  0,  0), #   3600     0 CET
        datetime(2021,  3, 28,  1,  0,  0), #   7200  3600 CEST
        datetime(2021, 10, 31,  1,  0,  0), #   3600     0 CET
        datetime(2022,  3, 27,  1,  0,  0), #   7200  3600 CEST
        datetime(2022, 10, 30,  1,  0,  0), #   3600     0 CET
        datetime(2023,  3, 26,  1,  0,  0), #   7200  3600 CEST
        datetime(2023, 10, 29,  1,  0,  0), #   3600     0 CET
        datetime(2024,  3, 31,  1,  0,  0), #   7200  3600 CEST
        datetime(2024, 10, 27,  1,  0,  0), #   3600     0 CET
        datetime(2025,  3, 30,  1,  0,  0), #   7200  3600 CEST
        datetime(2025, 10, 26,  1,  0,  0), #   3600     0 CET
        datetime(2026,  3, 29,  1,  0,  0), #   7200  3600 CEST
        datetime(2026, 10, 25,  1,  0,  0), #   3600     0 CET
        datetime(2027,  3, 28,  1,  0,  0), #   7200  3600 CEST
        datetime(2027, 10, 31,  1,  0,  0), #   3600     0 CET
        datetime(2028,  3, 26,  1,  0,  0), #   7200  3600 CEST
        datetime(2028, 10, 29,  1,  0,  0), #   3600     0 CET
        datetime(2029,  3, 25,  1,  0,  0), #   7200  3600 CEST
        datetime(2029, 10, 28,  1,  0,  0), #   3600     0 CET
        datetime(2030,  3, 31,  1,  0,  0), #   7200  3600 CEST
        datetime(2030, 10, 27,  1,  0,  0), #   3600     0 CET
        datetime(2031,  3, 30,  1,  0,  0), #   7200  3600 CEST
        datetime(2031, 10, 26,  1,  0,  0), #   3600     0 CET
        datetime(2032,  3, 28,  1,  0,  0), #   7200  3600 CEST
        datetime(2032, 10, 31,  1,  0,  0), #   3600     0 CET
        datetime(2033,  3, 27,  1,  0,  0), #   7200  3600 CEST
        datetime(2033, 10, 30,  1,  0,  0), #   3600     0 CET
        datetime(2034,  3, 26,  1,  0,  0), #   7200  3600 CEST
        datetime(2034, 10, 29,  1,  0,  0), #   3600     0 CET
        datetime(2035,  3, 25,  1,  0,  0), #   7200  3600 CEST
        datetime(2035, 10, 28,  1,  0,  0), #   3600     0 CET
        datetime(2036,  3, 30,  1,  0,  0), #   7200  3600 CEST
        datetime(2036, 10, 26,  1,  0,  0), #   3600     0 CET
        datetime(2037,  3, 29,  1,  0,  0), #   7200  3600 CEST
        datetime(2037, 10, 25,  1,  0,  0), #   3600     0 CET
        ]

    _transition_info = [
        ttinfo(  4760,      0,  'LMT'),
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
        ]

Tirane = Tirane() # Singleton

