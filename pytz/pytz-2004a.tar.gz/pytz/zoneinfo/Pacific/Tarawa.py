'''
tzinfo timezone information for Pacific/Tarawa.

Generated from the Olson timezone database:
    ftp://elsie.nci.nih.gov/pub/tz*.tar.gz
'''

from pytz.tzinfo import StaticTzInfo
from pytz.tzinfo import memorized_timedelta as timedelta

class Tarawa(StaticTzInfo):
    '''Pacific/Tarawa timezone definition. See datetime.tzinfo for details'''
    _zone = 'Pacific/Tarawa'
    _utcoffset = timedelta(seconds=43200)
    _tzname = 'GILT'

Tarawa = Tarawa() # Singleton

