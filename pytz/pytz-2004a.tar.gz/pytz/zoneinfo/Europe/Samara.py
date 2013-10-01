'''
tzinfo timezone information for Europe/Samara.

Generated from the Olson timezone database:
    ftp://elsie.nci.nih.gov/pub/tz*.tar.gz
'''

from pytz.tzinfo import DstTzInfo
from pytz.tzinfo import memorized_datetime as datetime
from pytz.tzinfo import memorized_ttinfo as ttinfo

class Samara(DstTzInfo):
    '''Europe/Samara timezone definition. See datetime.tzinfo for details'''

    _zone = 'Europe/Samara'

    _utc_transition_times = [
        datetime(   1,  1,  1,  0,  0,  0), #  12036     0 LMT
        datetime(1919,  6, 30, 22, 39, 24), #  10800     0 KUYT
        datetime(1930,  6, 20, 21,  0,  0), #  14400     0 KUYT
        datetime(1981,  3, 31, 20,  0,  0), #  18000  3600 KUYST
        datetime(1981,  9, 30, 19,  0,  0), #  14400     0 KUYT
        datetime(1982,  3, 31, 20,  0,  0), #  18000  3600 KUYST
        datetime(1982,  9, 30, 19,  0,  0), #  14400     0 KUYT
        datetime(1983,  3, 31, 20,  0,  0), #  18000  3600 KUYST
        datetime(1983,  9, 30, 19,  0,  0), #  14400     0 KUYT
        datetime(1984,  3, 31, 20,  0,  0), #  18000  3600 KUYST
        datetime(1984,  9, 29, 22,  0,  0), #  14400     0 KUYT
        datetime(1985,  3, 30, 22,  0,  0), #  18000  3600 KUYST
        datetime(1985,  9, 28, 22,  0,  0), #  14400     0 KUYT
        datetime(1986,  3, 29, 22,  0,  0), #  18000  3600 KUYST
        datetime(1986,  9, 27, 22,  0,  0), #  14400     0 KUYT
        datetime(1987,  3, 28, 22,  0,  0), #  18000  3600 KUYST
        datetime(1987,  9, 26, 22,  0,  0), #  14400     0 KUYT
        datetime(1988,  3, 26, 22,  0,  0), #  18000  3600 KUYST
        datetime(1988,  9, 24, 22,  0,  0), #  14400     0 KUYT
        datetime(1989,  3, 25, 22,  0,  0), #  14400     0 KUYST
        datetime(1989,  9, 23, 23,  0,  0), #  10800     0 KUYT
        datetime(1990,  3, 24, 23,  0,  0), #  14400  3600 KUYST
        datetime(1990,  9, 29, 23,  0,  0), #  10800     0 KUYT
        datetime(1991,  3, 30, 23,  0,  0), #  10800     0 KUYST
        datetime(1991,  9, 29,  0,  0,  0), #  10800     0 KUYT
        datetime(1991, 10, 20,  0,  0,  0), #  14400     0 SAMT
        datetime(1992,  3, 28, 19,  0,  0), #  18000  3600 SAMST
        datetime(1992,  9, 26, 18,  0,  0), #  14400     0 SAMT
        datetime(1993,  3, 27, 22,  0,  0), #  18000  3600 SAMST
        datetime(1993,  9, 25, 22,  0,  0), #  14400     0 SAMT
        datetime(1994,  3, 26, 22,  0,  0), #  18000  3600 SAMST
        datetime(1994,  9, 24, 22,  0,  0), #  14400     0 SAMT
        datetime(1995,  3, 25, 22,  0,  0), #  18000  3600 SAMST
        datetime(1995,  9, 23, 22,  0,  0), #  14400     0 SAMT
        datetime(1996,  3, 30, 22,  0,  0), #  18000  3600 SAMST
        datetime(1996, 10, 26, 22,  0,  0), #  14400     0 SAMT
        datetime(1997,  3, 29, 22,  0,  0), #  18000  3600 SAMST
        datetime(1997, 10, 25, 22,  0,  0), #  14400     0 SAMT
        datetime(1998,  3, 28, 22,  0,  0), #  18000  3600 SAMST
        datetime(1998, 10, 24, 22,  0,  0), #  14400     0 SAMT
        datetime(1999,  3, 27, 22,  0,  0), #  18000  3600 SAMST
        datetime(1999, 10, 30, 22,  0,  0), #  14400     0 SAMT
        datetime(2000,  3, 25, 22,  0,  0), #  18000  3600 SAMST
        datetime(2000, 10, 28, 22,  0,  0), #  14400     0 SAMT
        datetime(2001,  3, 24, 22,  0,  0), #  18000  3600 SAMST
        datetime(2001, 10, 27, 22,  0,  0), #  14400     0 SAMT
        datetime(2002,  3, 30, 22,  0,  0), #  18000  3600 SAMST
        datetime(2002, 10, 26, 22,  0,  0), #  14400     0 SAMT
        datetime(2003,  3, 29, 22,  0,  0), #  18000  3600 SAMST
        datetime(2003, 10, 25, 22,  0,  0), #  14400     0 SAMT
        datetime(2004,  3, 27, 22,  0,  0), #  18000  3600 SAMST
        datetime(2004, 10, 30, 22,  0,  0), #  14400     0 SAMT
        datetime(2005,  3, 26, 22,  0,  0), #  18000  3600 SAMST
        datetime(2005, 10, 29, 22,  0,  0), #  14400     0 SAMT
        datetime(2006,  3, 25, 22,  0,  0), #  18000  3600 SAMST
        datetime(2006, 10, 28, 22,  0,  0), #  14400     0 SAMT
        datetime(2007,  3, 24, 22,  0,  0), #  18000  3600 SAMST
        datetime(2007, 10, 27, 22,  0,  0), #  14400     0 SAMT
        datetime(2008,  3, 29, 22,  0,  0), #  18000  3600 SAMST
        datetime(2008, 10, 25, 22,  0,  0), #  14400     0 SAMT
        datetime(2009,  3, 28, 22,  0,  0), #  18000  3600 SAMST
        datetime(2009, 10, 24, 22,  0,  0), #  14400     0 SAMT
        datetime(2010,  3, 27, 22,  0,  0), #  18000  3600 SAMST
        datetime(2010, 10, 30, 22,  0,  0), #  14400     0 SAMT
        datetime(2011,  3, 26, 22,  0,  0), #  18000  3600 SAMST
        datetime(2011, 10, 29, 22,  0,  0), #  14400     0 SAMT
        datetime(2012,  3, 24, 22,  0,  0), #  18000  3600 SAMST
        datetime(2012, 10, 27, 22,  0,  0), #  14400     0 SAMT
        datetime(2013,  3, 30, 22,  0,  0), #  18000  3600 SAMST
        datetime(2013, 10, 26, 22,  0,  0), #  14400     0 SAMT
        datetime(2014,  3, 29, 22,  0,  0), #  18000  3600 SAMST
        datetime(2014, 10, 25, 22,  0,  0), #  14400     0 SAMT
        datetime(2015,  3, 28, 22,  0,  0), #  18000  3600 SAMST
        datetime(2015, 10, 24, 22,  0,  0), #  14400     0 SAMT
        datetime(2016,  3, 26, 22,  0,  0), #  18000  3600 SAMST
        datetime(2016, 10, 29, 22,  0,  0), #  14400     0 SAMT
        datetime(2017,  3, 25, 22,  0,  0), #  18000  3600 SAMST
        datetime(2017, 10, 28, 22,  0,  0), #  14400     0 SAMT
        datetime(2018,  3, 24, 22,  0,  0), #  18000  3600 SAMST
        datetime(2018, 10, 27, 22,  0,  0), #  14400     0 SAMT
        datetime(2019,  3, 30, 22,  0,  0), #  18000  3600 SAMST
        datetime(2019, 10, 26, 22,  0,  0), #  14400     0 SAMT
        datetime(2020,  3, 28, 22,  0,  0), #  18000  3600 SAMST
        datetime(2020, 10, 24, 22,  0,  0), #  14400     0 SAMT
        datetime(2021,  3, 27, 22,  0,  0), #  18000  3600 SAMST
        datetime(2021, 10, 30, 22,  0,  0), #  14400     0 SAMT
        datetime(2022,  3, 26, 22,  0,  0), #  18000  3600 SAMST
        datetime(2022, 10, 29, 22,  0,  0), #  14400     0 SAMT
        datetime(2023,  3, 25, 22,  0,  0), #  18000  3600 SAMST
        datetime(2023, 10, 28, 22,  0,  0), #  14400     0 SAMT
        datetime(2024,  3, 30, 22,  0,  0), #  18000  3600 SAMST
        datetime(2024, 10, 26, 22,  0,  0), #  14400     0 SAMT
        datetime(2025,  3, 29, 22,  0,  0), #  18000  3600 SAMST
        datetime(2025, 10, 25, 22,  0,  0), #  14400     0 SAMT
        datetime(2026,  3, 28, 22,  0,  0), #  18000  3600 SAMST
        datetime(2026, 10, 24, 22,  0,  0), #  14400     0 SAMT
        datetime(2027,  3, 27, 22,  0,  0), #  18000  3600 SAMST
        datetime(2027, 10, 30, 22,  0,  0), #  14400     0 SAMT
        datetime(2028,  3, 25, 22,  0,  0), #  18000  3600 SAMST
        datetime(2028, 10, 28, 22,  0,  0), #  14400     0 SAMT
        datetime(2029,  3, 24, 22,  0,  0), #  18000  3600 SAMST
        datetime(2029, 10, 27, 22,  0,  0), #  14400     0 SAMT
        datetime(2030,  3, 30, 22,  0,  0), #  18000  3600 SAMST
        datetime(2030, 10, 26, 22,  0,  0), #  14400     0 SAMT
        datetime(2031,  3, 29, 22,  0,  0), #  18000  3600 SAMST
        datetime(2031, 10, 25, 22,  0,  0), #  14400     0 SAMT
        datetime(2032,  3, 27, 22,  0,  0), #  18000  3600 SAMST
        datetime(2032, 10, 30, 22,  0,  0), #  14400     0 SAMT
        datetime(2033,  3, 26, 22,  0,  0), #  18000  3600 SAMST
        datetime(2033, 10, 29, 22,  0,  0), #  14400     0 SAMT
        datetime(2034,  3, 25, 22,  0,  0), #  18000  3600 SAMST
        datetime(2034, 10, 28, 22,  0,  0), #  14400     0 SAMT
        datetime(2035,  3, 24, 22,  0,  0), #  18000  3600 SAMST
        datetime(2035, 10, 27, 22,  0,  0), #  14400     0 SAMT
        datetime(2036,  3, 29, 22,  0,  0), #  18000  3600 SAMST
        datetime(2036, 10, 25, 22,  0,  0), #  14400     0 SAMT
        datetime(2037,  3, 28, 22,  0,  0), #  18000  3600 SAMST
        datetime(2037, 10, 24, 22,  0,  0), #  14400     0 SAMT
        ]

    _transition_info = [
        ttinfo( 12036,      0,  'LMT'),
        ttinfo( 10800,      0, 'KUYT'),
        ttinfo( 14400,      0, 'KUYT'),
        ttinfo( 18000,   3600, 'KUYST'),
        ttinfo( 14400,      0, 'KUYT'),
        ttinfo( 18000,   3600, 'KUYST'),
        ttinfo( 14400,      0, 'KUYT'),
        ttinfo( 18000,   3600, 'KUYST'),
        ttinfo( 14400,      0, 'KUYT'),
        ttinfo( 18000,   3600, 'KUYST'),
        ttinfo( 14400,      0, 'KUYT'),
        ttinfo( 18000,   3600, 'KUYST'),
        ttinfo( 14400,      0, 'KUYT'),
        ttinfo( 18000,   3600, 'KUYST'),
        ttinfo( 14400,      0, 'KUYT'),
        ttinfo( 18000,   3600, 'KUYST'),
        ttinfo( 14400,      0, 'KUYT'),
        ttinfo( 18000,   3600, 'KUYST'),
        ttinfo( 14400,      0, 'KUYT'),
        ttinfo( 14400,      0, 'KUYST'),
        ttinfo( 10800,      0, 'KUYT'),
        ttinfo( 14400,   3600, 'KUYST'),
        ttinfo( 10800,      0, 'KUYT'),
        ttinfo( 10800,      0, 'KUYST'),
        ttinfo( 10800,      0, 'KUYT'),
        ttinfo( 14400,      0, 'SAMT'),
        ttinfo( 18000,   3600, 'SAMST'),
        ttinfo( 14400,      0, 'SAMT'),
        ttinfo( 18000,   3600, 'SAMST'),
        ttinfo( 14400,      0, 'SAMT'),
        ttinfo( 18000,   3600, 'SAMST'),
        ttinfo( 14400,      0, 'SAMT'),
        ttinfo( 18000,   3600, 'SAMST'),
        ttinfo( 14400,      0, 'SAMT'),
        ttinfo( 18000,   3600, 'SAMST'),
        ttinfo( 14400,      0, 'SAMT'),
        ttinfo( 18000,   3600, 'SAMST'),
        ttinfo( 14400,      0, 'SAMT'),
        ttinfo( 18000,   3600, 'SAMST'),
        ttinfo( 14400,      0, 'SAMT'),
        ttinfo( 18000,   3600, 'SAMST'),
        ttinfo( 14400,      0, 'SAMT'),
        ttinfo( 18000,   3600, 'SAMST'),
        ttinfo( 14400,      0, 'SAMT'),
        ttinfo( 18000,   3600, 'SAMST'),
        ttinfo( 14400,      0, 'SAMT'),
        ttinfo( 18000,   3600, 'SAMST'),
        ttinfo( 14400,      0, 'SAMT'),
        ttinfo( 18000,   3600, 'SAMST'),
        ttinfo( 14400,      0, 'SAMT'),
        ttinfo( 18000,   3600, 'SAMST'),
        ttinfo( 14400,      0, 'SAMT'),
        ttinfo( 18000,   3600, 'SAMST'),
        ttinfo( 14400,      0, 'SAMT'),
        ttinfo( 18000,   3600, 'SAMST'),
        ttinfo( 14400,      0, 'SAMT'),
        ttinfo( 18000,   3600, 'SAMST'),
        ttinfo( 14400,      0, 'SAMT'),
        ttinfo( 18000,   3600, 'SAMST'),
        ttinfo( 14400,      0, 'SAMT'),
        ttinfo( 18000,   3600, 'SAMST'),
        ttinfo( 14400,      0, 'SAMT'),
        ttinfo( 18000,   3600, 'SAMST'),
        ttinfo( 14400,      0, 'SAMT'),
        ttinfo( 18000,   3600, 'SAMST'),
        ttinfo( 14400,      0, 'SAMT'),
        ttinfo( 18000,   3600, 'SAMST'),
        ttinfo( 14400,      0, 'SAMT'),
        ttinfo( 18000,   3600, 'SAMST'),
        ttinfo( 14400,      0, 'SAMT'),
        ttinfo( 18000,   3600, 'SAMST'),
        ttinfo( 14400,      0, 'SAMT'),
        ttinfo( 18000,   3600, 'SAMST'),
        ttinfo( 14400,      0, 'SAMT'),
        ttinfo( 18000,   3600, 'SAMST'),
        ttinfo( 14400,      0, 'SAMT'),
        ttinfo( 18000,   3600, 'SAMST'),
        ttinfo( 14400,      0, 'SAMT'),
        ttinfo( 18000,   3600, 'SAMST'),
        ttinfo( 14400,      0, 'SAMT'),
        ttinfo( 18000,   3600, 'SAMST'),
        ttinfo( 14400,      0, 'SAMT'),
        ttinfo( 18000,   3600, 'SAMST'),
        ttinfo( 14400,      0, 'SAMT'),
        ttinfo( 18000,   3600, 'SAMST'),
        ttinfo( 14400,      0, 'SAMT'),
        ttinfo( 18000,   3600, 'SAMST'),
        ttinfo( 14400,      0, 'SAMT'),
        ttinfo( 18000,   3600, 'SAMST'),
        ttinfo( 14400,      0, 'SAMT'),
        ttinfo( 18000,   3600, 'SAMST'),
        ttinfo( 14400,      0, 'SAMT'),
        ttinfo( 18000,   3600, 'SAMST'),
        ttinfo( 14400,      0, 'SAMT'),
        ttinfo( 18000,   3600, 'SAMST'),
        ttinfo( 14400,      0, 'SAMT'),
        ttinfo( 18000,   3600, 'SAMST'),
        ttinfo( 14400,      0, 'SAMT'),
        ttinfo( 18000,   3600, 'SAMST'),
        ttinfo( 14400,      0, 'SAMT'),
        ttinfo( 18000,   3600, 'SAMST'),
        ttinfo( 14400,      0, 'SAMT'),
        ttinfo( 18000,   3600, 'SAMST'),
        ttinfo( 14400,      0, 'SAMT'),
        ttinfo( 18000,   3600, 'SAMST'),
        ttinfo( 14400,      0, 'SAMT'),
        ttinfo( 18000,   3600, 'SAMST'),
        ttinfo( 14400,      0, 'SAMT'),
        ttinfo( 18000,   3600, 'SAMST'),
        ttinfo( 14400,      0, 'SAMT'),
        ttinfo( 18000,   3600, 'SAMST'),
        ttinfo( 14400,      0, 'SAMT'),
        ttinfo( 18000,   3600, 'SAMST'),
        ttinfo( 14400,      0, 'SAMT'),
        ttinfo( 18000,   3600, 'SAMST'),
        ttinfo( 14400,      0, 'SAMT'),
        ttinfo( 18000,   3600, 'SAMST'),
        ttinfo( 14400,      0, 'SAMT'),
        ]

Samara = Samara() # Singleton

