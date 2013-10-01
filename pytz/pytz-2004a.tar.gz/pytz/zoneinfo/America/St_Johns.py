'''
tzinfo timezone information for America/St_Johns.

Generated from the Olson timezone database:
    ftp://elsie.nci.nih.gov/pub/tz*.tar.gz
'''

from pytz.tzinfo import DstTzInfo
from pytz.tzinfo import memorized_datetime as datetime
from pytz.tzinfo import memorized_ttinfo as ttinfo

class St_Johns(DstTzInfo):
    '''America/St_Johns timezone definition. See datetime.tzinfo for details'''

    _zone = 'America/St_Johns'

    _utc_transition_times = [
        datetime(   1,  1,  1,  0,  0,  0), # -12652     0 NST
        datetime(1917,  4,  8,  5, 30, 52), #  -9052  3600 NDT
        datetime(1917,  9, 17,  4, 30, 52), # -12652     0 NST
        datetime(1918,  4, 14,  5, 30, 52), #  -9052  3600 NDT
        datetime(1918, 10, 31,  4, 30, 52), # -12652     0 NST
        datetime(1919,  5,  6,  2, 30, 52), #  -9052  3600 NDT
        datetime(1919,  8, 13,  1, 30, 52), # -12652     0 NST
        datetime(1920,  5,  3,  2, 30, 52), #  -9052  3600 NDT
        datetime(1920, 11,  1,  1, 30, 52), # -12652     0 NST
        datetime(1921,  5,  2,  2, 30, 52), #  -9052  3600 NDT
        datetime(1921, 10, 31,  1, 30, 52), # -12652     0 NST
        datetime(1922,  5,  8,  2, 30, 52), #  -9052  3600 NDT
        datetime(1922, 10, 30,  1, 30, 52), # -12652     0 NST
        datetime(1923,  5,  7,  2, 30, 52), #  -9052  3600 NDT
        datetime(1923, 10, 29,  1, 30, 52), # -12652     0 NST
        datetime(1924,  5,  5,  2, 30, 52), #  -9052  3600 NDT
        datetime(1924, 10, 27,  1, 30, 52), # -12652     0 NST
        datetime(1925,  5,  4,  2, 30, 52), #  -9052  3600 NDT
        datetime(1925, 10, 26,  1, 30, 52), # -12652     0 NST
        datetime(1926,  5,  3,  2, 30, 52), #  -9052  3600 NDT
        datetime(1926, 11,  1,  1, 30, 52), # -12652     0 NST
        datetime(1927,  5,  2,  2, 30, 52), #  -9052  3600 NDT
        datetime(1927, 10, 31,  1, 30, 52), # -12652     0 NST
        datetime(1928,  5,  7,  2, 30, 52), #  -9052  3600 NDT
        datetime(1928, 10, 29,  1, 30, 52), # -12652     0 NST
        datetime(1929,  5,  6,  2, 30, 52), #  -9052  3600 NDT
        datetime(1929, 10, 28,  1, 30, 52), # -12652     0 NST
        datetime(1930,  5,  5,  2, 30, 52), #  -9052  3600 NDT
        datetime(1930, 10, 27,  1, 30, 52), # -12652     0 NST
        datetime(1931,  5,  4,  2, 30, 52), #  -9052  3600 NDT
        datetime(1931, 10, 26,  1, 30, 52), # -12652     0 NST
        datetime(1932,  5,  2,  2, 30, 52), #  -9052  3600 NDT
        datetime(1932, 10, 31,  1, 30, 52), # -12652     0 NST
        datetime(1933,  5,  8,  2, 30, 52), #  -9052  3600 NDT
        datetime(1933, 10, 30,  1, 30, 52), # -12652     0 NST
        datetime(1934,  5,  7,  2, 30, 52), #  -9052  3600 NDT
        datetime(1934, 10, 29,  1, 30, 52), # -12652     0 NST
        datetime(1935,  3, 30,  3, 30, 52), # -12600     0 NST
        datetime(1935,  5,  6,  2, 30,  0), #  -9000  3600 NDT
        datetime(1935, 10, 28,  1, 30,  0), # -12600     0 NST
        datetime(1936,  5, 11,  3, 30,  0), #  -9000  3600 NDT
        datetime(1936, 10,  5,  2, 30,  0), # -12600     0 NST
        datetime(1937,  5, 10,  3, 30,  0), #  -9000  3600 NDT
        datetime(1937, 10,  4,  2, 30,  0), # -12600     0 NST
        datetime(1938,  5,  9,  3, 30,  0), #  -9000  3600 NDT
        datetime(1938, 10,  3,  2, 30,  0), # -12600     0 NST
        datetime(1939,  5, 15,  3, 30,  0), #  -9000  3600 NDT
        datetime(1939, 10,  2,  2, 30,  0), # -12600     0 NST
        datetime(1940,  5, 13,  3, 30,  0), #  -9000  3600 NDT
        datetime(1940, 10,  7,  2, 30,  0), # -12600     0 NST
        datetime(1941,  5, 12,  3, 30,  0), #  -9000  3600 NDT
        datetime(1941, 10,  6,  2, 30,  0), # -12600     0 NST
        datetime(1942,  5, 11,  3, 30,  0), #  -9000  3600 NWT
        datetime(1945,  8, 14, 23,  0,  0), #  -9000     0 NPT
        datetime(1945,  9, 30,  4, 30,  0), # -12600     0 NST
        datetime(1946,  5, 12,  5, 30,  0), #  -9000  3600 NDT
        datetime(1946, 10,  6,  4, 30,  0), # -12600     0 NST
        datetime(1947,  5, 11,  5, 30,  0), #  -9000  3600 NDT
        datetime(1947, 10,  5,  4, 30,  0), # -12600     0 NST
        datetime(1948,  5,  9,  5, 30,  0), #  -9000  3600 NDT
        datetime(1948, 10,  3,  4, 30,  0), # -12600     0 NST
        datetime(1949,  5,  8,  5, 30,  0), #  -9000  3600 NDT
        datetime(1949, 10,  2,  4, 30,  0), # -12600     0 NST
        datetime(1950,  5, 14,  5, 30,  0), #  -9000  3600 NDT
        datetime(1950, 10,  8,  4, 30,  0), # -12600     0 NST
        datetime(1951,  4, 29,  5, 30,  0), #  -9000  3600 NDT
        datetime(1951,  9, 30,  4, 30,  0), # -12600     0 NST
        datetime(1952,  4, 27,  5, 30,  0), #  -9000  3600 NDT
        datetime(1952,  9, 28,  4, 30,  0), # -12600     0 NST
        datetime(1953,  4, 26,  5, 30,  0), #  -9000  3600 NDT
        datetime(1953,  9, 27,  4, 30,  0), # -12600     0 NST
        datetime(1954,  4, 25,  5, 30,  0), #  -9000  3600 NDT
        datetime(1954,  9, 26,  4, 30,  0), # -12600     0 NST
        datetime(1955,  4, 24,  5, 30,  0), #  -9000  3600 NDT
        datetime(1955,  9, 25,  4, 30,  0), # -12600     0 NST
        datetime(1956,  4, 29,  5, 30,  0), #  -9000  3600 NDT
        datetime(1956,  9, 30,  4, 30,  0), # -12600     0 NST
        datetime(1957,  4, 28,  5, 30,  0), #  -9000  3600 NDT
        datetime(1957,  9, 29,  4, 30,  0), # -12600     0 NST
        datetime(1958,  4, 27,  5, 30,  0), #  -9000  3600 NDT
        datetime(1958,  9, 28,  4, 30,  0), # -12600     0 NST
        datetime(1959,  4, 26,  5, 30,  0), #  -9000  3600 NDT
        datetime(1959,  9, 27,  4, 30,  0), # -12600     0 NST
        datetime(1960,  4, 24,  5, 30,  0), #  -9000  3600 NDT
        datetime(1960, 10, 30,  4, 30,  0), # -12600     0 NST
        datetime(1961,  4, 30,  5, 30,  0), #  -9000  3600 NDT
        datetime(1961, 10, 29,  4, 30,  0), # -12600     0 NST
        datetime(1962,  4, 29,  5, 30,  0), #  -9000  3600 NDT
        datetime(1962, 10, 28,  4, 30,  0), # -12600     0 NST
        datetime(1963,  4, 28,  5, 30,  0), #  -9000  3600 NDT
        datetime(1963, 10, 27,  4, 30,  0), # -12600     0 NST
        datetime(1964,  4, 26,  5, 30,  0), #  -9000  3600 NDT
        datetime(1964, 10, 25,  4, 30,  0), # -12600     0 NST
        datetime(1965,  4, 25,  5, 30,  0), #  -9000  3600 NDT
        datetime(1965, 10, 31,  4, 30,  0), # -12600     0 NST
        datetime(1966,  4, 24,  5, 30,  0), #  -9000  3600 NDT
        datetime(1966, 10, 30,  4, 30,  0), # -12600     0 NST
        datetime(1967,  4, 30,  5, 30,  0), #  -9000  3600 NDT
        datetime(1967, 10, 29,  4, 30,  0), # -12600     0 NST
        datetime(1968,  4, 28,  5, 30,  0), #  -9000  3600 NDT
        datetime(1968, 10, 27,  4, 30,  0), # -12600     0 NST
        datetime(1969,  4, 27,  5, 30,  0), #  -9000  3600 NDT
        datetime(1969, 10, 26,  4, 30,  0), # -12600     0 NST
        datetime(1970,  4, 26,  5, 30,  0), #  -9000  3600 NDT
        datetime(1970, 10, 25,  4, 30,  0), # -12600     0 NST
        datetime(1971,  4, 25,  5, 30,  0), #  -9000  3600 NDT
        datetime(1971, 10, 31,  4, 30,  0), # -12600     0 NST
        datetime(1972,  4, 30,  5, 30,  0), #  -9000  3600 NDT
        datetime(1972, 10, 29,  4, 30,  0), # -12600     0 NST
        datetime(1973,  4, 29,  5, 30,  0), #  -9000  3600 NDT
        datetime(1973, 10, 28,  4, 30,  0), # -12600     0 NST
        datetime(1974,  4, 28,  5, 30,  0), #  -9000  3600 NDT
        datetime(1974, 10, 27,  4, 30,  0), # -12600     0 NST
        datetime(1975,  4, 27,  5, 30,  0), #  -9000  3600 NDT
        datetime(1975, 10, 26,  4, 30,  0), # -12600     0 NST
        datetime(1976,  4, 25,  5, 30,  0), #  -9000  3600 NDT
        datetime(1976, 10, 31,  4, 30,  0), # -12600     0 NST
        datetime(1977,  4, 24,  5, 30,  0), #  -9000  3600 NDT
        datetime(1977, 10, 30,  4, 30,  0), # -12600     0 NST
        datetime(1978,  4, 30,  5, 30,  0), #  -9000  3600 NDT
        datetime(1978, 10, 29,  4, 30,  0), # -12600     0 NST
        datetime(1979,  4, 29,  5, 30,  0), #  -9000  3600 NDT
        datetime(1979, 10, 28,  4, 30,  0), # -12600     0 NST
        datetime(1980,  4, 27,  5, 30,  0), #  -9000  3600 NDT
        datetime(1980, 10, 26,  4, 30,  0), # -12600     0 NST
        datetime(1981,  4, 26,  5, 30,  0), #  -9000  3600 NDT
        datetime(1981, 10, 25,  4, 30,  0), # -12600     0 NST
        datetime(1982,  4, 25,  5, 30,  0), #  -9000  3600 NDT
        datetime(1982, 10, 31,  4, 30,  0), # -12600     0 NST
        datetime(1983,  4, 24,  5, 30,  0), #  -9000  3600 NDT
        datetime(1983, 10, 30,  4, 30,  0), # -12600     0 NST
        datetime(1984,  4, 29,  5, 30,  0), #  -9000  3600 NDT
        datetime(1984, 10, 28,  4, 30,  0), # -12600     0 NST
        datetime(1985,  4, 28,  5, 30,  0), #  -9000  3600 NDT
        datetime(1985, 10, 27,  4, 30,  0), # -12600     0 NST
        datetime(1986,  4, 27,  5, 30,  0), #  -9000  3600 NDT
        datetime(1986, 10, 26,  4, 30,  0), # -12600     0 NST
        datetime(1987,  4,  5,  3, 31,  0), #  -9000  3600 NDT
        datetime(1987, 10, 25,  2, 31,  0), # -12600     0 NST
        datetime(1988,  4,  3,  3, 31,  0), #  -5400  7200 NDDT
        datetime(1988, 10, 30,  1, 31,  0), # -12600     0 NST
        datetime(1989,  4,  2,  3, 31,  0), #  -9000  3600 NDT
        datetime(1989, 10, 29,  2, 31,  0), # -12600     0 NST
        datetime(1990,  4,  1,  3, 31,  0), #  -9000  3600 NDT
        datetime(1990, 10, 28,  2, 31,  0), # -12600     0 NST
        datetime(1991,  4,  7,  3, 31,  0), #  -9000  3600 NDT
        datetime(1991, 10, 27,  2, 31,  0), # -12600     0 NST
        datetime(1992,  4,  5,  3, 31,  0), #  -9000  3600 NDT
        datetime(1992, 10, 25,  2, 31,  0), # -12600     0 NST
        datetime(1993,  4,  4,  3, 31,  0), #  -9000  3600 NDT
        datetime(1993, 10, 31,  2, 31,  0), # -12600     0 NST
        datetime(1994,  4,  3,  3, 31,  0), #  -9000  3600 NDT
        datetime(1994, 10, 30,  2, 31,  0), # -12600     0 NST
        datetime(1995,  4,  2,  3, 31,  0), #  -9000  3600 NDT
        datetime(1995, 10, 29,  2, 31,  0), # -12600     0 NST
        datetime(1996,  4,  7,  3, 31,  0), #  -9000  3600 NDT
        datetime(1996, 10, 27,  2, 31,  0), # -12600     0 NST
        datetime(1997,  4,  6,  3, 31,  0), #  -9000  3600 NDT
        datetime(1997, 10, 26,  2, 31,  0), # -12600     0 NST
        datetime(1998,  4,  5,  3, 31,  0), #  -9000  3600 NDT
        datetime(1998, 10, 25,  2, 31,  0), # -12600     0 NST
        datetime(1999,  4,  4,  3, 31,  0), #  -9000  3600 NDT
        datetime(1999, 10, 31,  2, 31,  0), # -12600     0 NST
        datetime(2000,  4,  2,  3, 31,  0), #  -9000  3600 NDT
        datetime(2000, 10, 29,  2, 31,  0), # -12600     0 NST
        datetime(2001,  4,  1,  3, 31,  0), #  -9000  3600 NDT
        datetime(2001, 10, 28,  2, 31,  0), # -12600     0 NST
        datetime(2002,  4,  7,  3, 31,  0), #  -9000  3600 NDT
        datetime(2002, 10, 27,  2, 31,  0), # -12600     0 NST
        datetime(2003,  4,  6,  3, 31,  0), #  -9000  3600 NDT
        datetime(2003, 10, 26,  2, 31,  0), # -12600     0 NST
        datetime(2004,  4,  4,  3, 31,  0), #  -9000  3600 NDT
        datetime(2004, 10, 31,  2, 31,  0), # -12600     0 NST
        datetime(2005,  4,  3,  3, 31,  0), #  -9000  3600 NDT
        datetime(2005, 10, 30,  2, 31,  0), # -12600     0 NST
        datetime(2006,  4,  2,  3, 31,  0), #  -9000  3600 NDT
        datetime(2006, 10, 29,  2, 31,  0), # -12600     0 NST
        datetime(2007,  4,  1,  3, 31,  0), #  -9000  3600 NDT
        datetime(2007, 10, 28,  2, 31,  0), # -12600     0 NST
        datetime(2008,  4,  6,  3, 31,  0), #  -9000  3600 NDT
        datetime(2008, 10, 26,  2, 31,  0), # -12600     0 NST
        datetime(2009,  4,  5,  3, 31,  0), #  -9000  3600 NDT
        datetime(2009, 10, 25,  2, 31,  0), # -12600     0 NST
        datetime(2010,  4,  4,  3, 31,  0), #  -9000  3600 NDT
        datetime(2010, 10, 31,  2, 31,  0), # -12600     0 NST
        datetime(2011,  4,  3,  3, 31,  0), #  -9000  3600 NDT
        datetime(2011, 10, 30,  2, 31,  0), # -12600     0 NST
        datetime(2012,  4,  1,  3, 31,  0), #  -9000  3600 NDT
        datetime(2012, 10, 28,  2, 31,  0), # -12600     0 NST
        datetime(2013,  4,  7,  3, 31,  0), #  -9000  3600 NDT
        datetime(2013, 10, 27,  2, 31,  0), # -12600     0 NST
        datetime(2014,  4,  6,  3, 31,  0), #  -9000  3600 NDT
        datetime(2014, 10, 26,  2, 31,  0), # -12600     0 NST
        datetime(2015,  4,  5,  3, 31,  0), #  -9000  3600 NDT
        datetime(2015, 10, 25,  2, 31,  0), # -12600     0 NST
        datetime(2016,  4,  3,  3, 31,  0), #  -9000  3600 NDT
        datetime(2016, 10, 30,  2, 31,  0), # -12600     0 NST
        datetime(2017,  4,  2,  3, 31,  0), #  -9000  3600 NDT
        datetime(2017, 10, 29,  2, 31,  0), # -12600     0 NST
        datetime(2018,  4,  1,  3, 31,  0), #  -9000  3600 NDT
        datetime(2018, 10, 28,  2, 31,  0), # -12600     0 NST
        datetime(2019,  4,  7,  3, 31,  0), #  -9000  3600 NDT
        datetime(2019, 10, 27,  2, 31,  0), # -12600     0 NST
        datetime(2020,  4,  5,  3, 31,  0), #  -9000  3600 NDT
        datetime(2020, 10, 25,  2, 31,  0), # -12600     0 NST
        datetime(2021,  4,  4,  3, 31,  0), #  -9000  3600 NDT
        datetime(2021, 10, 31,  2, 31,  0), # -12600     0 NST
        datetime(2022,  4,  3,  3, 31,  0), #  -9000  3600 NDT
        datetime(2022, 10, 30,  2, 31,  0), # -12600     0 NST
        datetime(2023,  4,  2,  3, 31,  0), #  -9000  3600 NDT
        datetime(2023, 10, 29,  2, 31,  0), # -12600     0 NST
        datetime(2024,  4,  7,  3, 31,  0), #  -9000  3600 NDT
        datetime(2024, 10, 27,  2, 31,  0), # -12600     0 NST
        datetime(2025,  4,  6,  3, 31,  0), #  -9000  3600 NDT
        datetime(2025, 10, 26,  2, 31,  0), # -12600     0 NST
        datetime(2026,  4,  5,  3, 31,  0), #  -9000  3600 NDT
        datetime(2026, 10, 25,  2, 31,  0), # -12600     0 NST
        datetime(2027,  4,  4,  3, 31,  0), #  -9000  3600 NDT
        datetime(2027, 10, 31,  2, 31,  0), # -12600     0 NST
        datetime(2028,  4,  2,  3, 31,  0), #  -9000  3600 NDT
        datetime(2028, 10, 29,  2, 31,  0), # -12600     0 NST
        datetime(2029,  4,  1,  3, 31,  0), #  -9000  3600 NDT
        datetime(2029, 10, 28,  2, 31,  0), # -12600     0 NST
        datetime(2030,  4,  7,  3, 31,  0), #  -9000  3600 NDT
        datetime(2030, 10, 27,  2, 31,  0), # -12600     0 NST
        datetime(2031,  4,  6,  3, 31,  0), #  -9000  3600 NDT
        datetime(2031, 10, 26,  2, 31,  0), # -12600     0 NST
        datetime(2032,  4,  4,  3, 31,  0), #  -9000  3600 NDT
        datetime(2032, 10, 31,  2, 31,  0), # -12600     0 NST
        datetime(2033,  4,  3,  3, 31,  0), #  -9000  3600 NDT
        datetime(2033, 10, 30,  2, 31,  0), # -12600     0 NST
        datetime(2034,  4,  2,  3, 31,  0), #  -9000  3600 NDT
        datetime(2034, 10, 29,  2, 31,  0), # -12600     0 NST
        datetime(2035,  4,  1,  3, 31,  0), #  -9000  3600 NDT
        datetime(2035, 10, 28,  2, 31,  0), # -12600     0 NST
        datetime(2036,  4,  6,  3, 31,  0), #  -9000  3600 NDT
        datetime(2036, 10, 26,  2, 31,  0), # -12600     0 NST
        datetime(2037,  4,  5,  3, 31,  0), #  -9000  3600 NDT
        datetime(2037, 10, 25,  2, 31,  0), # -12600     0 NST
        ]

    _transition_info = [
        ttinfo(-12652,      0,  'NST'),
        ttinfo( -9052,   3600,  'NDT'),
        ttinfo(-12652,      0,  'NST'),
        ttinfo( -9052,   3600,  'NDT'),
        ttinfo(-12652,      0,  'NST'),
        ttinfo( -9052,   3600,  'NDT'),
        ttinfo(-12652,      0,  'NST'),
        ttinfo( -9052,   3600,  'NDT'),
        ttinfo(-12652,      0,  'NST'),
        ttinfo( -9052,   3600,  'NDT'),
        ttinfo(-12652,      0,  'NST'),
        ttinfo( -9052,   3600,  'NDT'),
        ttinfo(-12652,      0,  'NST'),
        ttinfo( -9052,   3600,  'NDT'),
        ttinfo(-12652,      0,  'NST'),
        ttinfo( -9052,   3600,  'NDT'),
        ttinfo(-12652,      0,  'NST'),
        ttinfo( -9052,   3600,  'NDT'),
        ttinfo(-12652,      0,  'NST'),
        ttinfo( -9052,   3600,  'NDT'),
        ttinfo(-12652,      0,  'NST'),
        ttinfo( -9052,   3600,  'NDT'),
        ttinfo(-12652,      0,  'NST'),
        ttinfo( -9052,   3600,  'NDT'),
        ttinfo(-12652,      0,  'NST'),
        ttinfo( -9052,   3600,  'NDT'),
        ttinfo(-12652,      0,  'NST'),
        ttinfo( -9052,   3600,  'NDT'),
        ttinfo(-12652,      0,  'NST'),
        ttinfo( -9052,   3600,  'NDT'),
        ttinfo(-12652,      0,  'NST'),
        ttinfo( -9052,   3600,  'NDT'),
        ttinfo(-12652,      0,  'NST'),
        ttinfo( -9052,   3600,  'NDT'),
        ttinfo(-12652,      0,  'NST'),
        ttinfo( -9052,   3600,  'NDT'),
        ttinfo(-12652,      0,  'NST'),
        ttinfo(-12600,      0,  'NST'),
        ttinfo( -9000,   3600,  'NDT'),
        ttinfo(-12600,      0,  'NST'),
        ttinfo( -9000,   3600,  'NDT'),
        ttinfo(-12600,      0,  'NST'),
        ttinfo( -9000,   3600,  'NDT'),
        ttinfo(-12600,      0,  'NST'),
        ttinfo( -9000,   3600,  'NDT'),
        ttinfo(-12600,      0,  'NST'),
        ttinfo( -9000,   3600,  'NDT'),
        ttinfo(-12600,      0,  'NST'),
        ttinfo( -9000,   3600,  'NDT'),
        ttinfo(-12600,      0,  'NST'),
        ttinfo( -9000,   3600,  'NDT'),
        ttinfo(-12600,      0,  'NST'),
        ttinfo( -9000,   3600,  'NWT'),
        ttinfo( -9000,      0,  'NPT'),
        ttinfo(-12600,      0,  'NST'),
        ttinfo( -9000,   3600,  'NDT'),
        ttinfo(-12600,      0,  'NST'),
        ttinfo( -9000,   3600,  'NDT'),
        ttinfo(-12600,      0,  'NST'),
        ttinfo( -9000,   3600,  'NDT'),
        ttinfo(-12600,      0,  'NST'),
        ttinfo( -9000,   3600,  'NDT'),
        ttinfo(-12600,      0,  'NST'),
        ttinfo( -9000,   3600,  'NDT'),
        ttinfo(-12600,      0,  'NST'),
        ttinfo( -9000,   3600,  'NDT'),
        ttinfo(-12600,      0,  'NST'),
        ttinfo( -9000,   3600,  'NDT'),
        ttinfo(-12600,      0,  'NST'),
        ttinfo( -9000,   3600,  'NDT'),
        ttinfo(-12600,      0,  'NST'),
        ttinfo( -9000,   3600,  'NDT'),
        ttinfo(-12600,      0,  'NST'),
        ttinfo( -9000,   3600,  'NDT'),
        ttinfo(-12600,      0,  'NST'),
        ttinfo( -9000,   3600,  'NDT'),
        ttinfo(-12600,      0,  'NST'),
        ttinfo( -9000,   3600,  'NDT'),
        ttinfo(-12600,      0,  'NST'),
        ttinfo( -9000,   3600,  'NDT'),
        ttinfo(-12600,      0,  'NST'),
        ttinfo( -9000,   3600,  'NDT'),
        ttinfo(-12600,      0,  'NST'),
        ttinfo( -9000,   3600,  'NDT'),
        ttinfo(-12600,      0,  'NST'),
        ttinfo( -9000,   3600,  'NDT'),
        ttinfo(-12600,      0,  'NST'),
        ttinfo( -9000,   3600,  'NDT'),
        ttinfo(-12600,      0,  'NST'),
        ttinfo( -9000,   3600,  'NDT'),
        ttinfo(-12600,      0,  'NST'),
        ttinfo( -9000,   3600,  'NDT'),
        ttinfo(-12600,      0,  'NST'),
        ttinfo( -9000,   3600,  'NDT'),
        ttinfo(-12600,      0,  'NST'),
        ttinfo( -9000,   3600,  'NDT'),
        ttinfo(-12600,      0,  'NST'),
        ttinfo( -9000,   3600,  'NDT'),
        ttinfo(-12600,      0,  'NST'),
        ttinfo( -9000,   3600,  'NDT'),
        ttinfo(-12600,      0,  'NST'),
        ttinfo( -9000,   3600,  'NDT'),
        ttinfo(-12600,      0,  'NST'),
        ttinfo( -9000,   3600,  'NDT'),
        ttinfo(-12600,      0,  'NST'),
        ttinfo( -9000,   3600,  'NDT'),
        ttinfo(-12600,      0,  'NST'),
        ttinfo( -9000,   3600,  'NDT'),
        ttinfo(-12600,      0,  'NST'),
        ttinfo( -9000,   3600,  'NDT'),
        ttinfo(-12600,      0,  'NST'),
        ttinfo( -9000,   3600,  'NDT'),
        ttinfo(-12600,      0,  'NST'),
        ttinfo( -9000,   3600,  'NDT'),
        ttinfo(-12600,      0,  'NST'),
        ttinfo( -9000,   3600,  'NDT'),
        ttinfo(-12600,      0,  'NST'),
        ttinfo( -9000,   3600,  'NDT'),
        ttinfo(-12600,      0,  'NST'),
        ttinfo( -9000,   3600,  'NDT'),
        ttinfo(-12600,      0,  'NST'),
        ttinfo( -9000,   3600,  'NDT'),
        ttinfo(-12600,      0,  'NST'),
        ttinfo( -9000,   3600,  'NDT'),
        ttinfo(-12600,      0,  'NST'),
        ttinfo( -9000,   3600,  'NDT'),
        ttinfo(-12600,      0,  'NST'),
        ttinfo( -9000,   3600,  'NDT'),
        ttinfo(-12600,      0,  'NST'),
        ttinfo( -9000,   3600,  'NDT'),
        ttinfo(-12600,      0,  'NST'),
        ttinfo( -9000,   3600,  'NDT'),
        ttinfo(-12600,      0,  'NST'),
        ttinfo( -9000,   3600,  'NDT'),
        ttinfo(-12600,      0,  'NST'),
        ttinfo( -9000,   3600,  'NDT'),
        ttinfo(-12600,      0,  'NST'),
        ttinfo( -9000,   3600,  'NDT'),
        ttinfo(-12600,      0,  'NST'),
        ttinfo( -5400,   7200, 'NDDT'),
        ttinfo(-12600,      0,  'NST'),
        ttinfo( -9000,   3600,  'NDT'),
        ttinfo(-12600,      0,  'NST'),
        ttinfo( -9000,   3600,  'NDT'),
        ttinfo(-12600,      0,  'NST'),
        ttinfo( -9000,   3600,  'NDT'),
        ttinfo(-12600,      0,  'NST'),
        ttinfo( -9000,   3600,  'NDT'),
        ttinfo(-12600,      0,  'NST'),
        ttinfo( -9000,   3600,  'NDT'),
        ttinfo(-12600,      0,  'NST'),
        ttinfo( -9000,   3600,  'NDT'),
        ttinfo(-12600,      0,  'NST'),
        ttinfo( -9000,   3600,  'NDT'),
        ttinfo(-12600,      0,  'NST'),
        ttinfo( -9000,   3600,  'NDT'),
        ttinfo(-12600,      0,  'NST'),
        ttinfo( -9000,   3600,  'NDT'),
        ttinfo(-12600,      0,  'NST'),
        ttinfo( -9000,   3600,  'NDT'),
        ttinfo(-12600,      0,  'NST'),
        ttinfo( -9000,   3600,  'NDT'),
        ttinfo(-12600,      0,  'NST'),
        ttinfo( -9000,   3600,  'NDT'),
        ttinfo(-12600,      0,  'NST'),
        ttinfo( -9000,   3600,  'NDT'),
        ttinfo(-12600,      0,  'NST'),
        ttinfo( -9000,   3600,  'NDT'),
        ttinfo(-12600,      0,  'NST'),
        ttinfo( -9000,   3600,  'NDT'),
        ttinfo(-12600,      0,  'NST'),
        ttinfo( -9000,   3600,  'NDT'),
        ttinfo(-12600,      0,  'NST'),
        ttinfo( -9000,   3600,  'NDT'),
        ttinfo(-12600,      0,  'NST'),
        ttinfo( -9000,   3600,  'NDT'),
        ttinfo(-12600,      0,  'NST'),
        ttinfo( -9000,   3600,  'NDT'),
        ttinfo(-12600,      0,  'NST'),
        ttinfo( -9000,   3600,  'NDT'),
        ttinfo(-12600,      0,  'NST'),
        ttinfo( -9000,   3600,  'NDT'),
        ttinfo(-12600,      0,  'NST'),
        ttinfo( -9000,   3600,  'NDT'),
        ttinfo(-12600,      0,  'NST'),
        ttinfo( -9000,   3600,  'NDT'),
        ttinfo(-12600,      0,  'NST'),
        ttinfo( -9000,   3600,  'NDT'),
        ttinfo(-12600,      0,  'NST'),
        ttinfo( -9000,   3600,  'NDT'),
        ttinfo(-12600,      0,  'NST'),
        ttinfo( -9000,   3600,  'NDT'),
        ttinfo(-12600,      0,  'NST'),
        ttinfo( -9000,   3600,  'NDT'),
        ttinfo(-12600,      0,  'NST'),
        ttinfo( -9000,   3600,  'NDT'),
        ttinfo(-12600,      0,  'NST'),
        ttinfo( -9000,   3600,  'NDT'),
        ttinfo(-12600,      0,  'NST'),
        ttinfo( -9000,   3600,  'NDT'),
        ttinfo(-12600,      0,  'NST'),
        ttinfo( -9000,   3600,  'NDT'),
        ttinfo(-12600,      0,  'NST'),
        ttinfo( -9000,   3600,  'NDT'),
        ttinfo(-12600,      0,  'NST'),
        ttinfo( -9000,   3600,  'NDT'),
        ttinfo(-12600,      0,  'NST'),
        ttinfo( -9000,   3600,  'NDT'),
        ttinfo(-12600,      0,  'NST'),
        ttinfo( -9000,   3600,  'NDT'),
        ttinfo(-12600,      0,  'NST'),
        ttinfo( -9000,   3600,  'NDT'),
        ttinfo(-12600,      0,  'NST'),
        ttinfo( -9000,   3600,  'NDT'),
        ttinfo(-12600,      0,  'NST'),
        ttinfo( -9000,   3600,  'NDT'),
        ttinfo(-12600,      0,  'NST'),
        ttinfo( -9000,   3600,  'NDT'),
        ttinfo(-12600,      0,  'NST'),
        ttinfo( -9000,   3600,  'NDT'),
        ttinfo(-12600,      0,  'NST'),
        ttinfo( -9000,   3600,  'NDT'),
        ttinfo(-12600,      0,  'NST'),
        ttinfo( -9000,   3600,  'NDT'),
        ttinfo(-12600,      0,  'NST'),
        ttinfo( -9000,   3600,  'NDT'),
        ttinfo(-12600,      0,  'NST'),
        ttinfo( -9000,   3600,  'NDT'),
        ttinfo(-12600,      0,  'NST'),
        ttinfo( -9000,   3600,  'NDT'),
        ttinfo(-12600,      0,  'NST'),
        ttinfo( -9000,   3600,  'NDT'),
        ttinfo(-12600,      0,  'NST'),
        ttinfo( -9000,   3600,  'NDT'),
        ttinfo(-12600,      0,  'NST'),
        ttinfo( -9000,   3600,  'NDT'),
        ttinfo(-12600,      0,  'NST'),
        ttinfo( -9000,   3600,  'NDT'),
        ttinfo(-12600,      0,  'NST'),
        ]

St_Johns = St_Johns() # Singleton

