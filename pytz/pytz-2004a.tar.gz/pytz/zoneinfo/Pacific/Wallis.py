'''
tzinfo timezone information for Pacific/Wallis.

Generated from the Olson timezone database:
    ftp://elsie.nci.nih.gov/pub/tz*.tar.gz
'''

from pytz.tzinfo import StaticTzInfo
from pytz.tzinfo import memorized_timedelta as timedelta

class Wallis(StaticTzInfo):
    '''Pacific/Wallis timezone definition. See datetime.tzinfo for details'''
    _zone = 'Pacific/Wallis'
    _utcoffset = timedelta(seconds=43200)
    _tzname = 'WFT'

Wallis = Wallis() # Singleton

