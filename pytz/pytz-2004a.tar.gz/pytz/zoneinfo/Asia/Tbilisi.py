'''
tzinfo timezone information for Asia/Tbilisi.

Generated from the Olson timezone database:
    ftp://elsie.nci.nih.gov/pub/tz*.tar.gz
'''

from pytz.tzinfo import DstTzInfo
from pytz.tzinfo import memorized_datetime as datetime
from pytz.tzinfo import memorized_ttinfo as ttinfo

class Tbilisi(DstTzInfo):
    '''Asia/Tbilisi timezone definition. See datetime.tzinfo for details'''

    _zone = 'Asia/Tbilisi'

    _utc_transition_times = [
        datetime(   1,  1,  1,  0,  0,  0), #  10756     0 TBMT
        datetime(1924,  5,  1, 21,  0, 44), #  10800     0 TBIT
        datetime(1957,  2, 28, 21,  0,  0), #  14400     0 TBIT
        datetime(1981,  3, 31, 20,  0,  0), #  18000  3600 TBIST
        datetime(1981,  9, 30, 19,  0,  0), #  14400     0 TBIT
        datetime(1982,  3, 31, 20,  0,  0), #  18000  3600 TBIST
        datetime(1982,  9, 30, 19,  0,  0), #  14400     0 TBIT
        datetime(1983,  3, 31, 20,  0,  0), #  18000  3600 TBIST
        datetime(1983,  9, 30, 19,  0,  0), #  14400     0 TBIT
        datetime(1984,  3, 31, 20,  0,  0), #  18000  3600 TBIST
        datetime(1984,  9, 29, 22,  0,  0), #  14400     0 TBIT
        datetime(1985,  3, 30, 22,  0,  0), #  18000  3600 TBIST
        datetime(1985,  9, 28, 22,  0,  0), #  14400     0 TBIT
        datetime(1986,  3, 29, 22,  0,  0), #  18000  3600 TBIST
        datetime(1986,  9, 27, 22,  0,  0), #  14400     0 TBIT
        datetime(1987,  3, 28, 22,  0,  0), #  18000  3600 TBIST
        datetime(1987,  9, 26, 22,  0,  0), #  14400     0 TBIT
        datetime(1988,  3, 26, 22,  0,  0), #  18000  3600 TBIST
        datetime(1988,  9, 24, 22,  0,  0), #  14400     0 TBIT
        datetime(1989,  3, 25, 22,  0,  0), #  18000  3600 TBIST
        datetime(1989,  9, 23, 22,  0,  0), #  14400     0 TBIT
        datetime(1990,  3, 24, 22,  0,  0), #  18000  3600 TBIST
        datetime(1990,  9, 29, 22,  0,  0), #  14400     0 TBIT
        datetime(1991,  3, 30, 22,  0,  0), #  14400     0 TBIST
        datetime(1991,  4,  8, 20,  0,  0), #  14400     0 GEST
        datetime(1991,  9, 28, 23,  0,  0), #  10800     0 GET
        datetime(1991, 12, 31, 21,  0,  0), #  10800     0 GET
        datetime(1992,  3, 28, 21,  0,  0), #  14400  3600 GEST
        datetime(1992,  9, 26, 20,  0,  0), #  10800     0 GET
        datetime(1993,  3, 27, 21,  0,  0), #  14400  3600 GEST
        datetime(1993,  9, 25, 20,  0,  0), #  10800     0 GET
        datetime(1994,  3, 26, 21,  0,  0), #  14400  3600 GEST
        datetime(1994,  9, 24, 20,  0,  0), #  14400     0 GET
        datetime(1995,  3, 25, 20,  0,  0), #  18000  3600 GEST
        datetime(1995,  9, 23, 19,  0,  0), #  14400     0 GET
        datetime(1996,  3, 30, 20,  0,  0), #  18000  3600 GEST
        datetime(1997,  3, 29, 19,  0,  0), #  18000     0 GEST
        datetime(1997, 10, 25, 19,  0,  0), #  14400     0 GET
        datetime(1998,  3, 28, 20,  0,  0), #  18000  3600 GEST
        datetime(1998, 10, 24, 19,  0,  0), #  14400     0 GET
        datetime(1999,  3, 27, 20,  0,  0), #  18000  3600 GEST
        datetime(1999, 10, 30, 19,  0,  0), #  14400     0 GET
        datetime(2000,  3, 25, 20,  0,  0), #  18000  3600 GEST
        datetime(2000, 10, 28, 19,  0,  0), #  14400     0 GET
        datetime(2001,  3, 24, 20,  0,  0), #  18000  3600 GEST
        datetime(2001, 10, 27, 19,  0,  0), #  14400     0 GET
        datetime(2002,  3, 30, 20,  0,  0), #  18000  3600 GEST
        datetime(2002, 10, 26, 19,  0,  0), #  14400     0 GET
        datetime(2003,  3, 29, 20,  0,  0), #  18000  3600 GEST
        datetime(2003, 10, 25, 19,  0,  0), #  14400     0 GET
        datetime(2004,  3, 27, 20,  0,  0), #  18000  3600 GEST
        datetime(2004, 10, 30, 19,  0,  0), #  14400     0 GET
        datetime(2005,  3, 26, 20,  0,  0), #  18000  3600 GEST
        datetime(2005, 10, 29, 19,  0,  0), #  14400     0 GET
        datetime(2006,  3, 25, 20,  0,  0), #  18000  3600 GEST
        datetime(2006, 10, 28, 19,  0,  0), #  14400     0 GET
        datetime(2007,  3, 24, 20,  0,  0), #  18000  3600 GEST
        datetime(2007, 10, 27, 19,  0,  0), #  14400     0 GET
        datetime(2008,  3, 29, 20,  0,  0), #  18000  3600 GEST
        datetime(2008, 10, 25, 19,  0,  0), #  14400     0 GET
        datetime(2009,  3, 28, 20,  0,  0), #  18000  3600 GEST
        datetime(2009, 10, 24, 19,  0,  0), #  14400     0 GET
        datetime(2010,  3, 27, 20,  0,  0), #  18000  3600 GEST
        datetime(2010, 10, 30, 19,  0,  0), #  14400     0 GET
        datetime(2011,  3, 26, 20,  0,  0), #  18000  3600 GEST
        datetime(2011, 10, 29, 19,  0,  0), #  14400     0 GET
        datetime(2012,  3, 24, 20,  0,  0), #  18000  3600 GEST
        datetime(2012, 10, 27, 19,  0,  0), #  14400     0 GET
        datetime(2013,  3, 30, 20,  0,  0), #  18000  3600 GEST
        datetime(2013, 10, 26, 19,  0,  0), #  14400     0 GET
        datetime(2014,  3, 29, 20,  0,  0), #  18000  3600 GEST
        datetime(2014, 10, 25, 19,  0,  0), #  14400     0 GET
        datetime(2015,  3, 28, 20,  0,  0), #  18000  3600 GEST
        datetime(2015, 10, 24, 19,  0,  0), #  14400     0 GET
        datetime(2016,  3, 26, 20,  0,  0), #  18000  3600 GEST
        datetime(2016, 10, 29, 19,  0,  0), #  14400     0 GET
        datetime(2017,  3, 25, 20,  0,  0), #  18000  3600 GEST
        datetime(2017, 10, 28, 19,  0,  0), #  14400     0 GET
        datetime(2018,  3, 24, 20,  0,  0), #  18000  3600 GEST
        datetime(2018, 10, 27, 19,  0,  0), #  14400     0 GET
        datetime(2019,  3, 30, 20,  0,  0), #  18000  3600 GEST
        datetime(2019, 10, 26, 19,  0,  0), #  14400     0 GET
        datetime(2020,  3, 28, 20,  0,  0), #  18000  3600 GEST
        datetime(2020, 10, 24, 19,  0,  0), #  14400     0 GET
        datetime(2021,  3, 27, 20,  0,  0), #  18000  3600 GEST
        datetime(2021, 10, 30, 19,  0,  0), #  14400     0 GET
        datetime(2022,  3, 26, 20,  0,  0), #  18000  3600 GEST
        datetime(2022, 10, 29, 19,  0,  0), #  14400     0 GET
        datetime(2023,  3, 25, 20,  0,  0), #  18000  3600 GEST
        datetime(2023, 10, 28, 19,  0,  0), #  14400     0 GET
        datetime(2024,  3, 30, 20,  0,  0), #  18000  3600 GEST
        datetime(2024, 10, 26, 19,  0,  0), #  14400     0 GET
        datetime(2025,  3, 29, 20,  0,  0), #  18000  3600 GEST
        datetime(2025, 10, 25, 19,  0,  0), #  14400     0 GET
        datetime(2026,  3, 28, 20,  0,  0), #  18000  3600 GEST
        datetime(2026, 10, 24, 19,  0,  0), #  14400     0 GET
        datetime(2027,  3, 27, 20,  0,  0), #  18000  3600 GEST
        datetime(2027, 10, 30, 19,  0,  0), #  14400     0 GET
        datetime(2028,  3, 25, 20,  0,  0), #  18000  3600 GEST
        datetime(2028, 10, 28, 19,  0,  0), #  14400     0 GET
        datetime(2029,  3, 24, 20,  0,  0), #  18000  3600 GEST
        datetime(2029, 10, 27, 19,  0,  0), #  14400     0 GET
        datetime(2030,  3, 30, 20,  0,  0), #  18000  3600 GEST
        datetime(2030, 10, 26, 19,  0,  0), #  14400     0 GET
        datetime(2031,  3, 29, 20,  0,  0), #  18000  3600 GEST
        datetime(2031, 10, 25, 19,  0,  0), #  14400     0 GET
        datetime(2032,  3, 27, 20,  0,  0), #  18000  3600 GEST
        datetime(2032, 10, 30, 19,  0,  0), #  14400     0 GET
        datetime(2033,  3, 26, 20,  0,  0), #  18000  3600 GEST
        datetime(2033, 10, 29, 19,  0,  0), #  14400     0 GET
        datetime(2034,  3, 25, 20,  0,  0), #  18000  3600 GEST
        datetime(2034, 10, 28, 19,  0,  0), #  14400     0 GET
        datetime(2035,  3, 24, 20,  0,  0), #  18000  3600 GEST
        datetime(2035, 10, 27, 19,  0,  0), #  14400     0 GET
        datetime(2036,  3, 29, 20,  0,  0), #  18000  3600 GEST
        datetime(2036, 10, 25, 19,  0,  0), #  14400     0 GET
        datetime(2037,  3, 28, 20,  0,  0), #  18000  3600 GEST
        datetime(2037, 10, 24, 19,  0,  0), #  14400     0 GET
        ]

    _transition_info = [
        ttinfo( 10756,      0, 'TBMT'),
        ttinfo( 10800,      0, 'TBIT'),
        ttinfo( 14400,      0, 'TBIT'),
        ttinfo( 18000,   3600, 'TBIST'),
        ttinfo( 14400,      0, 'TBIT'),
        ttinfo( 18000,   3600, 'TBIST'),
        ttinfo( 14400,      0, 'TBIT'),
        ttinfo( 18000,   3600, 'TBIST'),
        ttinfo( 14400,      0, 'TBIT'),
        ttinfo( 18000,   3600, 'TBIST'),
        ttinfo( 14400,      0, 'TBIT'),
        ttinfo( 18000,   3600, 'TBIST'),
        ttinfo( 14400,      0, 'TBIT'),
        ttinfo( 18000,   3600, 'TBIST'),
        ttinfo( 14400,      0, 'TBIT'),
        ttinfo( 18000,   3600, 'TBIST'),
        ttinfo( 14400,      0, 'TBIT'),
        ttinfo( 18000,   3600, 'TBIST'),
        ttinfo( 14400,      0, 'TBIT'),
        ttinfo( 18000,   3600, 'TBIST'),
        ttinfo( 14400,      0, 'TBIT'),
        ttinfo( 18000,   3600, 'TBIST'),
        ttinfo( 14400,      0, 'TBIT'),
        ttinfo( 14400,      0, 'TBIST'),
        ttinfo( 14400,      0, 'GEST'),
        ttinfo( 10800,      0,  'GET'),
        ttinfo( 10800,      0,  'GET'),
        ttinfo( 14400,   3600, 'GEST'),
        ttinfo( 10800,      0,  'GET'),
        ttinfo( 14400,   3600, 'GEST'),
        ttinfo( 10800,      0,  'GET'),
        ttinfo( 14400,   3600, 'GEST'),
        ttinfo( 14400,      0,  'GET'),
        ttinfo( 18000,   3600, 'GEST'),
        ttinfo( 14400,      0,  'GET'),
        ttinfo( 18000,   3600, 'GEST'),
        ttinfo( 18000,      0, 'GEST'),
        ttinfo( 14400,      0,  'GET'),
        ttinfo( 18000,   3600, 'GEST'),
        ttinfo( 14400,      0,  'GET'),
        ttinfo( 18000,   3600, 'GEST'),
        ttinfo( 14400,      0,  'GET'),
        ttinfo( 18000,   3600, 'GEST'),
        ttinfo( 14400,      0,  'GET'),
        ttinfo( 18000,   3600, 'GEST'),
        ttinfo( 14400,      0,  'GET'),
        ttinfo( 18000,   3600, 'GEST'),
        ttinfo( 14400,      0,  'GET'),
        ttinfo( 18000,   3600, 'GEST'),
        ttinfo( 14400,      0,  'GET'),
        ttinfo( 18000,   3600, 'GEST'),
        ttinfo( 14400,      0,  'GET'),
        ttinfo( 18000,   3600, 'GEST'),
        ttinfo( 14400,      0,  'GET'),
        ttinfo( 18000,   3600, 'GEST'),
        ttinfo( 14400,      0,  'GET'),
        ttinfo( 18000,   3600, 'GEST'),
        ttinfo( 14400,      0,  'GET'),
        ttinfo( 18000,   3600, 'GEST'),
        ttinfo( 14400,      0,  'GET'),
        ttinfo( 18000,   3600, 'GEST'),
        ttinfo( 14400,      0,  'GET'),
        ttinfo( 18000,   3600, 'GEST'),
        ttinfo( 14400,      0,  'GET'),
        ttinfo( 18000,   3600, 'GEST'),
        ttinfo( 14400,      0,  'GET'),
        ttinfo( 18000,   3600, 'GEST'),
        ttinfo( 14400,      0,  'GET'),
        ttinfo( 18000,   3600, 'GEST'),
        ttinfo( 14400,      0,  'GET'),
        ttinfo( 18000,   3600, 'GEST'),
        ttinfo( 14400,      0,  'GET'),
        ttinfo( 18000,   3600, 'GEST'),
        ttinfo( 14400,      0,  'GET'),
        ttinfo( 18000,   3600, 'GEST'),
        ttinfo( 14400,      0,  'GET'),
        ttinfo( 18000,   3600, 'GEST'),
        ttinfo( 14400,      0,  'GET'),
        ttinfo( 18000,   3600, 'GEST'),
        ttinfo( 14400,      0,  'GET'),
        ttinfo( 18000,   3600, 'GEST'),
        ttinfo( 14400,      0,  'GET'),
        ttinfo( 18000,   3600, 'GEST'),
        ttinfo( 14400,      0,  'GET'),
        ttinfo( 18000,   3600, 'GEST'),
        ttinfo( 14400,      0,  'GET'),
        ttinfo( 18000,   3600, 'GEST'),
        ttinfo( 14400,      0,  'GET'),
        ttinfo( 18000,   3600, 'GEST'),
        ttinfo( 14400,      0,  'GET'),
        ttinfo( 18000,   3600, 'GEST'),
        ttinfo( 14400,      0,  'GET'),
        ttinfo( 18000,   3600, 'GEST'),
        ttinfo( 14400,      0,  'GET'),
        ttinfo( 18000,   3600, 'GEST'),
        ttinfo( 14400,      0,  'GET'),
        ttinfo( 18000,   3600, 'GEST'),
        ttinfo( 14400,      0,  'GET'),
        ttinfo( 18000,   3600, 'GEST'),
        ttinfo( 14400,      0,  'GET'),
        ttinfo( 18000,   3600, 'GEST'),
        ttinfo( 14400,      0,  'GET'),
        ttinfo( 18000,   3600, 'GEST'),
        ttinfo( 14400,      0,  'GET'),
        ttinfo( 18000,   3600, 'GEST'),
        ttinfo( 14400,      0,  'GET'),
        ttinfo( 18000,   3600, 'GEST'),
        ttinfo( 14400,      0,  'GET'),
        ttinfo( 18000,   3600, 'GEST'),
        ttinfo( 14400,      0,  'GET'),
        ttinfo( 18000,   3600, 'GEST'),
        ttinfo( 14400,      0,  'GET'),
        ttinfo( 18000,   3600, 'GEST'),
        ttinfo( 14400,      0,  'GET'),
        ttinfo( 18000,   3600, 'GEST'),
        ttinfo( 14400,      0,  'GET'),
        ttinfo( 18000,   3600, 'GEST'),
        ttinfo( 14400,      0,  'GET'),
        ]

Tbilisi = Tbilisi() # Singleton

