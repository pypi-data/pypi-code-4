import datetime
import time


def first(dt = None):
    dt = dt or d()
    return datetime.datetime(dt.year, dt.month, 1)

def last(dt = None):
    dt = dt or d()
    return first(first(dt) + datetime.timedelta(35)) - datetime.timedelta(1)

def firstw(dt = None):
    dt = dt or d()
    return dt - datetime.timedelta(dt.isocalendar()[2] - 1)

def lastw(dt = None):
    dt = dt or d()
    return dt + datetime.timedelta(7 - dt.isocalendar()[2])

def addmonths(dt = None, months = 0):
    dt = dt or d()
    month = dt.month + months
    year = dt.year + (month / 12)
    month = month % 12
    return datetime.datetime(year, month, 1)

def d(datestr = None):
    if not datestr:
        return datetime.datetime.now()
    if ":" in datestr:
        return datetime.datetime.strptime(datestr, '%Y-%m-%d %H:%M:%S')
    return datetime.datetime.strptime(datestr, '%Y-%m-%d')

def decode_date(datestr, other=None):
    if not datestr: return None
    try:
        return d(datestr)
    except:
        return eval(datestr, {
                "__builtins__": {},
                "datetime": datetime,
                "time": time,
                "other": other,
                "d": d,
                "first": first,
                "last": last,
                "firstw": firstw,
                "lastw": "lastw",
                "addmonths": addmonths})

def decode_period(period):
    start, end = period.split("..")
    end = decode_date(end.strip())
    start = decode_date(start.strip(), end)

    if not start:
        if not end:
            end = datetime.datetime.now()
        start = end - datetime.interval(30)
    if not end:
        end = start + datetime.interval(30)
    return (start, end)



# Old API

def last_day_of_month(year, month):
    return last(datetime.date(year, month, 1))

def first_day_of_week(year, week):
    """
    Return a date object representing the first day of the specified week
    """
    start = datetime.date(year, 1, 7)
    nyear, nweek, nweekday = start.isocalendar()
    assert nyear == year
    return start + datetime.timedelta(7 * (week - nweek) - (nweekday - 1))

def last_day_of_week(year, week):
    """
    Return a date object representing the last day of the specified week
    """
    return first_day_of_week(year, week) + datetime.timedelta(6)
