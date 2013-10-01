'''
tzinfo timezone information for Etc/GMT_minus_14.

Generated from the Olson timezone database:
    ftp://elsie.nci.nih.gov/pub/tz*.tar.gz
'''

from pytz.tzinfo import StaticTzInfo
from pytz.tzinfo import memorized_timedelta as timedelta

class GMT_minus_14(StaticTzInfo):
    '''Etc/GMT_minus_14 timezone definition. See datetime.tzinfo for details'''
    _zone = 'Etc/GMT_minus_14'
    _utcoffset = timedelta(seconds=50400)
    _tzname = 'GMT-14'

GMT_minus_14 = GMT_minus_14() # Singleton

