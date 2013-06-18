__all__ = ('random_datetime', 'random_date', 'random_time')

import datetime
from random import randint

try:
    from dateutil.parser import parse
except:
    from radar.utils import parse

from radar.utils import gettext as _
from radar.exceptions import InvalidDateRange

def random_datetime(start=None, stop=None):
    """
    Generates a random ``datetime.datetime`` or ``datetime.date`` object from ranges given.

    :param mixed start: Can be either a ``datetime.datetime`` or a ``str``. Defaults to 1970-01-01.
    :param mixed end: Can be either a ``datetime.datetime`` or a ``str``. Defaults to ``datetime.datetime.now``.
    :return datetime.datetime:
    """
    if start is not None:
        assert isinstance(start, (datetime.datetime, datetime.date, str))
        if isinstance(start, str):
            start = parse(start)
    else:
        start = datetime.datetime(year=1979, month=1, day=1)

    if stop is not None:
        assert isinstance(stop, (datetime.datetime, datetime.date, str))

        if isinstance(stop, str):
            stop = parse(stop)
    else:
        stop = datetime.datetime.now()

    if start > stop:
        raise InvalidDateRange(_("Invalid date range: ``start`` should not be greater than ``stop``."))

    random_datetime = start + datetime.timedelta(seconds=randint(0, int((stop - start).total_seconds())))

    return random_datetime

def random_date(start=None, stop=None):
    """
    Generates a random ``datetime.date`` object from ranges given.

    :param mixed start: Can be either a ``datetime.datetime`` or a ``str``.
    :param mixed end: Can be either a ``datetime.datetime`` or a ``str``.
    :return datetime.date:
    """
    d = random_datetime(start=start, stop=stop)
    return d.date()

def random_time(start=None, stop=None):
    """
    Generates a random ``datetime.time`` object from ranges given.

    :param mixed start: Can be either a ``datetime.datetime`` or a ``str``.
    :param mixed end: Can be either a ``datetime.datetime`` or a ``str``.
    :return datetime.time:
    """
    d = random_datetime(start=start, stop=stop)
    return d.time()
