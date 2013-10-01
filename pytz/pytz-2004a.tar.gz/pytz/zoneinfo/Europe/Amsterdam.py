'''
tzinfo timezone information for Europe/Amsterdam.

Generated from the Olson timezone database:
    ftp://elsie.nci.nih.gov/pub/tz*.tar.gz
'''

from pytz.tzinfo import DstTzInfo
from pytz.tzinfo import memorized_datetime as datetime
from pytz.tzinfo import memorized_ttinfo as ttinfo

class Amsterdam(DstTzInfo):
    '''Europe/Amsterdam timezone definition. See datetime.tzinfo for details'''

    _zone = 'Europe/Amsterdam'

    _utc_transition_times = [
        datetime(   1,  1,  1,  0,  0,  0), #   1172     0 AMT
        datetime(1916,  4, 30, 23, 40, 28), #   4772  3600 NST
        datetime(1916,  9, 30, 22, 40, 28), #   1172     0 AMT
        datetime(1917,  4, 16,  1, 40, 28), #   4772  3600 NST
        datetime(1917,  9, 17,  1, 40, 28), #   1172     0 AMT
        datetime(1918,  4,  1,  1, 40, 28), #   4772  3600 NST
        datetime(1918,  9, 30,  1, 40, 28), #   1172     0 AMT
        datetime(1919,  4,  7,  1, 40, 28), #   4772  3600 NST
        datetime(1919,  9, 29,  1, 40, 28), #   1172     0 AMT
        datetime(1920,  4,  5,  1, 40, 28), #   4772  3600 NST
        datetime(1920,  9, 27,  1, 40, 28), #   1172     0 AMT
        datetime(1921,  4,  4,  1, 40, 28), #   4772  3600 NST
        datetime(1921,  9, 26,  1, 40, 28), #   1172     0 AMT
        datetime(1922,  3, 26,  1, 40, 28), #   4772  3600 NST
        datetime(1922, 10,  8,  1, 40, 28), #   1172     0 AMT
        datetime(1923,  6,  1,  1, 40, 28), #   4772  3600 NST
        datetime(1923, 10,  7,  1, 40, 28), #   1172     0 AMT
        datetime(1924,  3, 30,  1, 40, 28), #   4772  3600 NST
        datetime(1924, 10,  5,  1, 40, 28), #   1172     0 AMT
        datetime(1925,  6,  5,  1, 40, 28), #   4772  3600 NST
        datetime(1925, 10,  4,  1, 40, 28), #   1172     0 AMT
        datetime(1926,  5, 15,  1, 40, 28), #   4772  3600 NST
        datetime(1926, 10,  3,  1, 40, 28), #   1172     0 AMT
        datetime(1927,  5, 15,  1, 40, 28), #   4772  3600 NST
        datetime(1927, 10,  2,  1, 40, 28), #   1172     0 AMT
        datetime(1928,  5, 15,  1, 40, 28), #   4772  3600 NST
        datetime(1928, 10,  7,  1, 40, 28), #   1172     0 AMT
        datetime(1929,  5, 15,  1, 40, 28), #   4772  3600 NST
        datetime(1929, 10,  6,  1, 40, 28), #   1172     0 AMT
        datetime(1930,  5, 15,  1, 40, 28), #   4772  3600 NST
        datetime(1930, 10,  5,  1, 40, 28), #   1172     0 AMT
        datetime(1931,  5, 15,  1, 40, 28), #   4772  3600 NST
        datetime(1931, 10,  4,  1, 40, 28), #   1172     0 AMT
        datetime(1932,  5, 22,  1, 40, 28), #   4772  3600 NST
        datetime(1932, 10,  2,  1, 40, 28), #   1172     0 AMT
        datetime(1933,  5, 15,  1, 40, 28), #   4772  3600 NST
        datetime(1933, 10,  8,  1, 40, 28), #   1172     0 AMT
        datetime(1934,  5, 15,  1, 40, 28), #   4772  3600 NST
        datetime(1934, 10,  7,  1, 40, 28), #   1172     0 AMT
        datetime(1935,  5, 15,  1, 40, 28), #   4772  3600 NST
        datetime(1935, 10,  6,  1, 40, 28), #   1172     0 AMT
        datetime(1936,  5, 15,  1, 40, 28), #   4772  3600 NST
        datetime(1936, 10,  4,  1, 40, 28), #   1172     0 AMT
        datetime(1937,  5, 22,  1, 40, 28), #   4772  3600 NST
        datetime(1937,  6, 30, 22, 40, 28), #   4800    28 NEST
        datetime(1937, 10,  3,  1, 40,  0), #   1200     0 NET
        datetime(1938,  5, 15,  1, 40,  0), #   4800  3600 NEST
        datetime(1938, 10,  2,  1, 40,  0), #   1200     0 NET
        datetime(1939,  5, 15,  1, 40,  0), #   4800  3600 NEST
        datetime(1939, 10,  8,  1, 40,  0), #   1200     0 NET
        datetime(1940,  5, 15, 23, 40,  0), #   7200  6000 CEST
        datetime(1942, 11,  2,  1,  0,  0), #   3600     0 CET
        datetime(1943,  3, 29,  1,  0,  0), #   7200  3600 CEST
        datetime(1943, 10,  4,  1,  0,  0), #   3600     0 CET
        datetime(1944,  4,  3,  1,  0,  0), #   7200  3600 CEST
        datetime(1944, 10,  2,  1,  0,  0), #   3600     0 CET
        datetime(1945,  4,  2,  1,  0,  0), #   7200  3600 CEST
        datetime(1945,  9, 16,  1,  0,  0), #   3600     0 CET
        datetime(1976, 12, 31, 23,  0,  0), #   3600     0 CET
        datetime(1977,  4,  3,  1,  0,  0), #   7200  3600 CEST
        datetime(1977,  9, 25,  1,  0,  0), #   3600     0 CET
        datetime(1978,  4,  2,  1,  0,  0), #   7200  3600 CEST
        datetime(1978, 10,  1,  1,  0,  0), #   3600     0 CET
        datetime(1979,  4,  1,  1,  0,  0), #   7200  3600 CEST
        datetime(1979,  9, 30,  1,  0,  0), #   3600     0 CET
        datetime(1980,  4,  6,  1,  0,  0), #   7200  3600 CEST
        datetime(1980,  9, 28,  1,  0,  0), #   3600     0 CET
        datetime(1981,  3, 29,  1,  0,  0), #   7200  3600 CEST
        datetime(1981,  9, 27,  1,  0,  0), #   3600     0 CET
        datetime(1982,  3, 28,  1,  0,  0), #   7200  3600 CEST
        datetime(1982,  9, 26,  1,  0,  0), #   3600     0 CET
        datetime(1983,  3, 27,  1,  0,  0), #   7200  3600 CEST
        datetime(1983,  9, 25,  1,  0,  0), #   3600     0 CET
        datetime(1984,  3, 25,  1,  0,  0), #   7200  3600 CEST
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
        ttinfo(  1172,      0,  'AMT'),
        ttinfo(  4772,   3600,  'NST'),
        ttinfo(  1172,      0,  'AMT'),
        ttinfo(  4772,   3600,  'NST'),
        ttinfo(  1172,      0,  'AMT'),
        ttinfo(  4772,   3600,  'NST'),
        ttinfo(  1172,      0,  'AMT'),
        ttinfo(  4772,   3600,  'NST'),
        ttinfo(  1172,      0,  'AMT'),
        ttinfo(  4772,   3600,  'NST'),
        ttinfo(  1172,      0,  'AMT'),
        ttinfo(  4772,   3600,  'NST'),
        ttinfo(  1172,      0,  'AMT'),
        ttinfo(  4772,   3600,  'NST'),
        ttinfo(  1172,      0,  'AMT'),
        ttinfo(  4772,   3600,  'NST'),
        ttinfo(  1172,      0,  'AMT'),
        ttinfo(  4772,   3600,  'NST'),
        ttinfo(  1172,      0,  'AMT'),
        ttinfo(  4772,   3600,  'NST'),
        ttinfo(  1172,      0,  'AMT'),
        ttinfo(  4772,   3600,  'NST'),
        ttinfo(  1172,      0,  'AMT'),
        ttinfo(  4772,   3600,  'NST'),
        ttinfo(  1172,      0,  'AMT'),
        ttinfo(  4772,   3600,  'NST'),
        ttinfo(  1172,      0,  'AMT'),
        ttinfo(  4772,   3600,  'NST'),
        ttinfo(  1172,      0,  'AMT'),
        ttinfo(  4772,   3600,  'NST'),
        ttinfo(  1172,      0,  'AMT'),
        ttinfo(  4772,   3600,  'NST'),
        ttinfo(  1172,      0,  'AMT'),
        ttinfo(  4772,   3600,  'NST'),
        ttinfo(  1172,      0,  'AMT'),
        ttinfo(  4772,   3600,  'NST'),
        ttinfo(  1172,      0,  'AMT'),
        ttinfo(  4772,   3600,  'NST'),
        ttinfo(  1172,      0,  'AMT'),
        ttinfo(  4772,   3600,  'NST'),
        ttinfo(  1172,      0,  'AMT'),
        ttinfo(  4772,   3600,  'NST'),
        ttinfo(  1172,      0,  'AMT'),
        ttinfo(  4772,   3600,  'NST'),
        ttinfo(  4800,     28, 'NEST'),
        ttinfo(  1200,      0,  'NET'),
        ttinfo(  4800,   3600, 'NEST'),
        ttinfo(  1200,      0,  'NET'),
        ttinfo(  4800,   3600, 'NEST'),
        ttinfo(  1200,      0,  'NET'),
        ttinfo(  7200,   6000, 'CEST'),
        ttinfo(  3600,      0,  'CET'),
        ttinfo(  7200,   3600, 'CEST'),
        ttinfo(  3600,      0,  'CET'),
        ttinfo(  7200,   3600, 'CEST'),
        ttinfo(  3600,      0,  'CET'),
        ttinfo(  7200,   3600, 'CEST'),
        ttinfo(  3600,      0,  'CET'),
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

Amsterdam = Amsterdam() # Singleton

