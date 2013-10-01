'''
tzinfo timezone information for Etc/GMT_minus_4.

Generated from the Olson timezone database:
    ftp://elsie.nci.nih.gov/pub/tz*.tar.gz
'''

from pytz.tzinfo import StaticTzInfo
from pytz.tzinfo import memorized_timedelta as timedelta

class GMT_minus_4(StaticTzInfo):
    '''Etc/GMT_minus_4 timezone definition. See datetime.tzinfo for details'''
    _zone = 'Etc/GMT_minus_4'
    _utcoffset = timedelta(seconds=14400)
    _tzname = 'GMT-4'

GMT_minus_4 = GMT_minus_4() # Singleton

