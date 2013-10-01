'''
tzinfo timezone information for Africa/Bujumbura.

Generated from the Olson timezone database:
    ftp://elsie.nci.nih.gov/pub/tz*.tar.gz
'''

from pytz.tzinfo import StaticTzInfo
from pytz.tzinfo import memorized_timedelta as timedelta

class Bujumbura(StaticTzInfo):
    '''Africa/Bujumbura timezone definition. See datetime.tzinfo for details'''
    _zone = 'Africa/Bujumbura'
    _utcoffset = timedelta(seconds=7200)
    _tzname = 'CAT'

Bujumbura = Bujumbura() # Singleton

