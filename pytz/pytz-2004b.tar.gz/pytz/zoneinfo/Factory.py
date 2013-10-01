'''tzinfo timezone information for Factory.'''
from pytz.tzinfo import StaticTzInfo
from pytz.tzinfo import memorized_timedelta as timedelta

class Factory(StaticTzInfo):
    '''Factory timezone definition. See datetime.tzinfo for details'''
    _zone = 'Factory'
    _utcoffset = timedelta(seconds=0)
    _tzname = 'Local time zone must be set--see zic manual page'

Factory = Factory()

