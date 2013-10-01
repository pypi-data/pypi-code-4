'''
tzinfo timezone information for Greenwich.

Generated from the Olson timezone database:
    ftp://elsie.nci.nih.gov/pub/tz*.tar.gz
'''

from pytz.tzinfo import StaticTzInfo
from pytz.tzinfo import memorized_timedelta as timedelta

class Greenwich(StaticTzInfo):
    '''Greenwich timezone definition. See datetime.tzinfo for details'''
    _zone = 'Greenwich'
    _utcoffset = timedelta(seconds=0)
    _tzname = 'GMT'

Greenwich = Greenwich() # Singleton

