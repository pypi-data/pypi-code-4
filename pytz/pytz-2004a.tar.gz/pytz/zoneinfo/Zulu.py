'''
tzinfo timezone information for Zulu.

Generated from the Olson timezone database:
    ftp://elsie.nci.nih.gov/pub/tz*.tar.gz
'''

from pytz.tzinfo import StaticTzInfo
from pytz.tzinfo import memorized_timedelta as timedelta

class Zulu(StaticTzInfo):
    '''Zulu timezone definition. See datetime.tzinfo for details'''
    _zone = 'Zulu'
    _utcoffset = timedelta(seconds=0)
    _tzname = 'UTC'

Zulu = Zulu() # Singleton

