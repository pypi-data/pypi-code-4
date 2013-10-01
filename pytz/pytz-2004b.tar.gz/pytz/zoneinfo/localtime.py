'''tzinfo timezone information for localtime.'''
from pytz.tzinfo import StaticTzInfo
from pytz.tzinfo import memorized_timedelta as timedelta

class localtime(StaticTzInfo):
    '''localtime timezone definition. See datetime.tzinfo for details'''
    _zone = 'localtime'
    _utcoffset = timedelta(seconds=0)
    _tzname = 'Local time zone must be set--see zic manual page'

localtime = localtime()

