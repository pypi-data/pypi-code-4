from datetime import datetime
from utils import *

class WorkingHoursDateTime(datetime):
    def to_datetime(self):
        return datetime(year=self.year, month=self.month,
            day=self.day, hour=self.hour, minute=self.minute,
            second=self.second, microsecond=self.microsecond,
            tzinfo=self.tzinfo)

    @classmethod
    def from_datetime(cls, dt):
        return WorkingHoursDateTime(year=dt.year, month=dt.month, day=dt.day,
            hour=dt.hour, minute=dt.minute, second=dt.second,
            microsecond=dt.microsecond, tzinfo=dt.tzinfo)

    def __add__(self, x):
        if type(x) == timedelta:
            dt = add_workhours(self.to_datetime(), x.total_seconds()/3600)
            return WorkingHoursDateTime.from_datetime(dt)

        return super(WorkingHoursDateTime, self).__add__(x)

    def __sub__(self, x):
        if type(x) == timedelta:
            dt = subtract_workhours(self.to_datetime(), x.total_seconds()/3600)
            return WorkingHoursDateTime.from_datetime(dt)
        elif type(x) == datetime:
            return time_between(self.to_datetime(), x)
        elif type(x) == WorkingHoursDateTime:
            return time_between(self.to_datetime(), x.to_datetime())
            
        return super(WorkingHoursDateTime, self).__sub__(x)

    @classmethod
    def now(cls):
        now = super(WorkingHoursDateTime, cls).now()
        return WorkingHoursDateTime.from_datetime(now)
