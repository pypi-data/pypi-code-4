import datetime

def format(obj):
    if isinstance(obj, datetime.datetime):
        return format_datetime(obj)
    if isinstance(obj, datetime.timedelta):
        return format_timedelta(obj)
    if isinstance(obj, datetime.time):
        return format_time(obj)
    if isinstance(obj, datetime.date):
        return format_date(obj)

def format_datetime(obj):
    return format_date(obj) + 'T' + format_time(obj)

def format_date(obj):
    return obj.strftime("%Y-%m-%d")

def format_time(obj):
    return obj.strftime("%H:%M:%S")

def format_timedelta(obj):
    parts = ["P"]
    if obj.days / 7:
        parts.append(str(obj.days / 7) + "W")
        obj -= datetime.timedelta(days=7 * (obj.days / 7))
    if obj.days:
        parts.append(str(obj.days) + "D")
        obj -= datetime.timedelta(days=obj.days)
    if obj.seconds:
        parts.append("T")
        if obj.seconds / 3600:
            parts.append(str(obj.seconds / 3600) + "H")
            obj -= datetime.timedelta(seconds=3600 * (obj.seconds / 3600))
        if obj.seconds / 60:
            parts.append(str(obj.seconds / 60) + "M")
            obj -= datetime.timedelta(seconds=60 * (obj.seconds / 60))
        if obj.seconds:
            parts.append(str(obj.seconds) + "S")
    
    return "".join(parts)