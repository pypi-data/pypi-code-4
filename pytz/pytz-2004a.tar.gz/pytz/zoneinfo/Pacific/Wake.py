'''
tzinfo timezone information for Pacific/Wake.

Generated from the Olson timezone database:
    ftp://elsie.nci.nih.gov/pub/tz*.tar.gz
'''

from pytz.tzinfo import StaticTzInfo
from pytz.tzinfo import memorized_timedelta as timedelta

class Wake(StaticTzInfo):
    '''Pacific/Wake timezone definition. See datetime.tzinfo for details'''
    _zone = 'Pacific/Wake'
    _utcoffset = timedelta(seconds=43200)
    _tzname = 'WAKT'

Wake = Wake() # Singleton

