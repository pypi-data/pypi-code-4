'''
tzinfo timezone information for Etc/Zulu.

Generated from the Olson timezone database:
    ftp://elsie.nci.nih.gov/pub/tz*.tar.gz
'''

from pytz.tzinfo import StaticTzInfo
from pytz.tzinfo import memorized_timedelta as timedelta

class Zulu(StaticTzInfo):
    '''Etc/Zulu timezone definition. See datetime.tzinfo for details'''
    _zone = 'Etc/Zulu'
    _utcoffset = timedelta(seconds=0)
    _tzname = 'UTC'

Zulu = Zulu() # Singleton

