'''
tzinfo timezone information for Etc/GMT_minus_8.

Generated from the Olson timezone database:
    ftp://elsie.nci.nih.gov/pub/tz*.tar.gz
'''

from pytz.tzinfo import StaticTzInfo
from pytz.tzinfo import memorized_timedelta as timedelta

class GMT_minus_8(StaticTzInfo):
    '''Etc/GMT_minus_8 timezone definition. See datetime.tzinfo for details'''
    _zone = 'Etc/GMT_minus_8'
    _utcoffset = timedelta(seconds=28800)
    _tzname = 'GMT-8'

GMT_minus_8 = GMT_minus_8() # Singleton

