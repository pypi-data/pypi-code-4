'''
tzinfo timezone information for Asia/Anadyr.

Generated from the Olson timezone database:
    ftp://elsie.nci.nih.gov/pub/tz*.tar.gz
'''

from pytz.tzinfo import DstTzInfo
from pytz.tzinfo import memorized_datetime as datetime
from pytz.tzinfo import memorized_ttinfo as ttinfo

class Anadyr(DstTzInfo):
    '''Asia/Anadyr timezone definition. See datetime.tzinfo for details'''

    _zone = 'Asia/Anadyr'

    _utc_transition_times = [
        datetime(   1,  1,  1,  0,  0,  0), #  42596     0 LMT
        datetime(1924,  5,  1, 12, 10,  4), #  43200     0 ANAT
        datetime(1930,  6, 20, 12,  0,  0), #  46800     0 ANAT
        datetime(1981,  3, 31, 11,  0,  0), #  50400  3600 ANAST
        datetime(1981,  9, 30, 10,  0,  0), #  46800     0 ANAT
        datetime(1982,  3, 31, 11,  0,  0), #  46800     0 ANAST
        datetime(1982,  9, 30, 11,  0,  0), #  43200     0 ANAT
        datetime(1983,  3, 31, 12,  0,  0), #  46800  3600 ANAST
        datetime(1983,  9, 30, 11,  0,  0), #  43200     0 ANAT
        datetime(1984,  3, 31, 12,  0,  0), #  46800  3600 ANAST
        datetime(1984,  9, 29, 14,  0,  0), #  43200     0 ANAT
        datetime(1985,  3, 30, 14,  0,  0), #  46800  3600 ANAST
        datetime(1985,  9, 28, 14,  0,  0), #  43200     0 ANAT
        datetime(1986,  3, 29, 14,  0,  0), #  46800  3600 ANAST
        datetime(1986,  9, 27, 14,  0,  0), #  43200     0 ANAT
        datetime(1987,  3, 28, 14,  0,  0), #  46800  3600 ANAST
        datetime(1987,  9, 26, 14,  0,  0), #  43200     0 ANAT
        datetime(1988,  3, 26, 14,  0,  0), #  46800  3600 ANAST
        datetime(1988,  9, 24, 14,  0,  0), #  43200     0 ANAT
        datetime(1989,  3, 25, 14,  0,  0), #  46800  3600 ANAST
        datetime(1989,  9, 23, 14,  0,  0), #  43200     0 ANAT
        datetime(1990,  3, 24, 14,  0,  0), #  46800  3600 ANAST
        datetime(1990,  9, 29, 14,  0,  0), #  43200     0 ANAT
        datetime(1991,  3, 30, 14,  0,  0), #  43200     0 ANAST
        datetime(1991,  9, 28, 15,  0,  0), #  39600     0 ANAT
        datetime(1992,  1, 18, 15,  0,  0), #  43200     0 ANAT
        datetime(1992,  3, 28, 11,  0,  0), #  46800  3600 ANAST
        datetime(1992,  9, 26, 10,  0,  0), #  43200     0 ANAT
        datetime(1993,  3, 27, 14,  0,  0), #  46800  3600 ANAST
        datetime(1993,  9, 25, 14,  0,  0), #  43200     0 ANAT
        datetime(1994,  3, 26, 14,  0,  0), #  46800  3600 ANAST
        datetime(1994,  9, 24, 14,  0,  0), #  43200     0 ANAT
        datetime(1995,  3, 25, 14,  0,  0), #  46800  3600 ANAST
        datetime(1995,  9, 23, 14,  0,  0), #  43200     0 ANAT
        datetime(1996,  3, 30, 14,  0,  0), #  46800  3600 ANAST
        datetime(1996, 10, 26, 14,  0,  0), #  43200     0 ANAT
        datetime(1997,  3, 29, 14,  0,  0), #  46800  3600 ANAST
        datetime(1997, 10, 25, 14,  0,  0), #  43200     0 ANAT
        datetime(1998,  3, 28, 14,  0,  0), #  46800  3600 ANAST
        datetime(1998, 10, 24, 14,  0,  0), #  43200     0 ANAT
        datetime(1999,  3, 27, 14,  0,  0), #  46800  3600 ANAST
        datetime(1999, 10, 30, 14,  0,  0), #  43200     0 ANAT
        datetime(2000,  3, 25, 14,  0,  0), #  46800  3600 ANAST
        datetime(2000, 10, 28, 14,  0,  0), #  43200     0 ANAT
        datetime(2001,  3, 24, 14,  0,  0), #  46800  3600 ANAST
        datetime(2001, 10, 27, 14,  0,  0), #  43200     0 ANAT
        datetime(2002,  3, 30, 14,  0,  0), #  46800  3600 ANAST
        datetime(2002, 10, 26, 14,  0,  0), #  43200     0 ANAT
        datetime(2003,  3, 29, 14,  0,  0), #  46800  3600 ANAST
        datetime(2003, 10, 25, 14,  0,  0), #  43200     0 ANAT
        datetime(2004,  3, 27, 14,  0,  0), #  46800  3600 ANAST
        datetime(2004, 10, 30, 14,  0,  0), #  43200     0 ANAT
        datetime(2005,  3, 26, 14,  0,  0), #  46800  3600 ANAST
        datetime(2005, 10, 29, 14,  0,  0), #  43200     0 ANAT
        datetime(2006,  3, 25, 14,  0,  0), #  46800  3600 ANAST
        datetime(2006, 10, 28, 14,  0,  0), #  43200     0 ANAT
        datetime(2007,  3, 24, 14,  0,  0), #  46800  3600 ANAST
        datetime(2007, 10, 27, 14,  0,  0), #  43200     0 ANAT
        datetime(2008,  3, 29, 14,  0,  0), #  46800  3600 ANAST
        datetime(2008, 10, 25, 14,  0,  0), #  43200     0 ANAT
        datetime(2009,  3, 28, 14,  0,  0), #  46800  3600 ANAST
        datetime(2009, 10, 24, 14,  0,  0), #  43200     0 ANAT
        datetime(2010,  3, 27, 14,  0,  0), #  46800  3600 ANAST
        datetime(2010, 10, 30, 14,  0,  0), #  43200     0 ANAT
        datetime(2011,  3, 26, 14,  0,  0), #  46800  3600 ANAST
        datetime(2011, 10, 29, 14,  0,  0), #  43200     0 ANAT
        datetime(2012,  3, 24, 14,  0,  0), #  46800  3600 ANAST
        datetime(2012, 10, 27, 14,  0,  0), #  43200     0 ANAT
        datetime(2013,  3, 30, 14,  0,  0), #  46800  3600 ANAST
        datetime(2013, 10, 26, 14,  0,  0), #  43200     0 ANAT
        datetime(2014,  3, 29, 14,  0,  0), #  46800  3600 ANAST
        datetime(2014, 10, 25, 14,  0,  0), #  43200     0 ANAT
        datetime(2015,  3, 28, 14,  0,  0), #  46800  3600 ANAST
        datetime(2015, 10, 24, 14,  0,  0), #  43200     0 ANAT
        datetime(2016,  3, 26, 14,  0,  0), #  46800  3600 ANAST
        datetime(2016, 10, 29, 14,  0,  0), #  43200     0 ANAT
        datetime(2017,  3, 25, 14,  0,  0), #  46800  3600 ANAST
        datetime(2017, 10, 28, 14,  0,  0), #  43200     0 ANAT
        datetime(2018,  3, 24, 14,  0,  0), #  46800  3600 ANAST
        datetime(2018, 10, 27, 14,  0,  0), #  43200     0 ANAT
        datetime(2019,  3, 30, 14,  0,  0), #  46800  3600 ANAST
        datetime(2019, 10, 26, 14,  0,  0), #  43200     0 ANAT
        datetime(2020,  3, 28, 14,  0,  0), #  46800  3600 ANAST
        datetime(2020, 10, 24, 14,  0,  0), #  43200     0 ANAT
        datetime(2021,  3, 27, 14,  0,  0), #  46800  3600 ANAST
        datetime(2021, 10, 30, 14,  0,  0), #  43200     0 ANAT
        datetime(2022,  3, 26, 14,  0,  0), #  46800  3600 ANAST
        datetime(2022, 10, 29, 14,  0,  0), #  43200     0 ANAT
        datetime(2023,  3, 25, 14,  0,  0), #  46800  3600 ANAST
        datetime(2023, 10, 28, 14,  0,  0), #  43200     0 ANAT
        datetime(2024,  3, 30, 14,  0,  0), #  46800  3600 ANAST
        datetime(2024, 10, 26, 14,  0,  0), #  43200     0 ANAT
        datetime(2025,  3, 29, 14,  0,  0), #  46800  3600 ANAST
        datetime(2025, 10, 25, 14,  0,  0), #  43200     0 ANAT
        datetime(2026,  3, 28, 14,  0,  0), #  46800  3600 ANAST
        datetime(2026, 10, 24, 14,  0,  0), #  43200     0 ANAT
        datetime(2027,  3, 27, 14,  0,  0), #  46800  3600 ANAST
        datetime(2027, 10, 30, 14,  0,  0), #  43200     0 ANAT
        datetime(2028,  3, 25, 14,  0,  0), #  46800  3600 ANAST
        datetime(2028, 10, 28, 14,  0,  0), #  43200     0 ANAT
        datetime(2029,  3, 24, 14,  0,  0), #  46800  3600 ANAST
        datetime(2029, 10, 27, 14,  0,  0), #  43200     0 ANAT
        datetime(2030,  3, 30, 14,  0,  0), #  46800  3600 ANAST
        datetime(2030, 10, 26, 14,  0,  0), #  43200     0 ANAT
        datetime(2031,  3, 29, 14,  0,  0), #  46800  3600 ANAST
        datetime(2031, 10, 25, 14,  0,  0), #  43200     0 ANAT
        datetime(2032,  3, 27, 14,  0,  0), #  46800  3600 ANAST
        datetime(2032, 10, 30, 14,  0,  0), #  43200     0 ANAT
        datetime(2033,  3, 26, 14,  0,  0), #  46800  3600 ANAST
        datetime(2033, 10, 29, 14,  0,  0), #  43200     0 ANAT
        datetime(2034,  3, 25, 14,  0,  0), #  46800  3600 ANAST
        datetime(2034, 10, 28, 14,  0,  0), #  43200     0 ANAT
        datetime(2035,  3, 24, 14,  0,  0), #  46800  3600 ANAST
        datetime(2035, 10, 27, 14,  0,  0), #  43200     0 ANAT
        datetime(2036,  3, 29, 14,  0,  0), #  46800  3600 ANAST
        datetime(2036, 10, 25, 14,  0,  0), #  43200     0 ANAT
        datetime(2037,  3, 28, 14,  0,  0), #  46800  3600 ANAST
        datetime(2037, 10, 24, 14,  0,  0), #  43200     0 ANAT
        ]

    _transition_info = [
        ttinfo( 42596,      0,  'LMT'),
        ttinfo( 43200,      0, 'ANAT'),
        ttinfo( 46800,      0, 'ANAT'),
        ttinfo( 50400,   3600, 'ANAST'),
        ttinfo( 46800,      0, 'ANAT'),
        ttinfo( 46800,      0, 'ANAST'),
        ttinfo( 43200,      0, 'ANAT'),
        ttinfo( 46800,   3600, 'ANAST'),
        ttinfo( 43200,      0, 'ANAT'),
        ttinfo( 46800,   3600, 'ANAST'),
        ttinfo( 43200,      0, 'ANAT'),
        ttinfo( 46800,   3600, 'ANAST'),
        ttinfo( 43200,      0, 'ANAT'),
        ttinfo( 46800,   3600, 'ANAST'),
        ttinfo( 43200,      0, 'ANAT'),
        ttinfo( 46800,   3600, 'ANAST'),
        ttinfo( 43200,      0, 'ANAT'),
        ttinfo( 46800,   3600, 'ANAST'),
        ttinfo( 43200,      0, 'ANAT'),
        ttinfo( 46800,   3600, 'ANAST'),
        ttinfo( 43200,      0, 'ANAT'),
        ttinfo( 46800,   3600, 'ANAST'),
        ttinfo( 43200,      0, 'ANAT'),
        ttinfo( 43200,      0, 'ANAST'),
        ttinfo( 39600,      0, 'ANAT'),
        ttinfo( 43200,      0, 'ANAT'),
        ttinfo( 46800,   3600, 'ANAST'),
        ttinfo( 43200,      0, 'ANAT'),
        ttinfo( 46800,   3600, 'ANAST'),
        ttinfo( 43200,      0, 'ANAT'),
        ttinfo( 46800,   3600, 'ANAST'),
        ttinfo( 43200,      0, 'ANAT'),
        ttinfo( 46800,   3600, 'ANAST'),
        ttinfo( 43200,      0, 'ANAT'),
        ttinfo( 46800,   3600, 'ANAST'),
        ttinfo( 43200,      0, 'ANAT'),
        ttinfo( 46800,   3600, 'ANAST'),
        ttinfo( 43200,      0, 'ANAT'),
        ttinfo( 46800,   3600, 'ANAST'),
        ttinfo( 43200,      0, 'ANAT'),
        ttinfo( 46800,   3600, 'ANAST'),
        ttinfo( 43200,      0, 'ANAT'),
        ttinfo( 46800,   3600, 'ANAST'),
        ttinfo( 43200,      0, 'ANAT'),
        ttinfo( 46800,   3600, 'ANAST'),
        ttinfo( 43200,      0, 'ANAT'),
        ttinfo( 46800,   3600, 'ANAST'),
        ttinfo( 43200,      0, 'ANAT'),
        ttinfo( 46800,   3600, 'ANAST'),
        ttinfo( 43200,      0, 'ANAT'),
        ttinfo( 46800,   3600, 'ANAST'),
        ttinfo( 43200,      0, 'ANAT'),
        ttinfo( 46800,   3600, 'ANAST'),
        ttinfo( 43200,      0, 'ANAT'),
        ttinfo( 46800,   3600, 'ANAST'),
        ttinfo( 43200,      0, 'ANAT'),
        ttinfo( 46800,   3600, 'ANAST'),
        ttinfo( 43200,      0, 'ANAT'),
        ttinfo( 46800,   3600, 'ANAST'),
        ttinfo( 43200,      0, 'ANAT'),
        ttinfo( 46800,   3600, 'ANAST'),
        ttinfo( 43200,      0, 'ANAT'),
        ttinfo( 46800,   3600, 'ANAST'),
        ttinfo( 43200,      0, 'ANAT'),
        ttinfo( 46800,   3600, 'ANAST'),
        ttinfo( 43200,      0, 'ANAT'),
        ttinfo( 46800,   3600, 'ANAST'),
        ttinfo( 43200,      0, 'ANAT'),
        ttinfo( 46800,   3600, 'ANAST'),
        ttinfo( 43200,      0, 'ANAT'),
        ttinfo( 46800,   3600, 'ANAST'),
        ttinfo( 43200,      0, 'ANAT'),
        ttinfo( 46800,   3600, 'ANAST'),
        ttinfo( 43200,      0, 'ANAT'),
        ttinfo( 46800,   3600, 'ANAST'),
        ttinfo( 43200,      0, 'ANAT'),
        ttinfo( 46800,   3600, 'ANAST'),
        ttinfo( 43200,      0, 'ANAT'),
        ttinfo( 46800,   3600, 'ANAST'),
        ttinfo( 43200,      0, 'ANAT'),
        ttinfo( 46800,   3600, 'ANAST'),
        ttinfo( 43200,      0, 'ANAT'),
        ttinfo( 46800,   3600, 'ANAST'),
        ttinfo( 43200,      0, 'ANAT'),
        ttinfo( 46800,   3600, 'ANAST'),
        ttinfo( 43200,      0, 'ANAT'),
        ttinfo( 46800,   3600, 'ANAST'),
        ttinfo( 43200,      0, 'ANAT'),
        ttinfo( 46800,   3600, 'ANAST'),
        ttinfo( 43200,      0, 'ANAT'),
        ttinfo( 46800,   3600, 'ANAST'),
        ttinfo( 43200,      0, 'ANAT'),
        ttinfo( 46800,   3600, 'ANAST'),
        ttinfo( 43200,      0, 'ANAT'),
        ttinfo( 46800,   3600, 'ANAST'),
        ttinfo( 43200,      0, 'ANAT'),
        ttinfo( 46800,   3600, 'ANAST'),
        ttinfo( 43200,      0, 'ANAT'),
        ttinfo( 46800,   3600, 'ANAST'),
        ttinfo( 43200,      0, 'ANAT'),
        ttinfo( 46800,   3600, 'ANAST'),
        ttinfo( 43200,      0, 'ANAT'),
        ttinfo( 46800,   3600, 'ANAST'),
        ttinfo( 43200,      0, 'ANAT'),
        ttinfo( 46800,   3600, 'ANAST'),
        ttinfo( 43200,      0, 'ANAT'),
        ttinfo( 46800,   3600, 'ANAST'),
        ttinfo( 43200,      0, 'ANAT'),
        ttinfo( 46800,   3600, 'ANAST'),
        ttinfo( 43200,      0, 'ANAT'),
        ttinfo( 46800,   3600, 'ANAST'),
        ttinfo( 43200,      0, 'ANAT'),
        ttinfo( 46800,   3600, 'ANAST'),
        ttinfo( 43200,      0, 'ANAT'),
        ttinfo( 46800,   3600, 'ANAST'),
        ttinfo( 43200,      0, 'ANAT'),
        ttinfo( 46800,   3600, 'ANAST'),
        ttinfo( 43200,      0, 'ANAT'),
        ]

Anadyr = Anadyr() # Singleton

