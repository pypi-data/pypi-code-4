'''
tzinfo timezone information for Iran.

Generated from the Olson timezone database:
    ftp://elsie.nci.nih.gov/pub/tz*.tar.gz
'''

from pytz.tzinfo import DstTzInfo
from pytz.tzinfo import memorized_datetime as datetime
from pytz.tzinfo import memorized_ttinfo as ttinfo

class Iran(DstTzInfo):
    '''Iran timezone definition. See datetime.tzinfo for details'''

    _zone = 'Iran'

    _utc_transition_times = [
        datetime(   1,  1,  1,  0,  0,  0), #  12344     0 LMT
        datetime(1915, 12, 31, 20, 34, 16), #  12344     0 TMT
        datetime(1945, 12, 31, 20, 34, 16), #  12600     0 IRST
        datetime(1977, 10, 31, 20, 30,  0), #  14400     0 IRST
        datetime(1978,  3, 20, 20,  0,  0), #  18000  3600 IRDT
        datetime(1978, 10, 20, 19,  0,  0), #  14400     0 IRST
        datetime(1978, 12, 31, 20,  0,  0), #  12600     0 IRST
        datetime(1979,  3, 20, 20, 30,  0), #  16200  3600 IRDT
        datetime(1979,  9, 18, 19, 30,  0), #  12600     0 IRST
        datetime(1980,  3, 20, 20, 30,  0), #  16200  3600 IRDT
        datetime(1980,  9, 22, 19, 30,  0), #  12600     0 IRST
        datetime(1991,  5,  2, 20, 30,  0), #  16200  3600 IRDT
        datetime(1991,  9, 21, 19, 30,  0), #  12600     0 IRST
        datetime(1992,  3, 21, 20, 30,  0), #  16200  3600 IRDT
        datetime(1992,  9, 21, 19, 30,  0), #  12600     0 IRST
        datetime(1993,  3, 21, 20, 30,  0), #  16200  3600 IRDT
        datetime(1993,  9, 21, 19, 30,  0), #  12600     0 IRST
        datetime(1994,  3, 21, 20, 30,  0), #  16200  3600 IRDT
        datetime(1994,  9, 21, 19, 30,  0), #  12600     0 IRST
        datetime(1995,  3, 21, 20, 30,  0), #  16200  3600 IRDT
        datetime(1995,  9, 21, 19, 30,  0), #  12600     0 IRST
        datetime(1996,  3, 20, 20, 30,  0), #  16200  3600 IRDT
        datetime(1996,  9, 20, 19, 30,  0), #  12600     0 IRST
        datetime(1997,  3, 21, 20, 30,  0), #  16200  3600 IRDT
        datetime(1997,  9, 21, 19, 30,  0), #  12600     0 IRST
        datetime(1998,  3, 21, 20, 30,  0), #  16200  3600 IRDT
        datetime(1998,  9, 21, 19, 30,  0), #  12600     0 IRST
        datetime(1999,  3, 21, 20, 30,  0), #  16200  3600 IRDT
        datetime(1999,  9, 21, 19, 30,  0), #  12600     0 IRST
        datetime(2000,  3, 20, 20, 30,  0), #  16200  3600 IRDT
        datetime(2000,  9, 20, 19, 30,  0), #  12600     0 IRST
        datetime(2001,  3, 21, 20, 30,  0), #  16200  3600 IRDT
        datetime(2001,  9, 21, 19, 30,  0), #  12600     0 IRST
        datetime(2002,  3, 21, 20, 30,  0), #  16200  3600 IRDT
        datetime(2002,  9, 21, 19, 30,  0), #  12600     0 IRST
        datetime(2003,  3, 21, 20, 30,  0), #  16200  3600 IRDT
        datetime(2003,  9, 21, 19, 30,  0), #  12600     0 IRST
        datetime(2004,  3, 20, 20, 30,  0), #  16200  3600 IRDT
        datetime(2004,  9, 20, 19, 30,  0), #  12600     0 IRST
        datetime(2005,  3, 21, 20, 30,  0), #  16200  3600 IRDT
        datetime(2005,  9, 21, 19, 30,  0), #  12600     0 IRST
        datetime(2006,  3, 21, 20, 30,  0), #  16200  3600 IRDT
        datetime(2006,  9, 21, 19, 30,  0), #  12600     0 IRST
        datetime(2007,  3, 21, 20, 30,  0), #  16200  3600 IRDT
        datetime(2007,  9, 21, 19, 30,  0), #  12600     0 IRST
        datetime(2008,  3, 20, 20, 30,  0), #  16200  3600 IRDT
        datetime(2008,  9, 20, 19, 30,  0), #  12600     0 IRST
        datetime(2009,  3, 21, 20, 30,  0), #  16200  3600 IRDT
        datetime(2009,  9, 21, 19, 30,  0), #  12600     0 IRST
        datetime(2010,  3, 21, 20, 30,  0), #  16200  3600 IRDT
        datetime(2010,  9, 21, 19, 30,  0), #  12600     0 IRST
        datetime(2011,  3, 21, 20, 30,  0), #  16200  3600 IRDT
        datetime(2011,  9, 21, 19, 30,  0), #  12600     0 IRST
        datetime(2012,  3, 20, 20, 30,  0), #  16200  3600 IRDT
        datetime(2012,  9, 20, 19, 30,  0), #  12600     0 IRST
        datetime(2013,  3, 21, 20, 30,  0), #  16200  3600 IRDT
        datetime(2013,  9, 21, 19, 30,  0), #  12600     0 IRST
        datetime(2014,  3, 21, 20, 30,  0), #  16200  3600 IRDT
        datetime(2014,  9, 21, 19, 30,  0), #  12600     0 IRST
        datetime(2015,  3, 21, 20, 30,  0), #  16200  3600 IRDT
        datetime(2015,  9, 21, 19, 30,  0), #  12600     0 IRST
        datetime(2016,  3, 20, 20, 30,  0), #  16200  3600 IRDT
        datetime(2016,  9, 20, 19, 30,  0), #  12600     0 IRST
        datetime(2017,  3, 21, 20, 30,  0), #  16200  3600 IRDT
        datetime(2017,  9, 21, 19, 30,  0), #  12600     0 IRST
        datetime(2018,  3, 21, 20, 30,  0), #  16200  3600 IRDT
        datetime(2018,  9, 21, 19, 30,  0), #  12600     0 IRST
        datetime(2019,  3, 21, 20, 30,  0), #  16200  3600 IRDT
        datetime(2019,  9, 21, 19, 30,  0), #  12600     0 IRST
        datetime(2020,  3, 20, 20, 30,  0), #  16200  3600 IRDT
        datetime(2020,  9, 20, 19, 30,  0), #  12600     0 IRST
        datetime(2021,  3, 21, 20, 30,  0), #  16200  3600 IRDT
        datetime(2021,  9, 21, 19, 30,  0), #  12600     0 IRST
        datetime(2022,  3, 21, 20, 30,  0), #  16200  3600 IRDT
        datetime(2022,  9, 21, 19, 30,  0), #  12600     0 IRST
        datetime(2023,  3, 21, 20, 30,  0), #  16200  3600 IRDT
        datetime(2023,  9, 21, 19, 30,  0), #  12600     0 IRST
        datetime(2024,  3, 20, 20, 30,  0), #  16200  3600 IRDT
        datetime(2024,  9, 20, 19, 30,  0), #  12600     0 IRST
        datetime(2025,  3, 20, 20, 30,  0), #  16200  3600 IRDT
        datetime(2025,  9, 20, 19, 30,  0), #  12600     0 IRST
        datetime(2026,  3, 21, 20, 30,  0), #  16200  3600 IRDT
        datetime(2026,  9, 21, 19, 30,  0), #  12600     0 IRST
        datetime(2027,  3, 21, 20, 30,  0), #  16200  3600 IRDT
        datetime(2027,  9, 21, 19, 30,  0), #  12600     0 IRST
        datetime(2028,  3, 20, 20, 30,  0), #  16200  3600 IRDT
        datetime(2028,  9, 20, 19, 30,  0), #  12600     0 IRST
        datetime(2029,  3, 20, 20, 30,  0), #  16200  3600 IRDT
        datetime(2029,  9, 20, 19, 30,  0), #  12600     0 IRST
        datetime(2030,  3, 21, 20, 30,  0), #  16200  3600 IRDT
        datetime(2030,  9, 21, 19, 30,  0), #  12600     0 IRST
        datetime(2031,  3, 21, 20, 30,  0), #  16200  3600 IRDT
        datetime(2031,  9, 21, 19, 30,  0), #  12600     0 IRST
        datetime(2032,  3, 20, 20, 30,  0), #  16200  3600 IRDT
        datetime(2032,  9, 20, 19, 30,  0), #  12600     0 IRST
        datetime(2033,  3, 20, 20, 30,  0), #  16200  3600 IRDT
        datetime(2033,  9, 20, 19, 30,  0), #  12600     0 IRST
        datetime(2034,  3, 21, 20, 30,  0), #  16200  3600 IRDT
        datetime(2034,  9, 21, 19, 30,  0), #  12600     0 IRST
        datetime(2035,  3, 21, 20, 30,  0), #  16200  3600 IRDT
        datetime(2035,  9, 21, 19, 30,  0), #  12600     0 IRST
        datetime(2036,  3, 20, 20, 30,  0), #  16200  3600 IRDT
        datetime(2036,  9, 20, 19, 30,  0), #  12600     0 IRST
        datetime(2037,  3, 20, 20, 30,  0), #  16200  3600 IRDT
        datetime(2037,  9, 20, 19, 30,  0), #  12600     0 IRST
        ]

    _transition_info = [
        ttinfo( 12344,      0,  'LMT'),
        ttinfo( 12344,      0,  'TMT'),
        ttinfo( 12600,      0, 'IRST'),
        ttinfo( 14400,      0, 'IRST'),
        ttinfo( 18000,   3600, 'IRDT'),
        ttinfo( 14400,      0, 'IRST'),
        ttinfo( 12600,      0, 'IRST'),
        ttinfo( 16200,   3600, 'IRDT'),
        ttinfo( 12600,      0, 'IRST'),
        ttinfo( 16200,   3600, 'IRDT'),
        ttinfo( 12600,      0, 'IRST'),
        ttinfo( 16200,   3600, 'IRDT'),
        ttinfo( 12600,      0, 'IRST'),
        ttinfo( 16200,   3600, 'IRDT'),
        ttinfo( 12600,      0, 'IRST'),
        ttinfo( 16200,   3600, 'IRDT'),
        ttinfo( 12600,      0, 'IRST'),
        ttinfo( 16200,   3600, 'IRDT'),
        ttinfo( 12600,      0, 'IRST'),
        ttinfo( 16200,   3600, 'IRDT'),
        ttinfo( 12600,      0, 'IRST'),
        ttinfo( 16200,   3600, 'IRDT'),
        ttinfo( 12600,      0, 'IRST'),
        ttinfo( 16200,   3600, 'IRDT'),
        ttinfo( 12600,      0, 'IRST'),
        ttinfo( 16200,   3600, 'IRDT'),
        ttinfo( 12600,      0, 'IRST'),
        ttinfo( 16200,   3600, 'IRDT'),
        ttinfo( 12600,      0, 'IRST'),
        ttinfo( 16200,   3600, 'IRDT'),
        ttinfo( 12600,      0, 'IRST'),
        ttinfo( 16200,   3600, 'IRDT'),
        ttinfo( 12600,      0, 'IRST'),
        ttinfo( 16200,   3600, 'IRDT'),
        ttinfo( 12600,      0, 'IRST'),
        ttinfo( 16200,   3600, 'IRDT'),
        ttinfo( 12600,      0, 'IRST'),
        ttinfo( 16200,   3600, 'IRDT'),
        ttinfo( 12600,      0, 'IRST'),
        ttinfo( 16200,   3600, 'IRDT'),
        ttinfo( 12600,      0, 'IRST'),
        ttinfo( 16200,   3600, 'IRDT'),
        ttinfo( 12600,      0, 'IRST'),
        ttinfo( 16200,   3600, 'IRDT'),
        ttinfo( 12600,      0, 'IRST'),
        ttinfo( 16200,   3600, 'IRDT'),
        ttinfo( 12600,      0, 'IRST'),
        ttinfo( 16200,   3600, 'IRDT'),
        ttinfo( 12600,      0, 'IRST'),
        ttinfo( 16200,   3600, 'IRDT'),
        ttinfo( 12600,      0, 'IRST'),
        ttinfo( 16200,   3600, 'IRDT'),
        ttinfo( 12600,      0, 'IRST'),
        ttinfo( 16200,   3600, 'IRDT'),
        ttinfo( 12600,      0, 'IRST'),
        ttinfo( 16200,   3600, 'IRDT'),
        ttinfo( 12600,      0, 'IRST'),
        ttinfo( 16200,   3600, 'IRDT'),
        ttinfo( 12600,      0, 'IRST'),
        ttinfo( 16200,   3600, 'IRDT'),
        ttinfo( 12600,      0, 'IRST'),
        ttinfo( 16200,   3600, 'IRDT'),
        ttinfo( 12600,      0, 'IRST'),
        ttinfo( 16200,   3600, 'IRDT'),
        ttinfo( 12600,      0, 'IRST'),
        ttinfo( 16200,   3600, 'IRDT'),
        ttinfo( 12600,      0, 'IRST'),
        ttinfo( 16200,   3600, 'IRDT'),
        ttinfo( 12600,      0, 'IRST'),
        ttinfo( 16200,   3600, 'IRDT'),
        ttinfo( 12600,      0, 'IRST'),
        ttinfo( 16200,   3600, 'IRDT'),
        ttinfo( 12600,      0, 'IRST'),
        ttinfo( 16200,   3600, 'IRDT'),
        ttinfo( 12600,      0, 'IRST'),
        ttinfo( 16200,   3600, 'IRDT'),
        ttinfo( 12600,      0, 'IRST'),
        ttinfo( 16200,   3600, 'IRDT'),
        ttinfo( 12600,      0, 'IRST'),
        ttinfo( 16200,   3600, 'IRDT'),
        ttinfo( 12600,      0, 'IRST'),
        ttinfo( 16200,   3600, 'IRDT'),
        ttinfo( 12600,      0, 'IRST'),
        ttinfo( 16200,   3600, 'IRDT'),
        ttinfo( 12600,      0, 'IRST'),
        ttinfo( 16200,   3600, 'IRDT'),
        ttinfo( 12600,      0, 'IRST'),
        ttinfo( 16200,   3600, 'IRDT'),
        ttinfo( 12600,      0, 'IRST'),
        ttinfo( 16200,   3600, 'IRDT'),
        ttinfo( 12600,      0, 'IRST'),
        ttinfo( 16200,   3600, 'IRDT'),
        ttinfo( 12600,      0, 'IRST'),
        ttinfo( 16200,   3600, 'IRDT'),
        ttinfo( 12600,      0, 'IRST'),
        ttinfo( 16200,   3600, 'IRDT'),
        ttinfo( 12600,      0, 'IRST'),
        ttinfo( 16200,   3600, 'IRDT'),
        ttinfo( 12600,      0, 'IRST'),
        ttinfo( 16200,   3600, 'IRDT'),
        ttinfo( 12600,      0, 'IRST'),
        ttinfo( 16200,   3600, 'IRDT'),
        ttinfo( 12600,      0, 'IRST'),
        ttinfo( 16200,   3600, 'IRDT'),
        ttinfo( 12600,      0, 'IRST'),
        ]

Iran = Iran() # Singleton

