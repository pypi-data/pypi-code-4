'''
tzinfo timezone information for Pacific/Palau.

Generated from the Olson timezone database:
    ftp://elsie.nci.nih.gov/pub/tz*.tar.gz
'''

from pytz.tzinfo import StaticTzInfo
from pytz.tzinfo import memorized_timedelta as timedelta

class Palau(StaticTzInfo):
    '''Pacific/Palau timezone definition. See datetime.tzinfo for details'''
    _zone = 'Pacific/Palau'
    _utcoffset = timedelta(seconds=32400)
    _tzname = 'PWT'

Palau = Palau() # Singleton

