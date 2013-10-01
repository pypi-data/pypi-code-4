'''
tzinfo timezone information for SystemV/AST4ADT.

Generated from the Olson timezone database:
    ftp://elsie.nci.nih.gov/pub/tz*.tar.gz
'''

from pytz.tzinfo import DstTzInfo
from pytz.tzinfo import memorized_datetime as datetime
from pytz.tzinfo import memorized_ttinfo as ttinfo

class AST4ADT(DstTzInfo):
    '''SystemV/AST4ADT timezone definition. See datetime.tzinfo for details'''

    _zone = 'SystemV/AST4ADT'

    _utc_transition_times = [
        datetime(   1,  1,  1,  0,  0,  0), # -15264     0 LMT
        datetime(1902,  6, 15,  4, 14, 24), # -14400     0 AST
        datetime(1916,  4,  1,  4,  0,  0), # -10800  3600 ADT
        datetime(1916, 10,  1,  3,  0,  0), # -14400     0 AST
        datetime(1918,  4, 14,  6,  0,  0), # -10800  3600 ADT
        datetime(1918, 10, 31,  5,  0,  0), # -14400     0 AST
        datetime(1920,  5,  9,  4,  0,  0), # -10800  3600 ADT
        datetime(1920,  8, 29,  3,  0,  0), # -14400     0 AST
        datetime(1921,  5,  6,  4,  0,  0), # -10800  3600 ADT
        datetime(1921,  9,  5,  3,  0,  0), # -14400     0 AST
        datetime(1922,  4, 30,  4,  0,  0), # -10800  3600 ADT
        datetime(1922,  9,  5,  3,  0,  0), # -14400     0 AST
        datetime(1923,  5,  6,  4,  0,  0), # -10800  3600 ADT
        datetime(1923,  9,  4,  3,  0,  0), # -14400     0 AST
        datetime(1924,  5,  4,  4,  0,  0), # -10800  3600 ADT
        datetime(1924,  9, 15,  3,  0,  0), # -14400     0 AST
        datetime(1925,  5,  3,  4,  0,  0), # -10800  3600 ADT
        datetime(1925,  9, 28,  3,  0,  0), # -14400     0 AST
        datetime(1926,  5, 16,  4,  0,  0), # -10800  3600 ADT
        datetime(1926,  9, 13,  3,  0,  0), # -14400     0 AST
        datetime(1927,  5,  1,  4,  0,  0), # -10800  3600 ADT
        datetime(1927,  9, 26,  3,  0,  0), # -14400     0 AST
        datetime(1928,  5, 13,  4,  0,  0), # -10800  3600 ADT
        datetime(1928,  9,  9,  3,  0,  0), # -14400     0 AST
        datetime(1929,  5, 12,  4,  0,  0), # -10800  3600 ADT
        datetime(1929,  9,  3,  3,  0,  0), # -14400     0 AST
        datetime(1930,  5, 11,  4,  0,  0), # -10800  3600 ADT
        datetime(1930,  9, 15,  3,  0,  0), # -14400     0 AST
        datetime(1931,  5, 10,  4,  0,  0), # -10800  3600 ADT
        datetime(1931,  9, 28,  3,  0,  0), # -14400     0 AST
        datetime(1932,  5,  1,  4,  0,  0), # -10800  3600 ADT
        datetime(1932,  9, 26,  3,  0,  0), # -14400     0 AST
        datetime(1933,  4, 30,  4,  0,  0), # -10800  3600 ADT
        datetime(1933, 10,  2,  3,  0,  0), # -14400     0 AST
        datetime(1934,  5, 20,  4,  0,  0), # -10800  3600 ADT
        datetime(1934,  9, 16,  3,  0,  0), # -14400     0 AST
        datetime(1935,  6,  2,  4,  0,  0), # -10800  3600 ADT
        datetime(1935,  9, 30,  3,  0,  0), # -14400     0 AST
        datetime(1936,  6,  1,  4,  0,  0), # -10800  3600 ADT
        datetime(1936,  9, 14,  3,  0,  0), # -14400     0 AST
        datetime(1937,  5,  2,  4,  0,  0), # -10800  3600 ADT
        datetime(1937,  9, 27,  3,  0,  0), # -14400     0 AST
        datetime(1938,  5,  1,  4,  0,  0), # -10800  3600 ADT
        datetime(1938,  9, 26,  3,  0,  0), # -14400     0 AST
        datetime(1939,  5, 28,  4,  0,  0), # -10800  3600 ADT
        datetime(1939,  9, 25,  3,  0,  0), # -14400     0 AST
        datetime(1940,  5,  5,  4,  0,  0), # -10800  3600 ADT
        datetime(1940,  9, 30,  3,  0,  0), # -14400     0 AST
        datetime(1941,  5,  4,  4,  0,  0), # -10800  3600 ADT
        datetime(1941,  9, 29,  3,  0,  0), # -14400     0 AST
        datetime(1942,  2,  9,  6,  0,  0), # -10800  3600 AWT
        datetime(1945,  8, 14, 23,  0,  0), # -10800     0 APT
        datetime(1945,  9, 30,  5,  0,  0), # -14400     0 AST
        datetime(1946,  4, 28,  6,  0,  0), # -10800  3600 ADT
        datetime(1946,  9, 29,  5,  0,  0), # -14400     0 AST
        datetime(1947,  4, 27,  6,  0,  0), # -10800  3600 ADT
        datetime(1947,  9, 28,  5,  0,  0), # -14400     0 AST
        datetime(1948,  4, 25,  6,  0,  0), # -10800  3600 ADT
        datetime(1948,  9, 26,  5,  0,  0), # -14400     0 AST
        datetime(1949,  4, 24,  6,  0,  0), # -10800  3600 ADT
        datetime(1949,  9, 25,  5,  0,  0), # -14400     0 AST
        datetime(1951,  4, 29,  6,  0,  0), # -10800  3600 ADT
        datetime(1951,  9, 30,  5,  0,  0), # -14400     0 AST
        datetime(1952,  4, 27,  6,  0,  0), # -10800  3600 ADT
        datetime(1952,  9, 28,  5,  0,  0), # -14400     0 AST
        datetime(1953,  4, 26,  6,  0,  0), # -10800  3600 ADT
        datetime(1953,  9, 27,  5,  0,  0), # -14400     0 AST
        datetime(1954,  4, 25,  6,  0,  0), # -10800  3600 ADT
        datetime(1954,  9, 26,  5,  0,  0), # -14400     0 AST
        datetime(1956,  4, 29,  6,  0,  0), # -10800  3600 ADT
        datetime(1956,  9, 30,  5,  0,  0), # -14400     0 AST
        datetime(1957,  4, 28,  6,  0,  0), # -10800  3600 ADT
        datetime(1957,  9, 29,  5,  0,  0), # -14400     0 AST
        datetime(1958,  4, 27,  6,  0,  0), # -10800  3600 ADT
        datetime(1958,  9, 28,  5,  0,  0), # -14400     0 AST
        datetime(1959,  4, 26,  6,  0,  0), # -10800  3600 ADT
        datetime(1959,  9, 27,  5,  0,  0), # -14400     0 AST
        datetime(1962,  4, 29,  6,  0,  0), # -10800  3600 ADT
        datetime(1962, 10, 28,  5,  0,  0), # -14400     0 AST
        datetime(1963,  4, 28,  6,  0,  0), # -10800  3600 ADT
        datetime(1963, 10, 27,  5,  0,  0), # -14400     0 AST
        datetime(1964,  4, 26,  6,  0,  0), # -10800  3600 ADT
        datetime(1964, 10, 25,  5,  0,  0), # -14400     0 AST
        datetime(1965,  4, 25,  6,  0,  0), # -10800  3600 ADT
        datetime(1965, 10, 31,  5,  0,  0), # -14400     0 AST
        datetime(1966,  4, 24,  6,  0,  0), # -10800  3600 ADT
        datetime(1966, 10, 30,  5,  0,  0), # -14400     0 AST
        datetime(1967,  4, 30,  6,  0,  0), # -10800  3600 ADT
        datetime(1967, 10, 29,  5,  0,  0), # -14400     0 AST
        datetime(1968,  4, 28,  6,  0,  0), # -10800  3600 ADT
        datetime(1968, 10, 27,  5,  0,  0), # -14400     0 AST
        datetime(1969,  4, 27,  6,  0,  0), # -10800  3600 ADT
        datetime(1969, 10, 26,  5,  0,  0), # -14400     0 AST
        datetime(1970,  4, 26,  6,  0,  0), # -10800  3600 ADT
        datetime(1970, 10, 25,  5,  0,  0), # -14400     0 AST
        datetime(1971,  4, 25,  6,  0,  0), # -10800  3600 ADT
        datetime(1971, 10, 31,  5,  0,  0), # -14400     0 AST
        datetime(1972,  4, 30,  6,  0,  0), # -10800  3600 ADT
        datetime(1972, 10, 29,  5,  0,  0), # -14400     0 AST
        datetime(1973,  4, 29,  6,  0,  0), # -10800  3600 ADT
        datetime(1973, 10, 28,  5,  0,  0), # -14400     0 AST
        datetime(1974,  4, 28,  6,  0,  0), # -10800  3600 ADT
        datetime(1974, 10, 27,  5,  0,  0), # -14400     0 AST
        datetime(1975,  4, 27,  6,  0,  0), # -10800  3600 ADT
        datetime(1975, 10, 26,  5,  0,  0), # -14400     0 AST
        datetime(1976,  4, 25,  6,  0,  0), # -10800  3600 ADT
        datetime(1976, 10, 31,  5,  0,  0), # -14400     0 AST
        datetime(1977,  4, 24,  6,  0,  0), # -10800  3600 ADT
        datetime(1977, 10, 30,  5,  0,  0), # -14400     0 AST
        datetime(1978,  4, 30,  6,  0,  0), # -10800  3600 ADT
        datetime(1978, 10, 29,  5,  0,  0), # -14400     0 AST
        datetime(1979,  4, 29,  6,  0,  0), # -10800  3600 ADT
        datetime(1979, 10, 28,  5,  0,  0), # -14400     0 AST
        datetime(1980,  4, 27,  6,  0,  0), # -10800  3600 ADT
        datetime(1980, 10, 26,  5,  0,  0), # -14400     0 AST
        datetime(1981,  4, 26,  6,  0,  0), # -10800  3600 ADT
        datetime(1981, 10, 25,  5,  0,  0), # -14400     0 AST
        datetime(1982,  4, 25,  6,  0,  0), # -10800  3600 ADT
        datetime(1982, 10, 31,  5,  0,  0), # -14400     0 AST
        datetime(1983,  4, 24,  6,  0,  0), # -10800  3600 ADT
        datetime(1983, 10, 30,  5,  0,  0), # -14400     0 AST
        datetime(1984,  4, 29,  6,  0,  0), # -10800  3600 ADT
        datetime(1984, 10, 28,  5,  0,  0), # -14400     0 AST
        datetime(1985,  4, 28,  6,  0,  0), # -10800  3600 ADT
        datetime(1985, 10, 27,  5,  0,  0), # -14400     0 AST
        datetime(1986,  4, 27,  6,  0,  0), # -10800  3600 ADT
        datetime(1986, 10, 26,  5,  0,  0), # -14400     0 AST
        datetime(1987,  4,  5,  6,  0,  0), # -10800  3600 ADT
        datetime(1987, 10, 25,  5,  0,  0), # -14400     0 AST
        datetime(1988,  4,  3,  6,  0,  0), # -10800  3600 ADT
        datetime(1988, 10, 30,  5,  0,  0), # -14400     0 AST
        datetime(1989,  4,  2,  6,  0,  0), # -10800  3600 ADT
        datetime(1989, 10, 29,  5,  0,  0), # -14400     0 AST
        datetime(1990,  4,  1,  6,  0,  0), # -10800  3600 ADT
        datetime(1990, 10, 28,  5,  0,  0), # -14400     0 AST
        datetime(1991,  4,  7,  6,  0,  0), # -10800  3600 ADT
        datetime(1991, 10, 27,  5,  0,  0), # -14400     0 AST
        datetime(1992,  4,  5,  6,  0,  0), # -10800  3600 ADT
        datetime(1992, 10, 25,  5,  0,  0), # -14400     0 AST
        datetime(1993,  4,  4,  6,  0,  0), # -10800  3600 ADT
        datetime(1993, 10, 31,  5,  0,  0), # -14400     0 AST
        datetime(1994,  4,  3,  6,  0,  0), # -10800  3600 ADT
        datetime(1994, 10, 30,  5,  0,  0), # -14400     0 AST
        datetime(1995,  4,  2,  6,  0,  0), # -10800  3600 ADT
        datetime(1995, 10, 29,  5,  0,  0), # -14400     0 AST
        datetime(1996,  4,  7,  6,  0,  0), # -10800  3600 ADT
        datetime(1996, 10, 27,  5,  0,  0), # -14400     0 AST
        datetime(1997,  4,  6,  6,  0,  0), # -10800  3600 ADT
        datetime(1997, 10, 26,  5,  0,  0), # -14400     0 AST
        datetime(1998,  4,  5,  6,  0,  0), # -10800  3600 ADT
        datetime(1998, 10, 25,  5,  0,  0), # -14400     0 AST
        datetime(1999,  4,  4,  6,  0,  0), # -10800  3600 ADT
        datetime(1999, 10, 31,  5,  0,  0), # -14400     0 AST
        datetime(2000,  4,  2,  6,  0,  0), # -10800  3600 ADT
        datetime(2000, 10, 29,  5,  0,  0), # -14400     0 AST
        datetime(2001,  4,  1,  6,  0,  0), # -10800  3600 ADT
        datetime(2001, 10, 28,  5,  0,  0), # -14400     0 AST
        datetime(2002,  4,  7,  6,  0,  0), # -10800  3600 ADT
        datetime(2002, 10, 27,  5,  0,  0), # -14400     0 AST
        datetime(2003,  4,  6,  6,  0,  0), # -10800  3600 ADT
        datetime(2003, 10, 26,  5,  0,  0), # -14400     0 AST
        datetime(2004,  4,  4,  6,  0,  0), # -10800  3600 ADT
        datetime(2004, 10, 31,  5,  0,  0), # -14400     0 AST
        datetime(2005,  4,  3,  6,  0,  0), # -10800  3600 ADT
        datetime(2005, 10, 30,  5,  0,  0), # -14400     0 AST
        datetime(2006,  4,  2,  6,  0,  0), # -10800  3600 ADT
        datetime(2006, 10, 29,  5,  0,  0), # -14400     0 AST
        datetime(2007,  4,  1,  6,  0,  0), # -10800  3600 ADT
        datetime(2007, 10, 28,  5,  0,  0), # -14400     0 AST
        datetime(2008,  4,  6,  6,  0,  0), # -10800  3600 ADT
        datetime(2008, 10, 26,  5,  0,  0), # -14400     0 AST
        datetime(2009,  4,  5,  6,  0,  0), # -10800  3600 ADT
        datetime(2009, 10, 25,  5,  0,  0), # -14400     0 AST
        datetime(2010,  4,  4,  6,  0,  0), # -10800  3600 ADT
        datetime(2010, 10, 31,  5,  0,  0), # -14400     0 AST
        datetime(2011,  4,  3,  6,  0,  0), # -10800  3600 ADT
        datetime(2011, 10, 30,  5,  0,  0), # -14400     0 AST
        datetime(2012,  4,  1,  6,  0,  0), # -10800  3600 ADT
        datetime(2012, 10, 28,  5,  0,  0), # -14400     0 AST
        datetime(2013,  4,  7,  6,  0,  0), # -10800  3600 ADT
        datetime(2013, 10, 27,  5,  0,  0), # -14400     0 AST
        datetime(2014,  4,  6,  6,  0,  0), # -10800  3600 ADT
        datetime(2014, 10, 26,  5,  0,  0), # -14400     0 AST
        datetime(2015,  4,  5,  6,  0,  0), # -10800  3600 ADT
        datetime(2015, 10, 25,  5,  0,  0), # -14400     0 AST
        datetime(2016,  4,  3,  6,  0,  0), # -10800  3600 ADT
        datetime(2016, 10, 30,  5,  0,  0), # -14400     0 AST
        datetime(2017,  4,  2,  6,  0,  0), # -10800  3600 ADT
        datetime(2017, 10, 29,  5,  0,  0), # -14400     0 AST
        datetime(2018,  4,  1,  6,  0,  0), # -10800  3600 ADT
        datetime(2018, 10, 28,  5,  0,  0), # -14400     0 AST
        datetime(2019,  4,  7,  6,  0,  0), # -10800  3600 ADT
        datetime(2019, 10, 27,  5,  0,  0), # -14400     0 AST
        datetime(2020,  4,  5,  6,  0,  0), # -10800  3600 ADT
        datetime(2020, 10, 25,  5,  0,  0), # -14400     0 AST
        datetime(2021,  4,  4,  6,  0,  0), # -10800  3600 ADT
        datetime(2021, 10, 31,  5,  0,  0), # -14400     0 AST
        datetime(2022,  4,  3,  6,  0,  0), # -10800  3600 ADT
        datetime(2022, 10, 30,  5,  0,  0), # -14400     0 AST
        datetime(2023,  4,  2,  6,  0,  0), # -10800  3600 ADT
        datetime(2023, 10, 29,  5,  0,  0), # -14400     0 AST
        datetime(2024,  4,  7,  6,  0,  0), # -10800  3600 ADT
        datetime(2024, 10, 27,  5,  0,  0), # -14400     0 AST
        datetime(2025,  4,  6,  6,  0,  0), # -10800  3600 ADT
        datetime(2025, 10, 26,  5,  0,  0), # -14400     0 AST
        datetime(2026,  4,  5,  6,  0,  0), # -10800  3600 ADT
        datetime(2026, 10, 25,  5,  0,  0), # -14400     0 AST
        datetime(2027,  4,  4,  6,  0,  0), # -10800  3600 ADT
        datetime(2027, 10, 31,  5,  0,  0), # -14400     0 AST
        datetime(2028,  4,  2,  6,  0,  0), # -10800  3600 ADT
        datetime(2028, 10, 29,  5,  0,  0), # -14400     0 AST
        datetime(2029,  4,  1,  6,  0,  0), # -10800  3600 ADT
        datetime(2029, 10, 28,  5,  0,  0), # -14400     0 AST
        datetime(2030,  4,  7,  6,  0,  0), # -10800  3600 ADT
        datetime(2030, 10, 27,  5,  0,  0), # -14400     0 AST
        datetime(2031,  4,  6,  6,  0,  0), # -10800  3600 ADT
        datetime(2031, 10, 26,  5,  0,  0), # -14400     0 AST
        datetime(2032,  4,  4,  6,  0,  0), # -10800  3600 ADT
        datetime(2032, 10, 31,  5,  0,  0), # -14400     0 AST
        datetime(2033,  4,  3,  6,  0,  0), # -10800  3600 ADT
        datetime(2033, 10, 30,  5,  0,  0), # -14400     0 AST
        datetime(2034,  4,  2,  6,  0,  0), # -10800  3600 ADT
        datetime(2034, 10, 29,  5,  0,  0), # -14400     0 AST
        datetime(2035,  4,  1,  6,  0,  0), # -10800  3600 ADT
        datetime(2035, 10, 28,  5,  0,  0), # -14400     0 AST
        datetime(2036,  4,  6,  6,  0,  0), # -10800  3600 ADT
        datetime(2036, 10, 26,  5,  0,  0), # -14400     0 AST
        datetime(2037,  4,  5,  6,  0,  0), # -10800  3600 ADT
        datetime(2037, 10, 25,  5,  0,  0), # -14400     0 AST
        ]

    _transition_info = [
        ttinfo(-15264,      0,  'LMT'),
        ttinfo(-14400,      0,  'AST'),
        ttinfo(-10800,   3600,  'ADT'),
        ttinfo(-14400,      0,  'AST'),
        ttinfo(-10800,   3600,  'ADT'),
        ttinfo(-14400,      0,  'AST'),
        ttinfo(-10800,   3600,  'ADT'),
        ttinfo(-14400,      0,  'AST'),
        ttinfo(-10800,   3600,  'ADT'),
        ttinfo(-14400,      0,  'AST'),
        ttinfo(-10800,   3600,  'ADT'),
        ttinfo(-14400,      0,  'AST'),
        ttinfo(-10800,   3600,  'ADT'),
        ttinfo(-14400,      0,  'AST'),
        ttinfo(-10800,   3600,  'ADT'),
        ttinfo(-14400,      0,  'AST'),
        ttinfo(-10800,   3600,  'ADT'),
        ttinfo(-14400,      0,  'AST'),
        ttinfo(-10800,   3600,  'ADT'),
        ttinfo(-14400,      0,  'AST'),
        ttinfo(-10800,   3600,  'ADT'),
        ttinfo(-14400,      0,  'AST'),
        ttinfo(-10800,   3600,  'ADT'),
        ttinfo(-14400,      0,  'AST'),
        ttinfo(-10800,   3600,  'ADT'),
        ttinfo(-14400,      0,  'AST'),
        ttinfo(-10800,   3600,  'ADT'),
        ttinfo(-14400,      0,  'AST'),
        ttinfo(-10800,   3600,  'ADT'),
        ttinfo(-14400,      0,  'AST'),
        ttinfo(-10800,   3600,  'ADT'),
        ttinfo(-14400,      0,  'AST'),
        ttinfo(-10800,   3600,  'ADT'),
        ttinfo(-14400,      0,  'AST'),
        ttinfo(-10800,   3600,  'ADT'),
        ttinfo(-14400,      0,  'AST'),
        ttinfo(-10800,   3600,  'ADT'),
        ttinfo(-14400,      0,  'AST'),
        ttinfo(-10800,   3600,  'ADT'),
        ttinfo(-14400,      0,  'AST'),
        ttinfo(-10800,   3600,  'ADT'),
        ttinfo(-14400,      0,  'AST'),
        ttinfo(-10800,   3600,  'ADT'),
        ttinfo(-14400,      0,  'AST'),
        ttinfo(-10800,   3600,  'ADT'),
        ttinfo(-14400,      0,  'AST'),
        ttinfo(-10800,   3600,  'ADT'),
        ttinfo(-14400,      0,  'AST'),
        ttinfo(-10800,   3600,  'ADT'),
        ttinfo(-14400,      0,  'AST'),
        ttinfo(-10800,   3600,  'AWT'),
        ttinfo(-10800,      0,  'APT'),
        ttinfo(-14400,      0,  'AST'),
        ttinfo(-10800,   3600,  'ADT'),
        ttinfo(-14400,      0,  'AST'),
        ttinfo(-10800,   3600,  'ADT'),
        ttinfo(-14400,      0,  'AST'),
        ttinfo(-10800,   3600,  'ADT'),
        ttinfo(-14400,      0,  'AST'),
        ttinfo(-10800,   3600,  'ADT'),
        ttinfo(-14400,      0,  'AST'),
        ttinfo(-10800,   3600,  'ADT'),
        ttinfo(-14400,      0,  'AST'),
        ttinfo(-10800,   3600,  'ADT'),
        ttinfo(-14400,      0,  'AST'),
        ttinfo(-10800,   3600,  'ADT'),
        ttinfo(-14400,      0,  'AST'),
        ttinfo(-10800,   3600,  'ADT'),
        ttinfo(-14400,      0,  'AST'),
        ttinfo(-10800,   3600,  'ADT'),
        ttinfo(-14400,      0,  'AST'),
        ttinfo(-10800,   3600,  'ADT'),
        ttinfo(-14400,      0,  'AST'),
        ttinfo(-10800,   3600,  'ADT'),
        ttinfo(-14400,      0,  'AST'),
        ttinfo(-10800,   3600,  'ADT'),
        ttinfo(-14400,      0,  'AST'),
        ttinfo(-10800,   3600,  'ADT'),
        ttinfo(-14400,      0,  'AST'),
        ttinfo(-10800,   3600,  'ADT'),
        ttinfo(-14400,      0,  'AST'),
        ttinfo(-10800,   3600,  'ADT'),
        ttinfo(-14400,      0,  'AST'),
        ttinfo(-10800,   3600,  'ADT'),
        ttinfo(-14400,      0,  'AST'),
        ttinfo(-10800,   3600,  'ADT'),
        ttinfo(-14400,      0,  'AST'),
        ttinfo(-10800,   3600,  'ADT'),
        ttinfo(-14400,      0,  'AST'),
        ttinfo(-10800,   3600,  'ADT'),
        ttinfo(-14400,      0,  'AST'),
        ttinfo(-10800,   3600,  'ADT'),
        ttinfo(-14400,      0,  'AST'),
        ttinfo(-10800,   3600,  'ADT'),
        ttinfo(-14400,      0,  'AST'),
        ttinfo(-10800,   3600,  'ADT'),
        ttinfo(-14400,      0,  'AST'),
        ttinfo(-10800,   3600,  'ADT'),
        ttinfo(-14400,      0,  'AST'),
        ttinfo(-10800,   3600,  'ADT'),
        ttinfo(-14400,      0,  'AST'),
        ttinfo(-10800,   3600,  'ADT'),
        ttinfo(-14400,      0,  'AST'),
        ttinfo(-10800,   3600,  'ADT'),
        ttinfo(-14400,      0,  'AST'),
        ttinfo(-10800,   3600,  'ADT'),
        ttinfo(-14400,      0,  'AST'),
        ttinfo(-10800,   3600,  'ADT'),
        ttinfo(-14400,      0,  'AST'),
        ttinfo(-10800,   3600,  'ADT'),
        ttinfo(-14400,      0,  'AST'),
        ttinfo(-10800,   3600,  'ADT'),
        ttinfo(-14400,      0,  'AST'),
        ttinfo(-10800,   3600,  'ADT'),
        ttinfo(-14400,      0,  'AST'),
        ttinfo(-10800,   3600,  'ADT'),
        ttinfo(-14400,      0,  'AST'),
        ttinfo(-10800,   3600,  'ADT'),
        ttinfo(-14400,      0,  'AST'),
        ttinfo(-10800,   3600,  'ADT'),
        ttinfo(-14400,      0,  'AST'),
        ttinfo(-10800,   3600,  'ADT'),
        ttinfo(-14400,      0,  'AST'),
        ttinfo(-10800,   3600,  'ADT'),
        ttinfo(-14400,      0,  'AST'),
        ttinfo(-10800,   3600,  'ADT'),
        ttinfo(-14400,      0,  'AST'),
        ttinfo(-10800,   3600,  'ADT'),
        ttinfo(-14400,      0,  'AST'),
        ttinfo(-10800,   3600,  'ADT'),
        ttinfo(-14400,      0,  'AST'),
        ttinfo(-10800,   3600,  'ADT'),
        ttinfo(-14400,      0,  'AST'),
        ttinfo(-10800,   3600,  'ADT'),
        ttinfo(-14400,      0,  'AST'),
        ttinfo(-10800,   3600,  'ADT'),
        ttinfo(-14400,      0,  'AST'),
        ttinfo(-10800,   3600,  'ADT'),
        ttinfo(-14400,      0,  'AST'),
        ttinfo(-10800,   3600,  'ADT'),
        ttinfo(-14400,      0,  'AST'),
        ttinfo(-10800,   3600,  'ADT'),
        ttinfo(-14400,      0,  'AST'),
        ttinfo(-10800,   3600,  'ADT'),
        ttinfo(-14400,      0,  'AST'),
        ttinfo(-10800,   3600,  'ADT'),
        ttinfo(-14400,      0,  'AST'),
        ttinfo(-10800,   3600,  'ADT'),
        ttinfo(-14400,      0,  'AST'),
        ttinfo(-10800,   3600,  'ADT'),
        ttinfo(-14400,      0,  'AST'),
        ttinfo(-10800,   3600,  'ADT'),
        ttinfo(-14400,      0,  'AST'),
        ttinfo(-10800,   3600,  'ADT'),
        ttinfo(-14400,      0,  'AST'),
        ttinfo(-10800,   3600,  'ADT'),
        ttinfo(-14400,      0,  'AST'),
        ttinfo(-10800,   3600,  'ADT'),
        ttinfo(-14400,      0,  'AST'),
        ttinfo(-10800,   3600,  'ADT'),
        ttinfo(-14400,      0,  'AST'),
        ttinfo(-10800,   3600,  'ADT'),
        ttinfo(-14400,      0,  'AST'),
        ttinfo(-10800,   3600,  'ADT'),
        ttinfo(-14400,      0,  'AST'),
        ttinfo(-10800,   3600,  'ADT'),
        ttinfo(-14400,      0,  'AST'),
        ttinfo(-10800,   3600,  'ADT'),
        ttinfo(-14400,      0,  'AST'),
        ttinfo(-10800,   3600,  'ADT'),
        ttinfo(-14400,      0,  'AST'),
        ttinfo(-10800,   3600,  'ADT'),
        ttinfo(-14400,      0,  'AST'),
        ttinfo(-10800,   3600,  'ADT'),
        ttinfo(-14400,      0,  'AST'),
        ttinfo(-10800,   3600,  'ADT'),
        ttinfo(-14400,      0,  'AST'),
        ttinfo(-10800,   3600,  'ADT'),
        ttinfo(-14400,      0,  'AST'),
        ttinfo(-10800,   3600,  'ADT'),
        ttinfo(-14400,      0,  'AST'),
        ttinfo(-10800,   3600,  'ADT'),
        ttinfo(-14400,      0,  'AST'),
        ttinfo(-10800,   3600,  'ADT'),
        ttinfo(-14400,      0,  'AST'),
        ttinfo(-10800,   3600,  'ADT'),
        ttinfo(-14400,      0,  'AST'),
        ttinfo(-10800,   3600,  'ADT'),
        ttinfo(-14400,      0,  'AST'),
        ttinfo(-10800,   3600,  'ADT'),
        ttinfo(-14400,      0,  'AST'),
        ttinfo(-10800,   3600,  'ADT'),
        ttinfo(-14400,      0,  'AST'),
        ttinfo(-10800,   3600,  'ADT'),
        ttinfo(-14400,      0,  'AST'),
        ttinfo(-10800,   3600,  'ADT'),
        ttinfo(-14400,      0,  'AST'),
        ttinfo(-10800,   3600,  'ADT'),
        ttinfo(-14400,      0,  'AST'),
        ttinfo(-10800,   3600,  'ADT'),
        ttinfo(-14400,      0,  'AST'),
        ttinfo(-10800,   3600,  'ADT'),
        ttinfo(-14400,      0,  'AST'),
        ttinfo(-10800,   3600,  'ADT'),
        ttinfo(-14400,      0,  'AST'),
        ttinfo(-10800,   3600,  'ADT'),
        ttinfo(-14400,      0,  'AST'),
        ttinfo(-10800,   3600,  'ADT'),
        ttinfo(-14400,      0,  'AST'),
        ttinfo(-10800,   3600,  'ADT'),
        ttinfo(-14400,      0,  'AST'),
        ttinfo(-10800,   3600,  'ADT'),
        ttinfo(-14400,      0,  'AST'),
        ttinfo(-10800,   3600,  'ADT'),
        ttinfo(-14400,      0,  'AST'),
        ttinfo(-10800,   3600,  'ADT'),
        ttinfo(-14400,      0,  'AST'),
        ttinfo(-10800,   3600,  'ADT'),
        ttinfo(-14400,      0,  'AST'),
        ttinfo(-10800,   3600,  'ADT'),
        ttinfo(-14400,      0,  'AST'),
        ttinfo(-10800,   3600,  'ADT'),
        ttinfo(-14400,      0,  'AST'),
        ttinfo(-10800,   3600,  'ADT'),
        ttinfo(-14400,      0,  'AST'),
        ttinfo(-10800,   3600,  'ADT'),
        ttinfo(-14400,      0,  'AST'),
        ttinfo(-10800,   3600,  'ADT'),
        ttinfo(-14400,      0,  'AST'),
        ]

AST4ADT = AST4ADT() # Singleton

