'''
tzinfo timezone information for Asia/Bishkek.

Generated from the Olson timezone database:
    ftp://elsie.nci.nih.gov/pub/tz*.tar.gz
'''

from pytz.tzinfo import DstTzInfo
from pytz.tzinfo import memorized_datetime as datetime
from pytz.tzinfo import memorized_ttinfo as ttinfo

class Bishkek(DstTzInfo):
    '''Asia/Bishkek timezone definition. See datetime.tzinfo for details'''

    _zone = 'Asia/Bishkek'

    _utc_transition_times = [
        datetime(   1,  1,  1,  0,  0,  0), #  17904     0 LMT
        datetime(1924,  5,  1, 19,  1, 36), #  18000     0 FRUT
        datetime(1930,  6, 20, 19,  0,  0), #  21600     0 FRUT
        datetime(1981,  3, 31, 18,  0,  0), #  25200  3600 FRUST
        datetime(1981,  9, 30, 17,  0,  0), #  21600     0 FRUT
        datetime(1982,  3, 31, 18,  0,  0), #  25200  3600 FRUST
        datetime(1982,  9, 30, 17,  0,  0), #  21600     0 FRUT
        datetime(1983,  3, 31, 18,  0,  0), #  25200  3600 FRUST
        datetime(1983,  9, 30, 17,  0,  0), #  21600     0 FRUT
        datetime(1984,  3, 31, 18,  0,  0), #  25200  3600 FRUST
        datetime(1984,  9, 29, 20,  0,  0), #  21600     0 FRUT
        datetime(1985,  3, 30, 20,  0,  0), #  25200  3600 FRUST
        datetime(1985,  9, 28, 20,  0,  0), #  21600     0 FRUT
        datetime(1986,  3, 29, 20,  0,  0), #  25200  3600 FRUST
        datetime(1986,  9, 27, 20,  0,  0), #  21600     0 FRUT
        datetime(1987,  3, 28, 20,  0,  0), #  25200  3600 FRUST
        datetime(1987,  9, 26, 20,  0,  0), #  21600     0 FRUT
        datetime(1988,  3, 26, 20,  0,  0), #  25200  3600 FRUST
        datetime(1988,  9, 24, 20,  0,  0), #  21600     0 FRUT
        datetime(1989,  3, 25, 20,  0,  0), #  25200  3600 FRUST
        datetime(1989,  9, 23, 20,  0,  0), #  21600     0 FRUT
        datetime(1990,  3, 24, 20,  0,  0), #  25200  3600 FRUST
        datetime(1990,  9, 29, 20,  0,  0), #  21600     0 FRUT
        datetime(1991,  3, 30, 20,  0,  0), #  21600     0 FRUST
        datetime(1991,  8, 30, 20,  0,  0), #  18000     0 KGT
        datetime(1992,  4, 11, 19,  0,  0), #  21600  3600 KGST
        datetime(1992,  9, 26, 18,  0,  0), #  18000     0 KGT
        datetime(1993,  4, 10, 19,  0,  0), #  21600  3600 KGST
        datetime(1993,  9, 25, 18,  0,  0), #  18000     0 KGT
        datetime(1994,  4,  9, 19,  0,  0), #  21600  3600 KGST
        datetime(1994,  9, 24, 18,  0,  0), #  18000     0 KGT
        datetime(1995,  4,  8, 19,  0,  0), #  21600  3600 KGST
        datetime(1995,  9, 23, 18,  0,  0), #  18000     0 KGT
        datetime(1996,  4,  6, 19,  0,  0), #  21600  3600 KGST
        datetime(1996,  9, 28, 18,  0,  0), #  18000     0 KGT
        datetime(1997,  3, 29, 21, 30,  0), #  21600  3600 KGST
        datetime(1997, 10, 25, 20, 30,  0), #  18000     0 KGT
        datetime(1998,  3, 28, 21, 30,  0), #  21600  3600 KGST
        datetime(1998, 10, 24, 20, 30,  0), #  18000     0 KGT
        datetime(1999,  3, 27, 21, 30,  0), #  21600  3600 KGST
        datetime(1999, 10, 30, 20, 30,  0), #  18000     0 KGT
        datetime(2000,  3, 25, 21, 30,  0), #  21600  3600 KGST
        datetime(2000, 10, 28, 20, 30,  0), #  18000     0 KGT
        datetime(2001,  3, 24, 21, 30,  0), #  21600  3600 KGST
        datetime(2001, 10, 27, 20, 30,  0), #  18000     0 KGT
        datetime(2002,  3, 30, 21, 30,  0), #  21600  3600 KGST
        datetime(2002, 10, 26, 20, 30,  0), #  18000     0 KGT
        datetime(2003,  3, 29, 21, 30,  0), #  21600  3600 KGST
        datetime(2003, 10, 25, 20, 30,  0), #  18000     0 KGT
        datetime(2004,  3, 27, 21, 30,  0), #  21600  3600 KGST
        datetime(2004, 10, 30, 20, 30,  0), #  18000     0 KGT
        datetime(2005,  3, 26, 21, 30,  0), #  21600  3600 KGST
        datetime(2005, 10, 29, 20, 30,  0), #  18000     0 KGT
        datetime(2006,  3, 25, 21, 30,  0), #  21600  3600 KGST
        datetime(2006, 10, 28, 20, 30,  0), #  18000     0 KGT
        datetime(2007,  3, 24, 21, 30,  0), #  21600  3600 KGST
        datetime(2007, 10, 27, 20, 30,  0), #  18000     0 KGT
        datetime(2008,  3, 29, 21, 30,  0), #  21600  3600 KGST
        datetime(2008, 10, 25, 20, 30,  0), #  18000     0 KGT
        datetime(2009,  3, 28, 21, 30,  0), #  21600  3600 KGST
        datetime(2009, 10, 24, 20, 30,  0), #  18000     0 KGT
        datetime(2010,  3, 27, 21, 30,  0), #  21600  3600 KGST
        datetime(2010, 10, 30, 20, 30,  0), #  18000     0 KGT
        datetime(2011,  3, 26, 21, 30,  0), #  21600  3600 KGST
        datetime(2011, 10, 29, 20, 30,  0), #  18000     0 KGT
        datetime(2012,  3, 24, 21, 30,  0), #  21600  3600 KGST
        datetime(2012, 10, 27, 20, 30,  0), #  18000     0 KGT
        datetime(2013,  3, 30, 21, 30,  0), #  21600  3600 KGST
        datetime(2013, 10, 26, 20, 30,  0), #  18000     0 KGT
        datetime(2014,  3, 29, 21, 30,  0), #  21600  3600 KGST
        datetime(2014, 10, 25, 20, 30,  0), #  18000     0 KGT
        datetime(2015,  3, 28, 21, 30,  0), #  21600  3600 KGST
        datetime(2015, 10, 24, 20, 30,  0), #  18000     0 KGT
        datetime(2016,  3, 26, 21, 30,  0), #  21600  3600 KGST
        datetime(2016, 10, 29, 20, 30,  0), #  18000     0 KGT
        datetime(2017,  3, 25, 21, 30,  0), #  21600  3600 KGST
        datetime(2017, 10, 28, 20, 30,  0), #  18000     0 KGT
        datetime(2018,  3, 24, 21, 30,  0), #  21600  3600 KGST
        datetime(2018, 10, 27, 20, 30,  0), #  18000     0 KGT
        datetime(2019,  3, 30, 21, 30,  0), #  21600  3600 KGST
        datetime(2019, 10, 26, 20, 30,  0), #  18000     0 KGT
        datetime(2020,  3, 28, 21, 30,  0), #  21600  3600 KGST
        datetime(2020, 10, 24, 20, 30,  0), #  18000     0 KGT
        datetime(2021,  3, 27, 21, 30,  0), #  21600  3600 KGST
        datetime(2021, 10, 30, 20, 30,  0), #  18000     0 KGT
        datetime(2022,  3, 26, 21, 30,  0), #  21600  3600 KGST
        datetime(2022, 10, 29, 20, 30,  0), #  18000     0 KGT
        datetime(2023,  3, 25, 21, 30,  0), #  21600  3600 KGST
        datetime(2023, 10, 28, 20, 30,  0), #  18000     0 KGT
        datetime(2024,  3, 30, 21, 30,  0), #  21600  3600 KGST
        datetime(2024, 10, 26, 20, 30,  0), #  18000     0 KGT
        datetime(2025,  3, 29, 21, 30,  0), #  21600  3600 KGST
        datetime(2025, 10, 25, 20, 30,  0), #  18000     0 KGT
        datetime(2026,  3, 28, 21, 30,  0), #  21600  3600 KGST
        datetime(2026, 10, 24, 20, 30,  0), #  18000     0 KGT
        datetime(2027,  3, 27, 21, 30,  0), #  21600  3600 KGST
        datetime(2027, 10, 30, 20, 30,  0), #  18000     0 KGT
        datetime(2028,  3, 25, 21, 30,  0), #  21600  3600 KGST
        datetime(2028, 10, 28, 20, 30,  0), #  18000     0 KGT
        datetime(2029,  3, 24, 21, 30,  0), #  21600  3600 KGST
        datetime(2029, 10, 27, 20, 30,  0), #  18000     0 KGT
        datetime(2030,  3, 30, 21, 30,  0), #  21600  3600 KGST
        datetime(2030, 10, 26, 20, 30,  0), #  18000     0 KGT
        datetime(2031,  3, 29, 21, 30,  0), #  21600  3600 KGST
        datetime(2031, 10, 25, 20, 30,  0), #  18000     0 KGT
        datetime(2032,  3, 27, 21, 30,  0), #  21600  3600 KGST
        datetime(2032, 10, 30, 20, 30,  0), #  18000     0 KGT
        datetime(2033,  3, 26, 21, 30,  0), #  21600  3600 KGST
        datetime(2033, 10, 29, 20, 30,  0), #  18000     0 KGT
        datetime(2034,  3, 25, 21, 30,  0), #  21600  3600 KGST
        datetime(2034, 10, 28, 20, 30,  0), #  18000     0 KGT
        datetime(2035,  3, 24, 21, 30,  0), #  21600  3600 KGST
        datetime(2035, 10, 27, 20, 30,  0), #  18000     0 KGT
        datetime(2036,  3, 29, 21, 30,  0), #  21600  3600 KGST
        datetime(2036, 10, 25, 20, 30,  0), #  18000     0 KGT
        datetime(2037,  3, 28, 21, 30,  0), #  21600  3600 KGST
        datetime(2037, 10, 24, 20, 30,  0), #  18000     0 KGT
        ]

    _transition_info = [
        ttinfo( 17904,      0,  'LMT'),
        ttinfo( 18000,      0, 'FRUT'),
        ttinfo( 21600,      0, 'FRUT'),
        ttinfo( 25200,   3600, 'FRUST'),
        ttinfo( 21600,      0, 'FRUT'),
        ttinfo( 25200,   3600, 'FRUST'),
        ttinfo( 21600,      0, 'FRUT'),
        ttinfo( 25200,   3600, 'FRUST'),
        ttinfo( 21600,      0, 'FRUT'),
        ttinfo( 25200,   3600, 'FRUST'),
        ttinfo( 21600,      0, 'FRUT'),
        ttinfo( 25200,   3600, 'FRUST'),
        ttinfo( 21600,      0, 'FRUT'),
        ttinfo( 25200,   3600, 'FRUST'),
        ttinfo( 21600,      0, 'FRUT'),
        ttinfo( 25200,   3600, 'FRUST'),
        ttinfo( 21600,      0, 'FRUT'),
        ttinfo( 25200,   3600, 'FRUST'),
        ttinfo( 21600,      0, 'FRUT'),
        ttinfo( 25200,   3600, 'FRUST'),
        ttinfo( 21600,      0, 'FRUT'),
        ttinfo( 25200,   3600, 'FRUST'),
        ttinfo( 21600,      0, 'FRUT'),
        ttinfo( 21600,      0, 'FRUST'),
        ttinfo( 18000,      0,  'KGT'),
        ttinfo( 21600,   3600, 'KGST'),
        ttinfo( 18000,      0,  'KGT'),
        ttinfo( 21600,   3600, 'KGST'),
        ttinfo( 18000,      0,  'KGT'),
        ttinfo( 21600,   3600, 'KGST'),
        ttinfo( 18000,      0,  'KGT'),
        ttinfo( 21600,   3600, 'KGST'),
        ttinfo( 18000,      0,  'KGT'),
        ttinfo( 21600,   3600, 'KGST'),
        ttinfo( 18000,      0,  'KGT'),
        ttinfo( 21600,   3600, 'KGST'),
        ttinfo( 18000,      0,  'KGT'),
        ttinfo( 21600,   3600, 'KGST'),
        ttinfo( 18000,      0,  'KGT'),
        ttinfo( 21600,   3600, 'KGST'),
        ttinfo( 18000,      0,  'KGT'),
        ttinfo( 21600,   3600, 'KGST'),
        ttinfo( 18000,      0,  'KGT'),
        ttinfo( 21600,   3600, 'KGST'),
        ttinfo( 18000,      0,  'KGT'),
        ttinfo( 21600,   3600, 'KGST'),
        ttinfo( 18000,      0,  'KGT'),
        ttinfo( 21600,   3600, 'KGST'),
        ttinfo( 18000,      0,  'KGT'),
        ttinfo( 21600,   3600, 'KGST'),
        ttinfo( 18000,      0,  'KGT'),
        ttinfo( 21600,   3600, 'KGST'),
        ttinfo( 18000,      0,  'KGT'),
        ttinfo( 21600,   3600, 'KGST'),
        ttinfo( 18000,      0,  'KGT'),
        ttinfo( 21600,   3600, 'KGST'),
        ttinfo( 18000,      0,  'KGT'),
        ttinfo( 21600,   3600, 'KGST'),
        ttinfo( 18000,      0,  'KGT'),
        ttinfo( 21600,   3600, 'KGST'),
        ttinfo( 18000,      0,  'KGT'),
        ttinfo( 21600,   3600, 'KGST'),
        ttinfo( 18000,      0,  'KGT'),
        ttinfo( 21600,   3600, 'KGST'),
        ttinfo( 18000,      0,  'KGT'),
        ttinfo( 21600,   3600, 'KGST'),
        ttinfo( 18000,      0,  'KGT'),
        ttinfo( 21600,   3600, 'KGST'),
        ttinfo( 18000,      0,  'KGT'),
        ttinfo( 21600,   3600, 'KGST'),
        ttinfo( 18000,      0,  'KGT'),
        ttinfo( 21600,   3600, 'KGST'),
        ttinfo( 18000,      0,  'KGT'),
        ttinfo( 21600,   3600, 'KGST'),
        ttinfo( 18000,      0,  'KGT'),
        ttinfo( 21600,   3600, 'KGST'),
        ttinfo( 18000,      0,  'KGT'),
        ttinfo( 21600,   3600, 'KGST'),
        ttinfo( 18000,      0,  'KGT'),
        ttinfo( 21600,   3600, 'KGST'),
        ttinfo( 18000,      0,  'KGT'),
        ttinfo( 21600,   3600, 'KGST'),
        ttinfo( 18000,      0,  'KGT'),
        ttinfo( 21600,   3600, 'KGST'),
        ttinfo( 18000,      0,  'KGT'),
        ttinfo( 21600,   3600, 'KGST'),
        ttinfo( 18000,      0,  'KGT'),
        ttinfo( 21600,   3600, 'KGST'),
        ttinfo( 18000,      0,  'KGT'),
        ttinfo( 21600,   3600, 'KGST'),
        ttinfo( 18000,      0,  'KGT'),
        ttinfo( 21600,   3600, 'KGST'),
        ttinfo( 18000,      0,  'KGT'),
        ttinfo( 21600,   3600, 'KGST'),
        ttinfo( 18000,      0,  'KGT'),
        ttinfo( 21600,   3600, 'KGST'),
        ttinfo( 18000,      0,  'KGT'),
        ttinfo( 21600,   3600, 'KGST'),
        ttinfo( 18000,      0,  'KGT'),
        ttinfo( 21600,   3600, 'KGST'),
        ttinfo( 18000,      0,  'KGT'),
        ttinfo( 21600,   3600, 'KGST'),
        ttinfo( 18000,      0,  'KGT'),
        ttinfo( 21600,   3600, 'KGST'),
        ttinfo( 18000,      0,  'KGT'),
        ttinfo( 21600,   3600, 'KGST'),
        ttinfo( 18000,      0,  'KGT'),
        ttinfo( 21600,   3600, 'KGST'),
        ttinfo( 18000,      0,  'KGT'),
        ttinfo( 21600,   3600, 'KGST'),
        ttinfo( 18000,      0,  'KGT'),
        ttinfo( 21600,   3600, 'KGST'),
        ttinfo( 18000,      0,  'KGT'),
        ttinfo( 21600,   3600, 'KGST'),
        ttinfo( 18000,      0,  'KGT'),
        ttinfo( 21600,   3600, 'KGST'),
        ttinfo( 18000,      0,  'KGT'),
        ]

Bishkek = Bishkek() # Singleton

