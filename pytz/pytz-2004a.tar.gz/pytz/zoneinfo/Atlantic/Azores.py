'''
tzinfo timezone information for Atlantic/Azores.

Generated from the Olson timezone database:
    ftp://elsie.nci.nih.gov/pub/tz*.tar.gz
'''

from pytz.tzinfo import DstTzInfo
from pytz.tzinfo import memorized_datetime as datetime
from pytz.tzinfo import memorized_ttinfo as ttinfo

class Azores(DstTzInfo):
    '''Atlantic/Azores timezone definition. See datetime.tzinfo for details'''

    _zone = 'Atlantic/Azores'

    _utc_transition_times = [
        datetime(   1,  1,  1,  0,  0,  0), #  -6872     0 HMT
        datetime(1911,  5, 24,  1, 54, 32), #  -7200     0 AZOT
        datetime(1916,  6, 18,  1,  0,  0), #  -3600  3600 AZOST
        datetime(1916, 11,  1,  2,  0,  0), #  -7200     0 AZOT
        datetime(1917,  3,  1,  1,  0,  0), #  -3600  3600 AZOST
        datetime(1917, 10, 15,  1,  0,  0), #  -7200     0 AZOT
        datetime(1918,  3,  2,  1,  0,  0), #  -3600  3600 AZOST
        datetime(1918, 10, 15,  1,  0,  0), #  -7200     0 AZOT
        datetime(1919,  3,  1,  1,  0,  0), #  -3600  3600 AZOST
        datetime(1919, 10, 15,  1,  0,  0), #  -7200     0 AZOT
        datetime(1920,  3,  1,  1,  0,  0), #  -3600  3600 AZOST
        datetime(1920, 10, 15,  1,  0,  0), #  -7200     0 AZOT
        datetime(1921,  3,  1,  1,  0,  0), #  -3600  3600 AZOST
        datetime(1921, 10, 15,  1,  0,  0), #  -7200     0 AZOT
        datetime(1924,  4, 17,  1,  0,  0), #  -3600  3600 AZOST
        datetime(1924, 10, 15,  1,  0,  0), #  -7200     0 AZOT
        datetime(1926,  4, 18,  1,  0,  0), #  -3600  3600 AZOST
        datetime(1926, 10,  3,  1,  0,  0), #  -7200     0 AZOT
        datetime(1927,  4, 10,  1,  0,  0), #  -3600  3600 AZOST
        datetime(1927, 10,  2,  1,  0,  0), #  -7200     0 AZOT
        datetime(1928,  4, 15,  1,  0,  0), #  -3600  3600 AZOST
        datetime(1928, 10,  7,  1,  0,  0), #  -7200     0 AZOT
        datetime(1929,  4, 21,  1,  0,  0), #  -3600  3600 AZOST
        datetime(1929, 10,  6,  1,  0,  0), #  -7200     0 AZOT
        datetime(1931,  4, 19,  1,  0,  0), #  -3600  3600 AZOST
        datetime(1931, 10,  4,  1,  0,  0), #  -7200     0 AZOT
        datetime(1932,  4,  3,  1,  0,  0), #  -3600  3600 AZOST
        datetime(1932, 10,  2,  1,  0,  0), #  -7200     0 AZOT
        datetime(1934,  4,  8,  1,  0,  0), #  -3600  3600 AZOST
        datetime(1934, 10,  7,  1,  0,  0), #  -7200     0 AZOT
        datetime(1935,  3, 31,  1,  0,  0), #  -3600  3600 AZOST
        datetime(1935, 10,  6,  1,  0,  0), #  -7200     0 AZOT
        datetime(1936,  4, 19,  1,  0,  0), #  -3600  3600 AZOST
        datetime(1936, 10,  4,  1,  0,  0), #  -7200     0 AZOT
        datetime(1937,  4,  4,  1,  0,  0), #  -3600  3600 AZOST
        datetime(1937, 10,  3,  1,  0,  0), #  -7200     0 AZOT
        datetime(1938,  3, 27,  1,  0,  0), #  -3600  3600 AZOST
        datetime(1938, 10,  2,  1,  0,  0), #  -7200     0 AZOT
        datetime(1939,  4, 16,  1,  0,  0), #  -3600  3600 AZOST
        datetime(1939, 11, 19,  1,  0,  0), #  -7200     0 AZOT
        datetime(1940,  2, 25,  1,  0,  0), #  -3600  3600 AZOST
        datetime(1940, 10,  6,  1,  0,  0), #  -7200     0 AZOT
        datetime(1941,  4,  6,  1,  0,  0), #  -3600  3600 AZOST
        datetime(1941, 10,  6,  1,  0,  0), #  -7200     0 AZOT
        datetime(1942,  3, 15,  1,  0,  0), #  -3600  3600 AZOST
        datetime(1942,  4, 26,  0,  0,  0), #      0  3600 AZOMT
        datetime(1942,  8, 16,  0,  0,  0), #  -3600 -3600 AZOST
        datetime(1942, 10, 25,  1,  0,  0), #  -7200     0 AZOT
        datetime(1943,  3, 14,  1,  0,  0), #  -3600  3600 AZOST
        datetime(1943,  4, 18,  0,  0,  0), #      0  3600 AZOMT
        datetime(1943,  8, 29,  0,  0,  0), #  -3600 -3600 AZOST
        datetime(1943, 10, 31,  1,  0,  0), #  -7200     0 AZOT
        datetime(1944,  3, 12,  1,  0,  0), #  -3600  3600 AZOST
        datetime(1944,  4, 23,  0,  0,  0), #      0  3600 AZOMT
        datetime(1944,  8, 27,  0,  0,  0), #  -3600 -3600 AZOST
        datetime(1944, 10, 29,  1,  0,  0), #  -7200     0 AZOT
        datetime(1945,  3, 11,  1,  0,  0), #  -3600  3600 AZOST
        datetime(1945,  4, 22,  0,  0,  0), #      0  3600 AZOMT
        datetime(1945,  8, 26,  0,  0,  0), #  -3600 -3600 AZOST
        datetime(1945, 10, 28,  1,  0,  0), #  -7200     0 AZOT
        datetime(1946,  4,  7,  1,  0,  0), #  -3600  3600 AZOST
        datetime(1946, 10,  6,  1,  0,  0), #  -7200     0 AZOT
        datetime(1947,  4,  6,  4,  0,  0), #  -3600  3600 AZOST
        datetime(1947, 10,  5,  4,  0,  0), #  -7200     0 AZOT
        datetime(1948,  4,  4,  4,  0,  0), #  -3600  3600 AZOST
        datetime(1948, 10,  3,  4,  0,  0), #  -7200     0 AZOT
        datetime(1949,  4,  3,  4,  0,  0), #  -3600  3600 AZOST
        datetime(1949, 10,  2,  4,  0,  0), #  -7200     0 AZOT
        datetime(1951,  4,  1,  4,  0,  0), #  -3600  3600 AZOST
        datetime(1951, 10,  7,  4,  0,  0), #  -7200     0 AZOT
        datetime(1952,  4,  6,  4,  0,  0), #  -3600  3600 AZOST
        datetime(1952, 10,  5,  4,  0,  0), #  -7200     0 AZOT
        datetime(1953,  4,  5,  4,  0,  0), #  -3600  3600 AZOST
        datetime(1953, 10,  4,  4,  0,  0), #  -7200     0 AZOT
        datetime(1954,  4,  4,  4,  0,  0), #  -3600  3600 AZOST
        datetime(1954, 10,  3,  4,  0,  0), #  -7200     0 AZOT
        datetime(1955,  4,  3,  4,  0,  0), #  -3600  3600 AZOST
        datetime(1955, 10,  2,  4,  0,  0), #  -7200     0 AZOT
        datetime(1956,  4,  1,  4,  0,  0), #  -3600  3600 AZOST
        datetime(1956, 10,  7,  4,  0,  0), #  -7200     0 AZOT
        datetime(1957,  4,  7,  4,  0,  0), #  -3600  3600 AZOST
        datetime(1957, 10,  6,  4,  0,  0), #  -7200     0 AZOT
        datetime(1958,  4,  6,  4,  0,  0), #  -3600  3600 AZOST
        datetime(1958, 10,  5,  4,  0,  0), #  -7200     0 AZOT
        datetime(1959,  4,  5,  4,  0,  0), #  -3600  3600 AZOST
        datetime(1959, 10,  4,  4,  0,  0), #  -7200     0 AZOT
        datetime(1960,  4,  3,  4,  0,  0), #  -3600  3600 AZOST
        datetime(1960, 10,  2,  4,  0,  0), #  -7200     0 AZOT
        datetime(1961,  4,  2,  4,  0,  0), #  -3600  3600 AZOST
        datetime(1961, 10,  1,  4,  0,  0), #  -7200     0 AZOT
        datetime(1962,  4,  1,  4,  0,  0), #  -3600  3600 AZOST
        datetime(1962, 10,  7,  4,  0,  0), #  -7200     0 AZOT
        datetime(1963,  4,  7,  4,  0,  0), #  -3600  3600 AZOST
        datetime(1963, 10,  6,  4,  0,  0), #  -7200     0 AZOT
        datetime(1964,  4,  5,  4,  0,  0), #  -3600  3600 AZOST
        datetime(1964, 10,  4,  4,  0,  0), #  -7200     0 AZOT
        datetime(1965,  4,  4,  4,  0,  0), #  -3600  3600 AZOST
        datetime(1965, 10,  3,  4,  0,  0), #  -7200     0 AZOT
        datetime(1966,  4,  3,  4,  0,  0), #  -3600     0 AZOT
        datetime(1977,  3, 27,  1,  0,  0), #      0  3600 AZOST
        datetime(1977,  9, 25,  1,  0,  0), #  -3600     0 AZOT
        datetime(1978,  4,  2,  1,  0,  0), #      0  3600 AZOST
        datetime(1978, 10,  1,  1,  0,  0), #  -3600     0 AZOT
        datetime(1979,  4,  1,  1,  0,  0), #      0  3600 AZOST
        datetime(1979,  9, 30,  2,  0,  0), #  -3600     0 AZOT
        datetime(1980,  3, 30,  1,  0,  0), #      0  3600 AZOST
        datetime(1980,  9, 28,  2,  0,  0), #  -3600     0 AZOT
        datetime(1981,  3, 29,  2,  0,  0), #      0  3600 AZOST
        datetime(1981,  9, 27,  2,  0,  0), #  -3600     0 AZOT
        datetime(1982,  3, 28,  2,  0,  0), #      0  3600 AZOST
        datetime(1982,  9, 26,  2,  0,  0), #  -3600     0 AZOT
        datetime(1983,  3, 27,  3,  0,  0), #      0  3600 AZOST
        datetime(1983,  9, 25,  2,  0,  0), #  -3600     0 AZOT
        datetime(1984,  3, 25,  2,  0,  0), #      0  3600 AZOST
        datetime(1984,  9, 30,  2,  0,  0), #  -3600     0 AZOT
        datetime(1985,  3, 31,  2,  0,  0), #      0  3600 AZOST
        datetime(1985,  9, 29,  2,  0,  0), #  -3600     0 AZOT
        datetime(1986,  3, 30,  2,  0,  0), #      0  3600 AZOST
        datetime(1986,  9, 28,  2,  0,  0), #  -3600     0 AZOT
        datetime(1987,  3, 29,  2,  0,  0), #      0  3600 AZOST
        datetime(1987,  9, 27,  2,  0,  0), #  -3600     0 AZOT
        datetime(1988,  3, 27,  2,  0,  0), #      0  3600 AZOST
        datetime(1988,  9, 25,  2,  0,  0), #  -3600     0 AZOT
        datetime(1989,  3, 26,  2,  0,  0), #      0  3600 AZOST
        datetime(1989,  9, 24,  2,  0,  0), #  -3600     0 AZOT
        datetime(1990,  3, 25,  2,  0,  0), #      0  3600 AZOST
        datetime(1990,  9, 30,  2,  0,  0), #  -3600     0 AZOT
        datetime(1991,  3, 31,  2,  0,  0), #      0  3600 AZOST
        datetime(1991,  9, 29,  2,  0,  0), #  -3600     0 AZOT
        datetime(1992,  3, 29,  2,  0,  0), #      0  3600 AZOST
        datetime(1992,  9, 27,  2,  0,  0), #      0     0 WET
        datetime(1993,  3, 28,  1,  0,  0), #      0     0 AZOST
        datetime(1993,  9, 26,  1,  0,  0), #  -3600     0 AZOT
        datetime(1994,  3, 27,  1,  0,  0), #      0  3600 AZOST
        datetime(1994,  9, 25,  1,  0,  0), #  -3600     0 AZOT
        datetime(1995,  3, 26,  1,  0,  0), #      0  3600 AZOST
        datetime(1995,  9, 24,  1,  0,  0), #  -3600     0 AZOT
        datetime(1996,  3, 31,  1,  0,  0), #      0  3600 AZOST
        datetime(1996, 10, 27,  1,  0,  0), #  -3600     0 AZOT
        datetime(1997,  3, 30,  1,  0,  0), #      0  3600 AZOST
        datetime(1997, 10, 26,  1,  0,  0), #  -3600     0 AZOT
        datetime(1998,  3, 29,  1,  0,  0), #      0  3600 AZOST
        datetime(1998, 10, 25,  1,  0,  0), #  -3600     0 AZOT
        datetime(1999,  3, 28,  1,  0,  0), #      0  3600 AZOST
        datetime(1999, 10, 31,  1,  0,  0), #  -3600     0 AZOT
        datetime(2000,  3, 26,  1,  0,  0), #      0  3600 AZOST
        datetime(2000, 10, 29,  1,  0,  0), #  -3600     0 AZOT
        datetime(2001,  3, 25,  1,  0,  0), #      0  3600 AZOST
        datetime(2001, 10, 28,  1,  0,  0), #  -3600     0 AZOT
        datetime(2002,  3, 31,  1,  0,  0), #      0  3600 AZOST
        datetime(2002, 10, 27,  1,  0,  0), #  -3600     0 AZOT
        datetime(2003,  3, 30,  1,  0,  0), #      0  3600 AZOST
        datetime(2003, 10, 26,  1,  0,  0), #  -3600     0 AZOT
        datetime(2004,  3, 28,  1,  0,  0), #      0  3600 AZOST
        datetime(2004, 10, 31,  1,  0,  0), #  -3600     0 AZOT
        datetime(2005,  3, 27,  1,  0,  0), #      0  3600 AZOST
        datetime(2005, 10, 30,  1,  0,  0), #  -3600     0 AZOT
        datetime(2006,  3, 26,  1,  0,  0), #      0  3600 AZOST
        datetime(2006, 10, 29,  1,  0,  0), #  -3600     0 AZOT
        datetime(2007,  3, 25,  1,  0,  0), #      0  3600 AZOST
        datetime(2007, 10, 28,  1,  0,  0), #  -3600     0 AZOT
        datetime(2008,  3, 30,  1,  0,  0), #      0  3600 AZOST
        datetime(2008, 10, 26,  1,  0,  0), #  -3600     0 AZOT
        datetime(2009,  3, 29,  1,  0,  0), #      0  3600 AZOST
        datetime(2009, 10, 25,  1,  0,  0), #  -3600     0 AZOT
        datetime(2010,  3, 28,  1,  0,  0), #      0  3600 AZOST
        datetime(2010, 10, 31,  1,  0,  0), #  -3600     0 AZOT
        datetime(2011,  3, 27,  1,  0,  0), #      0  3600 AZOST
        datetime(2011, 10, 30,  1,  0,  0), #  -3600     0 AZOT
        datetime(2012,  3, 25,  1,  0,  0), #      0  3600 AZOST
        datetime(2012, 10, 28,  1,  0,  0), #  -3600     0 AZOT
        datetime(2013,  3, 31,  1,  0,  0), #      0  3600 AZOST
        datetime(2013, 10, 27,  1,  0,  0), #  -3600     0 AZOT
        datetime(2014,  3, 30,  1,  0,  0), #      0  3600 AZOST
        datetime(2014, 10, 26,  1,  0,  0), #  -3600     0 AZOT
        datetime(2015,  3, 29,  1,  0,  0), #      0  3600 AZOST
        datetime(2015, 10, 25,  1,  0,  0), #  -3600     0 AZOT
        datetime(2016,  3, 27,  1,  0,  0), #      0  3600 AZOST
        datetime(2016, 10, 30,  1,  0,  0), #  -3600     0 AZOT
        datetime(2017,  3, 26,  1,  0,  0), #      0  3600 AZOST
        datetime(2017, 10, 29,  1,  0,  0), #  -3600     0 AZOT
        datetime(2018,  3, 25,  1,  0,  0), #      0  3600 AZOST
        datetime(2018, 10, 28,  1,  0,  0), #  -3600     0 AZOT
        datetime(2019,  3, 31,  1,  0,  0), #      0  3600 AZOST
        datetime(2019, 10, 27,  1,  0,  0), #  -3600     0 AZOT
        datetime(2020,  3, 29,  1,  0,  0), #      0  3600 AZOST
        datetime(2020, 10, 25,  1,  0,  0), #  -3600     0 AZOT
        datetime(2021,  3, 28,  1,  0,  0), #      0  3600 AZOST
        datetime(2021, 10, 31,  1,  0,  0), #  -3600     0 AZOT
        datetime(2022,  3, 27,  1,  0,  0), #      0  3600 AZOST
        datetime(2022, 10, 30,  1,  0,  0), #  -3600     0 AZOT
        datetime(2023,  3, 26,  1,  0,  0), #      0  3600 AZOST
        datetime(2023, 10, 29,  1,  0,  0), #  -3600     0 AZOT
        datetime(2024,  3, 31,  1,  0,  0), #      0  3600 AZOST
        datetime(2024, 10, 27,  1,  0,  0), #  -3600     0 AZOT
        datetime(2025,  3, 30,  1,  0,  0), #      0  3600 AZOST
        datetime(2025, 10, 26,  1,  0,  0), #  -3600     0 AZOT
        datetime(2026,  3, 29,  1,  0,  0), #      0  3600 AZOST
        datetime(2026, 10, 25,  1,  0,  0), #  -3600     0 AZOT
        datetime(2027,  3, 28,  1,  0,  0), #      0  3600 AZOST
        datetime(2027, 10, 31,  1,  0,  0), #  -3600     0 AZOT
        datetime(2028,  3, 26,  1,  0,  0), #      0  3600 AZOST
        datetime(2028, 10, 29,  1,  0,  0), #  -3600     0 AZOT
        datetime(2029,  3, 25,  1,  0,  0), #      0  3600 AZOST
        datetime(2029, 10, 28,  1,  0,  0), #  -3600     0 AZOT
        datetime(2030,  3, 31,  1,  0,  0), #      0  3600 AZOST
        datetime(2030, 10, 27,  1,  0,  0), #  -3600     0 AZOT
        datetime(2031,  3, 30,  1,  0,  0), #      0  3600 AZOST
        datetime(2031, 10, 26,  1,  0,  0), #  -3600     0 AZOT
        datetime(2032,  3, 28,  1,  0,  0), #      0  3600 AZOST
        datetime(2032, 10, 31,  1,  0,  0), #  -3600     0 AZOT
        datetime(2033,  3, 27,  1,  0,  0), #      0  3600 AZOST
        datetime(2033, 10, 30,  1,  0,  0), #  -3600     0 AZOT
        datetime(2034,  3, 26,  1,  0,  0), #      0  3600 AZOST
        datetime(2034, 10, 29,  1,  0,  0), #  -3600     0 AZOT
        datetime(2035,  3, 25,  1,  0,  0), #      0  3600 AZOST
        datetime(2035, 10, 28,  1,  0,  0), #  -3600     0 AZOT
        datetime(2036,  3, 30,  1,  0,  0), #      0  3600 AZOST
        datetime(2036, 10, 26,  1,  0,  0), #  -3600     0 AZOT
        datetime(2037,  3, 29,  1,  0,  0), #      0  3600 AZOST
        datetime(2037, 10, 25,  1,  0,  0), #  -3600     0 AZOT
        ]

    _transition_info = [
        ttinfo( -6872,      0,  'HMT'),
        ttinfo( -7200,      0, 'AZOT'),
        ttinfo( -3600,   3600, 'AZOST'),
        ttinfo( -7200,      0, 'AZOT'),
        ttinfo( -3600,   3600, 'AZOST'),
        ttinfo( -7200,      0, 'AZOT'),
        ttinfo( -3600,   3600, 'AZOST'),
        ttinfo( -7200,      0, 'AZOT'),
        ttinfo( -3600,   3600, 'AZOST'),
        ttinfo( -7200,      0, 'AZOT'),
        ttinfo( -3600,   3600, 'AZOST'),
        ttinfo( -7200,      0, 'AZOT'),
        ttinfo( -3600,   3600, 'AZOST'),
        ttinfo( -7200,      0, 'AZOT'),
        ttinfo( -3600,   3600, 'AZOST'),
        ttinfo( -7200,      0, 'AZOT'),
        ttinfo( -3600,   3600, 'AZOST'),
        ttinfo( -7200,      0, 'AZOT'),
        ttinfo( -3600,   3600, 'AZOST'),
        ttinfo( -7200,      0, 'AZOT'),
        ttinfo( -3600,   3600, 'AZOST'),
        ttinfo( -7200,      0, 'AZOT'),
        ttinfo( -3600,   3600, 'AZOST'),
        ttinfo( -7200,      0, 'AZOT'),
        ttinfo( -3600,   3600, 'AZOST'),
        ttinfo( -7200,      0, 'AZOT'),
        ttinfo( -3600,   3600, 'AZOST'),
        ttinfo( -7200,      0, 'AZOT'),
        ttinfo( -3600,   3600, 'AZOST'),
        ttinfo( -7200,      0, 'AZOT'),
        ttinfo( -3600,   3600, 'AZOST'),
        ttinfo( -7200,      0, 'AZOT'),
        ttinfo( -3600,   3600, 'AZOST'),
        ttinfo( -7200,      0, 'AZOT'),
        ttinfo( -3600,   3600, 'AZOST'),
        ttinfo( -7200,      0, 'AZOT'),
        ttinfo( -3600,   3600, 'AZOST'),
        ttinfo( -7200,      0, 'AZOT'),
        ttinfo( -3600,   3600, 'AZOST'),
        ttinfo( -7200,      0, 'AZOT'),
        ttinfo( -3600,   3600, 'AZOST'),
        ttinfo( -7200,      0, 'AZOT'),
        ttinfo( -3600,   3600, 'AZOST'),
        ttinfo( -7200,      0, 'AZOT'),
        ttinfo( -3600,   3600, 'AZOST'),
        ttinfo(     0,   3600, 'AZOMT'),
        ttinfo( -3600,  -3600, 'AZOST'),
        ttinfo( -7200,      0, 'AZOT'),
        ttinfo( -3600,   3600, 'AZOST'),
        ttinfo(     0,   3600, 'AZOMT'),
        ttinfo( -3600,  -3600, 'AZOST'),
        ttinfo( -7200,      0, 'AZOT'),
        ttinfo( -3600,   3600, 'AZOST'),
        ttinfo(     0,   3600, 'AZOMT'),
        ttinfo( -3600,  -3600, 'AZOST'),
        ttinfo( -7200,      0, 'AZOT'),
        ttinfo( -3600,   3600, 'AZOST'),
        ttinfo(     0,   3600, 'AZOMT'),
        ttinfo( -3600,  -3600, 'AZOST'),
        ttinfo( -7200,      0, 'AZOT'),
        ttinfo( -3600,   3600, 'AZOST'),
        ttinfo( -7200,      0, 'AZOT'),
        ttinfo( -3600,   3600, 'AZOST'),
        ttinfo( -7200,      0, 'AZOT'),
        ttinfo( -3600,   3600, 'AZOST'),
        ttinfo( -7200,      0, 'AZOT'),
        ttinfo( -3600,   3600, 'AZOST'),
        ttinfo( -7200,      0, 'AZOT'),
        ttinfo( -3600,   3600, 'AZOST'),
        ttinfo( -7200,      0, 'AZOT'),
        ttinfo( -3600,   3600, 'AZOST'),
        ttinfo( -7200,      0, 'AZOT'),
        ttinfo( -3600,   3600, 'AZOST'),
        ttinfo( -7200,      0, 'AZOT'),
        ttinfo( -3600,   3600, 'AZOST'),
        ttinfo( -7200,      0, 'AZOT'),
        ttinfo( -3600,   3600, 'AZOST'),
        ttinfo( -7200,      0, 'AZOT'),
        ttinfo( -3600,   3600, 'AZOST'),
        ttinfo( -7200,      0, 'AZOT'),
        ttinfo( -3600,   3600, 'AZOST'),
        ttinfo( -7200,      0, 'AZOT'),
        ttinfo( -3600,   3600, 'AZOST'),
        ttinfo( -7200,      0, 'AZOT'),
        ttinfo( -3600,   3600, 'AZOST'),
        ttinfo( -7200,      0, 'AZOT'),
        ttinfo( -3600,   3600, 'AZOST'),
        ttinfo( -7200,      0, 'AZOT'),
        ttinfo( -3600,   3600, 'AZOST'),
        ttinfo( -7200,      0, 'AZOT'),
        ttinfo( -3600,   3600, 'AZOST'),
        ttinfo( -7200,      0, 'AZOT'),
        ttinfo( -3600,   3600, 'AZOST'),
        ttinfo( -7200,      0, 'AZOT'),
        ttinfo( -3600,   3600, 'AZOST'),
        ttinfo( -7200,      0, 'AZOT'),
        ttinfo( -3600,   3600, 'AZOST'),
        ttinfo( -7200,      0, 'AZOT'),
        ttinfo( -3600,      0, 'AZOT'),
        ttinfo(     0,   3600, 'AZOST'),
        ttinfo( -3600,      0, 'AZOT'),
        ttinfo(     0,   3600, 'AZOST'),
        ttinfo( -3600,      0, 'AZOT'),
        ttinfo(     0,   3600, 'AZOST'),
        ttinfo( -3600,      0, 'AZOT'),
        ttinfo(     0,   3600, 'AZOST'),
        ttinfo( -3600,      0, 'AZOT'),
        ttinfo(     0,   3600, 'AZOST'),
        ttinfo( -3600,      0, 'AZOT'),
        ttinfo(     0,   3600, 'AZOST'),
        ttinfo( -3600,      0, 'AZOT'),
        ttinfo(     0,   3600, 'AZOST'),
        ttinfo( -3600,      0, 'AZOT'),
        ttinfo(     0,   3600, 'AZOST'),
        ttinfo( -3600,      0, 'AZOT'),
        ttinfo(     0,   3600, 'AZOST'),
        ttinfo( -3600,      0, 'AZOT'),
        ttinfo(     0,   3600, 'AZOST'),
        ttinfo( -3600,      0, 'AZOT'),
        ttinfo(     0,   3600, 'AZOST'),
        ttinfo( -3600,      0, 'AZOT'),
        ttinfo(     0,   3600, 'AZOST'),
        ttinfo( -3600,      0, 'AZOT'),
        ttinfo(     0,   3600, 'AZOST'),
        ttinfo( -3600,      0, 'AZOT'),
        ttinfo(     0,   3600, 'AZOST'),
        ttinfo( -3600,      0, 'AZOT'),
        ttinfo(     0,   3600, 'AZOST'),
        ttinfo( -3600,      0, 'AZOT'),
        ttinfo(     0,   3600, 'AZOST'),
        ttinfo(     0,      0,  'WET'),
        ttinfo(     0,      0, 'AZOST'),
        ttinfo( -3600,      0, 'AZOT'),
        ttinfo(     0,   3600, 'AZOST'),
        ttinfo( -3600,      0, 'AZOT'),
        ttinfo(     0,   3600, 'AZOST'),
        ttinfo( -3600,      0, 'AZOT'),
        ttinfo(     0,   3600, 'AZOST'),
        ttinfo( -3600,      0, 'AZOT'),
        ttinfo(     0,   3600, 'AZOST'),
        ttinfo( -3600,      0, 'AZOT'),
        ttinfo(     0,   3600, 'AZOST'),
        ttinfo( -3600,      0, 'AZOT'),
        ttinfo(     0,   3600, 'AZOST'),
        ttinfo( -3600,      0, 'AZOT'),
        ttinfo(     0,   3600, 'AZOST'),
        ttinfo( -3600,      0, 'AZOT'),
        ttinfo(     0,   3600, 'AZOST'),
        ttinfo( -3600,      0, 'AZOT'),
        ttinfo(     0,   3600, 'AZOST'),
        ttinfo( -3600,      0, 'AZOT'),
        ttinfo(     0,   3600, 'AZOST'),
        ttinfo( -3600,      0, 'AZOT'),
        ttinfo(     0,   3600, 'AZOST'),
        ttinfo( -3600,      0, 'AZOT'),
        ttinfo(     0,   3600, 'AZOST'),
        ttinfo( -3600,      0, 'AZOT'),
        ttinfo(     0,   3600, 'AZOST'),
        ttinfo( -3600,      0, 'AZOT'),
        ttinfo(     0,   3600, 'AZOST'),
        ttinfo( -3600,      0, 'AZOT'),
        ttinfo(     0,   3600, 'AZOST'),
        ttinfo( -3600,      0, 'AZOT'),
        ttinfo(     0,   3600, 'AZOST'),
        ttinfo( -3600,      0, 'AZOT'),
        ttinfo(     0,   3600, 'AZOST'),
        ttinfo( -3600,      0, 'AZOT'),
        ttinfo(     0,   3600, 'AZOST'),
        ttinfo( -3600,      0, 'AZOT'),
        ttinfo(     0,   3600, 'AZOST'),
        ttinfo( -3600,      0, 'AZOT'),
        ttinfo(     0,   3600, 'AZOST'),
        ttinfo( -3600,      0, 'AZOT'),
        ttinfo(     0,   3600, 'AZOST'),
        ttinfo( -3600,      0, 'AZOT'),
        ttinfo(     0,   3600, 'AZOST'),
        ttinfo( -3600,      0, 'AZOT'),
        ttinfo(     0,   3600, 'AZOST'),
        ttinfo( -3600,      0, 'AZOT'),
        ttinfo(     0,   3600, 'AZOST'),
        ttinfo( -3600,      0, 'AZOT'),
        ttinfo(     0,   3600, 'AZOST'),
        ttinfo( -3600,      0, 'AZOT'),
        ttinfo(     0,   3600, 'AZOST'),
        ttinfo( -3600,      0, 'AZOT'),
        ttinfo(     0,   3600, 'AZOST'),
        ttinfo( -3600,      0, 'AZOT'),
        ttinfo(     0,   3600, 'AZOST'),
        ttinfo( -3600,      0, 'AZOT'),
        ttinfo(     0,   3600, 'AZOST'),
        ttinfo( -3600,      0, 'AZOT'),
        ttinfo(     0,   3600, 'AZOST'),
        ttinfo( -3600,      0, 'AZOT'),
        ttinfo(     0,   3600, 'AZOST'),
        ttinfo( -3600,      0, 'AZOT'),
        ttinfo(     0,   3600, 'AZOST'),
        ttinfo( -3600,      0, 'AZOT'),
        ttinfo(     0,   3600, 'AZOST'),
        ttinfo( -3600,      0, 'AZOT'),
        ttinfo(     0,   3600, 'AZOST'),
        ttinfo( -3600,      0, 'AZOT'),
        ttinfo(     0,   3600, 'AZOST'),
        ttinfo( -3600,      0, 'AZOT'),
        ttinfo(     0,   3600, 'AZOST'),
        ttinfo( -3600,      0, 'AZOT'),
        ttinfo(     0,   3600, 'AZOST'),
        ttinfo( -3600,      0, 'AZOT'),
        ttinfo(     0,   3600, 'AZOST'),
        ttinfo( -3600,      0, 'AZOT'),
        ttinfo(     0,   3600, 'AZOST'),
        ttinfo( -3600,      0, 'AZOT'),
        ttinfo(     0,   3600, 'AZOST'),
        ttinfo( -3600,      0, 'AZOT'),
        ttinfo(     0,   3600, 'AZOST'),
        ttinfo( -3600,      0, 'AZOT'),
        ttinfo(     0,   3600, 'AZOST'),
        ttinfo( -3600,      0, 'AZOT'),
        ttinfo(     0,   3600, 'AZOST'),
        ttinfo( -3600,      0, 'AZOT'),
        ttinfo(     0,   3600, 'AZOST'),
        ttinfo( -3600,      0, 'AZOT'),
        ]

Azores = Azores() # Singleton

