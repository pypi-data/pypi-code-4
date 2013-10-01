'''
tzinfo timezone information for America/Belize.

Generated from the Olson timezone database:
    ftp://elsie.nci.nih.gov/pub/tz*.tar.gz
'''

from pytz.tzinfo import DstTzInfo
from pytz.tzinfo import memorized_datetime as datetime
from pytz.tzinfo import memorized_ttinfo as ttinfo

class Belize(DstTzInfo):
    '''America/Belize timezone definition. See datetime.tzinfo for details'''

    _zone = 'America/Belize'

    _utc_transition_times = [
        datetime(   1,  1,  1,  0,  0,  0), # -21168     0 LMT
        datetime(1912,  4,  1,  5, 52, 48), # -21600     0 CST
        datetime(1918, 10,  6,  6,  0,  0), # -19800  1800 CHDT
        datetime(1919,  2,  9,  5, 30,  0), # -21600     0 CST
        datetime(1919, 10,  5,  6,  0,  0), # -19800  1800 CHDT
        datetime(1920,  2, 15,  5, 30,  0), # -21600     0 CST
        datetime(1920, 10,  3,  6,  0,  0), # -19800  1800 CHDT
        datetime(1921,  2, 13,  5, 30,  0), # -21600     0 CST
        datetime(1921, 10,  2,  6,  0,  0), # -19800  1800 CHDT
        datetime(1922,  2, 12,  5, 30,  0), # -21600     0 CST
        datetime(1922, 10,  8,  6,  0,  0), # -19800  1800 CHDT
        datetime(1923,  2, 11,  5, 30,  0), # -21600     0 CST
        datetime(1923, 10,  7,  6,  0,  0), # -19800  1800 CHDT
        datetime(1924,  2, 10,  5, 30,  0), # -21600     0 CST
        datetime(1924, 10,  5,  6,  0,  0), # -19800  1800 CHDT
        datetime(1925,  2, 15,  5, 30,  0), # -21600     0 CST
        datetime(1925, 10,  4,  6,  0,  0), # -19800  1800 CHDT
        datetime(1926,  2, 14,  5, 30,  0), # -21600     0 CST
        datetime(1926, 10,  3,  6,  0,  0), # -19800  1800 CHDT
        datetime(1927,  2, 13,  5, 30,  0), # -21600     0 CST
        datetime(1927, 10,  2,  6,  0,  0), # -19800  1800 CHDT
        datetime(1928,  2, 12,  5, 30,  0), # -21600     0 CST
        datetime(1928, 10,  7,  6,  0,  0), # -19800  1800 CHDT
        datetime(1929,  2, 10,  5, 30,  0), # -21600     0 CST
        datetime(1929, 10,  6,  6,  0,  0), # -19800  1800 CHDT
        datetime(1930,  2,  9,  5, 30,  0), # -21600     0 CST
        datetime(1930, 10,  5,  6,  0,  0), # -19800  1800 CHDT
        datetime(1931,  2, 15,  5, 30,  0), # -21600     0 CST
        datetime(1931, 10,  4,  6,  0,  0), # -19800  1800 CHDT
        datetime(1932,  2, 14,  5, 30,  0), # -21600     0 CST
        datetime(1932, 10,  2,  6,  0,  0), # -19800  1800 CHDT
        datetime(1933,  2, 12,  5, 30,  0), # -21600     0 CST
        datetime(1933, 10,  8,  6,  0,  0), # -19800  1800 CHDT
        datetime(1934,  2, 11,  5, 30,  0), # -21600     0 CST
        datetime(1934, 10,  7,  6,  0,  0), # -19800  1800 CHDT
        datetime(1935,  2, 10,  5, 30,  0), # -21600     0 CST
        datetime(1935, 10,  6,  6,  0,  0), # -19800  1800 CHDT
        datetime(1936,  2,  9,  5, 30,  0), # -21600     0 CST
        datetime(1936, 10,  4,  6,  0,  0), # -19800  1800 CHDT
        datetime(1937,  2, 14,  5, 30,  0), # -21600     0 CST
        datetime(1937, 10,  3,  6,  0,  0), # -19800  1800 CHDT
        datetime(1938,  2, 13,  5, 30,  0), # -21600     0 CST
        datetime(1938, 10,  2,  6,  0,  0), # -19800  1800 CHDT
        datetime(1939,  2, 12,  5, 30,  0), # -21600     0 CST
        datetime(1939, 10,  8,  6,  0,  0), # -19800  1800 CHDT
        datetime(1940,  2, 11,  5, 30,  0), # -21600     0 CST
        datetime(1940, 10,  6,  6,  0,  0), # -19800  1800 CHDT
        datetime(1941,  2,  9,  5, 30,  0), # -21600     0 CST
        datetime(1941, 10,  5,  6,  0,  0), # -19800  1800 CHDT
        datetime(1942,  2, 15,  5, 30,  0), # -21600     0 CST
        datetime(1942, 10,  4,  6,  0,  0), # -19800  1800 CHDT
        datetime(1943,  2, 14,  5, 30,  0), # -21600     0 CST
        datetime(1973, 12,  5,  6,  0,  0), # -18000  3600 CDT
        datetime(1974,  2,  9,  5,  0,  0), # -21600     0 CST
        datetime(1982, 12, 18,  6,  0,  0), # -18000  3600 CDT
        datetime(1983,  2, 12,  5,  0,  0), # -21600     0 CST
        ]

    _transition_info = [
        ttinfo(-21168,      0,  'LMT'),
        ttinfo(-21600,      0,  'CST'),
        ttinfo(-19800,   1800, 'CHDT'),
        ttinfo(-21600,      0,  'CST'),
        ttinfo(-19800,   1800, 'CHDT'),
        ttinfo(-21600,      0,  'CST'),
        ttinfo(-19800,   1800, 'CHDT'),
        ttinfo(-21600,      0,  'CST'),
        ttinfo(-19800,   1800, 'CHDT'),
        ttinfo(-21600,      0,  'CST'),
        ttinfo(-19800,   1800, 'CHDT'),
        ttinfo(-21600,      0,  'CST'),
        ttinfo(-19800,   1800, 'CHDT'),
        ttinfo(-21600,      0,  'CST'),
        ttinfo(-19800,   1800, 'CHDT'),
        ttinfo(-21600,      0,  'CST'),
        ttinfo(-19800,   1800, 'CHDT'),
        ttinfo(-21600,      0,  'CST'),
        ttinfo(-19800,   1800, 'CHDT'),
        ttinfo(-21600,      0,  'CST'),
        ttinfo(-19800,   1800, 'CHDT'),
        ttinfo(-21600,      0,  'CST'),
        ttinfo(-19800,   1800, 'CHDT'),
        ttinfo(-21600,      0,  'CST'),
        ttinfo(-19800,   1800, 'CHDT'),
        ttinfo(-21600,      0,  'CST'),
        ttinfo(-19800,   1800, 'CHDT'),
        ttinfo(-21600,      0,  'CST'),
        ttinfo(-19800,   1800, 'CHDT'),
        ttinfo(-21600,      0,  'CST'),
        ttinfo(-19800,   1800, 'CHDT'),
        ttinfo(-21600,      0,  'CST'),
        ttinfo(-19800,   1800, 'CHDT'),
        ttinfo(-21600,      0,  'CST'),
        ttinfo(-19800,   1800, 'CHDT'),
        ttinfo(-21600,      0,  'CST'),
        ttinfo(-19800,   1800, 'CHDT'),
        ttinfo(-21600,      0,  'CST'),
        ttinfo(-19800,   1800, 'CHDT'),
        ttinfo(-21600,      0,  'CST'),
        ttinfo(-19800,   1800, 'CHDT'),
        ttinfo(-21600,      0,  'CST'),
        ttinfo(-19800,   1800, 'CHDT'),
        ttinfo(-21600,      0,  'CST'),
        ttinfo(-19800,   1800, 'CHDT'),
        ttinfo(-21600,      0,  'CST'),
        ttinfo(-19800,   1800, 'CHDT'),
        ttinfo(-21600,      0,  'CST'),
        ttinfo(-19800,   1800, 'CHDT'),
        ttinfo(-21600,      0,  'CST'),
        ttinfo(-19800,   1800, 'CHDT'),
        ttinfo(-21600,      0,  'CST'),
        ttinfo(-18000,   3600,  'CDT'),
        ttinfo(-21600,      0,  'CST'),
        ttinfo(-18000,   3600,  'CDT'),
        ttinfo(-21600,      0,  'CST'),
        ]

Belize = Belize() # Singleton

