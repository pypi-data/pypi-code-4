'''
tzinfo timezone information for Asia/Baku.

Generated from the Olson timezone database:
    ftp://elsie.nci.nih.gov/pub/tz*.tar.gz
'''

from pytz.tzinfo import DstTzInfo
from pytz.tzinfo import memorized_datetime as datetime
from pytz.tzinfo import memorized_ttinfo as ttinfo

class Baku(DstTzInfo):
    '''Asia/Baku timezone definition. See datetime.tzinfo for details'''

    _zone = 'Asia/Baku'

    _utc_transition_times = [
        datetime(   1,  1,  1,  0,  0,  0), #  11964     0 LMT
        datetime(1924,  5,  1, 20, 40, 36), #  10800     0 BAKT
        datetime(1957,  2, 28, 21,  0,  0), #  14400     0 BAKT
        datetime(1981,  3, 31, 20,  0,  0), #  18000  3600 BAKST
        datetime(1981,  9, 30, 19,  0,  0), #  14400     0 BAKT
        datetime(1982,  3, 31, 20,  0,  0), #  18000  3600 BAKST
        datetime(1982,  9, 30, 19,  0,  0), #  14400     0 BAKT
        datetime(1983,  3, 31, 20,  0,  0), #  18000  3600 BAKST
        datetime(1983,  9, 30, 19,  0,  0), #  14400     0 BAKT
        datetime(1984,  3, 31, 20,  0,  0), #  18000  3600 BAKST
        datetime(1984,  9, 29, 22,  0,  0), #  14400     0 BAKT
        datetime(1985,  3, 30, 22,  0,  0), #  18000  3600 BAKST
        datetime(1985,  9, 28, 22,  0,  0), #  14400     0 BAKT
        datetime(1986,  3, 29, 22,  0,  0), #  18000  3600 BAKST
        datetime(1986,  9, 27, 22,  0,  0), #  14400     0 BAKT
        datetime(1987,  3, 28, 22,  0,  0), #  18000  3600 BAKST
        datetime(1987,  9, 26, 22,  0,  0), #  14400     0 BAKT
        datetime(1988,  3, 26, 22,  0,  0), #  18000  3600 BAKST
        datetime(1988,  9, 24, 22,  0,  0), #  14400     0 BAKT
        datetime(1989,  3, 25, 22,  0,  0), #  18000  3600 BAKST
        datetime(1989,  9, 23, 22,  0,  0), #  14400     0 BAKT
        datetime(1990,  3, 24, 22,  0,  0), #  18000  3600 BAKST
        datetime(1990,  9, 29, 22,  0,  0), #  14400     0 BAKT
        datetime(1991,  3, 30, 22,  0,  0), #  14400     0 BAKST
        datetime(1991,  8, 29, 20,  0,  0), #  14400     0 AZST
        datetime(1991,  9, 28, 23,  0,  0), #  10800     0 AZT
        datetime(1992,  3, 28, 20,  0,  0), #  14400  3600 AZST
        datetime(1992,  9, 26, 19,  0,  0), #  10800     0 AZT
        datetime(1992,  9, 26, 23,  0,  0), #  14400     0 AZT
        datetime(1995, 12, 31, 20,  0,  0), #  18000  3600 AZST
        datetime(1996,  3, 31,  1,  0,  0), #  18000     0 AZST
        datetime(1996, 10, 27,  1,  0,  0), #  14400     0 AZT
        datetime(1996, 12, 31, 20,  0,  0), #  14400     0 AZT
        datetime(1997,  3, 29, 21,  0,  0), #  18000  3600 AZST
        datetime(1997, 10, 25, 20,  0,  0), #  14400     0 AZT
        datetime(1998,  3, 28, 21,  0,  0), #  18000  3600 AZST
        datetime(1998, 10, 24, 20,  0,  0), #  14400     0 AZT
        datetime(1999,  3, 27, 21,  0,  0), #  18000  3600 AZST
        datetime(1999, 10, 30, 20,  0,  0), #  14400     0 AZT
        datetime(2000,  3, 25, 21,  0,  0), #  18000  3600 AZST
        datetime(2000, 10, 28, 20,  0,  0), #  14400     0 AZT
        datetime(2001,  3, 24, 21,  0,  0), #  18000  3600 AZST
        datetime(2001, 10, 27, 20,  0,  0), #  14400     0 AZT
        datetime(2002,  3, 30, 21,  0,  0), #  18000  3600 AZST
        datetime(2002, 10, 26, 20,  0,  0), #  14400     0 AZT
        datetime(2003,  3, 29, 21,  0,  0), #  18000  3600 AZST
        datetime(2003, 10, 25, 20,  0,  0), #  14400     0 AZT
        datetime(2004,  3, 27, 21,  0,  0), #  18000  3600 AZST
        datetime(2004, 10, 30, 20,  0,  0), #  14400     0 AZT
        datetime(2005,  3, 26, 21,  0,  0), #  18000  3600 AZST
        datetime(2005, 10, 29, 20,  0,  0), #  14400     0 AZT
        datetime(2006,  3, 25, 21,  0,  0), #  18000  3600 AZST
        datetime(2006, 10, 28, 20,  0,  0), #  14400     0 AZT
        datetime(2007,  3, 24, 21,  0,  0), #  18000  3600 AZST
        datetime(2007, 10, 27, 20,  0,  0), #  14400     0 AZT
        datetime(2008,  3, 29, 21,  0,  0), #  18000  3600 AZST
        datetime(2008, 10, 25, 20,  0,  0), #  14400     0 AZT
        datetime(2009,  3, 28, 21,  0,  0), #  18000  3600 AZST
        datetime(2009, 10, 24, 20,  0,  0), #  14400     0 AZT
        datetime(2010,  3, 27, 21,  0,  0), #  18000  3600 AZST
        datetime(2010, 10, 30, 20,  0,  0), #  14400     0 AZT
        datetime(2011,  3, 26, 21,  0,  0), #  18000  3600 AZST
        datetime(2011, 10, 29, 20,  0,  0), #  14400     0 AZT
        datetime(2012,  3, 24, 21,  0,  0), #  18000  3600 AZST
        datetime(2012, 10, 27, 20,  0,  0), #  14400     0 AZT
        datetime(2013,  3, 30, 21,  0,  0), #  18000  3600 AZST
        datetime(2013, 10, 26, 20,  0,  0), #  14400     0 AZT
        datetime(2014,  3, 29, 21,  0,  0), #  18000  3600 AZST
        datetime(2014, 10, 25, 20,  0,  0), #  14400     0 AZT
        datetime(2015,  3, 28, 21,  0,  0), #  18000  3600 AZST
        datetime(2015, 10, 24, 20,  0,  0), #  14400     0 AZT
        datetime(2016,  3, 26, 21,  0,  0), #  18000  3600 AZST
        datetime(2016, 10, 29, 20,  0,  0), #  14400     0 AZT
        datetime(2017,  3, 25, 21,  0,  0), #  18000  3600 AZST
        datetime(2017, 10, 28, 20,  0,  0), #  14400     0 AZT
        datetime(2018,  3, 24, 21,  0,  0), #  18000  3600 AZST
        datetime(2018, 10, 27, 20,  0,  0), #  14400     0 AZT
        datetime(2019,  3, 30, 21,  0,  0), #  18000  3600 AZST
        datetime(2019, 10, 26, 20,  0,  0), #  14400     0 AZT
        datetime(2020,  3, 28, 21,  0,  0), #  18000  3600 AZST
        datetime(2020, 10, 24, 20,  0,  0), #  14400     0 AZT
        datetime(2021,  3, 27, 21,  0,  0), #  18000  3600 AZST
        datetime(2021, 10, 30, 20,  0,  0), #  14400     0 AZT
        datetime(2022,  3, 26, 21,  0,  0), #  18000  3600 AZST
        datetime(2022, 10, 29, 20,  0,  0), #  14400     0 AZT
        datetime(2023,  3, 25, 21,  0,  0), #  18000  3600 AZST
        datetime(2023, 10, 28, 20,  0,  0), #  14400     0 AZT
        datetime(2024,  3, 30, 21,  0,  0), #  18000  3600 AZST
        datetime(2024, 10, 26, 20,  0,  0), #  14400     0 AZT
        datetime(2025,  3, 29, 21,  0,  0), #  18000  3600 AZST
        datetime(2025, 10, 25, 20,  0,  0), #  14400     0 AZT
        datetime(2026,  3, 28, 21,  0,  0), #  18000  3600 AZST
        datetime(2026, 10, 24, 20,  0,  0), #  14400     0 AZT
        datetime(2027,  3, 27, 21,  0,  0), #  18000  3600 AZST
        datetime(2027, 10, 30, 20,  0,  0), #  14400     0 AZT
        datetime(2028,  3, 25, 21,  0,  0), #  18000  3600 AZST
        datetime(2028, 10, 28, 20,  0,  0), #  14400     0 AZT
        datetime(2029,  3, 24, 21,  0,  0), #  18000  3600 AZST
        datetime(2029, 10, 27, 20,  0,  0), #  14400     0 AZT
        datetime(2030,  3, 30, 21,  0,  0), #  18000  3600 AZST
        datetime(2030, 10, 26, 20,  0,  0), #  14400     0 AZT
        datetime(2031,  3, 29, 21,  0,  0), #  18000  3600 AZST
        datetime(2031, 10, 25, 20,  0,  0), #  14400     0 AZT
        datetime(2032,  3, 27, 21,  0,  0), #  18000  3600 AZST
        datetime(2032, 10, 30, 20,  0,  0), #  14400     0 AZT
        datetime(2033,  3, 26, 21,  0,  0), #  18000  3600 AZST
        datetime(2033, 10, 29, 20,  0,  0), #  14400     0 AZT
        datetime(2034,  3, 25, 21,  0,  0), #  18000  3600 AZST
        datetime(2034, 10, 28, 20,  0,  0), #  14400     0 AZT
        datetime(2035,  3, 24, 21,  0,  0), #  18000  3600 AZST
        datetime(2035, 10, 27, 20,  0,  0), #  14400     0 AZT
        datetime(2036,  3, 29, 21,  0,  0), #  18000  3600 AZST
        datetime(2036, 10, 25, 20,  0,  0), #  14400     0 AZT
        datetime(2037,  3, 28, 21,  0,  0), #  18000  3600 AZST
        datetime(2037, 10, 24, 20,  0,  0), #  14400     0 AZT
        ]

    _transition_info = [
        ttinfo( 11964,      0,  'LMT'),
        ttinfo( 10800,      0, 'BAKT'),
        ttinfo( 14400,      0, 'BAKT'),
        ttinfo( 18000,   3600, 'BAKST'),
        ttinfo( 14400,      0, 'BAKT'),
        ttinfo( 18000,   3600, 'BAKST'),
        ttinfo( 14400,      0, 'BAKT'),
        ttinfo( 18000,   3600, 'BAKST'),
        ttinfo( 14400,      0, 'BAKT'),
        ttinfo( 18000,   3600, 'BAKST'),
        ttinfo( 14400,      0, 'BAKT'),
        ttinfo( 18000,   3600, 'BAKST'),
        ttinfo( 14400,      0, 'BAKT'),
        ttinfo( 18000,   3600, 'BAKST'),
        ttinfo( 14400,      0, 'BAKT'),
        ttinfo( 18000,   3600, 'BAKST'),
        ttinfo( 14400,      0, 'BAKT'),
        ttinfo( 18000,   3600, 'BAKST'),
        ttinfo( 14400,      0, 'BAKT'),
        ttinfo( 18000,   3600, 'BAKST'),
        ttinfo( 14400,      0, 'BAKT'),
        ttinfo( 18000,   3600, 'BAKST'),
        ttinfo( 14400,      0, 'BAKT'),
        ttinfo( 14400,      0, 'BAKST'),
        ttinfo( 14400,      0, 'AZST'),
        ttinfo( 10800,      0,  'AZT'),
        ttinfo( 14400,   3600, 'AZST'),
        ttinfo( 10800,      0,  'AZT'),
        ttinfo( 14400,      0,  'AZT'),
        ttinfo( 18000,   3600, 'AZST'),
        ttinfo( 18000,      0, 'AZST'),
        ttinfo( 14400,      0,  'AZT'),
        ttinfo( 14400,      0,  'AZT'),
        ttinfo( 18000,   3600, 'AZST'),
        ttinfo( 14400,      0,  'AZT'),
        ttinfo( 18000,   3600, 'AZST'),
        ttinfo( 14400,      0,  'AZT'),
        ttinfo( 18000,   3600, 'AZST'),
        ttinfo( 14400,      0,  'AZT'),
        ttinfo( 18000,   3600, 'AZST'),
        ttinfo( 14400,      0,  'AZT'),
        ttinfo( 18000,   3600, 'AZST'),
        ttinfo( 14400,      0,  'AZT'),
        ttinfo( 18000,   3600, 'AZST'),
        ttinfo( 14400,      0,  'AZT'),
        ttinfo( 18000,   3600, 'AZST'),
        ttinfo( 14400,      0,  'AZT'),
        ttinfo( 18000,   3600, 'AZST'),
        ttinfo( 14400,      0,  'AZT'),
        ttinfo( 18000,   3600, 'AZST'),
        ttinfo( 14400,      0,  'AZT'),
        ttinfo( 18000,   3600, 'AZST'),
        ttinfo( 14400,      0,  'AZT'),
        ttinfo( 18000,   3600, 'AZST'),
        ttinfo( 14400,      0,  'AZT'),
        ttinfo( 18000,   3600, 'AZST'),
        ttinfo( 14400,      0,  'AZT'),
        ttinfo( 18000,   3600, 'AZST'),
        ttinfo( 14400,      0,  'AZT'),
        ttinfo( 18000,   3600, 'AZST'),
        ttinfo( 14400,      0,  'AZT'),
        ttinfo( 18000,   3600, 'AZST'),
        ttinfo( 14400,      0,  'AZT'),
        ttinfo( 18000,   3600, 'AZST'),
        ttinfo( 14400,      0,  'AZT'),
        ttinfo( 18000,   3600, 'AZST'),
        ttinfo( 14400,      0,  'AZT'),
        ttinfo( 18000,   3600, 'AZST'),
        ttinfo( 14400,      0,  'AZT'),
        ttinfo( 18000,   3600, 'AZST'),
        ttinfo( 14400,      0,  'AZT'),
        ttinfo( 18000,   3600, 'AZST'),
        ttinfo( 14400,      0,  'AZT'),
        ttinfo( 18000,   3600, 'AZST'),
        ttinfo( 14400,      0,  'AZT'),
        ttinfo( 18000,   3600, 'AZST'),
        ttinfo( 14400,      0,  'AZT'),
        ttinfo( 18000,   3600, 'AZST'),
        ttinfo( 14400,      0,  'AZT'),
        ttinfo( 18000,   3600, 'AZST'),
        ttinfo( 14400,      0,  'AZT'),
        ttinfo( 18000,   3600, 'AZST'),
        ttinfo( 14400,      0,  'AZT'),
        ttinfo( 18000,   3600, 'AZST'),
        ttinfo( 14400,      0,  'AZT'),
        ttinfo( 18000,   3600, 'AZST'),
        ttinfo( 14400,      0,  'AZT'),
        ttinfo( 18000,   3600, 'AZST'),
        ttinfo( 14400,      0,  'AZT'),
        ttinfo( 18000,   3600, 'AZST'),
        ttinfo( 14400,      0,  'AZT'),
        ttinfo( 18000,   3600, 'AZST'),
        ttinfo( 14400,      0,  'AZT'),
        ttinfo( 18000,   3600, 'AZST'),
        ttinfo( 14400,      0,  'AZT'),
        ttinfo( 18000,   3600, 'AZST'),
        ttinfo( 14400,      0,  'AZT'),
        ttinfo( 18000,   3600, 'AZST'),
        ttinfo( 14400,      0,  'AZT'),
        ttinfo( 18000,   3600, 'AZST'),
        ttinfo( 14400,      0,  'AZT'),
        ttinfo( 18000,   3600, 'AZST'),
        ttinfo( 14400,      0,  'AZT'),
        ttinfo( 18000,   3600, 'AZST'),
        ttinfo( 14400,      0,  'AZT'),
        ttinfo( 18000,   3600, 'AZST'),
        ttinfo( 14400,      0,  'AZT'),
        ttinfo( 18000,   3600, 'AZST'),
        ttinfo( 14400,      0,  'AZT'),
        ttinfo( 18000,   3600, 'AZST'),
        ttinfo( 14400,      0,  'AZT'),
        ttinfo( 18000,   3600, 'AZST'),
        ttinfo( 14400,      0,  'AZT'),
        ttinfo( 18000,   3600, 'AZST'),
        ttinfo( 14400,      0,  'AZT'),
        ]

Baku = Baku() # Singleton

