from datetime import timedelta

def is_weekday(d):
    return d.weekday()<5

def next_midnight(d):
    return (d + timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)

def previous_midnight(d):
    midnight = d.replace(hour=0, minute=0, second=0, microsecond=0)
    if d == midnight:
        midnight -= timedelta(days=1)

    return midnight

def add_workhours(dt, hours):
    hours_remaining = hours

    while hours_remaining >=0:
        if is_weekday(dt):
            time_until_next_midnight = next_midnight(dt) - dt
            hours_unitl_next_midnight = time_until_next_midnight.total_seconds()/3600

            if hours_remaining >= hours_unitl_next_midnight:
                hours_remaining -= hours_unitl_next_midnight

                dt += time_until_next_midnight
            else:
                return dt + timedelta(hours=hours_remaining)
        else:
            dt = next_midnight(dt)


def subtract_workhours(dt, hours):
    if not is_weekday(dt):
        dt = previous_midnight(dt)
    
    hours_remaining = hours

    while hours_remaining > 0:
        if is_weekday(previous_midnight(dt)):
            time_to_previous_midnight = dt - previous_midnight(dt)
            hours_to_previous_midnight = time_to_previous_midnight.total_seconds()/3600

            if hours_remaining >= hours_to_previous_midnight:
                hours_remaining -= hours_to_previous_midnight

                dt -= time_to_previous_midnight
            else:
                result = dt - timedelta(hours=hours_remaining)
                while not is_weekday(result):
                    result -= timedelta(days=1)
                return result
        else:
            dt = previous_midnight(dt)
    return dt


def time_between(dt1, dt2):
    """ Respects working hours """

    invert = True
    if dt1>dt2:
        invert = False
        dt1, dt2 = dt2, dt1
    

    # builds an array: [start_date, <all the midnights between>, end_date]    
    dates = [dt1]
    for n in range((dt2-dt1).days):
        next_midnight = (dt1 + timedelta(days=(n+1))).replace(hour=0, minute=0, second=0, microsecond=0)
        dates.append(next_midnight)
    dates.append(dt2)

    # accumulates the differences between the elements if it is a workday
    delta = timedelta(seconds=0)
    for i,d in enumerate(dates[:-1]):
        if is_weekday(dates[i]):
            delta += dates[i+1] - dates[i]

    if invert:
        delta = timedelta(days=-1*delta.days, seconds=-1*delta.seconds, microseconds=-1*delta.microseconds)
    return delta
