'''
tzinfo timezone information for Africa/Lubumbashi.

Generated from the Olson timezone database:
    ftp://elsie.nci.nih.gov/pub/tz*.tar.gz
'''

from pytz.tzinfo import StaticTzInfo
from pytz.tzinfo import memorized_timedelta as timedelta

class Lubumbashi(StaticTzInfo):
    '''Africa/Lubumbashi timezone definition. See datetime.tzinfo for details'''
    _zone = 'Africa/Lubumbashi'
    _utcoffset = timedelta(seconds=7200)
    _tzname = 'CAT'

Lubumbashi = Lubumbashi() # Singleton

