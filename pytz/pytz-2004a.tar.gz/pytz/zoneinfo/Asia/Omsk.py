'''
tzinfo timezone information for Asia/Omsk.

Generated from the Olson timezone database:
    ftp://elsie.nci.nih.gov/pub/tz*.tar.gz
'''

from pytz.tzinfo import DstTzInfo
from pytz.tzinfo import memorized_datetime as datetime
from pytz.tzinfo import memorized_ttinfo as ttinfo

class Omsk(DstTzInfo):
    '''Asia/Omsk timezone definition. See datetime.tzinfo for details'''

    _zone = 'Asia/Omsk'

    _utc_transition_times = [
        datetime(   1,  1,  1,  0,  0,  0), #  17616     0 LMT
        datetime(1919, 11, 13, 19,  6, 24), #  18000     0 OMST
        datetime(1930,  6, 20, 19,  0,  0), #  21600     0 OMST
        datetime(1981,  3, 31, 18,  0,  0), #  25200  3600 OMSST
        datetime(1981,  9, 30, 17,  0,  0), #  21600     0 OMST
        datetime(1982,  3, 31, 18,  0,  0), #  25200  3600 OMSST
        datetime(1982,  9, 30, 17,  0,  0), #  21600     0 OMST
        datetime(1983,  3, 31, 18,  0,  0), #  25200  3600 OMSST
        datetime(1983,  9, 30, 17,  0,  0), #  21600     0 OMST
        datetime(1984,  3, 31, 18,  0,  0), #  25200  3600 OMSST
        datetime(1984,  9, 29, 20,  0,  0), #  21600     0 OMST
        datetime(1985,  3, 30, 20,  0,  0), #  25200  3600 OMSST
        datetime(1985,  9, 28, 20,  0,  0), #  21600     0 OMST
        datetime(1986,  3, 29, 20,  0,  0), #  25200  3600 OMSST
        datetime(1986,  9, 27, 20,  0,  0), #  21600     0 OMST
        datetime(1987,  3, 28, 20,  0,  0), #  25200  3600 OMSST
        datetime(1987,  9, 26, 20,  0,  0), #  21600     0 OMST
        datetime(1988,  3, 26, 20,  0,  0), #  25200  3600 OMSST
        datetime(1988,  9, 24, 20,  0,  0), #  21600     0 OMST
        datetime(1989,  3, 25, 20,  0,  0), #  25200  3600 OMSST
        datetime(1989,  9, 23, 20,  0,  0), #  21600     0 OMST
        datetime(1990,  3, 24, 20,  0,  0), #  25200  3600 OMSST
        datetime(1990,  9, 29, 20,  0,  0), #  21600     0 OMST
        datetime(1991,  3, 30, 20,  0,  0), #  21600     0 OMSST
        datetime(1991,  9, 28, 21,  0,  0), #  18000     0 OMST
        datetime(1992,  1, 18, 21,  0,  0), #  21600     0 OMST
        datetime(1992,  3, 28, 17,  0,  0), #  25200  3600 OMSST
        datetime(1992,  9, 26, 16,  0,  0), #  21600     0 OMST
        datetime(1993,  3, 27, 20,  0,  0), #  25200  3600 OMSST
        datetime(1993,  9, 25, 20,  0,  0), #  21600     0 OMST
        datetime(1994,  3, 26, 20,  0,  0), #  25200  3600 OMSST
        datetime(1994,  9, 24, 20,  0,  0), #  21600     0 OMST
        datetime(1995,  3, 25, 20,  0,  0), #  25200  3600 OMSST
        datetime(1995,  9, 23, 20,  0,  0), #  21600     0 OMST
        datetime(1996,  3, 30, 20,  0,  0), #  25200  3600 OMSST
        datetime(1996, 10, 26, 20,  0,  0), #  21600     0 OMST
        datetime(1997,  3, 29, 20,  0,  0), #  25200  3600 OMSST
        datetime(1997, 10, 25, 20,  0,  0), #  21600     0 OMST
        datetime(1998,  3, 28, 20,  0,  0), #  25200  3600 OMSST
        datetime(1998, 10, 24, 20,  0,  0), #  21600     0 OMST
        datetime(1999,  3, 27, 20,  0,  0), #  25200  3600 OMSST
        datetime(1999, 10, 30, 20,  0,  0), #  21600     0 OMST
        datetime(2000,  3, 25, 20,  0,  0), #  25200  3600 OMSST
        datetime(2000, 10, 28, 20,  0,  0), #  21600     0 OMST
        datetime(2001,  3, 24, 20,  0,  0), #  25200  3600 OMSST
        datetime(2001, 10, 27, 20,  0,  0), #  21600     0 OMST
        datetime(2002,  3, 30, 20,  0,  0), #  25200  3600 OMSST
        datetime(2002, 10, 26, 20,  0,  0), #  21600     0 OMST
        datetime(2003,  3, 29, 20,  0,  0), #  25200  3600 OMSST
        datetime(2003, 10, 25, 20,  0,  0), #  21600     0 OMST
        datetime(2004,  3, 27, 20,  0,  0), #  25200  3600 OMSST
        datetime(2004, 10, 30, 20,  0,  0), #  21600     0 OMST
        datetime(2005,  3, 26, 20,  0,  0), #  25200  3600 OMSST
        datetime(2005, 10, 29, 20,  0,  0), #  21600     0 OMST
        datetime(2006,  3, 25, 20,  0,  0), #  25200  3600 OMSST
        datetime(2006, 10, 28, 20,  0,  0), #  21600     0 OMST
        datetime(2007,  3, 24, 20,  0,  0), #  25200  3600 OMSST
        datetime(2007, 10, 27, 20,  0,  0), #  21600     0 OMST
        datetime(2008,  3, 29, 20,  0,  0), #  25200  3600 OMSST
        datetime(2008, 10, 25, 20,  0,  0), #  21600     0 OMST
        datetime(2009,  3, 28, 20,  0,  0), #  25200  3600 OMSST
        datetime(2009, 10, 24, 20,  0,  0), #  21600     0 OMST
        datetime(2010,  3, 27, 20,  0,  0), #  25200  3600 OMSST
        datetime(2010, 10, 30, 20,  0,  0), #  21600     0 OMST
        datetime(2011,  3, 26, 20,  0,  0), #  25200  3600 OMSST
        datetime(2011, 10, 29, 20,  0,  0), #  21600     0 OMST
        datetime(2012,  3, 24, 20,  0,  0), #  25200  3600 OMSST
        datetime(2012, 10, 27, 20,  0,  0), #  21600     0 OMST
        datetime(2013,  3, 30, 20,  0,  0), #  25200  3600 OMSST
        datetime(2013, 10, 26, 20,  0,  0), #  21600     0 OMST
        datetime(2014,  3, 29, 20,  0,  0), #  25200  3600 OMSST
        datetime(2014, 10, 25, 20,  0,  0), #  21600     0 OMST
        datetime(2015,  3, 28, 20,  0,  0), #  25200  3600 OMSST
        datetime(2015, 10, 24, 20,  0,  0), #  21600     0 OMST
        datetime(2016,  3, 26, 20,  0,  0), #  25200  3600 OMSST
        datetime(2016, 10, 29, 20,  0,  0), #  21600     0 OMST
        datetime(2017,  3, 25, 20,  0,  0), #  25200  3600 OMSST
        datetime(2017, 10, 28, 20,  0,  0), #  21600     0 OMST
        datetime(2018,  3, 24, 20,  0,  0), #  25200  3600 OMSST
        datetime(2018, 10, 27, 20,  0,  0), #  21600     0 OMST
        datetime(2019,  3, 30, 20,  0,  0), #  25200  3600 OMSST
        datetime(2019, 10, 26, 20,  0,  0), #  21600     0 OMST
        datetime(2020,  3, 28, 20,  0,  0), #  25200  3600 OMSST
        datetime(2020, 10, 24, 20,  0,  0), #  21600     0 OMST
        datetime(2021,  3, 27, 20,  0,  0), #  25200  3600 OMSST
        datetime(2021, 10, 30, 20,  0,  0), #  21600     0 OMST
        datetime(2022,  3, 26, 20,  0,  0), #  25200  3600 OMSST
        datetime(2022, 10, 29, 20,  0,  0), #  21600     0 OMST
        datetime(2023,  3, 25, 20,  0,  0), #  25200  3600 OMSST
        datetime(2023, 10, 28, 20,  0,  0), #  21600     0 OMST
        datetime(2024,  3, 30, 20,  0,  0), #  25200  3600 OMSST
        datetime(2024, 10, 26, 20,  0,  0), #  21600     0 OMST
        datetime(2025,  3, 29, 20,  0,  0), #  25200  3600 OMSST
        datetime(2025, 10, 25, 20,  0,  0), #  21600     0 OMST
        datetime(2026,  3, 28, 20,  0,  0), #  25200  3600 OMSST
        datetime(2026, 10, 24, 20,  0,  0), #  21600     0 OMST
        datetime(2027,  3, 27, 20,  0,  0), #  25200  3600 OMSST
        datetime(2027, 10, 30, 20,  0,  0), #  21600     0 OMST
        datetime(2028,  3, 25, 20,  0,  0), #  25200  3600 OMSST
        datetime(2028, 10, 28, 20,  0,  0), #  21600     0 OMST
        datetime(2029,  3, 24, 20,  0,  0), #  25200  3600 OMSST
        datetime(2029, 10, 27, 20,  0,  0), #  21600     0 OMST
        datetime(2030,  3, 30, 20,  0,  0), #  25200  3600 OMSST
        datetime(2030, 10, 26, 20,  0,  0), #  21600     0 OMST
        datetime(2031,  3, 29, 20,  0,  0), #  25200  3600 OMSST
        datetime(2031, 10, 25, 20,  0,  0), #  21600     0 OMST
        datetime(2032,  3, 27, 20,  0,  0), #  25200  3600 OMSST
        datetime(2032, 10, 30, 20,  0,  0), #  21600     0 OMST
        datetime(2033,  3, 26, 20,  0,  0), #  25200  3600 OMSST
        datetime(2033, 10, 29, 20,  0,  0), #  21600     0 OMST
        datetime(2034,  3, 25, 20,  0,  0), #  25200  3600 OMSST
        datetime(2034, 10, 28, 20,  0,  0), #  21600     0 OMST
        datetime(2035,  3, 24, 20,  0,  0), #  25200  3600 OMSST
        datetime(2035, 10, 27, 20,  0,  0), #  21600     0 OMST
        datetime(2036,  3, 29, 20,  0,  0), #  25200  3600 OMSST
        datetime(2036, 10, 25, 20,  0,  0), #  21600     0 OMST
        datetime(2037,  3, 28, 20,  0,  0), #  25200  3600 OMSST
        datetime(2037, 10, 24, 20,  0,  0), #  21600     0 OMST
        ]

    _transition_info = [
        ttinfo( 17616,      0,  'LMT'),
        ttinfo( 18000,      0, 'OMST'),
        ttinfo( 21600,      0, 'OMST'),
        ttinfo( 25200,   3600, 'OMSST'),
        ttinfo( 21600,      0, 'OMST'),
        ttinfo( 25200,   3600, 'OMSST'),
        ttinfo( 21600,      0, 'OMST'),
        ttinfo( 25200,   3600, 'OMSST'),
        ttinfo( 21600,      0, 'OMST'),
        ttinfo( 25200,   3600, 'OMSST'),
        ttinfo( 21600,      0, 'OMST'),
        ttinfo( 25200,   3600, 'OMSST'),
        ttinfo( 21600,      0, 'OMST'),
        ttinfo( 25200,   3600, 'OMSST'),
        ttinfo( 21600,      0, 'OMST'),
        ttinfo( 25200,   3600, 'OMSST'),
        ttinfo( 21600,      0, 'OMST'),
        ttinfo( 25200,   3600, 'OMSST'),
        ttinfo( 21600,      0, 'OMST'),
        ttinfo( 25200,   3600, 'OMSST'),
        ttinfo( 21600,      0, 'OMST'),
        ttinfo( 25200,   3600, 'OMSST'),
        ttinfo( 21600,      0, 'OMST'),
        ttinfo( 21600,      0, 'OMSST'),
        ttinfo( 18000,      0, 'OMST'),
        ttinfo( 21600,      0, 'OMST'),
        ttinfo( 25200,   3600, 'OMSST'),
        ttinfo( 21600,      0, 'OMST'),
        ttinfo( 25200,   3600, 'OMSST'),
        ttinfo( 21600,      0, 'OMST'),
        ttinfo( 25200,   3600, 'OMSST'),
        ttinfo( 21600,      0, 'OMST'),
        ttinfo( 25200,   3600, 'OMSST'),
        ttinfo( 21600,      0, 'OMST'),
        ttinfo( 25200,   3600, 'OMSST'),
        ttinfo( 21600,      0, 'OMST'),
        ttinfo( 25200,   3600, 'OMSST'),
        ttinfo( 21600,      0, 'OMST'),
        ttinfo( 25200,   3600, 'OMSST'),
        ttinfo( 21600,      0, 'OMST'),
        ttinfo( 25200,   3600, 'OMSST'),
        ttinfo( 21600,      0, 'OMST'),
        ttinfo( 25200,   3600, 'OMSST'),
        ttinfo( 21600,      0, 'OMST'),
        ttinfo( 25200,   3600, 'OMSST'),
        ttinfo( 21600,      0, 'OMST'),
        ttinfo( 25200,   3600, 'OMSST'),
        ttinfo( 21600,      0, 'OMST'),
        ttinfo( 25200,   3600, 'OMSST'),
        ttinfo( 21600,      0, 'OMST'),
        ttinfo( 25200,   3600, 'OMSST'),
        ttinfo( 21600,      0, 'OMST'),
        ttinfo( 25200,   3600, 'OMSST'),
        ttinfo( 21600,      0, 'OMST'),
        ttinfo( 25200,   3600, 'OMSST'),
        ttinfo( 21600,      0, 'OMST'),
        ttinfo( 25200,   3600, 'OMSST'),
        ttinfo( 21600,      0, 'OMST'),
        ttinfo( 25200,   3600, 'OMSST'),
        ttinfo( 21600,      0, 'OMST'),
        ttinfo( 25200,   3600, 'OMSST'),
        ttinfo( 21600,      0, 'OMST'),
        ttinfo( 25200,   3600, 'OMSST'),
        ttinfo( 21600,      0, 'OMST'),
        ttinfo( 25200,   3600, 'OMSST'),
        ttinfo( 21600,      0, 'OMST'),
        ttinfo( 25200,   3600, 'OMSST'),
        ttinfo( 21600,      0, 'OMST'),
        ttinfo( 25200,   3600, 'OMSST'),
        ttinfo( 21600,      0, 'OMST'),
        ttinfo( 25200,   3600, 'OMSST'),
        ttinfo( 21600,      0, 'OMST'),
        ttinfo( 25200,   3600, 'OMSST'),
        ttinfo( 21600,      0, 'OMST'),
        ttinfo( 25200,   3600, 'OMSST'),
        ttinfo( 21600,      0, 'OMST'),
        ttinfo( 25200,   3600, 'OMSST'),
        ttinfo( 21600,      0, 'OMST'),
        ttinfo( 25200,   3600, 'OMSST'),
        ttinfo( 21600,      0, 'OMST'),
        ttinfo( 25200,   3600, 'OMSST'),
        ttinfo( 21600,      0, 'OMST'),
        ttinfo( 25200,   3600, 'OMSST'),
        ttinfo( 21600,      0, 'OMST'),
        ttinfo( 25200,   3600, 'OMSST'),
        ttinfo( 21600,      0, 'OMST'),
        ttinfo( 25200,   3600, 'OMSST'),
        ttinfo( 21600,      0, 'OMST'),
        ttinfo( 25200,   3600, 'OMSST'),
        ttinfo( 21600,      0, 'OMST'),
        ttinfo( 25200,   3600, 'OMSST'),
        ttinfo( 21600,      0, 'OMST'),
        ttinfo( 25200,   3600, 'OMSST'),
        ttinfo( 21600,      0, 'OMST'),
        ttinfo( 25200,   3600, 'OMSST'),
        ttinfo( 21600,      0, 'OMST'),
        ttinfo( 25200,   3600, 'OMSST'),
        ttinfo( 21600,      0, 'OMST'),
        ttinfo( 25200,   3600, 'OMSST'),
        ttinfo( 21600,      0, 'OMST'),
        ttinfo( 25200,   3600, 'OMSST'),
        ttinfo( 21600,      0, 'OMST'),
        ttinfo( 25200,   3600, 'OMSST'),
        ttinfo( 21600,      0, 'OMST'),
        ttinfo( 25200,   3600, 'OMSST'),
        ttinfo( 21600,      0, 'OMST'),
        ttinfo( 25200,   3600, 'OMSST'),
        ttinfo( 21600,      0, 'OMST'),
        ttinfo( 25200,   3600, 'OMSST'),
        ttinfo( 21600,      0, 'OMST'),
        ttinfo( 25200,   3600, 'OMSST'),
        ttinfo( 21600,      0, 'OMST'),
        ttinfo( 25200,   3600, 'OMSST'),
        ttinfo( 21600,      0, 'OMST'),
        ttinfo( 25200,   3600, 'OMSST'),
        ttinfo( 21600,      0, 'OMST'),
        ttinfo( 25200,   3600, 'OMSST'),
        ttinfo( 21600,      0, 'OMST'),
        ]

Omsk = Omsk() # Singleton

