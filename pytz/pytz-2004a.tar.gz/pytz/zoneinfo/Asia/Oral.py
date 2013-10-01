'''
tzinfo timezone information for Asia/Oral.

Generated from the Olson timezone database:
    ftp://elsie.nci.nih.gov/pub/tz*.tar.gz
'''

from pytz.tzinfo import DstTzInfo
from pytz.tzinfo import memorized_datetime as datetime
from pytz.tzinfo import memorized_ttinfo as ttinfo

class Oral(DstTzInfo):
    '''Asia/Oral timezone definition. See datetime.tzinfo for details'''

    _zone = 'Asia/Oral'

    _utc_transition_times = [
        datetime(   1,  1,  1,  0,  0,  0), #  12324     0 LMT
        datetime(1924,  5,  1, 20, 34, 36), #  14400     0 URAT
        datetime(1930,  6, 20, 20,  0,  0), #  18000     0 URAT
        datetime(1981,  3, 31, 19,  0,  0), #  21600  3600 URAST
        datetime(1981,  9, 30, 18,  0,  0), #  21600     0 URAT
        datetime(1982,  3, 31, 18,  0,  0), #  21600     0 URAST
        datetime(1982,  9, 30, 18,  0,  0), #  18000     0 URAT
        datetime(1983,  3, 31, 19,  0,  0), #  21600  3600 URAST
        datetime(1983,  9, 30, 18,  0,  0), #  18000     0 URAT
        datetime(1984,  3, 31, 19,  0,  0), #  21600  3600 URAST
        datetime(1984,  9, 29, 21,  0,  0), #  18000     0 URAT
        datetime(1985,  3, 30, 21,  0,  0), #  21600  3600 URAST
        datetime(1985,  9, 28, 21,  0,  0), #  18000     0 URAT
        datetime(1986,  3, 29, 21,  0,  0), #  21600  3600 URAST
        datetime(1986,  9, 27, 21,  0,  0), #  18000     0 URAT
        datetime(1987,  3, 28, 21,  0,  0), #  21600  3600 URAST
        datetime(1987,  9, 26, 21,  0,  0), #  18000     0 URAT
        datetime(1988,  3, 26, 21,  0,  0), #  21600  3600 URAST
        datetime(1988,  9, 24, 21,  0,  0), #  18000     0 URAT
        datetime(1989,  3, 25, 21,  0,  0), #  18000     0 URAST
        datetime(1989,  9, 23, 22,  0,  0), #  14400     0 URAT
        datetime(1990,  3, 24, 22,  0,  0), #  18000  3600 URAST
        datetime(1990,  9, 29, 22,  0,  0), #  14400     0 URAT
        datetime(1990, 12, 31, 20,  0,  0), #  14400     0 URAT
        datetime(1991, 12, 15, 20,  0,  0), #  14400     0 ORAT
        datetime(1992,  3, 28, 19,  0,  0), #  18000  3600 ORAST
        datetime(1992,  9, 26, 18,  0,  0), #  14400     0 ORAT
        datetime(1993,  3, 27, 22,  0,  0), #  18000  3600 ORAST
        datetime(1993,  9, 25, 22,  0,  0), #  14400     0 ORAT
        datetime(1994,  3, 26, 22,  0,  0), #  18000  3600 ORAST
        datetime(1994,  9, 24, 22,  0,  0), #  14400     0 ORAT
        datetime(1995,  3, 25, 22,  0,  0), #  18000  3600 ORAST
        datetime(1995,  9, 23, 22,  0,  0), #  14400     0 ORAT
        datetime(1996,  3, 30, 22,  0,  0), #  18000  3600 ORAST
        datetime(1996, 10, 26, 22,  0,  0), #  14400     0 ORAT
        datetime(1997,  3, 29, 22,  0,  0), #  18000  3600 ORAST
        datetime(1997, 10, 25, 22,  0,  0), #  14400     0 ORAT
        datetime(1998,  3, 28, 22,  0,  0), #  18000  3600 ORAST
        datetime(1998, 10, 24, 22,  0,  0), #  14400     0 ORAT
        datetime(1999,  3, 27, 22,  0,  0), #  18000  3600 ORAST
        datetime(1999, 10, 30, 22,  0,  0), #  14400     0 ORAT
        datetime(2000,  3, 25, 22,  0,  0), #  18000  3600 ORAST
        datetime(2000, 10, 28, 22,  0,  0), #  14400     0 ORAT
        datetime(2001,  3, 24, 22,  0,  0), #  18000  3600 ORAST
        datetime(2001, 10, 27, 22,  0,  0), #  14400     0 ORAT
        datetime(2002,  3, 30, 22,  0,  0), #  18000  3600 ORAST
        datetime(2002, 10, 26, 22,  0,  0), #  14400     0 ORAT
        datetime(2003,  3, 29, 22,  0,  0), #  18000  3600 ORAST
        datetime(2003, 10, 25, 22,  0,  0), #  14400     0 ORAT
        datetime(2004,  3, 27, 22,  0,  0), #  18000  3600 ORAST
        datetime(2004, 10, 30, 22,  0,  0), #  14400     0 ORAT
        datetime(2005,  3, 26, 22,  0,  0), #  18000  3600 ORAST
        datetime(2005, 10, 29, 22,  0,  0), #  14400     0 ORAT
        datetime(2006,  3, 25, 22,  0,  0), #  18000  3600 ORAST
        datetime(2006, 10, 28, 22,  0,  0), #  14400     0 ORAT
        datetime(2007,  3, 24, 22,  0,  0), #  18000  3600 ORAST
        datetime(2007, 10, 27, 22,  0,  0), #  14400     0 ORAT
        datetime(2008,  3, 29, 22,  0,  0), #  18000  3600 ORAST
        datetime(2008, 10, 25, 22,  0,  0), #  14400     0 ORAT
        datetime(2009,  3, 28, 22,  0,  0), #  18000  3600 ORAST
        datetime(2009, 10, 24, 22,  0,  0), #  14400     0 ORAT
        datetime(2010,  3, 27, 22,  0,  0), #  18000  3600 ORAST
        datetime(2010, 10, 30, 22,  0,  0), #  14400     0 ORAT
        datetime(2011,  3, 26, 22,  0,  0), #  18000  3600 ORAST
        datetime(2011, 10, 29, 22,  0,  0), #  14400     0 ORAT
        datetime(2012,  3, 24, 22,  0,  0), #  18000  3600 ORAST
        datetime(2012, 10, 27, 22,  0,  0), #  14400     0 ORAT
        datetime(2013,  3, 30, 22,  0,  0), #  18000  3600 ORAST
        datetime(2013, 10, 26, 22,  0,  0), #  14400     0 ORAT
        datetime(2014,  3, 29, 22,  0,  0), #  18000  3600 ORAST
        datetime(2014, 10, 25, 22,  0,  0), #  14400     0 ORAT
        datetime(2015,  3, 28, 22,  0,  0), #  18000  3600 ORAST
        datetime(2015, 10, 24, 22,  0,  0), #  14400     0 ORAT
        datetime(2016,  3, 26, 22,  0,  0), #  18000  3600 ORAST
        datetime(2016, 10, 29, 22,  0,  0), #  14400     0 ORAT
        datetime(2017,  3, 25, 22,  0,  0), #  18000  3600 ORAST
        datetime(2017, 10, 28, 22,  0,  0), #  14400     0 ORAT
        datetime(2018,  3, 24, 22,  0,  0), #  18000  3600 ORAST
        datetime(2018, 10, 27, 22,  0,  0), #  14400     0 ORAT
        datetime(2019,  3, 30, 22,  0,  0), #  18000  3600 ORAST
        datetime(2019, 10, 26, 22,  0,  0), #  14400     0 ORAT
        datetime(2020,  3, 28, 22,  0,  0), #  18000  3600 ORAST
        datetime(2020, 10, 24, 22,  0,  0), #  14400     0 ORAT
        datetime(2021,  3, 27, 22,  0,  0), #  18000  3600 ORAST
        datetime(2021, 10, 30, 22,  0,  0), #  14400     0 ORAT
        datetime(2022,  3, 26, 22,  0,  0), #  18000  3600 ORAST
        datetime(2022, 10, 29, 22,  0,  0), #  14400     0 ORAT
        datetime(2023,  3, 25, 22,  0,  0), #  18000  3600 ORAST
        datetime(2023, 10, 28, 22,  0,  0), #  14400     0 ORAT
        datetime(2024,  3, 30, 22,  0,  0), #  18000  3600 ORAST
        datetime(2024, 10, 26, 22,  0,  0), #  14400     0 ORAT
        datetime(2025,  3, 29, 22,  0,  0), #  18000  3600 ORAST
        datetime(2025, 10, 25, 22,  0,  0), #  14400     0 ORAT
        datetime(2026,  3, 28, 22,  0,  0), #  18000  3600 ORAST
        datetime(2026, 10, 24, 22,  0,  0), #  14400     0 ORAT
        datetime(2027,  3, 27, 22,  0,  0), #  18000  3600 ORAST
        datetime(2027, 10, 30, 22,  0,  0), #  14400     0 ORAT
        datetime(2028,  3, 25, 22,  0,  0), #  18000  3600 ORAST
        datetime(2028, 10, 28, 22,  0,  0), #  14400     0 ORAT
        datetime(2029,  3, 24, 22,  0,  0), #  18000  3600 ORAST
        datetime(2029, 10, 27, 22,  0,  0), #  14400     0 ORAT
        datetime(2030,  3, 30, 22,  0,  0), #  18000  3600 ORAST
        datetime(2030, 10, 26, 22,  0,  0), #  14400     0 ORAT
        datetime(2031,  3, 29, 22,  0,  0), #  18000  3600 ORAST
        datetime(2031, 10, 25, 22,  0,  0), #  14400     0 ORAT
        datetime(2032,  3, 27, 22,  0,  0), #  18000  3600 ORAST
        datetime(2032, 10, 30, 22,  0,  0), #  14400     0 ORAT
        datetime(2033,  3, 26, 22,  0,  0), #  18000  3600 ORAST
        datetime(2033, 10, 29, 22,  0,  0), #  14400     0 ORAT
        datetime(2034,  3, 25, 22,  0,  0), #  18000  3600 ORAST
        datetime(2034, 10, 28, 22,  0,  0), #  14400     0 ORAT
        datetime(2035,  3, 24, 22,  0,  0), #  18000  3600 ORAST
        datetime(2035, 10, 27, 22,  0,  0), #  14400     0 ORAT
        datetime(2036,  3, 29, 22,  0,  0), #  18000  3600 ORAST
        datetime(2036, 10, 25, 22,  0,  0), #  14400     0 ORAT
        datetime(2037,  3, 28, 22,  0,  0), #  18000  3600 ORAST
        datetime(2037, 10, 24, 22,  0,  0), #  14400     0 ORAT
        ]

    _transition_info = [
        ttinfo( 12324,      0,  'LMT'),
        ttinfo( 14400,      0, 'URAT'),
        ttinfo( 18000,      0, 'URAT'),
        ttinfo( 21600,   3600, 'URAST'),
        ttinfo( 21600,      0, 'URAT'),
        ttinfo( 21600,      0, 'URAST'),
        ttinfo( 18000,      0, 'URAT'),
        ttinfo( 21600,   3600, 'URAST'),
        ttinfo( 18000,      0, 'URAT'),
        ttinfo( 21600,   3600, 'URAST'),
        ttinfo( 18000,      0, 'URAT'),
        ttinfo( 21600,   3600, 'URAST'),
        ttinfo( 18000,      0, 'URAT'),
        ttinfo( 21600,   3600, 'URAST'),
        ttinfo( 18000,      0, 'URAT'),
        ttinfo( 21600,   3600, 'URAST'),
        ttinfo( 18000,      0, 'URAT'),
        ttinfo( 21600,   3600, 'URAST'),
        ttinfo( 18000,      0, 'URAT'),
        ttinfo( 18000,      0, 'URAST'),
        ttinfo( 14400,      0, 'URAT'),
        ttinfo( 18000,   3600, 'URAST'),
        ttinfo( 14400,      0, 'URAT'),
        ttinfo( 14400,      0, 'URAT'),
        ttinfo( 14400,      0, 'ORAT'),
        ttinfo( 18000,   3600, 'ORAST'),
        ttinfo( 14400,      0, 'ORAT'),
        ttinfo( 18000,   3600, 'ORAST'),
        ttinfo( 14400,      0, 'ORAT'),
        ttinfo( 18000,   3600, 'ORAST'),
        ttinfo( 14400,      0, 'ORAT'),
        ttinfo( 18000,   3600, 'ORAST'),
        ttinfo( 14400,      0, 'ORAT'),
        ttinfo( 18000,   3600, 'ORAST'),
        ttinfo( 14400,      0, 'ORAT'),
        ttinfo( 18000,   3600, 'ORAST'),
        ttinfo( 14400,      0, 'ORAT'),
        ttinfo( 18000,   3600, 'ORAST'),
        ttinfo( 14400,      0, 'ORAT'),
        ttinfo( 18000,   3600, 'ORAST'),
        ttinfo( 14400,      0, 'ORAT'),
        ttinfo( 18000,   3600, 'ORAST'),
        ttinfo( 14400,      0, 'ORAT'),
        ttinfo( 18000,   3600, 'ORAST'),
        ttinfo( 14400,      0, 'ORAT'),
        ttinfo( 18000,   3600, 'ORAST'),
        ttinfo( 14400,      0, 'ORAT'),
        ttinfo( 18000,   3600, 'ORAST'),
        ttinfo( 14400,      0, 'ORAT'),
        ttinfo( 18000,   3600, 'ORAST'),
        ttinfo( 14400,      0, 'ORAT'),
        ttinfo( 18000,   3600, 'ORAST'),
        ttinfo( 14400,      0, 'ORAT'),
        ttinfo( 18000,   3600, 'ORAST'),
        ttinfo( 14400,      0, 'ORAT'),
        ttinfo( 18000,   3600, 'ORAST'),
        ttinfo( 14400,      0, 'ORAT'),
        ttinfo( 18000,   3600, 'ORAST'),
        ttinfo( 14400,      0, 'ORAT'),
        ttinfo( 18000,   3600, 'ORAST'),
        ttinfo( 14400,      0, 'ORAT'),
        ttinfo( 18000,   3600, 'ORAST'),
        ttinfo( 14400,      0, 'ORAT'),
        ttinfo( 18000,   3600, 'ORAST'),
        ttinfo( 14400,      0, 'ORAT'),
        ttinfo( 18000,   3600, 'ORAST'),
        ttinfo( 14400,      0, 'ORAT'),
        ttinfo( 18000,   3600, 'ORAST'),
        ttinfo( 14400,      0, 'ORAT'),
        ttinfo( 18000,   3600, 'ORAST'),
        ttinfo( 14400,      0, 'ORAT'),
        ttinfo( 18000,   3600, 'ORAST'),
        ttinfo( 14400,      0, 'ORAT'),
        ttinfo( 18000,   3600, 'ORAST'),
        ttinfo( 14400,      0, 'ORAT'),
        ttinfo( 18000,   3600, 'ORAST'),
        ttinfo( 14400,      0, 'ORAT'),
        ttinfo( 18000,   3600, 'ORAST'),
        ttinfo( 14400,      0, 'ORAT'),
        ttinfo( 18000,   3600, 'ORAST'),
        ttinfo( 14400,      0, 'ORAT'),
        ttinfo( 18000,   3600, 'ORAST'),
        ttinfo( 14400,      0, 'ORAT'),
        ttinfo( 18000,   3600, 'ORAST'),
        ttinfo( 14400,      0, 'ORAT'),
        ttinfo( 18000,   3600, 'ORAST'),
        ttinfo( 14400,      0, 'ORAT'),
        ttinfo( 18000,   3600, 'ORAST'),
        ttinfo( 14400,      0, 'ORAT'),
        ttinfo( 18000,   3600, 'ORAST'),
        ttinfo( 14400,      0, 'ORAT'),
        ttinfo( 18000,   3600, 'ORAST'),
        ttinfo( 14400,      0, 'ORAT'),
        ttinfo( 18000,   3600, 'ORAST'),
        ttinfo( 14400,      0, 'ORAT'),
        ttinfo( 18000,   3600, 'ORAST'),
        ttinfo( 14400,      0, 'ORAT'),
        ttinfo( 18000,   3600, 'ORAST'),
        ttinfo( 14400,      0, 'ORAT'),
        ttinfo( 18000,   3600, 'ORAST'),
        ttinfo( 14400,      0, 'ORAT'),
        ttinfo( 18000,   3600, 'ORAST'),
        ttinfo( 14400,      0, 'ORAT'),
        ttinfo( 18000,   3600, 'ORAST'),
        ttinfo( 14400,      0, 'ORAT'),
        ttinfo( 18000,   3600, 'ORAST'),
        ttinfo( 14400,      0, 'ORAT'),
        ttinfo( 18000,   3600, 'ORAST'),
        ttinfo( 14400,      0, 'ORAT'),
        ttinfo( 18000,   3600, 'ORAST'),
        ttinfo( 14400,      0, 'ORAT'),
        ttinfo( 18000,   3600, 'ORAST'),
        ttinfo( 14400,      0, 'ORAT'),
        ttinfo( 18000,   3600, 'ORAST'),
        ttinfo( 14400,      0, 'ORAT'),
        ttinfo( 18000,   3600, 'ORAST'),
        ttinfo( 14400,      0, 'ORAT'),
        ]

Oral = Oral() # Singleton

