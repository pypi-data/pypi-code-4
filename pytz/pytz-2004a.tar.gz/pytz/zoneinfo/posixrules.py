'''
tzinfo timezone information for posixrules.

Generated from the Olson timezone database:
    ftp://elsie.nci.nih.gov/pub/tz*.tar.gz
'''

from pytz.tzinfo import DstTzInfo
from pytz.tzinfo import memorized_datetime as datetime
from pytz.tzinfo import memorized_ttinfo as ttinfo

class posixrules(DstTzInfo):
    '''posixrules timezone definition. See datetime.tzinfo for details'''

    _zone = 'posixrules'

    _utc_transition_times = [
        datetime(   1,  1,  1,  0,  0,  0), # -18000     0 EST
        datetime(1918,  3, 31,  7,  0,  0), # -14400  3600 EDT
        datetime(1918, 10, 27,  6,  0,  0), # -18000     0 EST
        datetime(1919,  3, 30,  7,  0,  0), # -14400  3600 EDT
        datetime(1919, 10, 26,  6,  0,  0), # -18000     0 EST
        datetime(1920,  3, 28,  7,  0,  0), # -14400  3600 EDT
        datetime(1920, 10, 31,  6,  0,  0), # -18000     0 EST
        datetime(1921,  4, 24,  7,  0,  0), # -14400  3600 EDT
        datetime(1921,  9, 25,  6,  0,  0), # -18000     0 EST
        datetime(1922,  4, 30,  7,  0,  0), # -14400  3600 EDT
        datetime(1922,  9, 24,  6,  0,  0), # -18000     0 EST
        datetime(1923,  4, 29,  7,  0,  0), # -14400  3600 EDT
        datetime(1923,  9, 30,  6,  0,  0), # -18000     0 EST
        datetime(1924,  4, 27,  7,  0,  0), # -14400  3600 EDT
        datetime(1924,  9, 28,  6,  0,  0), # -18000     0 EST
        datetime(1925,  4, 26,  7,  0,  0), # -14400  3600 EDT
        datetime(1925,  9, 27,  6,  0,  0), # -18000     0 EST
        datetime(1926,  4, 25,  7,  0,  0), # -14400  3600 EDT
        datetime(1926,  9, 26,  6,  0,  0), # -18000     0 EST
        datetime(1927,  4, 24,  7,  0,  0), # -14400  3600 EDT
        datetime(1927,  9, 25,  6,  0,  0), # -18000     0 EST
        datetime(1928,  4, 29,  7,  0,  0), # -14400  3600 EDT
        datetime(1928,  9, 30,  6,  0,  0), # -18000     0 EST
        datetime(1929,  4, 28,  7,  0,  0), # -14400  3600 EDT
        datetime(1929,  9, 29,  6,  0,  0), # -18000     0 EST
        datetime(1930,  4, 27,  7,  0,  0), # -14400  3600 EDT
        datetime(1930,  9, 28,  6,  0,  0), # -18000     0 EST
        datetime(1931,  4, 26,  7,  0,  0), # -14400  3600 EDT
        datetime(1931,  9, 27,  6,  0,  0), # -18000     0 EST
        datetime(1932,  4, 24,  7,  0,  0), # -14400  3600 EDT
        datetime(1932,  9, 25,  6,  0,  0), # -18000     0 EST
        datetime(1933,  4, 30,  7,  0,  0), # -14400  3600 EDT
        datetime(1933,  9, 24,  6,  0,  0), # -18000     0 EST
        datetime(1934,  4, 29,  7,  0,  0), # -14400  3600 EDT
        datetime(1934,  9, 30,  6,  0,  0), # -18000     0 EST
        datetime(1935,  4, 28,  7,  0,  0), # -14400  3600 EDT
        datetime(1935,  9, 29,  6,  0,  0), # -18000     0 EST
        datetime(1936,  4, 26,  7,  0,  0), # -14400  3600 EDT
        datetime(1936,  9, 27,  6,  0,  0), # -18000     0 EST
        datetime(1937,  4, 25,  7,  0,  0), # -14400  3600 EDT
        datetime(1937,  9, 26,  6,  0,  0), # -18000     0 EST
        datetime(1938,  4, 24,  7,  0,  0), # -14400  3600 EDT
        datetime(1938,  9, 25,  6,  0,  0), # -18000     0 EST
        datetime(1939,  4, 30,  7,  0,  0), # -14400  3600 EDT
        datetime(1939,  9, 24,  6,  0,  0), # -18000     0 EST
        datetime(1940,  4, 28,  7,  0,  0), # -14400  3600 EDT
        datetime(1940,  9, 29,  6,  0,  0), # -18000     0 EST
        datetime(1941,  4, 27,  7,  0,  0), # -14400  3600 EDT
        datetime(1941,  9, 28,  6,  0,  0), # -18000     0 EST
        datetime(1942,  2,  9,  7,  0,  0), # -14400  3600 EWT
        datetime(1945,  8, 14, 23,  0,  0), # -14400     0 EPT
        datetime(1945,  9, 30,  6,  0,  0), # -18000     0 EST
        datetime(1946,  4, 28,  7,  0,  0), # -14400  3600 EDT
        datetime(1946,  9, 29,  6,  0,  0), # -18000     0 EST
        datetime(1947,  4, 27,  7,  0,  0), # -14400  3600 EDT
        datetime(1947,  9, 28,  6,  0,  0), # -18000     0 EST
        datetime(1948,  4, 25,  7,  0,  0), # -14400  3600 EDT
        datetime(1948,  9, 26,  6,  0,  0), # -18000     0 EST
        datetime(1949,  4, 24,  7,  0,  0), # -14400  3600 EDT
        datetime(1949,  9, 25,  6,  0,  0), # -18000     0 EST
        datetime(1950,  4, 30,  7,  0,  0), # -14400  3600 EDT
        datetime(1950,  9, 24,  6,  0,  0), # -18000     0 EST
        datetime(1951,  4, 29,  7,  0,  0), # -14400  3600 EDT
        datetime(1951,  9, 30,  6,  0,  0), # -18000     0 EST
        datetime(1952,  4, 27,  7,  0,  0), # -14400  3600 EDT
        datetime(1952,  9, 28,  6,  0,  0), # -18000     0 EST
        datetime(1953,  4, 26,  7,  0,  0), # -14400  3600 EDT
        datetime(1953,  9, 27,  6,  0,  0), # -18000     0 EST
        datetime(1954,  4, 25,  7,  0,  0), # -14400  3600 EDT
        datetime(1954,  9, 26,  6,  0,  0), # -18000     0 EST
        datetime(1955,  4, 24,  7,  0,  0), # -14400  3600 EDT
        datetime(1955, 10, 30,  6,  0,  0), # -18000     0 EST
        datetime(1956,  4, 29,  7,  0,  0), # -14400  3600 EDT
        datetime(1956, 10, 28,  6,  0,  0), # -18000     0 EST
        datetime(1957,  4, 28,  7,  0,  0), # -14400  3600 EDT
        datetime(1957, 10, 27,  6,  0,  0), # -18000     0 EST
        datetime(1958,  4, 27,  7,  0,  0), # -14400  3600 EDT
        datetime(1958, 10, 26,  6,  0,  0), # -18000     0 EST
        datetime(1959,  4, 26,  7,  0,  0), # -14400  3600 EDT
        datetime(1959, 10, 25,  6,  0,  0), # -18000     0 EST
        datetime(1960,  4, 24,  7,  0,  0), # -14400  3600 EDT
        datetime(1960, 10, 30,  6,  0,  0), # -18000     0 EST
        datetime(1961,  4, 30,  7,  0,  0), # -14400  3600 EDT
        datetime(1961, 10, 29,  6,  0,  0), # -18000     0 EST
        datetime(1962,  4, 29,  7,  0,  0), # -14400  3600 EDT
        datetime(1962, 10, 28,  6,  0,  0), # -18000     0 EST
        datetime(1963,  4, 28,  7,  0,  0), # -14400  3600 EDT
        datetime(1963, 10, 27,  6,  0,  0), # -18000     0 EST
        datetime(1964,  4, 26,  7,  0,  0), # -14400  3600 EDT
        datetime(1964, 10, 25,  6,  0,  0), # -18000     0 EST
        datetime(1965,  4, 25,  7,  0,  0), # -14400  3600 EDT
        datetime(1965, 10, 31,  6,  0,  0), # -18000     0 EST
        datetime(1966,  4, 24,  7,  0,  0), # -14400  3600 EDT
        datetime(1966, 10, 30,  6,  0,  0), # -18000     0 EST
        datetime(1967,  4, 30,  7,  0,  0), # -14400  3600 EDT
        datetime(1967, 10, 29,  6,  0,  0), # -18000     0 EST
        datetime(1968,  4, 28,  7,  0,  0), # -14400  3600 EDT
        datetime(1968, 10, 27,  6,  0,  0), # -18000     0 EST
        datetime(1969,  4, 27,  7,  0,  0), # -14400  3600 EDT
        datetime(1969, 10, 26,  6,  0,  0), # -18000     0 EST
        datetime(1970,  4, 26,  7,  0,  0), # -14400  3600 EDT
        datetime(1970, 10, 25,  6,  0,  0), # -18000     0 EST
        datetime(1971,  4, 25,  7,  0,  0), # -14400  3600 EDT
        datetime(1971, 10, 31,  6,  0,  0), # -18000     0 EST
        datetime(1972,  4, 30,  7,  0,  0), # -14400  3600 EDT
        datetime(1972, 10, 29,  6,  0,  0), # -18000     0 EST
        datetime(1973,  4, 29,  7,  0,  0), # -14400  3600 EDT
        datetime(1973, 10, 28,  6,  0,  0), # -18000     0 EST
        datetime(1974,  1,  6,  7,  0,  0), # -14400  3600 EDT
        datetime(1974, 10, 27,  6,  0,  0), # -18000     0 EST
        datetime(1975,  2, 23,  7,  0,  0), # -14400  3600 EDT
        datetime(1975, 10, 26,  6,  0,  0), # -18000     0 EST
        datetime(1976,  4, 25,  7,  0,  0), # -14400  3600 EDT
        datetime(1976, 10, 31,  6,  0,  0), # -18000     0 EST
        datetime(1977,  4, 24,  7,  0,  0), # -14400  3600 EDT
        datetime(1977, 10, 30,  6,  0,  0), # -18000     0 EST
        datetime(1978,  4, 30,  7,  0,  0), # -14400  3600 EDT
        datetime(1978, 10, 29,  6,  0,  0), # -18000     0 EST
        datetime(1979,  4, 29,  7,  0,  0), # -14400  3600 EDT
        datetime(1979, 10, 28,  6,  0,  0), # -18000     0 EST
        datetime(1980,  4, 27,  7,  0,  0), # -14400  3600 EDT
        datetime(1980, 10, 26,  6,  0,  0), # -18000     0 EST
        datetime(1981,  4, 26,  7,  0,  0), # -14400  3600 EDT
        datetime(1981, 10, 25,  6,  0,  0), # -18000     0 EST
        datetime(1982,  4, 25,  7,  0,  0), # -14400  3600 EDT
        datetime(1982, 10, 31,  6,  0,  0), # -18000     0 EST
        datetime(1983,  4, 24,  7,  0,  0), # -14400  3600 EDT
        datetime(1983, 10, 30,  6,  0,  0), # -18000     0 EST
        datetime(1984,  4, 29,  7,  0,  0), # -14400  3600 EDT
        datetime(1984, 10, 28,  6,  0,  0), # -18000     0 EST
        datetime(1985,  4, 28,  7,  0,  0), # -14400  3600 EDT
        datetime(1985, 10, 27,  6,  0,  0), # -18000     0 EST
        datetime(1986,  4, 27,  7,  0,  0), # -14400  3600 EDT
        datetime(1986, 10, 26,  6,  0,  0), # -18000     0 EST
        datetime(1987,  4,  5,  7,  0,  0), # -14400  3600 EDT
        datetime(1987, 10, 25,  6,  0,  0), # -18000     0 EST
        datetime(1988,  4,  3,  7,  0,  0), # -14400  3600 EDT
        datetime(1988, 10, 30,  6,  0,  0), # -18000     0 EST
        datetime(1989,  4,  2,  7,  0,  0), # -14400  3600 EDT
        datetime(1989, 10, 29,  6,  0,  0), # -18000     0 EST
        datetime(1990,  4,  1,  7,  0,  0), # -14400  3600 EDT
        datetime(1990, 10, 28,  6,  0,  0), # -18000     0 EST
        datetime(1991,  4,  7,  7,  0,  0), # -14400  3600 EDT
        datetime(1991, 10, 27,  6,  0,  0), # -18000     0 EST
        datetime(1992,  4,  5,  7,  0,  0), # -14400  3600 EDT
        datetime(1992, 10, 25,  6,  0,  0), # -18000     0 EST
        datetime(1993,  4,  4,  7,  0,  0), # -14400  3600 EDT
        datetime(1993, 10, 31,  6,  0,  0), # -18000     0 EST
        datetime(1994,  4,  3,  7,  0,  0), # -14400  3600 EDT
        datetime(1994, 10, 30,  6,  0,  0), # -18000     0 EST
        datetime(1995,  4,  2,  7,  0,  0), # -14400  3600 EDT
        datetime(1995, 10, 29,  6,  0,  0), # -18000     0 EST
        datetime(1996,  4,  7,  7,  0,  0), # -14400  3600 EDT
        datetime(1996, 10, 27,  6,  0,  0), # -18000     0 EST
        datetime(1997,  4,  6,  7,  0,  0), # -14400  3600 EDT
        datetime(1997, 10, 26,  6,  0,  0), # -18000     0 EST
        datetime(1998,  4,  5,  7,  0,  0), # -14400  3600 EDT
        datetime(1998, 10, 25,  6,  0,  0), # -18000     0 EST
        datetime(1999,  4,  4,  7,  0,  0), # -14400  3600 EDT
        datetime(1999, 10, 31,  6,  0,  0), # -18000     0 EST
        datetime(2000,  4,  2,  7,  0,  0), # -14400  3600 EDT
        datetime(2000, 10, 29,  6,  0,  0), # -18000     0 EST
        datetime(2001,  4,  1,  7,  0,  0), # -14400  3600 EDT
        datetime(2001, 10, 28,  6,  0,  0), # -18000     0 EST
        datetime(2002,  4,  7,  7,  0,  0), # -14400  3600 EDT
        datetime(2002, 10, 27,  6,  0,  0), # -18000     0 EST
        datetime(2003,  4,  6,  7,  0,  0), # -14400  3600 EDT
        datetime(2003, 10, 26,  6,  0,  0), # -18000     0 EST
        datetime(2004,  4,  4,  7,  0,  0), # -14400  3600 EDT
        datetime(2004, 10, 31,  6,  0,  0), # -18000     0 EST
        datetime(2005,  4,  3,  7,  0,  0), # -14400  3600 EDT
        datetime(2005, 10, 30,  6,  0,  0), # -18000     0 EST
        datetime(2006,  4,  2,  7,  0,  0), # -14400  3600 EDT
        datetime(2006, 10, 29,  6,  0,  0), # -18000     0 EST
        datetime(2007,  4,  1,  7,  0,  0), # -14400  3600 EDT
        datetime(2007, 10, 28,  6,  0,  0), # -18000     0 EST
        datetime(2008,  4,  6,  7,  0,  0), # -14400  3600 EDT
        datetime(2008, 10, 26,  6,  0,  0), # -18000     0 EST
        datetime(2009,  4,  5,  7,  0,  0), # -14400  3600 EDT
        datetime(2009, 10, 25,  6,  0,  0), # -18000     0 EST
        datetime(2010,  4,  4,  7,  0,  0), # -14400  3600 EDT
        datetime(2010, 10, 31,  6,  0,  0), # -18000     0 EST
        datetime(2011,  4,  3,  7,  0,  0), # -14400  3600 EDT
        datetime(2011, 10, 30,  6,  0,  0), # -18000     0 EST
        datetime(2012,  4,  1,  7,  0,  0), # -14400  3600 EDT
        datetime(2012, 10, 28,  6,  0,  0), # -18000     0 EST
        datetime(2013,  4,  7,  7,  0,  0), # -14400  3600 EDT
        datetime(2013, 10, 27,  6,  0,  0), # -18000     0 EST
        datetime(2014,  4,  6,  7,  0,  0), # -14400  3600 EDT
        datetime(2014, 10, 26,  6,  0,  0), # -18000     0 EST
        datetime(2015,  4,  5,  7,  0,  0), # -14400  3600 EDT
        datetime(2015, 10, 25,  6,  0,  0), # -18000     0 EST
        datetime(2016,  4,  3,  7,  0,  0), # -14400  3600 EDT
        datetime(2016, 10, 30,  6,  0,  0), # -18000     0 EST
        datetime(2017,  4,  2,  7,  0,  0), # -14400  3600 EDT
        datetime(2017, 10, 29,  6,  0,  0), # -18000     0 EST
        datetime(2018,  4,  1,  7,  0,  0), # -14400  3600 EDT
        datetime(2018, 10, 28,  6,  0,  0), # -18000     0 EST
        datetime(2019,  4,  7,  7,  0,  0), # -14400  3600 EDT
        datetime(2019, 10, 27,  6,  0,  0), # -18000     0 EST
        datetime(2020,  4,  5,  7,  0,  0), # -14400  3600 EDT
        datetime(2020, 10, 25,  6,  0,  0), # -18000     0 EST
        datetime(2021,  4,  4,  7,  0,  0), # -14400  3600 EDT
        datetime(2021, 10, 31,  6,  0,  0), # -18000     0 EST
        datetime(2022,  4,  3,  7,  0,  0), # -14400  3600 EDT
        datetime(2022, 10, 30,  6,  0,  0), # -18000     0 EST
        datetime(2023,  4,  2,  7,  0,  0), # -14400  3600 EDT
        datetime(2023, 10, 29,  6,  0,  0), # -18000     0 EST
        datetime(2024,  4,  7,  7,  0,  0), # -14400  3600 EDT
        datetime(2024, 10, 27,  6,  0,  0), # -18000     0 EST
        datetime(2025,  4,  6,  7,  0,  0), # -14400  3600 EDT
        datetime(2025, 10, 26,  6,  0,  0), # -18000     0 EST
        datetime(2026,  4,  5,  7,  0,  0), # -14400  3600 EDT
        datetime(2026, 10, 25,  6,  0,  0), # -18000     0 EST
        datetime(2027,  4,  4,  7,  0,  0), # -14400  3600 EDT
        datetime(2027, 10, 31,  6,  0,  0), # -18000     0 EST
        datetime(2028,  4,  2,  7,  0,  0), # -14400  3600 EDT
        datetime(2028, 10, 29,  6,  0,  0), # -18000     0 EST
        datetime(2029,  4,  1,  7,  0,  0), # -14400  3600 EDT
        datetime(2029, 10, 28,  6,  0,  0), # -18000     0 EST
        datetime(2030,  4,  7,  7,  0,  0), # -14400  3600 EDT
        datetime(2030, 10, 27,  6,  0,  0), # -18000     0 EST
        datetime(2031,  4,  6,  7,  0,  0), # -14400  3600 EDT
        datetime(2031, 10, 26,  6,  0,  0), # -18000     0 EST
        datetime(2032,  4,  4,  7,  0,  0), # -14400  3600 EDT
        datetime(2032, 10, 31,  6,  0,  0), # -18000     0 EST
        datetime(2033,  4,  3,  7,  0,  0), # -14400  3600 EDT
        datetime(2033, 10, 30,  6,  0,  0), # -18000     0 EST
        datetime(2034,  4,  2,  7,  0,  0), # -14400  3600 EDT
        datetime(2034, 10, 29,  6,  0,  0), # -18000     0 EST
        datetime(2035,  4,  1,  7,  0,  0), # -14400  3600 EDT
        datetime(2035, 10, 28,  6,  0,  0), # -18000     0 EST
        datetime(2036,  4,  6,  7,  0,  0), # -14400  3600 EDT
        datetime(2036, 10, 26,  6,  0,  0), # -18000     0 EST
        datetime(2037,  4,  5,  7,  0,  0), # -14400  3600 EDT
        datetime(2037, 10, 25,  6,  0,  0), # -18000     0 EST
        ]

    _transition_info = [
        ttinfo(-18000,      0,  'EST'),
        ttinfo(-14400,   3600,  'EDT'),
        ttinfo(-18000,      0,  'EST'),
        ttinfo(-14400,   3600,  'EDT'),
        ttinfo(-18000,      0,  'EST'),
        ttinfo(-14400,   3600,  'EDT'),
        ttinfo(-18000,      0,  'EST'),
        ttinfo(-14400,   3600,  'EDT'),
        ttinfo(-18000,      0,  'EST'),
        ttinfo(-14400,   3600,  'EDT'),
        ttinfo(-18000,      0,  'EST'),
        ttinfo(-14400,   3600,  'EDT'),
        ttinfo(-18000,      0,  'EST'),
        ttinfo(-14400,   3600,  'EDT'),
        ttinfo(-18000,      0,  'EST'),
        ttinfo(-14400,   3600,  'EDT'),
        ttinfo(-18000,      0,  'EST'),
        ttinfo(-14400,   3600,  'EDT'),
        ttinfo(-18000,      0,  'EST'),
        ttinfo(-14400,   3600,  'EDT'),
        ttinfo(-18000,      0,  'EST'),
        ttinfo(-14400,   3600,  'EDT'),
        ttinfo(-18000,      0,  'EST'),
        ttinfo(-14400,   3600,  'EDT'),
        ttinfo(-18000,      0,  'EST'),
        ttinfo(-14400,   3600,  'EDT'),
        ttinfo(-18000,      0,  'EST'),
        ttinfo(-14400,   3600,  'EDT'),
        ttinfo(-18000,      0,  'EST'),
        ttinfo(-14400,   3600,  'EDT'),
        ttinfo(-18000,      0,  'EST'),
        ttinfo(-14400,   3600,  'EDT'),
        ttinfo(-18000,      0,  'EST'),
        ttinfo(-14400,   3600,  'EDT'),
        ttinfo(-18000,      0,  'EST'),
        ttinfo(-14400,   3600,  'EDT'),
        ttinfo(-18000,      0,  'EST'),
        ttinfo(-14400,   3600,  'EDT'),
        ttinfo(-18000,      0,  'EST'),
        ttinfo(-14400,   3600,  'EDT'),
        ttinfo(-18000,      0,  'EST'),
        ttinfo(-14400,   3600,  'EDT'),
        ttinfo(-18000,      0,  'EST'),
        ttinfo(-14400,   3600,  'EDT'),
        ttinfo(-18000,      0,  'EST'),
        ttinfo(-14400,   3600,  'EDT'),
        ttinfo(-18000,      0,  'EST'),
        ttinfo(-14400,   3600,  'EDT'),
        ttinfo(-18000,      0,  'EST'),
        ttinfo(-14400,   3600,  'EWT'),
        ttinfo(-14400,      0,  'EPT'),
        ttinfo(-18000,      0,  'EST'),
        ttinfo(-14400,   3600,  'EDT'),
        ttinfo(-18000,      0,  'EST'),
        ttinfo(-14400,   3600,  'EDT'),
        ttinfo(-18000,      0,  'EST'),
        ttinfo(-14400,   3600,  'EDT'),
        ttinfo(-18000,      0,  'EST'),
        ttinfo(-14400,   3600,  'EDT'),
        ttinfo(-18000,      0,  'EST'),
        ttinfo(-14400,   3600,  'EDT'),
        ttinfo(-18000,      0,  'EST'),
        ttinfo(-14400,   3600,  'EDT'),
        ttinfo(-18000,      0,  'EST'),
        ttinfo(-14400,   3600,  'EDT'),
        ttinfo(-18000,      0,  'EST'),
        ttinfo(-14400,   3600,  'EDT'),
        ttinfo(-18000,      0,  'EST'),
        ttinfo(-14400,   3600,  'EDT'),
        ttinfo(-18000,      0,  'EST'),
        ttinfo(-14400,   3600,  'EDT'),
        ttinfo(-18000,      0,  'EST'),
        ttinfo(-14400,   3600,  'EDT'),
        ttinfo(-18000,      0,  'EST'),
        ttinfo(-14400,   3600,  'EDT'),
        ttinfo(-18000,      0,  'EST'),
        ttinfo(-14400,   3600,  'EDT'),
        ttinfo(-18000,      0,  'EST'),
        ttinfo(-14400,   3600,  'EDT'),
        ttinfo(-18000,      0,  'EST'),
        ttinfo(-14400,   3600,  'EDT'),
        ttinfo(-18000,      0,  'EST'),
        ttinfo(-14400,   3600,  'EDT'),
        ttinfo(-18000,      0,  'EST'),
        ttinfo(-14400,   3600,  'EDT'),
        ttinfo(-18000,      0,  'EST'),
        ttinfo(-14400,   3600,  'EDT'),
        ttinfo(-18000,      0,  'EST'),
        ttinfo(-14400,   3600,  'EDT'),
        ttinfo(-18000,      0,  'EST'),
        ttinfo(-14400,   3600,  'EDT'),
        ttinfo(-18000,      0,  'EST'),
        ttinfo(-14400,   3600,  'EDT'),
        ttinfo(-18000,      0,  'EST'),
        ttinfo(-14400,   3600,  'EDT'),
        ttinfo(-18000,      0,  'EST'),
        ttinfo(-14400,   3600,  'EDT'),
        ttinfo(-18000,      0,  'EST'),
        ttinfo(-14400,   3600,  'EDT'),
        ttinfo(-18000,      0,  'EST'),
        ttinfo(-14400,   3600,  'EDT'),
        ttinfo(-18000,      0,  'EST'),
        ttinfo(-14400,   3600,  'EDT'),
        ttinfo(-18000,      0,  'EST'),
        ttinfo(-14400,   3600,  'EDT'),
        ttinfo(-18000,      0,  'EST'),
        ttinfo(-14400,   3600,  'EDT'),
        ttinfo(-18000,      0,  'EST'),
        ttinfo(-14400,   3600,  'EDT'),
        ttinfo(-18000,      0,  'EST'),
        ttinfo(-14400,   3600,  'EDT'),
        ttinfo(-18000,      0,  'EST'),
        ttinfo(-14400,   3600,  'EDT'),
        ttinfo(-18000,      0,  'EST'),
        ttinfo(-14400,   3600,  'EDT'),
        ttinfo(-18000,      0,  'EST'),
        ttinfo(-14400,   3600,  'EDT'),
        ttinfo(-18000,      0,  'EST'),
        ttinfo(-14400,   3600,  'EDT'),
        ttinfo(-18000,      0,  'EST'),
        ttinfo(-14400,   3600,  'EDT'),
        ttinfo(-18000,      0,  'EST'),
        ttinfo(-14400,   3600,  'EDT'),
        ttinfo(-18000,      0,  'EST'),
        ttinfo(-14400,   3600,  'EDT'),
        ttinfo(-18000,      0,  'EST'),
        ttinfo(-14400,   3600,  'EDT'),
        ttinfo(-18000,      0,  'EST'),
        ttinfo(-14400,   3600,  'EDT'),
        ttinfo(-18000,      0,  'EST'),
        ttinfo(-14400,   3600,  'EDT'),
        ttinfo(-18000,      0,  'EST'),
        ttinfo(-14400,   3600,  'EDT'),
        ttinfo(-18000,      0,  'EST'),
        ttinfo(-14400,   3600,  'EDT'),
        ttinfo(-18000,      0,  'EST'),
        ttinfo(-14400,   3600,  'EDT'),
        ttinfo(-18000,      0,  'EST'),
        ttinfo(-14400,   3600,  'EDT'),
        ttinfo(-18000,      0,  'EST'),
        ttinfo(-14400,   3600,  'EDT'),
        ttinfo(-18000,      0,  'EST'),
        ttinfo(-14400,   3600,  'EDT'),
        ttinfo(-18000,      0,  'EST'),
        ttinfo(-14400,   3600,  'EDT'),
        ttinfo(-18000,      0,  'EST'),
        ttinfo(-14400,   3600,  'EDT'),
        ttinfo(-18000,      0,  'EST'),
        ttinfo(-14400,   3600,  'EDT'),
        ttinfo(-18000,      0,  'EST'),
        ttinfo(-14400,   3600,  'EDT'),
        ttinfo(-18000,      0,  'EST'),
        ttinfo(-14400,   3600,  'EDT'),
        ttinfo(-18000,      0,  'EST'),
        ttinfo(-14400,   3600,  'EDT'),
        ttinfo(-18000,      0,  'EST'),
        ttinfo(-14400,   3600,  'EDT'),
        ttinfo(-18000,      0,  'EST'),
        ttinfo(-14400,   3600,  'EDT'),
        ttinfo(-18000,      0,  'EST'),
        ttinfo(-14400,   3600,  'EDT'),
        ttinfo(-18000,      0,  'EST'),
        ttinfo(-14400,   3600,  'EDT'),
        ttinfo(-18000,      0,  'EST'),
        ttinfo(-14400,   3600,  'EDT'),
        ttinfo(-18000,      0,  'EST'),
        ttinfo(-14400,   3600,  'EDT'),
        ttinfo(-18000,      0,  'EST'),
        ttinfo(-14400,   3600,  'EDT'),
        ttinfo(-18000,      0,  'EST'),
        ttinfo(-14400,   3600,  'EDT'),
        ttinfo(-18000,      0,  'EST'),
        ttinfo(-14400,   3600,  'EDT'),
        ttinfo(-18000,      0,  'EST'),
        ttinfo(-14400,   3600,  'EDT'),
        ttinfo(-18000,      0,  'EST'),
        ttinfo(-14400,   3600,  'EDT'),
        ttinfo(-18000,      0,  'EST'),
        ttinfo(-14400,   3600,  'EDT'),
        ttinfo(-18000,      0,  'EST'),
        ttinfo(-14400,   3600,  'EDT'),
        ttinfo(-18000,      0,  'EST'),
        ttinfo(-14400,   3600,  'EDT'),
        ttinfo(-18000,      0,  'EST'),
        ttinfo(-14400,   3600,  'EDT'),
        ttinfo(-18000,      0,  'EST'),
        ttinfo(-14400,   3600,  'EDT'),
        ttinfo(-18000,      0,  'EST'),
        ttinfo(-14400,   3600,  'EDT'),
        ttinfo(-18000,      0,  'EST'),
        ttinfo(-14400,   3600,  'EDT'),
        ttinfo(-18000,      0,  'EST'),
        ttinfo(-14400,   3600,  'EDT'),
        ttinfo(-18000,      0,  'EST'),
        ttinfo(-14400,   3600,  'EDT'),
        ttinfo(-18000,      0,  'EST'),
        ttinfo(-14400,   3600,  'EDT'),
        ttinfo(-18000,      0,  'EST'),
        ttinfo(-14400,   3600,  'EDT'),
        ttinfo(-18000,      0,  'EST'),
        ttinfo(-14400,   3600,  'EDT'),
        ttinfo(-18000,      0,  'EST'),
        ttinfo(-14400,   3600,  'EDT'),
        ttinfo(-18000,      0,  'EST'),
        ttinfo(-14400,   3600,  'EDT'),
        ttinfo(-18000,      0,  'EST'),
        ttinfo(-14400,   3600,  'EDT'),
        ttinfo(-18000,      0,  'EST'),
        ttinfo(-14400,   3600,  'EDT'),
        ttinfo(-18000,      0,  'EST'),
        ttinfo(-14400,   3600,  'EDT'),
        ttinfo(-18000,      0,  'EST'),
        ttinfo(-14400,   3600,  'EDT'),
        ttinfo(-18000,      0,  'EST'),
        ttinfo(-14400,   3600,  'EDT'),
        ttinfo(-18000,      0,  'EST'),
        ttinfo(-14400,   3600,  'EDT'),
        ttinfo(-18000,      0,  'EST'),
        ttinfo(-14400,   3600,  'EDT'),
        ttinfo(-18000,      0,  'EST'),
        ttinfo(-14400,   3600,  'EDT'),
        ttinfo(-18000,      0,  'EST'),
        ttinfo(-14400,   3600,  'EDT'),
        ttinfo(-18000,      0,  'EST'),
        ttinfo(-14400,   3600,  'EDT'),
        ttinfo(-18000,      0,  'EST'),
        ttinfo(-14400,   3600,  'EDT'),
        ttinfo(-18000,      0,  'EST'),
        ttinfo(-14400,   3600,  'EDT'),
        ttinfo(-18000,      0,  'EST'),
        ttinfo(-14400,   3600,  'EDT'),
        ttinfo(-18000,      0,  'EST'),
        ttinfo(-14400,   3600,  'EDT'),
        ttinfo(-18000,      0,  'EST'),
        ttinfo(-14400,   3600,  'EDT'),
        ttinfo(-18000,      0,  'EST'),
        ]

posixrules = posixrules() # Singleton

