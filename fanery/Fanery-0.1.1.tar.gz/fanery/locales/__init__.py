from fanery.terms import date, datetime
from dateutil import relativedelta

class relativedelta(relativedelta.relativedelta):

    def __init__(self, *args, **argd):
        self.workdays = argd.pop('workdays', 0)
        if self.workdays:
            assert self.workdays > 0, 'workdays must be int > 0'
            self.calendar = cal = argd.pop('calendar', None)
            assert cal, 'workdays requires calendar'
        super(relativedelta, self).__init__(*args, **argd)

    def __add__(self, other):
        if self.workdays and isinstance(other, date):
            from dateutil.rrule import rrule, DAILY
            if not isinstance(other, datetime):
                other = datetime.fromordinal(other.toordinal())
            years = set()
            holidays = set()
            cal = self.calendar
            days = self.workdays
            rrule = rrule(DAILY, byweekday = cal.WORKDAY, dtstart = other)
            for day in rrule:
                if day.year not in years:
                    holidays.update(d.date() for d in cal.holidays(day.year))
                    years.add(day.year)
                if day.date() in holidays:
                    continue
                elif days > 0:
                    days -= 1
                else:
                    return day
        else:
            return super(relativedelta, self).__add__(other)

def easter(year = None):
    # from https://en.wikipedia.org/wiki/Computus
    year = year or date.today().year
    a = year % 19
    b = year >> 2
    c = b // 25 + 1
    d = (c * 3) >> 2
    e = ((a * 19) - ((c * 8 + 5) // 25) + d + 15) % 30
    e += (29578 - a - e * 32) >> 10
    e -= ((year % 7) + b - d + e + 2) % 7
    d = e >> 5
    day = e - d * 31
    month = d + 3
    return datetime(year, month, day)

