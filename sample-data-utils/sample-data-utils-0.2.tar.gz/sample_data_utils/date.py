import datetime
import time
import random
from dateutil.rrule import rrule, DAILY, weekdays


def date_to_timestamp(d):
    return int(time.mktime(d.timetuple()))


def date(start, end):
    """Get a random date between two dates"""

    stime = date_to_timestamp(start)
    etime = date_to_timestamp(end)

    ptime = stime + random.random() * (etime - stime)

    return datetime.date.fromtimestamp(ptime)


def day(start, end, weekday=weekdays):
    return random.choice(
        list(
            rrule(DAILY,
                  byweekday=weekday,
                  dtstart=start,
                  until=end)
        )
    ).date()
