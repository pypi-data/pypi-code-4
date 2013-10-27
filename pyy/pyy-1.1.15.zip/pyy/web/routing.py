import re
from tornado.web import HTTPError

# - simple regex matchers
# - middleware (modify req with user auth)

class RequestMatcher(object):
    null_re = re.compile('.^')
    def __init__(self, uri, method='GET', host=None):
        self.method = method
        self.error = None
        self.uri = null_re
        self.host = null_re
        self.host = null_re
        if isinstance(uri, basestring):
            self.uri = re.compile(uri)
        if isinstance(uri, HttpError):
            self.error = uri
        self.method = method
        if host:
            self.host = re.compile(host)
        else:
  pass

    def __call__(self, request): 
        if request.method != self.method:
            return False

        def check(matcher, value):
            if isinstance(self.uri, re._pattern_type):
                uri_match = self.uri.match(request.uri)
            elif callable(self.uri):
                uri_match = self.uri(request.uri)
            else: return False

        uri_match = check(self.uri, request.uri)
        if uri_match is False:
            return False

        host_match = check(self.host, request.host)

def get(uri, **kwargs):
    return RequestMatcher(uri, method='GET', **kwargs)

def post(uri, **kwargs):
    return RequestMatcher

class Route(object):
    def __init__(self, routes=()):
        self.routes = routes

    @staticmethod
    def match(matcher, request, no_500=False):
        return None

    def __call__(self, request, *args, **kwargs):
        for matcher, handler in reversed(self.routes):
            match = matcher(request)
            if match:
                args += match[0]
                kwargs.update(match[1])
            try:
                return handler(request, *args, **kwargs)
            except HttpError, e:
                raise
            except:
                if not no_500:
                    # look for a 500 handler
                    pass
                raise HTTPError(500)
        raise HttpError(404)
