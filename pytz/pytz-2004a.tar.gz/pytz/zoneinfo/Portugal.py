'''
tzinfo timezone information for Portugal.

Generated from the Olson timezone database:
    ftp://elsie.nci.nih.gov/pub/tz*.tar.gz
'''

from pytz.tzinfo import DstTzInfo
from pytz.tzinfo import memorized_datetime as datetime
from pytz.tzinfo import memorized_ttinfo as ttinfo

class Portugal(DstTzInfo):
    '''Portugal timezone definition. See datetime.tzinfo for details'''

    _zone = 'Portugal'

    _utc_transition_times = [
        datetime(   1,  1,  1,  0,  0,  0), #  -2192     0 LMT
        datetime(1912,  1,  1,  0, 36, 32), #      0     0 WET
        datetime(1916,  6, 17, 23,  0,  0), #   3600  3600 WEST
        datetime(1916, 11,  1,  0,  0,  0), #      0     0 WET
        datetime(1917,  2, 28, 23,  0,  0), #   3600  3600 WEST
        datetime(1917, 10, 14, 23,  0,  0), #      0     0 WET
        datetime(1918,  3,  1, 23,  0,  0), #   3600  3600 WEST
        datetime(1918, 10, 14, 23,  0,  0), #      0     0 WET
        datetime(1919,  2, 28, 23,  0,  0), #   3600  3600 WEST
        datetime(1919, 10, 14, 23,  0,  0), #      0     0 WET
        datetime(1920,  2, 29, 23,  0,  0), #   3600  3600 WEST
        datetime(1920, 10, 14, 23,  0,  0), #      0     0 WET
        datetime(1921,  2, 28, 23,  0,  0), #   3600  3600 WEST
        datetime(1921, 10, 14, 23,  0,  0), #      0     0 WET
        datetime(1924,  4, 16, 23,  0,  0), #   3600  3600 WEST
        datetime(1924, 10, 14, 23,  0,  0), #      0     0 WET
        datetime(1926,  4, 17, 23,  0,  0), #   3600  3600 WEST
        datetime(1926, 10,  2, 23,  0,  0), #      0     0 WET
        datetime(1927,  4,  9, 23,  0,  0), #   3600  3600 WEST
        datetime(1927, 10,  1, 23,  0,  0), #      0     0 WET
        datetime(1928,  4, 14, 23,  0,  0), #   3600  3600 WEST
        datetime(1928, 10,  6, 23,  0,  0), #      0     0 WET
        datetime(1929,  4, 20, 23,  0,  0), #   3600  3600 WEST
        datetime(1929, 10,  5, 23,  0,  0), #      0     0 WET
        datetime(1931,  4, 18, 23,  0,  0), #   3600  3600 WEST
        datetime(1931, 10,  3, 23,  0,  0), #      0     0 WET
        datetime(1932,  4,  2, 23,  0,  0), #   3600  3600 WEST
        datetime(1932, 10,  1, 23,  0,  0), #      0     0 WET
        datetime(1934,  4,  7, 23,  0,  0), #   3600  3600 WEST
        datetime(1934, 10,  6, 23,  0,  0), #      0     0 WET
        datetime(1935,  3, 30, 23,  0,  0), #   3600  3600 WEST
        datetime(1935, 10,  5, 23,  0,  0), #      0     0 WET
        datetime(1936,  4, 18, 23,  0,  0), #   3600  3600 WEST
        datetime(1936, 10,  3, 23,  0,  0), #      0     0 WET
        datetime(1937,  4,  3, 23,  0,  0), #   3600  3600 WEST
        datetime(1937, 10,  2, 23,  0,  0), #      0     0 WET
        datetime(1938,  3, 26, 23,  0,  0), #   3600  3600 WEST
        datetime(1938, 10,  1, 23,  0,  0), #      0     0 WET
        datetime(1939,  4, 15, 23,  0,  0), #   3600  3600 WEST
        datetime(1939, 11, 18, 23,  0,  0), #      0     0 WET
        datetime(1940,  2, 24, 23,  0,  0), #   3600  3600 WEST
        datetime(1940, 10,  5, 23,  0,  0), #      0     0 WET
        datetime(1941,  4,  5, 23,  0,  0), #   3600  3600 WEST
        datetime(1941, 10,  5, 23,  0,  0), #      0     0 WET
        datetime(1942,  3, 14, 23,  0,  0), #   3600  3600 WEST
        datetime(1942,  4, 25, 22,  0,  0), #   7200  3600 WEMT
        datetime(1942,  8, 15, 22,  0,  0), #   3600 -3600 WEST
        datetime(1942, 10, 24, 23,  0,  0), #      0     0 WET
        datetime(1943,  3, 13, 23,  0,  0), #   3600  3600 WEST
        datetime(1943,  4, 17, 22,  0,  0), #   7200  3600 WEMT
        datetime(1943,  8, 28, 22,  0,  0), #   3600 -3600 WEST
        datetime(1943, 10, 30, 23,  0,  0), #      0     0 WET
        datetime(1944,  3, 11, 23,  0,  0), #   3600  3600 WEST
        datetime(1944,  4, 22, 22,  0,  0), #   7200  3600 WEMT
        datetime(1944,  8, 26, 22,  0,  0), #   3600 -3600 WEST
        datetime(1944, 10, 28, 23,  0,  0), #      0     0 WET
        datetime(1945,  3, 10, 23,  0,  0), #   3600  3600 WEST
        datetime(1945,  4, 21, 22,  0,  0), #   7200  3600 WEMT
        datetime(1945,  8, 25, 22,  0,  0), #   3600 -3600 WEST
        datetime(1945, 10, 27, 23,  0,  0), #      0     0 WET
        datetime(1946,  4,  6, 23,  0,  0), #   3600  3600 WEST
        datetime(1946, 10,  5, 23,  0,  0), #      0     0 WET
        datetime(1947,  4,  6,  2,  0,  0), #   3600  3600 WEST
        datetime(1947, 10,  5,  2,  0,  0), #      0     0 WET
        datetime(1948,  4,  4,  2,  0,  0), #   3600  3600 WEST
        datetime(1948, 10,  3,  2,  0,  0), #      0     0 WET
        datetime(1949,  4,  3,  2,  0,  0), #   3600  3600 WEST
        datetime(1949, 10,  2,  2,  0,  0), #      0     0 WET
        datetime(1951,  4,  1,  2,  0,  0), #   3600  3600 WEST
        datetime(1951, 10,  7,  2,  0,  0), #      0     0 WET
        datetime(1952,  4,  6,  2,  0,  0), #   3600  3600 WEST
        datetime(1952, 10,  5,  2,  0,  0), #      0     0 WET
        datetime(1953,  4,  5,  2,  0,  0), #   3600  3600 WEST
        datetime(1953, 10,  4,  2,  0,  0), #      0     0 WET
        datetime(1954,  4,  4,  2,  0,  0), #   3600  3600 WEST
        datetime(1954, 10,  3,  2,  0,  0), #      0     0 WET
        datetime(1955,  4,  3,  2,  0,  0), #   3600  3600 WEST
        datetime(1955, 10,  2,  2,  0,  0), #      0     0 WET
        datetime(1956,  4,  1,  2,  0,  0), #   3600  3600 WEST
        datetime(1956, 10,  7,  2,  0,  0), #      0     0 WET
        datetime(1957,  4,  7,  2,  0,  0), #   3600  3600 WEST
        datetime(1957, 10,  6,  2,  0,  0), #      0     0 WET
        datetime(1958,  4,  6,  2,  0,  0), #   3600  3600 WEST
        datetime(1958, 10,  5,  2,  0,  0), #      0     0 WET
        datetime(1959,  4,  5,  2,  0,  0), #   3600  3600 WEST
        datetime(1959, 10,  4,  2,  0,  0), #      0     0 WET
        datetime(1960,  4,  3,  2,  0,  0), #   3600  3600 WEST
        datetime(1960, 10,  2,  2,  0,  0), #      0     0 WET
        datetime(1961,  4,  2,  2,  0,  0), #   3600  3600 WEST
        datetime(1961, 10,  1,  2,  0,  0), #      0     0 WET
        datetime(1962,  4,  1,  2,  0,  0), #   3600  3600 WEST
        datetime(1962, 10,  7,  2,  0,  0), #      0     0 WET
        datetime(1963,  4,  7,  2,  0,  0), #   3600  3600 WEST
        datetime(1963, 10,  6,  2,  0,  0), #      0     0 WET
        datetime(1964,  4,  5,  2,  0,  0), #   3600  3600 WEST
        datetime(1964, 10,  4,  2,  0,  0), #      0     0 WET
        datetime(1965,  4,  4,  2,  0,  0), #   3600  3600 WEST
        datetime(1965, 10,  3,  2,  0,  0), #      0     0 WET
        datetime(1966,  4,  3,  2,  0,  0), #   3600     0 CET
        datetime(1976,  9, 26,  0,  0,  0), #      0     0 WET
        datetime(1977,  3, 27,  0,  0,  0), #   3600  3600 WEST
        datetime(1977,  9, 25,  0,  0,  0), #      0     0 WET
        datetime(1978,  4,  2,  0,  0,  0), #   3600  3600 WEST
        datetime(1978, 10,  1,  0,  0,  0), #      0     0 WET
        datetime(1979,  4,  1,  0,  0,  0), #   3600  3600 WEST
        datetime(1979,  9, 30,  1,  0,  0), #      0     0 WET
        datetime(1980,  3, 30,  0,  0,  0), #   3600  3600 WEST
        datetime(1980,  9, 28,  1,  0,  0), #      0     0 WET
        datetime(1981,  3, 29,  1,  0,  0), #   3600  3600 WEST
        datetime(1981,  9, 27,  1,  0,  0), #      0     0 WET
        datetime(1982,  3, 28,  1,  0,  0), #   3600  3600 WEST
        datetime(1982,  9, 26,  1,  0,  0), #      0     0 WET
        datetime(1983,  3, 27,  2,  0,  0), #   3600  3600 WEST
        datetime(1983,  9, 25,  1,  0,  0), #      0     0 WET
        datetime(1984,  3, 25,  1,  0,  0), #   3600  3600 WEST
        datetime(1984,  9, 30,  1,  0,  0), #      0     0 WET
        datetime(1985,  3, 31,  1,  0,  0), #   3600  3600 WEST
        datetime(1985,  9, 29,  1,  0,  0), #      0     0 WET
        datetime(1986,  3, 30,  1,  0,  0), #   3600  3600 WEST
        datetime(1986,  9, 28,  1,  0,  0), #      0     0 WET
        datetime(1987,  3, 29,  1,  0,  0), #   3600  3600 WEST
        datetime(1987,  9, 27,  1,  0,  0), #      0     0 WET
        datetime(1988,  3, 27,  1,  0,  0), #   3600  3600 WEST
        datetime(1988,  9, 25,  1,  0,  0), #      0     0 WET
        datetime(1989,  3, 26,  1,  0,  0), #   3600  3600 WEST
        datetime(1989,  9, 24,  1,  0,  0), #      0     0 WET
        datetime(1990,  3, 25,  1,  0,  0), #   3600  3600 WEST
        datetime(1990,  9, 30,  1,  0,  0), #      0     0 WET
        datetime(1991,  3, 31,  1,  0,  0), #   3600  3600 WEST
        datetime(1991,  9, 29,  1,  0,  0), #      0     0 WET
        datetime(1992,  3, 29,  1,  0,  0), #   3600  3600 WEST
        datetime(1992,  9, 27,  1,  0,  0), #   3600     0 CET
        datetime(1993,  3, 28,  1,  0,  0), #   7200  3600 CEST
        datetime(1993,  9, 26,  1,  0,  0), #   3600     0 CET
        datetime(1994,  3, 27,  1,  0,  0), #   7200  3600 CEST
        datetime(1994,  9, 25,  1,  0,  0), #   3600     0 CET
        datetime(1995,  3, 26,  1,  0,  0), #   7200  3600 CEST
        datetime(1995,  9, 24,  1,  0,  0), #   3600     0 CET
        datetime(1996,  3, 31,  1,  0,  0), #   3600     0 WEST
        datetime(1996, 10, 27,  1,  0,  0), #      0     0 WET
        datetime(1997,  3, 30,  1,  0,  0), #   3600  3600 WEST
        datetime(1997, 10, 26,  1,  0,  0), #      0     0 WET
        datetime(1998,  3, 29,  1,  0,  0), #   3600  3600 WEST
        datetime(1998, 10, 25,  1,  0,  0), #      0     0 WET
        datetime(1999,  3, 28,  1,  0,  0), #   3600  3600 WEST
        datetime(1999, 10, 31,  1,  0,  0), #      0     0 WET
        datetime(2000,  3, 26,  1,  0,  0), #   3600  3600 WEST
        datetime(2000, 10, 29,  1,  0,  0), #      0     0 WET
        datetime(2001,  3, 25,  1,  0,  0), #   3600  3600 WEST
        datetime(2001, 10, 28,  1,  0,  0), #      0     0 WET
        datetime(2002,  3, 31,  1,  0,  0), #   3600  3600 WEST
        datetime(2002, 10, 27,  1,  0,  0), #      0     0 WET
        datetime(2003,  3, 30,  1,  0,  0), #   3600  3600 WEST
        datetime(2003, 10, 26,  1,  0,  0), #      0     0 WET
        datetime(2004,  3, 28,  1,  0,  0), #   3600  3600 WEST
        datetime(2004, 10, 31,  1,  0,  0), #      0     0 WET
        datetime(2005,  3, 27,  1,  0,  0), #   3600  3600 WEST
        datetime(2005, 10, 30,  1,  0,  0), #      0     0 WET
        datetime(2006,  3, 26,  1,  0,  0), #   3600  3600 WEST
        datetime(2006, 10, 29,  1,  0,  0), #      0     0 WET
        datetime(2007,  3, 25,  1,  0,  0), #   3600  3600 WEST
        datetime(2007, 10, 28,  1,  0,  0), #      0     0 WET
        datetime(2008,  3, 30,  1,  0,  0), #   3600  3600 WEST
        datetime(2008, 10, 26,  1,  0,  0), #      0     0 WET
        datetime(2009,  3, 29,  1,  0,  0), #   3600  3600 WEST
        datetime(2009, 10, 25,  1,  0,  0), #      0     0 WET
        datetime(2010,  3, 28,  1,  0,  0), #   3600  3600 WEST
        datetime(2010, 10, 31,  1,  0,  0), #      0     0 WET
        datetime(2011,  3, 27,  1,  0,  0), #   3600  3600 WEST
        datetime(2011, 10, 30,  1,  0,  0), #      0     0 WET
        datetime(2012,  3, 25,  1,  0,  0), #   3600  3600 WEST
        datetime(2012, 10, 28,  1,  0,  0), #      0     0 WET
        datetime(2013,  3, 31,  1,  0,  0), #   3600  3600 WEST
        datetime(2013, 10, 27,  1,  0,  0), #      0     0 WET
        datetime(2014,  3, 30,  1,  0,  0), #   3600  3600 WEST
        datetime(2014, 10, 26,  1,  0,  0), #      0     0 WET
        datetime(2015,  3, 29,  1,  0,  0), #   3600  3600 WEST
        datetime(2015, 10, 25,  1,  0,  0), #      0     0 WET
        datetime(2016,  3, 27,  1,  0,  0), #   3600  3600 WEST
        datetime(2016, 10, 30,  1,  0,  0), #      0     0 WET
        datetime(2017,  3, 26,  1,  0,  0), #   3600  3600 WEST
        datetime(2017, 10, 29,  1,  0,  0), #      0     0 WET
        datetime(2018,  3, 25,  1,  0,  0), #   3600  3600 WEST
        datetime(2018, 10, 28,  1,  0,  0), #      0     0 WET
        datetime(2019,  3, 31,  1,  0,  0), #   3600  3600 WEST
        datetime(2019, 10, 27,  1,  0,  0), #      0     0 WET
        datetime(2020,  3, 29,  1,  0,  0), #   3600  3600 WEST
        datetime(2020, 10, 25,  1,  0,  0), #      0     0 WET
        datetime(2021,  3, 28,  1,  0,  0), #   3600  3600 WEST
        datetime(2021, 10, 31,  1,  0,  0), #      0     0 WET
        datetime(2022,  3, 27,  1,  0,  0), #   3600  3600 WEST
        datetime(2022, 10, 30,  1,  0,  0), #      0     0 WET
        datetime(2023,  3, 26,  1,  0,  0), #   3600  3600 WEST
        datetime(2023, 10, 29,  1,  0,  0), #      0     0 WET
        datetime(2024,  3, 31,  1,  0,  0), #   3600  3600 WEST
        datetime(2024, 10, 27,  1,  0,  0), #      0     0 WET
        datetime(2025,  3, 30,  1,  0,  0), #   3600  3600 WEST
        datetime(2025, 10, 26,  1,  0,  0), #      0     0 WET
        datetime(2026,  3, 29,  1,  0,  0), #   3600  3600 WEST
        datetime(2026, 10, 25,  1,  0,  0), #      0     0 WET
        datetime(2027,  3, 28,  1,  0,  0), #   3600  3600 WEST
        datetime(2027, 10, 31,  1,  0,  0), #      0     0 WET
        datetime(2028,  3, 26,  1,  0,  0), #   3600  3600 WEST
        datetime(2028, 10, 29,  1,  0,  0), #      0     0 WET
        datetime(2029,  3, 25,  1,  0,  0), #   3600  3600 WEST
        datetime(2029, 10, 28,  1,  0,  0), #      0     0 WET
        datetime(2030,  3, 31,  1,  0,  0), #   3600  3600 WEST
        datetime(2030, 10, 27,  1,  0,  0), #      0     0 WET
        datetime(2031,  3, 30,  1,  0,  0), #   3600  3600 WEST
        datetime(2031, 10, 26,  1,  0,  0), #      0     0 WET
        datetime(2032,  3, 28,  1,  0,  0), #   3600  3600 WEST
        datetime(2032, 10, 31,  1,  0,  0), #      0     0 WET
        datetime(2033,  3, 27,  1,  0,  0), #   3600  3600 WEST
        datetime(2033, 10, 30,  1,  0,  0), #      0     0 WET
        datetime(2034,  3, 26,  1,  0,  0), #   3600  3600 WEST
        datetime(2034, 10, 29,  1,  0,  0), #      0     0 WET
        datetime(2035,  3, 25,  1,  0,  0), #   3600  3600 WEST
        datetime(2035, 10, 28,  1,  0,  0), #      0     0 WET
        datetime(2036,  3, 30,  1,  0,  0), #   3600  3600 WEST
        datetime(2036, 10, 26,  1,  0,  0), #      0     0 WET
        datetime(2037,  3, 29,  1,  0,  0), #   3600  3600 WEST
        datetime(2037, 10, 25,  1,  0,  0), #      0     0 WET
        ]

    _transition_info = [
        ttinfo( -2192,      0,  'LMT'),
        ttinfo(     0,      0,  'WET'),
        ttinfo(  3600,   3600, 'WEST'),
        ttinfo(     0,      0,  'WET'),
        ttinfo(  3600,   3600, 'WEST'),
        ttinfo(     0,      0,  'WET'),
        ttinfo(  3600,   3600, 'WEST'),
        ttinfo(     0,      0,  'WET'),
        ttinfo(  3600,   3600, 'WEST'),
        ttinfo(     0,      0,  'WET'),
        ttinfo(  3600,   3600, 'WEST'),
        ttinfo(     0,      0,  'WET'),
        ttinfo(  3600,   3600, 'WEST'),
        ttinfo(     0,      0,  'WET'),
        ttinfo(  3600,   3600, 'WEST'),
        ttinfo(     0,      0,  'WET'),
        ttinfo(  3600,   3600, 'WEST'),
        ttinfo(     0,      0,  'WET'),
        ttinfo(  3600,   3600, 'WEST'),
        ttinfo(     0,      0,  'WET'),
        ttinfo(  3600,   3600, 'WEST'),
        ttinfo(     0,      0,  'WET'),
        ttinfo(  3600,   3600, 'WEST'),
        ttinfo(     0,      0,  'WET'),
        ttinfo(  3600,   3600, 'WEST'),
        ttinfo(     0,      0,  'WET'),
        ttinfo(  3600,   3600, 'WEST'),
        ttinfo(     0,      0,  'WET'),
        ttinfo(  3600,   3600, 'WEST'),
        ttinfo(     0,      0,  'WET'),
        ttinfo(  3600,   3600, 'WEST'),
        ttinfo(     0,      0,  'WET'),
        ttinfo(  3600,   3600, 'WEST'),
        ttinfo(     0,      0,  'WET'),
        ttinfo(  3600,   3600, 'WEST'),
        ttinfo(     0,      0,  'WET'),
        ttinfo(  3600,   3600, 'WEST'),
        ttinfo(     0,      0,  'WET'),
        ttinfo(  3600,   3600, 'WEST'),
        ttinfo(     0,      0,  'WET'),
        ttinfo(  3600,   3600, 'WEST'),
        ttinfo(     0,      0,  'WET'),
        ttinfo(  3600,   3600, 'WEST'),
        ttinfo(     0,      0,  'WET'),
        ttinfo(  3600,   3600, 'WEST'),
        ttinfo(  7200,   3600, 'WEMT'),
        ttinfo(  3600,  -3600, 'WEST'),
        ttinfo(     0,      0,  'WET'),
        ttinfo(  3600,   3600, 'WEST'),
        ttinfo(  7200,   3600, 'WEMT'),
        ttinfo(  3600,  -3600, 'WEST'),
        ttinfo(     0,      0,  'WET'),
        ttinfo(  3600,   3600, 'WEST'),
        ttinfo(  7200,   3600, 'WEMT'),
        ttinfo(  3600,  -3600, 'WEST'),
        ttinfo(     0,      0,  'WET'),
        ttinfo(  3600,   3600, 'WEST'),
        ttinfo(  7200,   3600, 'WEMT'),
        ttinfo(  3600,  -3600, 'WEST'),
        ttinfo(     0,      0,  'WET'),
        ttinfo(  3600,   3600, 'WEST'),
        ttinfo(     0,      0,  'WET'),
        ttinfo(  3600,   3600, 'WEST'),
        ttinfo(     0,      0,  'WET'),
        ttinfo(  3600,   3600, 'WEST'),
        ttinfo(     0,      0,  'WET'),
        ttinfo(  3600,   3600, 'WEST'),
        ttinfo(     0,      0,  'WET'),
        ttinfo(  3600,   3600, 'WEST'),
        ttinfo(     0,      0,  'WET'),
        ttinfo(  3600,   3600, 'WEST'),
        ttinfo(     0,      0,  'WET'),
        ttinfo(  3600,   3600, 'WEST'),
        ttinfo(     0,      0,  'WET'),
        ttinfo(  3600,   3600, 'WEST'),
        ttinfo(     0,      0,  'WET'),
        ttinfo(  3600,   3600, 'WEST'),
        ttinfo(     0,      0,  'WET'),
        ttinfo(  3600,   3600, 'WEST'),
        ttinfo(     0,      0,  'WET'),
        ttinfo(  3600,   3600, 'WEST'),
        ttinfo(     0,      0,  'WET'),
        ttinfo(  3600,   3600, 'WEST'),
        ttinfo(     0,      0,  'WET'),
        ttinfo(  3600,   3600, 'WEST'),
        ttinfo(     0,      0,  'WET'),
        ttinfo(  3600,   3600, 'WEST'),
        ttinfo(     0,      0,  'WET'),
        ttinfo(  3600,   3600, 'WEST'),
        ttinfo(     0,      0,  'WET'),
        ttinfo(  3600,   3600, 'WEST'),
        ttinfo(     0,      0,  'WET'),
        ttinfo(  3600,   3600, 'WEST'),
        ttinfo(     0,      0,  'WET'),
        ttinfo(  3600,   3600, 'WEST'),
        ttinfo(     0,      0,  'WET'),
        ttinfo(  3600,   3600, 'WEST'),
        ttinfo(     0,      0,  'WET'),
        ttinfo(  3600,      0,  'CET'),
        ttinfo(     0,      0,  'WET'),
        ttinfo(  3600,   3600, 'WEST'),
        ttinfo(     0,      0,  'WET'),
        ttinfo(  3600,   3600, 'WEST'),
        ttinfo(     0,      0,  'WET'),
        ttinfo(  3600,   3600, 'WEST'),
        ttinfo(     0,      0,  'WET'),
        ttinfo(  3600,   3600, 'WEST'),
        ttinfo(     0,      0,  'WET'),
        ttinfo(  3600,   3600, 'WEST'),
        ttinfo(     0,      0,  'WET'),
        ttinfo(  3600,   3600, 'WEST'),
        ttinfo(     0,      0,  'WET'),
        ttinfo(  3600,   3600, 'WEST'),
        ttinfo(     0,      0,  'WET'),
        ttinfo(  3600,   3600, 'WEST'),
        ttinfo(     0,      0,  'WET'),
        ttinfo(  3600,   3600, 'WEST'),
        ttinfo(     0,      0,  'WET'),
        ttinfo(  3600,   3600, 'WEST'),
        ttinfo(     0,      0,  'WET'),
        ttinfo(  3600,   3600, 'WEST'),
        ttinfo(     0,      0,  'WET'),
        ttinfo(  3600,   3600, 'WEST'),
        ttinfo(     0,      0,  'WET'),
        ttinfo(  3600,   3600, 'WEST'),
        ttinfo(     0,      0,  'WET'),
        ttinfo(  3600,   3600, 'WEST'),
        ttinfo(     0,      0,  'WET'),
        ttinfo(  3600,   3600, 'WEST'),
        ttinfo(     0,      0,  'WET'),
        ttinfo(  3600,   3600, 'WEST'),
        ttinfo(  3600,      0,  'CET'),
        ttinfo(  7200,   3600, 'CEST'),
        ttinfo(  3600,      0,  'CET'),
        ttinfo(  7200,   3600, 'CEST'),
        ttinfo(  3600,      0,  'CET'),
        ttinfo(  7200,   3600, 'CEST'),
        ttinfo(  3600,      0,  'CET'),
        ttinfo(  3600,      0, 'WEST'),
        ttinfo(     0,      0,  'WET'),
        ttinfo(  3600,   3600, 'WEST'),
        ttinfo(     0,      0,  'WET'),
        ttinfo(  3600,   3600, 'WEST'),
        ttinfo(     0,      0,  'WET'),
        ttinfo(  3600,   3600, 'WEST'),
        ttinfo(     0,      0,  'WET'),
        ttinfo(  3600,   3600, 'WEST'),
        ttinfo(     0,      0,  'WET'),
        ttinfo(  3600,   3600, 'WEST'),
        ttinfo(     0,      0,  'WET'),
        ttinfo(  3600,   3600, 'WEST'),
        ttinfo(     0,      0,  'WET'),
        ttinfo(  3600,   3600, 'WEST'),
        ttinfo(     0,      0,  'WET'),
        ttinfo(  3600,   3600, 'WEST'),
        ttinfo(     0,      0,  'WET'),
        ttinfo(  3600,   3600, 'WEST'),
        ttinfo(     0,      0,  'WET'),
        ttinfo(  3600,   3600, 'WEST'),
        ttinfo(     0,      0,  'WET'),
        ttinfo(  3600,   3600, 'WEST'),
        ttinfo(     0,      0,  'WET'),
        ttinfo(  3600,   3600, 'WEST'),
        ttinfo(     0,      0,  'WET'),
        ttinfo(  3600,   3600, 'WEST'),
        ttinfo(     0,      0,  'WET'),
        ttinfo(  3600,   3600, 'WEST'),
        ttinfo(     0,      0,  'WET'),
        ttinfo(  3600,   3600, 'WEST'),
        ttinfo(     0,      0,  'WET'),
        ttinfo(  3600,   3600, 'WEST'),
        ttinfo(     0,      0,  'WET'),
        ttinfo(  3600,   3600, 'WEST'),
        ttinfo(     0,      0,  'WET'),
        ttinfo(  3600,   3600, 'WEST'),
        ttinfo(     0,      0,  'WET'),
        ttinfo(  3600,   3600, 'WEST'),
        ttinfo(     0,      0,  'WET'),
        ttinfo(  3600,   3600, 'WEST'),
        ttinfo(     0,      0,  'WET'),
        ttinfo(  3600,   3600, 'WEST'),
        ttinfo(     0,      0,  'WET'),
        ttinfo(  3600,   3600, 'WEST'),
        ttinfo(     0,      0,  'WET'),
        ttinfo(  3600,   3600, 'WEST'),
        ttinfo(     0,      0,  'WET'),
        ttinfo(  3600,   3600, 'WEST'),
        ttinfo(     0,      0,  'WET'),
        ttinfo(  3600,   3600, 'WEST'),
        ttinfo(     0,      0,  'WET'),
        ttinfo(  3600,   3600, 'WEST'),
        ttinfo(     0,      0,  'WET'),
        ttinfo(  3600,   3600, 'WEST'),
        ttinfo(     0,      0,  'WET'),
        ttinfo(  3600,   3600, 'WEST'),
        ttinfo(     0,      0,  'WET'),
        ttinfo(  3600,   3600, 'WEST'),
        ttinfo(     0,      0,  'WET'),
        ttinfo(  3600,   3600, 'WEST'),
        ttinfo(     0,      0,  'WET'),
        ttinfo(  3600,   3600, 'WEST'),
        ttinfo(     0,      0,  'WET'),
        ttinfo(  3600,   3600, 'WEST'),
        ttinfo(     0,      0,  'WET'),
        ttinfo(  3600,   3600, 'WEST'),
        ttinfo(     0,      0,  'WET'),
        ttinfo(  3600,   3600, 'WEST'),
        ttinfo(     0,      0,  'WET'),
        ttinfo(  3600,   3600, 'WEST'),
        ttinfo(     0,      0,  'WET'),
        ttinfo(  3600,   3600, 'WEST'),
        ttinfo(     0,      0,  'WET'),
        ttinfo(  3600,   3600, 'WEST'),
        ttinfo(     0,      0,  'WET'),
        ttinfo(  3600,   3600, 'WEST'),
        ttinfo(     0,      0,  'WET'),
        ttinfo(  3600,   3600, 'WEST'),
        ttinfo(     0,      0,  'WET'),
        ttinfo(  3600,   3600, 'WEST'),
        ttinfo(     0,      0,  'WET'),
        ttinfo(  3600,   3600, 'WEST'),
        ttinfo(     0,      0,  'WET'),
        ]

Portugal = Portugal() # Singleton

