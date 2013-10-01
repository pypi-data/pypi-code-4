'''
tzinfo timezone information for America/Port_of_Spain.

Generated from the Olson timezone database:
    ftp://elsie.nci.nih.gov/pub/tz*.tar.gz
'''

from pytz.tzinfo import DstTzInfo
from pytz.tzinfo import memorized_datetime as datetime
from pytz.tzinfo import memorized_ttinfo as ttinfo

class Port_of_Spain(DstTzInfo):
    '''America/Port_of_Spain timezone definition. See datetime.tzinfo for details'''

    _zone = 'America/Port_of_Spain'

    _utc_transition_times = [
        datetime(   1,  1,  1,  0,  0,  0), # -14764     0 LMT
        datetime(1912,  3,  2,  4,  6,  4), # -14400     0 AST
        ]

    _transition_info = [
        ttinfo(-14764,      0,  'LMT'),
        ttinfo(-14400,      0,  'AST'),
        ]

Port_of_Spain = Port_of_Spain() # Singleton

