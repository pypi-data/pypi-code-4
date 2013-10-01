'''
tzinfo timezone information for Etc/UTC.

Generated from the Olson timezone database:
    ftp://elsie.nci.nih.gov/pub/tz*.tar.gz
'''

from pytz.tzinfo import StaticTzInfo
from pytz.tzinfo import memorized_timedelta as timedelta

class UTC(StaticTzInfo):
    '''Etc/UTC timezone definition. See datetime.tzinfo for details'''
    _zone = 'Etc/UTC'
    _utcoffset = timedelta(seconds=0)
    _tzname = 'UTC'

UTC = UTC() # Singleton

