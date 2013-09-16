from flask import session
from datetime import datetime
import calendar
import requests

__all__ = ('SessionDescriptor', 'is_herokai', 'build_url', 'utc_timestamp',
           'herokai_only', 'build_requests_client', 'URLPatch')


class SessionDescriptor(object):

    def __init__(self, key, default=None):
        self.key = key
        self.default = default

    def __get__(self, obj, value):
        return session.get(self.key, self.default)

    def __set__(self, obj, value):
        session[self.key] = value


def is_herokai(email):
    return email.endswith("@heroku.com")


def build_url(path):
    return "https://api.heroku.com%s" % path


def utc_timestamp():
    d = datetime.utcnow()
    return calendar.timegm(d.utctimetuple())


def herokai_only(auth, f):
    f._herokai_only = True
    return f


class URLPatch(object):

    def __init__(self, session):
        self.session = session

    def get(self, url, **kwargs):
        url = build_url(url)
        return self.session.get(url, **kwargs)

    def post(self, url, **kwargs):
        url = build_url(url)
        return self.session.post(url, **kwargs)

    def put(self, url, **kwargs):
        url = build_url(url)
        return self.session.put(url, **kwargs)

    def patch(self, url, **kwargs):
        url = build_url(url)
        return self.session.patch(url, **kwargs)

    def delete(self, url, **kwargs):
        url = build_url(url)
        return self.session.delete(url, **kwargs)

    def options(self, url, **kwargs):
        url = build_url(url)
        return self.session.options(url, **kwargs)

    def head(self, url, **kwargs):
        url = build_url(url)
        return self.session.head(url, **kwargs)
