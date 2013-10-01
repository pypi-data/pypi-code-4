'''
tzinfo timezone information for US/Aleutian.

Generated from the Olson timezone database:
    ftp://elsie.nci.nih.gov/pub/tz*.tar.gz
'''

from pytz.tzinfo import DstTzInfo
from pytz.tzinfo import memorized_datetime as datetime
from pytz.tzinfo import memorized_ttinfo as ttinfo

class Aleutian(DstTzInfo):
    '''US/Aleutian timezone definition. See datetime.tzinfo for details'''

    _zone = 'US/Aleutian'

    _utc_transition_times = [
        datetime(   1,  1,  1,  0,  0,  0), # -39600     0 NST
        datetime(1942,  2,  9, 13,  0,  0), # -36000  3600 NWT
        datetime(1945,  8, 14, 23,  0,  0), # -36000     0 NPT
        datetime(1945,  9, 30, 12,  0,  0), # -39600     0 NST
        datetime(1967,  4,  1, 11,  0,  0), # -39600     0 BST
        datetime(1969,  4, 27, 13,  0,  0), # -36000  3600 BDT
        datetime(1969, 10, 26, 12,  0,  0), # -39600     0 BST
        datetime(1970,  4, 26, 13,  0,  0), # -36000  3600 BDT
        datetime(1970, 10, 25, 12,  0,  0), # -39600     0 BST
        datetime(1971,  4, 25, 13,  0,  0), # -36000  3600 BDT
        datetime(1971, 10, 31, 12,  0,  0), # -39600     0 BST
        datetime(1972,  4, 30, 13,  0,  0), # -36000  3600 BDT
        datetime(1972, 10, 29, 12,  0,  0), # -39600     0 BST
        datetime(1973,  4, 29, 13,  0,  0), # -36000  3600 BDT
        datetime(1973, 10, 28, 12,  0,  0), # -39600     0 BST
        datetime(1974,  1,  6, 13,  0,  0), # -36000  3600 BDT
        datetime(1974, 10, 27, 12,  0,  0), # -39600     0 BST
        datetime(1975,  2, 23, 13,  0,  0), # -36000  3600 BDT
        datetime(1975, 10, 26, 12,  0,  0), # -39600     0 BST
        datetime(1976,  4, 25, 13,  0,  0), # -36000  3600 BDT
        datetime(1976, 10, 31, 12,  0,  0), # -39600     0 BST
        datetime(1977,  4, 24, 13,  0,  0), # -36000  3600 BDT
        datetime(1977, 10, 30, 12,  0,  0), # -39600     0 BST
        datetime(1978,  4, 30, 13,  0,  0), # -36000  3600 BDT
        datetime(1978, 10, 29, 12,  0,  0), # -39600     0 BST
        datetime(1979,  4, 29, 13,  0,  0), # -36000  3600 BDT
        datetime(1979, 10, 28, 12,  0,  0), # -39600     0 BST
        datetime(1980,  4, 27, 13,  0,  0), # -36000  3600 BDT
        datetime(1980, 10, 26, 12,  0,  0), # -39600     0 BST
        datetime(1981,  4, 26, 13,  0,  0), # -36000  3600 BDT
        datetime(1981, 10, 25, 12,  0,  0), # -39600     0 BST
        datetime(1982,  4, 25, 13,  0,  0), # -36000  3600 BDT
        datetime(1982, 10, 31, 12,  0,  0), # -39600     0 BST
        datetime(1983,  4, 24, 13,  0,  0), # -36000  3600 BDT
        datetime(1983, 10, 30, 12,  0,  0), # -36000     0 AHST
        datetime(1983, 11, 30, 10,  0,  0), # -36000     0 HAST
        datetime(1984,  4, 29, 12,  0,  0), # -32400  3600 HADT
        datetime(1984, 10, 28, 11,  0,  0), # -36000     0 HAST
        datetime(1985,  4, 28, 12,  0,  0), # -32400  3600 HADT
        datetime(1985, 10, 27, 11,  0,  0), # -36000     0 HAST
        datetime(1986,  4, 27, 12,  0,  0), # -32400  3600 HADT
        datetime(1986, 10, 26, 11,  0,  0), # -36000     0 HAST
        datetime(1987,  4,  5, 12,  0,  0), # -32400  3600 HADT
        datetime(1987, 10, 25, 11,  0,  0), # -36000     0 HAST
        datetime(1988,  4,  3, 12,  0,  0), # -32400  3600 HADT
        datetime(1988, 10, 30, 11,  0,  0), # -36000     0 HAST
        datetime(1989,  4,  2, 12,  0,  0), # -32400  3600 HADT
        datetime(1989, 10, 29, 11,  0,  0), # -36000     0 HAST
        datetime(1990,  4,  1, 12,  0,  0), # -32400  3600 HADT
        datetime(1990, 10, 28, 11,  0,  0), # -36000     0 HAST
        datetime(1991,  4,  7, 12,  0,  0), # -32400  3600 HADT
        datetime(1991, 10, 27, 11,  0,  0), # -36000     0 HAST
        datetime(1992,  4,  5, 12,  0,  0), # -32400  3600 HADT
        datetime(1992, 10, 25, 11,  0,  0), # -36000     0 HAST
        datetime(1993,  4,  4, 12,  0,  0), # -32400  3600 HADT
        datetime(1993, 10, 31, 11,  0,  0), # -36000     0 HAST
        datetime(1994,  4,  3, 12,  0,  0), # -32400  3600 HADT
        datetime(1994, 10, 30, 11,  0,  0), # -36000     0 HAST
        datetime(1995,  4,  2, 12,  0,  0), # -32400  3600 HADT
        datetime(1995, 10, 29, 11,  0,  0), # -36000     0 HAST
        datetime(1996,  4,  7, 12,  0,  0), # -32400  3600 HADT
        datetime(1996, 10, 27, 11,  0,  0), # -36000     0 HAST
        datetime(1997,  4,  6, 12,  0,  0), # -32400  3600 HADT
        datetime(1997, 10, 26, 11,  0,  0), # -36000     0 HAST
        datetime(1998,  4,  5, 12,  0,  0), # -32400  3600 HADT
        datetime(1998, 10, 25, 11,  0,  0), # -36000     0 HAST
        datetime(1999,  4,  4, 12,  0,  0), # -32400  3600 HADT
        datetime(1999, 10, 31, 11,  0,  0), # -36000     0 HAST
        datetime(2000,  4,  2, 12,  0,  0), # -32400  3600 HADT
        datetime(2000, 10, 29, 11,  0,  0), # -36000     0 HAST
        datetime(2001,  4,  1, 12,  0,  0), # -32400  3600 HADT
        datetime(2001, 10, 28, 11,  0,  0), # -36000     0 HAST
        datetime(2002,  4,  7, 12,  0,  0), # -32400  3600 HADT
        datetime(2002, 10, 27, 11,  0,  0), # -36000     0 HAST
        datetime(2003,  4,  6, 12,  0,  0), # -32400  3600 HADT
        datetime(2003, 10, 26, 11,  0,  0), # -36000     0 HAST
        datetime(2004,  4,  4, 12,  0,  0), # -32400  3600 HADT
        datetime(2004, 10, 31, 11,  0,  0), # -36000     0 HAST
        datetime(2005,  4,  3, 12,  0,  0), # -32400  3600 HADT
        datetime(2005, 10, 30, 11,  0,  0), # -36000     0 HAST
        datetime(2006,  4,  2, 12,  0,  0), # -32400  3600 HADT
        datetime(2006, 10, 29, 11,  0,  0), # -36000     0 HAST
        datetime(2007,  4,  1, 12,  0,  0), # -32400  3600 HADT
        datetime(2007, 10, 28, 11,  0,  0), # -36000     0 HAST
        datetime(2008,  4,  6, 12,  0,  0), # -32400  3600 HADT
        datetime(2008, 10, 26, 11,  0,  0), # -36000     0 HAST
        datetime(2009,  4,  5, 12,  0,  0), # -32400  3600 HADT
        datetime(2009, 10, 25, 11,  0,  0), # -36000     0 HAST
        datetime(2010,  4,  4, 12,  0,  0), # -32400  3600 HADT
        datetime(2010, 10, 31, 11,  0,  0), # -36000     0 HAST
        datetime(2011,  4,  3, 12,  0,  0), # -32400  3600 HADT
        datetime(2011, 10, 30, 11,  0,  0), # -36000     0 HAST
        datetime(2012,  4,  1, 12,  0,  0), # -32400  3600 HADT
        datetime(2012, 10, 28, 11,  0,  0), # -36000     0 HAST
        datetime(2013,  4,  7, 12,  0,  0), # -32400  3600 HADT
        datetime(2013, 10, 27, 11,  0,  0), # -36000     0 HAST
        datetime(2014,  4,  6, 12,  0,  0), # -32400  3600 HADT
        datetime(2014, 10, 26, 11,  0,  0), # -36000     0 HAST
        datetime(2015,  4,  5, 12,  0,  0), # -32400  3600 HADT
        datetime(2015, 10, 25, 11,  0,  0), # -36000     0 HAST
        datetime(2016,  4,  3, 12,  0,  0), # -32400  3600 HADT
        datetime(2016, 10, 30, 11,  0,  0), # -36000     0 HAST
        datetime(2017,  4,  2, 12,  0,  0), # -32400  3600 HADT
        datetime(2017, 10, 29, 11,  0,  0), # -36000     0 HAST
        datetime(2018,  4,  1, 12,  0,  0), # -32400  3600 HADT
        datetime(2018, 10, 28, 11,  0,  0), # -36000     0 HAST
        datetime(2019,  4,  7, 12,  0,  0), # -32400  3600 HADT
        datetime(2019, 10, 27, 11,  0,  0), # -36000     0 HAST
        datetime(2020,  4,  5, 12,  0,  0), # -32400  3600 HADT
        datetime(2020, 10, 25, 11,  0,  0), # -36000     0 HAST
        datetime(2021,  4,  4, 12,  0,  0), # -32400  3600 HADT
        datetime(2021, 10, 31, 11,  0,  0), # -36000     0 HAST
        datetime(2022,  4,  3, 12,  0,  0), # -32400  3600 HADT
        datetime(2022, 10, 30, 11,  0,  0), # -36000     0 HAST
        datetime(2023,  4,  2, 12,  0,  0), # -32400  3600 HADT
        datetime(2023, 10, 29, 11,  0,  0), # -36000     0 HAST
        datetime(2024,  4,  7, 12,  0,  0), # -32400  3600 HADT
        datetime(2024, 10, 27, 11,  0,  0), # -36000     0 HAST
        datetime(2025,  4,  6, 12,  0,  0), # -32400  3600 HADT
        datetime(2025, 10, 26, 11,  0,  0), # -36000     0 HAST
        datetime(2026,  4,  5, 12,  0,  0), # -32400  3600 HADT
        datetime(2026, 10, 25, 11,  0,  0), # -36000     0 HAST
        datetime(2027,  4,  4, 12,  0,  0), # -32400  3600 HADT
        datetime(2027, 10, 31, 11,  0,  0), # -36000     0 HAST
        datetime(2028,  4,  2, 12,  0,  0), # -32400  3600 HADT
        datetime(2028, 10, 29, 11,  0,  0), # -36000     0 HAST
        datetime(2029,  4,  1, 12,  0,  0), # -32400  3600 HADT
        datetime(2029, 10, 28, 11,  0,  0), # -36000     0 HAST
        datetime(2030,  4,  7, 12,  0,  0), # -32400  3600 HADT
        datetime(2030, 10, 27, 11,  0,  0), # -36000     0 HAST
        datetime(2031,  4,  6, 12,  0,  0), # -32400  3600 HADT
        datetime(2031, 10, 26, 11,  0,  0), # -36000     0 HAST
        datetime(2032,  4,  4, 12,  0,  0), # -32400  3600 HADT
        datetime(2032, 10, 31, 11,  0,  0), # -36000     0 HAST
        datetime(2033,  4,  3, 12,  0,  0), # -32400  3600 HADT
        datetime(2033, 10, 30, 11,  0,  0), # -36000     0 HAST
        datetime(2034,  4,  2, 12,  0,  0), # -32400  3600 HADT
        datetime(2034, 10, 29, 11,  0,  0), # -36000     0 HAST
        datetime(2035,  4,  1, 12,  0,  0), # -32400  3600 HADT
        datetime(2035, 10, 28, 11,  0,  0), # -36000     0 HAST
        datetime(2036,  4,  6, 12,  0,  0), # -32400  3600 HADT
        datetime(2036, 10, 26, 11,  0,  0), # -36000     0 HAST
        datetime(2037,  4,  5, 12,  0,  0), # -32400  3600 HADT
        datetime(2037, 10, 25, 11,  0,  0), # -36000     0 HAST
        ]

    _transition_info = [
        ttinfo(-39600,      0,  'NST'),
        ttinfo(-36000,   3600,  'NWT'),
        ttinfo(-36000,      0,  'NPT'),
        ttinfo(-39600,      0,  'NST'),
        ttinfo(-39600,      0,  'BST'),
        ttinfo(-36000,   3600,  'BDT'),
        ttinfo(-39600,      0,  'BST'),
        ttinfo(-36000,   3600,  'BDT'),
        ttinfo(-39600,      0,  'BST'),
        ttinfo(-36000,   3600,  'BDT'),
        ttinfo(-39600,      0,  'BST'),
        ttinfo(-36000,   3600,  'BDT'),
        ttinfo(-39600,      0,  'BST'),
        ttinfo(-36000,   3600,  'BDT'),
        ttinfo(-39600,      0,  'BST'),
        ttinfo(-36000,   3600,  'BDT'),
        ttinfo(-39600,      0,  'BST'),
        ttinfo(-36000,   3600,  'BDT'),
        ttinfo(-39600,      0,  'BST'),
        ttinfo(-36000,   3600,  'BDT'),
        ttinfo(-39600,      0,  'BST'),
        ttinfo(-36000,   3600,  'BDT'),
        ttinfo(-39600,      0,  'BST'),
        ttinfo(-36000,   3600,  'BDT'),
        ttinfo(-39600,      0,  'BST'),
        ttinfo(-36000,   3600,  'BDT'),
        ttinfo(-39600,      0,  'BST'),
        ttinfo(-36000,   3600,  'BDT'),
        ttinfo(-39600,      0,  'BST'),
        ttinfo(-36000,   3600,  'BDT'),
        ttinfo(-39600,      0,  'BST'),
        ttinfo(-36000,   3600,  'BDT'),
        ttinfo(-39600,      0,  'BST'),
        ttinfo(-36000,   3600,  'BDT'),
        ttinfo(-36000,      0, 'AHST'),
        ttinfo(-36000,      0, 'HAST'),
        ttinfo(-32400,   3600, 'HADT'),
        ttinfo(-36000,      0, 'HAST'),
        ttinfo(-32400,   3600, 'HADT'),
        ttinfo(-36000,      0, 'HAST'),
        ttinfo(-32400,   3600, 'HADT'),
        ttinfo(-36000,      0, 'HAST'),
        ttinfo(-32400,   3600, 'HADT'),
        ttinfo(-36000,      0, 'HAST'),
        ttinfo(-32400,   3600, 'HADT'),
        ttinfo(-36000,      0, 'HAST'),
        ttinfo(-32400,   3600, 'HADT'),
        ttinfo(-36000,      0, 'HAST'),
        ttinfo(-32400,   3600, 'HADT'),
        ttinfo(-36000,      0, 'HAST'),
        ttinfo(-32400,   3600, 'HADT'),
        ttinfo(-36000,      0, 'HAST'),
        ttinfo(-32400,   3600, 'HADT'),
        ttinfo(-36000,      0, 'HAST'),
        ttinfo(-32400,   3600, 'HADT'),
        ttinfo(-36000,      0, 'HAST'),
        ttinfo(-32400,   3600, 'HADT'),
        ttinfo(-36000,      0, 'HAST'),
        ttinfo(-32400,   3600, 'HADT'),
        ttinfo(-36000,      0, 'HAST'),
        ttinfo(-32400,   3600, 'HADT'),
        ttinfo(-36000,      0, 'HAST'),
        ttinfo(-32400,   3600, 'HADT'),
        ttinfo(-36000,      0, 'HAST'),
        ttinfo(-32400,   3600, 'HADT'),
        ttinfo(-36000,      0, 'HAST'),
        ttinfo(-32400,   3600, 'HADT'),
        ttinfo(-36000,      0, 'HAST'),
        ttinfo(-32400,   3600, 'HADT'),
        ttinfo(-36000,      0, 'HAST'),
        ttinfo(-32400,   3600, 'HADT'),
        ttinfo(-36000,      0, 'HAST'),
        ttinfo(-32400,   3600, 'HADT'),
        ttinfo(-36000,      0, 'HAST'),
        ttinfo(-32400,   3600, 'HADT'),
        ttinfo(-36000,      0, 'HAST'),
        ttinfo(-32400,   3600, 'HADT'),
        ttinfo(-36000,      0, 'HAST'),
        ttinfo(-32400,   3600, 'HADT'),
        ttinfo(-36000,      0, 'HAST'),
        ttinfo(-32400,   3600, 'HADT'),
        ttinfo(-36000,      0, 'HAST'),
        ttinfo(-32400,   3600, 'HADT'),
        ttinfo(-36000,      0, 'HAST'),
        ttinfo(-32400,   3600, 'HADT'),
        ttinfo(-36000,      0, 'HAST'),
        ttinfo(-32400,   3600, 'HADT'),
        ttinfo(-36000,      0, 'HAST'),
        ttinfo(-32400,   3600, 'HADT'),
        ttinfo(-36000,      0, 'HAST'),
        ttinfo(-32400,   3600, 'HADT'),
        ttinfo(-36000,      0, 'HAST'),
        ttinfo(-32400,   3600, 'HADT'),
        ttinfo(-36000,      0, 'HAST'),
        ttinfo(-32400,   3600, 'HADT'),
        ttinfo(-36000,      0, 'HAST'),
        ttinfo(-32400,   3600, 'HADT'),
        ttinfo(-36000,      0, 'HAST'),
        ttinfo(-32400,   3600, 'HADT'),
        ttinfo(-36000,      0, 'HAST'),
        ttinfo(-32400,   3600, 'HADT'),
        ttinfo(-36000,      0, 'HAST'),
        ttinfo(-32400,   3600, 'HADT'),
        ttinfo(-36000,      0, 'HAST'),
        ttinfo(-32400,   3600, 'HADT'),
        ttinfo(-36000,      0, 'HAST'),
        ttinfo(-32400,   3600, 'HADT'),
        ttinfo(-36000,      0, 'HAST'),
        ttinfo(-32400,   3600, 'HADT'),
        ttinfo(-36000,      0, 'HAST'),
        ttinfo(-32400,   3600, 'HADT'),
        ttinfo(-36000,      0, 'HAST'),
        ttinfo(-32400,   3600, 'HADT'),
        ttinfo(-36000,      0, 'HAST'),
        ttinfo(-32400,   3600, 'HADT'),
        ttinfo(-36000,      0, 'HAST'),
        ttinfo(-32400,   3600, 'HADT'),
        ttinfo(-36000,      0, 'HAST'),
        ttinfo(-32400,   3600, 'HADT'),
        ttinfo(-36000,      0, 'HAST'),
        ttinfo(-32400,   3600, 'HADT'),
        ttinfo(-36000,      0, 'HAST'),
        ttinfo(-32400,   3600, 'HADT'),
        ttinfo(-36000,      0, 'HAST'),
        ttinfo(-32400,   3600, 'HADT'),
        ttinfo(-36000,      0, 'HAST'),
        ttinfo(-32400,   3600, 'HADT'),
        ttinfo(-36000,      0, 'HAST'),
        ttinfo(-32400,   3600, 'HADT'),
        ttinfo(-36000,      0, 'HAST'),
        ttinfo(-32400,   3600, 'HADT'),
        ttinfo(-36000,      0, 'HAST'),
        ttinfo(-32400,   3600, 'HADT'),
        ttinfo(-36000,      0, 'HAST'),
        ttinfo(-32400,   3600, 'HADT'),
        ttinfo(-36000,      0, 'HAST'),
        ttinfo(-32400,   3600, 'HADT'),
        ttinfo(-36000,      0, 'HAST'),
        ttinfo(-32400,   3600, 'HADT'),
        ttinfo(-36000,      0, 'HAST'),
        ttinfo(-32400,   3600, 'HADT'),
        ttinfo(-36000,      0, 'HAST'),
        ttinfo(-32400,   3600, 'HADT'),
        ttinfo(-36000,      0, 'HAST'),
        ]

Aleutian = Aleutian() # Singleton

