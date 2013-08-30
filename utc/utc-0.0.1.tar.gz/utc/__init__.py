import datetime as dt


ZERO = dt.timedelta(0)


class UTC(dt.tzinfo):
    def tzname(self, dt):
        return "UTC"
    def utcoffset(self, dt):
        return ZERO
    def dst(self, dt):
        return ZERO
    def __repr__(self):
        return "<UTC>"    



def now():
    return dt.datetime.utcnow().replace(tzinfo=UTC())


def datetime(*args, **kwargs):
    kwargs['tzinfo'] = UTC()
    return dt.datetime(*args, **kwargs)


def time(*args, **kwargs):
    kwargs['tzinfo'] = UTC()
    return dt.time(*args, **kwargs)
