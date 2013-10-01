'''
tzinfo timezone information for Asia/Kamchatka.

Generated from the Olson timezone database:
    ftp://elsie.nci.nih.gov/pub/tz*.tar.gz
'''

from pytz.tzinfo import DstTzInfo
from pytz.tzinfo import memorized_datetime as datetime
from pytz.tzinfo import memorized_ttinfo as ttinfo

class Kamchatka(DstTzInfo):
    '''Asia/Kamchatka timezone definition. See datetime.tzinfo for details'''

    _zone = 'Asia/Kamchatka'

    _utc_transition_times = [
        datetime(   1,  1,  1,  0,  0,  0), #  38076     0 LMT
        datetime(1922, 11,  9, 13, 25, 24), #  39600     0 PETT
        datetime(1930,  6, 20, 13,  0,  0), #  43200     0 PETT
        datetime(1981,  3, 31, 12,  0,  0), #  46800  3600 PETST
        datetime(1981,  9, 30, 11,  0,  0), #  43200     0 PETT
        datetime(1982,  3, 31, 12,  0,  0), #  46800  3600 PETST
        datetime(1982,  9, 30, 11,  0,  0), #  43200     0 PETT
        datetime(1983,  3, 31, 12,  0,  0), #  46800  3600 PETST
        datetime(1983,  9, 30, 11,  0,  0), #  43200     0 PETT
        datetime(1984,  3, 31, 12,  0,  0), #  46800  3600 PETST
        datetime(1984,  9, 29, 14,  0,  0), #  43200     0 PETT
        datetime(1985,  3, 30, 14,  0,  0), #  46800  3600 PETST
        datetime(1985,  9, 28, 14,  0,  0), #  43200     0 PETT
        datetime(1986,  3, 29, 14,  0,  0), #  46800  3600 PETST
        datetime(1986,  9, 27, 14,  0,  0), #  43200     0 PETT
        datetime(1987,  3, 28, 14,  0,  0), #  46800  3600 PETST
        datetime(1987,  9, 26, 14,  0,  0), #  43200     0 PETT
        datetime(1988,  3, 26, 14,  0,  0), #  46800  3600 PETST
        datetime(1988,  9, 24, 14,  0,  0), #  43200     0 PETT
        datetime(1989,  3, 25, 14,  0,  0), #  46800  3600 PETST
        datetime(1989,  9, 23, 14,  0,  0), #  43200     0 PETT
        datetime(1990,  3, 24, 14,  0,  0), #  46800  3600 PETST
        datetime(1990,  9, 29, 14,  0,  0), #  43200     0 PETT
        datetime(1991,  3, 30, 14,  0,  0), #  43200     0 PETST
        datetime(1991,  9, 28, 15,  0,  0), #  39600     0 PETT
        datetime(1992,  1, 18, 15,  0,  0), #  43200     0 PETT
        datetime(1992,  3, 28, 11,  0,  0), #  46800  3600 PETST
        datetime(1992,  9, 26, 10,  0,  0), #  43200     0 PETT
        datetime(1993,  3, 27, 14,  0,  0), #  46800  3600 PETST
        datetime(1993,  9, 25, 14,  0,  0), #  43200     0 PETT
        datetime(1994,  3, 26, 14,  0,  0), #  46800  3600 PETST
        datetime(1994,  9, 24, 14,  0,  0), #  43200     0 PETT
        datetime(1995,  3, 25, 14,  0,  0), #  46800  3600 PETST
        datetime(1995,  9, 23, 14,  0,  0), #  43200     0 PETT
        datetime(1996,  3, 30, 14,  0,  0), #  46800  3600 PETST
        datetime(1996, 10, 26, 14,  0,  0), #  43200     0 PETT
        datetime(1997,  3, 29, 14,  0,  0), #  46800  3600 PETST
        datetime(1997, 10, 25, 14,  0,  0), #  43200     0 PETT
        datetime(1998,  3, 28, 14,  0,  0), #  46800  3600 PETST
        datetime(1998, 10, 24, 14,  0,  0), #  43200     0 PETT
        datetime(1999,  3, 27, 14,  0,  0), #  46800  3600 PETST
        datetime(1999, 10, 30, 14,  0,  0), #  43200     0 PETT
        datetime(2000,  3, 25, 14,  0,  0), #  46800  3600 PETST
        datetime(2000, 10, 28, 14,  0,  0), #  43200     0 PETT
        datetime(2001,  3, 24, 14,  0,  0), #  46800  3600 PETST
        datetime(2001, 10, 27, 14,  0,  0), #  43200     0 PETT
        datetime(2002,  3, 30, 14,  0,  0), #  46800  3600 PETST
        datetime(2002, 10, 26, 14,  0,  0), #  43200     0 PETT
        datetime(2003,  3, 29, 14,  0,  0), #  46800  3600 PETST
        datetime(2003, 10, 25, 14,  0,  0), #  43200     0 PETT
        datetime(2004,  3, 27, 14,  0,  0), #  46800  3600 PETST
        datetime(2004, 10, 30, 14,  0,  0), #  43200     0 PETT
        datetime(2005,  3, 26, 14,  0,  0), #  46800  3600 PETST
        datetime(2005, 10, 29, 14,  0,  0), #  43200     0 PETT
        datetime(2006,  3, 25, 14,  0,  0), #  46800  3600 PETST
        datetime(2006, 10, 28, 14,  0,  0), #  43200     0 PETT
        datetime(2007,  3, 24, 14,  0,  0), #  46800  3600 PETST
        datetime(2007, 10, 27, 14,  0,  0), #  43200     0 PETT
        datetime(2008,  3, 29, 14,  0,  0), #  46800  3600 PETST
        datetime(2008, 10, 25, 14,  0,  0), #  43200     0 PETT
        datetime(2009,  3, 28, 14,  0,  0), #  46800  3600 PETST
        datetime(2009, 10, 24, 14,  0,  0), #  43200     0 PETT
        datetime(2010,  3, 27, 14,  0,  0), #  46800  3600 PETST
        datetime(2010, 10, 30, 14,  0,  0), #  43200     0 PETT
        datetime(2011,  3, 26, 14,  0,  0), #  46800  3600 PETST
        datetime(2011, 10, 29, 14,  0,  0), #  43200     0 PETT
        datetime(2012,  3, 24, 14,  0,  0), #  46800  3600 PETST
        datetime(2012, 10, 27, 14,  0,  0), #  43200     0 PETT
        datetime(2013,  3, 30, 14,  0,  0), #  46800  3600 PETST
        datetime(2013, 10, 26, 14,  0,  0), #  43200     0 PETT
        datetime(2014,  3, 29, 14,  0,  0), #  46800  3600 PETST
        datetime(2014, 10, 25, 14,  0,  0), #  43200     0 PETT
        datetime(2015,  3, 28, 14,  0,  0), #  46800  3600 PETST
        datetime(2015, 10, 24, 14,  0,  0), #  43200     0 PETT
        datetime(2016,  3, 26, 14,  0,  0), #  46800  3600 PETST
        datetime(2016, 10, 29, 14,  0,  0), #  43200     0 PETT
        datetime(2017,  3, 25, 14,  0,  0), #  46800  3600 PETST
        datetime(2017, 10, 28, 14,  0,  0), #  43200     0 PETT
        datetime(2018,  3, 24, 14,  0,  0), #  46800  3600 PETST
        datetime(2018, 10, 27, 14,  0,  0), #  43200     0 PETT
        datetime(2019,  3, 30, 14,  0,  0), #  46800  3600 PETST
        datetime(2019, 10, 26, 14,  0,  0), #  43200     0 PETT
        datetime(2020,  3, 28, 14,  0,  0), #  46800  3600 PETST
        datetime(2020, 10, 24, 14,  0,  0), #  43200     0 PETT
        datetime(2021,  3, 27, 14,  0,  0), #  46800  3600 PETST
        datetime(2021, 10, 30, 14,  0,  0), #  43200     0 PETT
        datetime(2022,  3, 26, 14,  0,  0), #  46800  3600 PETST
        datetime(2022, 10, 29, 14,  0,  0), #  43200     0 PETT
        datetime(2023,  3, 25, 14,  0,  0), #  46800  3600 PETST
        datetime(2023, 10, 28, 14,  0,  0), #  43200     0 PETT
        datetime(2024,  3, 30, 14,  0,  0), #  46800  3600 PETST
        datetime(2024, 10, 26, 14,  0,  0), #  43200     0 PETT
        datetime(2025,  3, 29, 14,  0,  0), #  46800  3600 PETST
        datetime(2025, 10, 25, 14,  0,  0), #  43200     0 PETT
        datetime(2026,  3, 28, 14,  0,  0), #  46800  3600 PETST
        datetime(2026, 10, 24, 14,  0,  0), #  43200     0 PETT
        datetime(2027,  3, 27, 14,  0,  0), #  46800  3600 PETST
        datetime(2027, 10, 30, 14,  0,  0), #  43200     0 PETT
        datetime(2028,  3, 25, 14,  0,  0), #  46800  3600 PETST
        datetime(2028, 10, 28, 14,  0,  0), #  43200     0 PETT
        datetime(2029,  3, 24, 14,  0,  0), #  46800  3600 PETST
        datetime(2029, 10, 27, 14,  0,  0), #  43200     0 PETT
        datetime(2030,  3, 30, 14,  0,  0), #  46800  3600 PETST
        datetime(2030, 10, 26, 14,  0,  0), #  43200     0 PETT
        datetime(2031,  3, 29, 14,  0,  0), #  46800  3600 PETST
        datetime(2031, 10, 25, 14,  0,  0), #  43200     0 PETT
        datetime(2032,  3, 27, 14,  0,  0), #  46800  3600 PETST
        datetime(2032, 10, 30, 14,  0,  0), #  43200     0 PETT
        datetime(2033,  3, 26, 14,  0,  0), #  46800  3600 PETST
        datetime(2033, 10, 29, 14,  0,  0), #  43200     0 PETT
        datetime(2034,  3, 25, 14,  0,  0), #  46800  3600 PETST
        datetime(2034, 10, 28, 14,  0,  0), #  43200     0 PETT
        datetime(2035,  3, 24, 14,  0,  0), #  46800  3600 PETST
        datetime(2035, 10, 27, 14,  0,  0), #  43200     0 PETT
        datetime(2036,  3, 29, 14,  0,  0), #  46800  3600 PETST
        datetime(2036, 10, 25, 14,  0,  0), #  43200     0 PETT
        datetime(2037,  3, 28, 14,  0,  0), #  46800  3600 PETST
        datetime(2037, 10, 24, 14,  0,  0), #  43200     0 PETT
        ]

    _transition_info = [
        ttinfo( 38076,      0,  'LMT'),
        ttinfo( 39600,      0, 'PETT'),
        ttinfo( 43200,      0, 'PETT'),
        ttinfo( 46800,   3600, 'PETST'),
        ttinfo( 43200,      0, 'PETT'),
        ttinfo( 46800,   3600, 'PETST'),
        ttinfo( 43200,      0, 'PETT'),
        ttinfo( 46800,   3600, 'PETST'),
        ttinfo( 43200,      0, 'PETT'),
        ttinfo( 46800,   3600, 'PETST'),
        ttinfo( 43200,      0, 'PETT'),
        ttinfo( 46800,   3600, 'PETST'),
        ttinfo( 43200,      0, 'PETT'),
        ttinfo( 46800,   3600, 'PETST'),
        ttinfo( 43200,      0, 'PETT'),
        ttinfo( 46800,   3600, 'PETST'),
        ttinfo( 43200,      0, 'PETT'),
        ttinfo( 46800,   3600, 'PETST'),
        ttinfo( 43200,      0, 'PETT'),
        ttinfo( 46800,   3600, 'PETST'),
        ttinfo( 43200,      0, 'PETT'),
        ttinfo( 46800,   3600, 'PETST'),
        ttinfo( 43200,      0, 'PETT'),
        ttinfo( 43200,      0, 'PETST'),
        ttinfo( 39600,      0, 'PETT'),
        ttinfo( 43200,      0, 'PETT'),
        ttinfo( 46800,   3600, 'PETST'),
        ttinfo( 43200,      0, 'PETT'),
        ttinfo( 46800,   3600, 'PETST'),
        ttinfo( 43200,      0, 'PETT'),
        ttinfo( 46800,   3600, 'PETST'),
        ttinfo( 43200,      0, 'PETT'),
        ttinfo( 46800,   3600, 'PETST'),
        ttinfo( 43200,      0, 'PETT'),
        ttinfo( 46800,   3600, 'PETST'),
        ttinfo( 43200,      0, 'PETT'),
        ttinfo( 46800,   3600, 'PETST'),
        ttinfo( 43200,      0, 'PETT'),
        ttinfo( 46800,   3600, 'PETST'),
        ttinfo( 43200,      0, 'PETT'),
        ttinfo( 46800,   3600, 'PETST'),
        ttinfo( 43200,      0, 'PETT'),
        ttinfo( 46800,   3600, 'PETST'),
        ttinfo( 43200,      0, 'PETT'),
        ttinfo( 46800,   3600, 'PETST'),
        ttinfo( 43200,      0, 'PETT'),
        ttinfo( 46800,   3600, 'PETST'),
        ttinfo( 43200,      0, 'PETT'),
        ttinfo( 46800,   3600, 'PETST'),
        ttinfo( 43200,      0, 'PETT'),
        ttinfo( 46800,   3600, 'PETST'),
        ttinfo( 43200,      0, 'PETT'),
        ttinfo( 46800,   3600, 'PETST'),
        ttinfo( 43200,      0, 'PETT'),
        ttinfo( 46800,   3600, 'PETST'),
        ttinfo( 43200,      0, 'PETT'),
        ttinfo( 46800,   3600, 'PETST'),
        ttinfo( 43200,      0, 'PETT'),
        ttinfo( 46800,   3600, 'PETST'),
        ttinfo( 43200,      0, 'PETT'),
        ttinfo( 46800,   3600, 'PETST'),
        ttinfo( 43200,      0, 'PETT'),
        ttinfo( 46800,   3600, 'PETST'),
        ttinfo( 43200,      0, 'PETT'),
        ttinfo( 46800,   3600, 'PETST'),
        ttinfo( 43200,      0, 'PETT'),
        ttinfo( 46800,   3600, 'PETST'),
        ttinfo( 43200,      0, 'PETT'),
        ttinfo( 46800,   3600, 'PETST'),
        ttinfo( 43200,      0, 'PETT'),
        ttinfo( 46800,   3600, 'PETST'),
        ttinfo( 43200,      0, 'PETT'),
        ttinfo( 46800,   3600, 'PETST'),
        ttinfo( 43200,      0, 'PETT'),
        ttinfo( 46800,   3600, 'PETST'),
        ttinfo( 43200,      0, 'PETT'),
        ttinfo( 46800,   3600, 'PETST'),
        ttinfo( 43200,      0, 'PETT'),
        ttinfo( 46800,   3600, 'PETST'),
        ttinfo( 43200,      0, 'PETT'),
        ttinfo( 46800,   3600, 'PETST'),
        ttinfo( 43200,      0, 'PETT'),
        ttinfo( 46800,   3600, 'PETST'),
        ttinfo( 43200,      0, 'PETT'),
        ttinfo( 46800,   3600, 'PETST'),
        ttinfo( 43200,      0, 'PETT'),
        ttinfo( 46800,   3600, 'PETST'),
        ttinfo( 43200,      0, 'PETT'),
        ttinfo( 46800,   3600, 'PETST'),
        ttinfo( 43200,      0, 'PETT'),
        ttinfo( 46800,   3600, 'PETST'),
        ttinfo( 43200,      0, 'PETT'),
        ttinfo( 46800,   3600, 'PETST'),
        ttinfo( 43200,      0, 'PETT'),
        ttinfo( 46800,   3600, 'PETST'),
        ttinfo( 43200,      0, 'PETT'),
        ttinfo( 46800,   3600, 'PETST'),
        ttinfo( 43200,      0, 'PETT'),
        ttinfo( 46800,   3600, 'PETST'),
        ttinfo( 43200,      0, 'PETT'),
        ttinfo( 46800,   3600, 'PETST'),
        ttinfo( 43200,      0, 'PETT'),
        ttinfo( 46800,   3600, 'PETST'),
        ttinfo( 43200,      0, 'PETT'),
        ttinfo( 46800,   3600, 'PETST'),
        ttinfo( 43200,      0, 'PETT'),
        ttinfo( 46800,   3600, 'PETST'),
        ttinfo( 43200,      0, 'PETT'),
        ttinfo( 46800,   3600, 'PETST'),
        ttinfo( 43200,      0, 'PETT'),
        ttinfo( 46800,   3600, 'PETST'),
        ttinfo( 43200,      0, 'PETT'),
        ttinfo( 46800,   3600, 'PETST'),
        ttinfo( 43200,      0, 'PETT'),
        ttinfo( 46800,   3600, 'PETST'),
        ttinfo( 43200,      0, 'PETT'),
        ttinfo( 46800,   3600, 'PETST'),
        ttinfo( 43200,      0, 'PETT'),
        ]

Kamchatka = Kamchatka() # Singleton

