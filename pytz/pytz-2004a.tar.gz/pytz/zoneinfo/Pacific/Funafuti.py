'''
tzinfo timezone information for Pacific/Funafuti.

Generated from the Olson timezone database:
    ftp://elsie.nci.nih.gov/pub/tz*.tar.gz
'''

from pytz.tzinfo import StaticTzInfo
from pytz.tzinfo import memorized_timedelta as timedelta

class Funafuti(StaticTzInfo):
    '''Pacific/Funafuti timezone definition. See datetime.tzinfo for details'''
    _zone = 'Pacific/Funafuti'
    _utcoffset = timedelta(seconds=43200)
    _tzname = 'TVT'

Funafuti = Funafuti() # Singleton

