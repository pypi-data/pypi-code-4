'''
tzinfo timezone information for Etc/Universal.

Generated from the Olson timezone database:
    ftp://elsie.nci.nih.gov/pub/tz*.tar.gz
'''

from pytz.tzinfo import StaticTzInfo
from pytz.tzinfo import memorized_timedelta as timedelta

class Universal(StaticTzInfo):
    '''Etc/Universal timezone definition. See datetime.tzinfo for details'''
    _zone = 'Etc/Universal'
    _utcoffset = timedelta(seconds=0)
    _tzname = 'UTC'

Universal = Universal() # Singleton

