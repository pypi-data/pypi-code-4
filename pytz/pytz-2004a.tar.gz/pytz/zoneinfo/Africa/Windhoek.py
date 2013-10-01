'''
tzinfo timezone information for Africa/Windhoek.

Generated from the Olson timezone database:
    ftp://elsie.nci.nih.gov/pub/tz*.tar.gz
'''

from pytz.tzinfo import DstTzInfo
from pytz.tzinfo import memorized_datetime as datetime
from pytz.tzinfo import memorized_ttinfo as ttinfo

class Windhoek(DstTzInfo):
    '''Africa/Windhoek timezone definition. See datetime.tzinfo for details'''

    _zone = 'Africa/Windhoek'

    _utc_transition_times = [
        datetime(   1,  1,  1,  0,  0,  0), #   5400     0 SWAT
        datetime(1903,  2, 28, 22, 30,  0), #   7200     0 SAST
        datetime(1942,  9, 20,  0,  0,  0), #  10800  3600 SAST
        datetime(1943,  3, 20, 23,  0,  0), #   7200     0 SAST
        datetime(1990,  3, 20, 22,  0,  0), #   7200     0 CAT
        datetime(1994,  4,  2, 22,  0,  0), #   3600     0 WAT
        datetime(1994,  9,  4,  1,  0,  0), #   7200  3600 WAST
        datetime(1995,  4,  2,  0,  0,  0), #   3600     0 WAT
        datetime(1995,  9,  3,  1,  0,  0), #   7200  3600 WAST
        datetime(1996,  4,  7,  0,  0,  0), #   3600     0 WAT
        datetime(1996,  9,  1,  1,  0,  0), #   7200  3600 WAST
        datetime(1997,  4,  6,  0,  0,  0), #   3600     0 WAT
        datetime(1997,  9,  7,  1,  0,  0), #   7200  3600 WAST
        datetime(1998,  4,  5,  0,  0,  0), #   3600     0 WAT
        datetime(1998,  9,  6,  1,  0,  0), #   7200  3600 WAST
        datetime(1999,  4,  4,  0,  0,  0), #   3600     0 WAT
        datetime(1999,  9,  5,  1,  0,  0), #   7200  3600 WAST
        datetime(2000,  4,  2,  0,  0,  0), #   3600     0 WAT
        datetime(2000,  9,  3,  1,  0,  0), #   7200  3600 WAST
        datetime(2001,  4,  1,  0,  0,  0), #   3600     0 WAT
        datetime(2001,  9,  2,  1,  0,  0), #   7200  3600 WAST
        datetime(2002,  4,  7,  0,  0,  0), #   3600     0 WAT
        datetime(2002,  9,  1,  1,  0,  0), #   7200  3600 WAST
        datetime(2003,  4,  6,  0,  0,  0), #   3600     0 WAT
        datetime(2003,  9,  7,  1,  0,  0), #   7200  3600 WAST
        datetime(2004,  4,  4,  0,  0,  0), #   3600     0 WAT
        datetime(2004,  9,  5,  1,  0,  0), #   7200  3600 WAST
        datetime(2005,  4,  3,  0,  0,  0), #   3600     0 WAT
        datetime(2005,  9,  4,  1,  0,  0), #   7200  3600 WAST
        datetime(2006,  4,  2,  0,  0,  0), #   3600     0 WAT
        datetime(2006,  9,  3,  1,  0,  0), #   7200  3600 WAST
        datetime(2007,  4,  1,  0,  0,  0), #   3600     0 WAT
        datetime(2007,  9,  2,  1,  0,  0), #   7200  3600 WAST
        datetime(2008,  4,  6,  0,  0,  0), #   3600     0 WAT
        datetime(2008,  9,  7,  1,  0,  0), #   7200  3600 WAST
        datetime(2009,  4,  5,  0,  0,  0), #   3600     0 WAT
        datetime(2009,  9,  6,  1,  0,  0), #   7200  3600 WAST
        datetime(2010,  4,  4,  0,  0,  0), #   3600     0 WAT
        datetime(2010,  9,  5,  1,  0,  0), #   7200  3600 WAST
        datetime(2011,  4,  3,  0,  0,  0), #   3600     0 WAT
        datetime(2011,  9,  4,  1,  0,  0), #   7200  3600 WAST
        datetime(2012,  4,  1,  0,  0,  0), #   3600     0 WAT
        datetime(2012,  9,  2,  1,  0,  0), #   7200  3600 WAST
        datetime(2013,  4,  7,  0,  0,  0), #   3600     0 WAT
        datetime(2013,  9,  1,  1,  0,  0), #   7200  3600 WAST
        datetime(2014,  4,  6,  0,  0,  0), #   3600     0 WAT
        datetime(2014,  9,  7,  1,  0,  0), #   7200  3600 WAST
        datetime(2015,  4,  5,  0,  0,  0), #   3600     0 WAT
        datetime(2015,  9,  6,  1,  0,  0), #   7200  3600 WAST
        datetime(2016,  4,  3,  0,  0,  0), #   3600     0 WAT
        datetime(2016,  9,  4,  1,  0,  0), #   7200  3600 WAST
        datetime(2017,  4,  2,  0,  0,  0), #   3600     0 WAT
        datetime(2017,  9,  3,  1,  0,  0), #   7200  3600 WAST
        datetime(2018,  4,  1,  0,  0,  0), #   3600     0 WAT
        datetime(2018,  9,  2,  1,  0,  0), #   7200  3600 WAST
        datetime(2019,  4,  7,  0,  0,  0), #   3600     0 WAT
        datetime(2019,  9,  1,  1,  0,  0), #   7200  3600 WAST
        datetime(2020,  4,  5,  0,  0,  0), #   3600     0 WAT
        datetime(2020,  9,  6,  1,  0,  0), #   7200  3600 WAST
        datetime(2021,  4,  4,  0,  0,  0), #   3600     0 WAT
        datetime(2021,  9,  5,  1,  0,  0), #   7200  3600 WAST
        datetime(2022,  4,  3,  0,  0,  0), #   3600     0 WAT
        datetime(2022,  9,  4,  1,  0,  0), #   7200  3600 WAST
        datetime(2023,  4,  2,  0,  0,  0), #   3600     0 WAT
        datetime(2023,  9,  3,  1,  0,  0), #   7200  3600 WAST
        datetime(2024,  4,  7,  0,  0,  0), #   3600     0 WAT
        datetime(2024,  9,  1,  1,  0,  0), #   7200  3600 WAST
        datetime(2025,  4,  6,  0,  0,  0), #   3600     0 WAT
        datetime(2025,  9,  7,  1,  0,  0), #   7200  3600 WAST
        datetime(2026,  4,  5,  0,  0,  0), #   3600     0 WAT
        datetime(2026,  9,  6,  1,  0,  0), #   7200  3600 WAST
        datetime(2027,  4,  4,  0,  0,  0), #   3600     0 WAT
        datetime(2027,  9,  5,  1,  0,  0), #   7200  3600 WAST
        datetime(2028,  4,  2,  0,  0,  0), #   3600     0 WAT
        datetime(2028,  9,  3,  1,  0,  0), #   7200  3600 WAST
        datetime(2029,  4,  1,  0,  0,  0), #   3600     0 WAT
        datetime(2029,  9,  2,  1,  0,  0), #   7200  3600 WAST
        datetime(2030,  4,  7,  0,  0,  0), #   3600     0 WAT
        datetime(2030,  9,  1,  1,  0,  0), #   7200  3600 WAST
        datetime(2031,  4,  6,  0,  0,  0), #   3600     0 WAT
        datetime(2031,  9,  7,  1,  0,  0), #   7200  3600 WAST
        datetime(2032,  4,  4,  0,  0,  0), #   3600     0 WAT
        datetime(2032,  9,  5,  1,  0,  0), #   7200  3600 WAST
        datetime(2033,  4,  3,  0,  0,  0), #   3600     0 WAT
        datetime(2033,  9,  4,  1,  0,  0), #   7200  3600 WAST
        datetime(2034,  4,  2,  0,  0,  0), #   3600     0 WAT
        datetime(2034,  9,  3,  1,  0,  0), #   7200  3600 WAST
        datetime(2035,  4,  1,  0,  0,  0), #   3600     0 WAT
        datetime(2035,  9,  2,  1,  0,  0), #   7200  3600 WAST
        datetime(2036,  4,  6,  0,  0,  0), #   3600     0 WAT
        datetime(2036,  9,  7,  1,  0,  0), #   7200  3600 WAST
        datetime(2037,  4,  5,  0,  0,  0), #   3600     0 WAT
        datetime(2037,  9,  6,  1,  0,  0), #   7200  3600 WAST
        ]

    _transition_info = [
        ttinfo(  5400,      0, 'SWAT'),
        ttinfo(  7200,      0, 'SAST'),
        ttinfo( 10800,   3600, 'SAST'),
        ttinfo(  7200,      0, 'SAST'),
        ttinfo(  7200,      0,  'CAT'),
        ttinfo(  3600,      0,  'WAT'),
        ttinfo(  7200,   3600, 'WAST'),
        ttinfo(  3600,      0,  'WAT'),
        ttinfo(  7200,   3600, 'WAST'),
        ttinfo(  3600,      0,  'WAT'),
        ttinfo(  7200,   3600, 'WAST'),
        ttinfo(  3600,      0,  'WAT'),
        ttinfo(  7200,   3600, 'WAST'),
        ttinfo(  3600,      0,  'WAT'),
        ttinfo(  7200,   3600, 'WAST'),
        ttinfo(  3600,      0,  'WAT'),
        ttinfo(  7200,   3600, 'WAST'),
        ttinfo(  3600,      0,  'WAT'),
        ttinfo(  7200,   3600, 'WAST'),
        ttinfo(  3600,      0,  'WAT'),
        ttinfo(  7200,   3600, 'WAST'),
        ttinfo(  3600,      0,  'WAT'),
        ttinfo(  7200,   3600, 'WAST'),
        ttinfo(  3600,      0,  'WAT'),
        ttinfo(  7200,   3600, 'WAST'),
        ttinfo(  3600,      0,  'WAT'),
        ttinfo(  7200,   3600, 'WAST'),
        ttinfo(  3600,      0,  'WAT'),
        ttinfo(  7200,   3600, 'WAST'),
        ttinfo(  3600,      0,  'WAT'),
        ttinfo(  7200,   3600, 'WAST'),
        ttinfo(  3600,      0,  'WAT'),
        ttinfo(  7200,   3600, 'WAST'),
        ttinfo(  3600,      0,  'WAT'),
        ttinfo(  7200,   3600, 'WAST'),
        ttinfo(  3600,      0,  'WAT'),
        ttinfo(  7200,   3600, 'WAST'),
        ttinfo(  3600,      0,  'WAT'),
        ttinfo(  7200,   3600, 'WAST'),
        ttinfo(  3600,      0,  'WAT'),
        ttinfo(  7200,   3600, 'WAST'),
        ttinfo(  3600,      0,  'WAT'),
        ttinfo(  7200,   3600, 'WAST'),
        ttinfo(  3600,      0,  'WAT'),
        ttinfo(  7200,   3600, 'WAST'),
        ttinfo(  3600,      0,  'WAT'),
        ttinfo(  7200,   3600, 'WAST'),
        ttinfo(  3600,      0,  'WAT'),
        ttinfo(  7200,   3600, 'WAST'),
        ttinfo(  3600,      0,  'WAT'),
        ttinfo(  7200,   3600, 'WAST'),
        ttinfo(  3600,      0,  'WAT'),
        ttinfo(  7200,   3600, 'WAST'),
        ttinfo(  3600,      0,  'WAT'),
        ttinfo(  7200,   3600, 'WAST'),
        ttinfo(  3600,      0,  'WAT'),
        ttinfo(  7200,   3600, 'WAST'),
        ttinfo(  3600,      0,  'WAT'),
        ttinfo(  7200,   3600, 'WAST'),
        ttinfo(  3600,      0,  'WAT'),
        ttinfo(  7200,   3600, 'WAST'),
        ttinfo(  3600,      0,  'WAT'),
        ttinfo(  7200,   3600, 'WAST'),
        ttinfo(  3600,      0,  'WAT'),
        ttinfo(  7200,   3600, 'WAST'),
        ttinfo(  3600,      0,  'WAT'),
        ttinfo(  7200,   3600, 'WAST'),
        ttinfo(  3600,      0,  'WAT'),
        ttinfo(  7200,   3600, 'WAST'),
        ttinfo(  3600,      0,  'WAT'),
        ttinfo(  7200,   3600, 'WAST'),
        ttinfo(  3600,      0,  'WAT'),
        ttinfo(  7200,   3600, 'WAST'),
        ttinfo(  3600,      0,  'WAT'),
        ttinfo(  7200,   3600, 'WAST'),
        ttinfo(  3600,      0,  'WAT'),
        ttinfo(  7200,   3600, 'WAST'),
        ttinfo(  3600,      0,  'WAT'),
        ttinfo(  7200,   3600, 'WAST'),
        ttinfo(  3600,      0,  'WAT'),
        ttinfo(  7200,   3600, 'WAST'),
        ttinfo(  3600,      0,  'WAT'),
        ttinfo(  7200,   3600, 'WAST'),
        ttinfo(  3600,      0,  'WAT'),
        ttinfo(  7200,   3600, 'WAST'),
        ttinfo(  3600,      0,  'WAT'),
        ttinfo(  7200,   3600, 'WAST'),
        ttinfo(  3600,      0,  'WAT'),
        ttinfo(  7200,   3600, 'WAST'),
        ttinfo(  3600,      0,  'WAT'),
        ttinfo(  7200,   3600, 'WAST'),
        ttinfo(  3600,      0,  'WAT'),
        ttinfo(  7200,   3600, 'WAST'),
        ]

Windhoek = Windhoek() # Singleton

