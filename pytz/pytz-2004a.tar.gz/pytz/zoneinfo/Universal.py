'''
tzinfo timezone information for Universal.

Generated from the Olson timezone database:
    ftp://elsie.nci.nih.gov/pub/tz*.tar.gz
'''

from pytz.tzinfo import StaticTzInfo
from pytz.tzinfo import memorized_timedelta as timedelta

class Universal(StaticTzInfo):
    '''Universal timezone definition. See datetime.tzinfo for details'''
    _zone = 'Universal'
    _utcoffset = timedelta(seconds=0)
    _tzname = 'UTC'

Universal = Universal() # Singleton

