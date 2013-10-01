'''
tzinfo timezone information for America/Barbados.

Generated from the Olson timezone database:
    ftp://elsie.nci.nih.gov/pub/tz*.tar.gz
'''

from pytz.tzinfo import DstTzInfo
from pytz.tzinfo import memorized_datetime as datetime
from pytz.tzinfo import memorized_ttinfo as ttinfo

class Barbados(DstTzInfo):
    '''America/Barbados timezone definition. See datetime.tzinfo for details'''

    _zone = 'America/Barbados'

    _utc_transition_times = [
        datetime(   1,  1,  1,  0,  0,  0), # -14308     0 LMT
        datetime(1924,  1,  1,  3, 58, 28), # -14308     0 BMT
        datetime(1932,  1,  1,  3, 58, 28), # -14400     0 AST
        datetime(1977,  6, 12,  6,  0,  0), # -10800  3600 ADT
        datetime(1977, 10,  2,  5,  0,  0), # -14400     0 AST
        datetime(1978,  4, 16,  6,  0,  0), # -10800  3600 ADT
        datetime(1978, 10,  1,  5,  0,  0), # -14400     0 AST
        datetime(1979,  4, 15,  6,  0,  0), # -10800  3600 ADT
        datetime(1979,  9, 30,  5,  0,  0), # -14400     0 AST
        datetime(1980,  4, 20,  6,  0,  0), # -10800  3600 ADT
        datetime(1980,  9, 25,  5,  0,  0), # -14400     0 AST
        ]

    _transition_info = [
        ttinfo(-14308,      0,  'LMT'),
        ttinfo(-14308,      0,  'BMT'),
        ttinfo(-14400,      0,  'AST'),
        ttinfo(-10800,   3600,  'ADT'),
        ttinfo(-14400,      0,  'AST'),
        ttinfo(-10800,   3600,  'ADT'),
        ttinfo(-14400,      0,  'AST'),
        ttinfo(-10800,   3600,  'ADT'),
        ttinfo(-14400,      0,  'AST'),
        ttinfo(-10800,   3600,  'ADT'),
        ttinfo(-14400,      0,  'AST'),
        ]

Barbados = Barbados() # Singleton

