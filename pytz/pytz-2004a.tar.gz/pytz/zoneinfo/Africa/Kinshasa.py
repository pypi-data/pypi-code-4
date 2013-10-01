'''
tzinfo timezone information for Africa/Kinshasa.

Generated from the Olson timezone database:
    ftp://elsie.nci.nih.gov/pub/tz*.tar.gz
'''

from pytz.tzinfo import StaticTzInfo
from pytz.tzinfo import memorized_timedelta as timedelta

class Kinshasa(StaticTzInfo):
    '''Africa/Kinshasa timezone definition. See datetime.tzinfo for details'''
    _zone = 'Africa/Kinshasa'
    _utcoffset = timedelta(seconds=3600)
    _tzname = 'WAT'

Kinshasa = Kinshasa() # Singleton

