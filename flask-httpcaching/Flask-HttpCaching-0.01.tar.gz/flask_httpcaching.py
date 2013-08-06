# -*- coding: utf-8 -*-


from functools import wraps
from datetime import datetime, timedelta
from flask import request, Response


__version__ = '0.0.1'


_HTTP_DATE_FMT = '%a, %d %b %Y %H:%M:%S GMT'


def httpdate_to_datetime(s):
    return datetime.strptime(s, _HTTP_DATE_FMT)


def datetime_to_httpdate(d):
    return datetime.strftime(d, _HTTP_DATE_FMT)


def httpdate_now():
    return datetime_to_httpdate(datetime.utcnow())


def http_caching(timeout=200, expires=None):
    '''
    Usage: http_caching(300, 200)

    timeout: 304 timeout seconds
    expires: http cache expires seconds
    '''
    def run(func):
        @wraps(func)
        def decorator(*args, **kwargs):
            if_modified_since = request.headers.get('If-Modified-Since')
            if if_modified_since:
                timespan = datetime.utcnow() - httpdate_to_datetime(if_modified_since)
                if timespan.total_seconds() <= timeout:
                    return Response(status=304)
            headers = {
                    'Last-Modified': httpdate_now(),
                    }
            if expires:
                headers['Cache-Control'] = 'max-age=%s' % expires
                headers['Expires'] = datetime_to_httpdate(datetime.utcnow() + timedelta(seconds=expires))
            return Response(func(*args, **kwargs), headers=headers)
        return decorator
    return run
