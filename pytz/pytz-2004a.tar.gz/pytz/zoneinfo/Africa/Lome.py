'''
tzinfo timezone information for Africa/Lome.

Generated from the Olson timezone database:
    ftp://elsie.nci.nih.gov/pub/tz*.tar.gz
'''

from pytz.tzinfo import StaticTzInfo
from pytz.tzinfo import memorized_timedelta as timedelta

class Lome(StaticTzInfo):
    '''Africa/Lome timezone definition. See datetime.tzinfo for details'''
    _zone = 'Africa/Lome'
    _utcoffset = timedelta(seconds=0)
    _tzname = 'GMT'

Lome = Lome() # Singleton

