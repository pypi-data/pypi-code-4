'''
tzinfo timezone information for Etc/GMT_minus_12.

Generated from the Olson timezone database:
    ftp://elsie.nci.nih.gov/pub/tz*.tar.gz
'''

from pytz.tzinfo import StaticTzInfo
from pytz.tzinfo import memorized_timedelta as timedelta

class GMT_minus_12(StaticTzInfo):
    '''Etc/GMT_minus_12 timezone definition. See datetime.tzinfo for details'''
    _zone = 'Etc/GMT_minus_12'
    _utcoffset = timedelta(seconds=43200)
    _tzname = 'GMT-12'

GMT_minus_12 = GMT_minus_12() # Singleton

