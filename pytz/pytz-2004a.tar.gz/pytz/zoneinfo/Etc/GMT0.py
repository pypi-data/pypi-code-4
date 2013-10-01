'''
tzinfo timezone information for Etc/GMT0.

Generated from the Olson timezone database:
    ftp://elsie.nci.nih.gov/pub/tz*.tar.gz
'''

from pytz.tzinfo import StaticTzInfo
from pytz.tzinfo import memorized_timedelta as timedelta

class GMT0(StaticTzInfo):
    '''Etc/GMT0 timezone definition. See datetime.tzinfo for details'''
    _zone = 'Etc/GMT0'
    _utcoffset = timedelta(seconds=0)
    _tzname = 'GMT'

GMT0 = GMT0() # Singleton

