"""
"""

from wheezy.core.collections import attrdict
from wheezy.core.collections import defaultdict
from wheezy.core.comp import Decimal
from wheezy.core.comp import HTTPConnection
from wheezy.core.comp import HTTPSConnection
from wheezy.core.comp import SimpleCookie
from wheezy.core.comp import json_loads
from wheezy.core.comp import urlencode
from wheezy.core.comp import urljoin
from wheezy.core.comp import urlsplit
from wheezy.core.gzip import decompress


class HTTPClient(object):
    """ HTTP client sends HTTP requests to server in order to accomplish
        an application specific use cases, e.g. remote web server API, etc.
    """

    def __init__(self, url, headers=None):
        """
            `url` - a base url for interaction with remote server.
            `headers` - a dictionary of headers.
        """
        scheme, netloc, path, query, fragment = urlsplit(url)
        http_class = scheme == 'http' and HTTPConnection or HTTPSConnection
        self.connection = http_class(netloc)
        self.default_headers = headers and headers or {}
        self.default_headers['Accept-Encoding'] = 'gzip'
        self.path = path
        self.method = None
        self.headers = None
        self.cookies = {}
        self.etags = {}
        self.status_code = 0
        self.body = None
        self.__content = None
        self.__json = None

    @property
    def content(self):
        """ Returns a content of the response.
        """
        if self.__content is None:
            self.__content = self.body.decode('utf-8')
        return self.__content

    @property
    def json(self):
        """ Returns a json response.
        """
        if self.__json is None:
            assert 'application/json' in self.headers['content-type'][0]
            self.__json = json_loads(self.content,
                                     object_hook=attrdict,
                                     parse_float=Decimal)
        return self.__json

    def get(self, path, **kwargs):
        """ Sends GET HTTP request.
        """
        return self.go(path, 'GET', **kwargs)

    def ajax_get(self, path, **kwargs):
        """ Sends GET HTTP AJAX request.
        """
        return self.ajax_go(path, 'GET', **kwargs)

    def head(self, path, **kwargs):
        """ Sends HEAD HTTP request.
        """
        return self.go(path, 'HEAD', **kwargs)

    def post(self, path, **kwargs):
        """ Sends POST HTTP request.
        """
        return self.go(path, 'POST', **kwargs)

    def ajax_post(self, path, **kwargs):
        """ Sends POST HTTP AJAX request.
        """
        return self.ajax_go(path, 'POST', **kwargs)

    def follow(self):
        """ Follows HTTP redirect (e.g. status code 302).
        """
        sc = self.status_code
        assert sc in [207, 301, 302, 303, 307]
        location = self.headers['location'][0]
        scheme, netloc, path, query, fragment = urlsplit(location)
        method = sc == 307 and self.method or 'GET'
        return self.go(path, method)

    def ajax_go(self, path=None, method='GET', params=None, headers=None):
        """ Sends HTTP AJAX request to web server.
        """
        headers = headers or {}
        headers['X-Requested-With'] = 'XMLHttpRequest'
        return self.go(path, method, params, headers)

    def go(self, path=None, method='GET', params=None, headers=None):
        """ Sends HTTP request to web server.
        """
        self.method = method
        headers = headers and dict(self.default_headers,
                                   **headers) or dict(self.default_headers)
        if self.cookies:
            headers['Cookie'] = '; '.join(
                '%s=%s' % cookie for cookie in self.cookies.items())
        path = urljoin(self.path, path)
        if path in self.etags:
            headers['If-None-Match'] = self.etags[path]
        body = ''
        if params:
            if method == 'GET':
                path += '?' + urlencode(params, doseq=True)
            else:
                body = urlencode(params, doseq=True)
                headers['Content-Type'] = 'application/x-www-form-urlencoded'

        self.status_code = 0
        self.body = None
        self.__content = None
        self.__json = None

        self.connection.connect()
        self.connection.request(method, path, body, headers)
        r = self.connection.getresponse()
        self.body = r.read()
        self.connection.close()

        self.status_code = r.status
        self.headers = defaultdict(list)
        for name, value in r.getheaders():
            self.headers[name].append(value)

        self.process_content_encoding()
        self.process_etag(path)
        self.process_cookies()
        return self.status_code

    # region: internal details

    def process_content_encoding(self):
        if 'content-encoding' in self.headers \
                and 'gzip' in self.headers['content-encoding']:
            self.body = decompress(self.body)

    def process_etag(self, path):
        if 'etag' in self.headers:
            self.etags[path] = self.headers['etag'][-1]

    def process_cookies(self):
        if 'set-cookie' in self.headers:
            for cookie_string in self.headers['set-cookie']:
                cookies = SimpleCookie(cookie_string)
                for name in cookies:
                    value = cookies[name].value
                    if value:
                        self.cookies[name] = value
                    elif name in self.cookies:
                        del self.cookies[name]
