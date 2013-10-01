'''
tzinfo timezone information for GMT.

Generated from the Olson timezone database:
    ftp://elsie.nci.nih.gov/pub/tz*.tar.gz
'''

from pytz.tzinfo import StaticTzInfo
from pytz.tzinfo import memorized_timedelta as timedelta

class GMT(StaticTzInfo):
    '''GMT timezone definition. See datetime.tzinfo for details'''
    _zone = 'GMT'
    _utcoffset = timedelta(seconds=0)
    _tzname = 'GMT'

GMT = GMT() # Singleton

