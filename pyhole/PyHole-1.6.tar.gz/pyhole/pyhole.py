import urllib2
import urllib
from copy import copy

class PyHole(object):

    def __init__(self, url, path=None, params=None, user_agent="PyHole",
                 timeout=10, opener=None, force_slash=False, extra_headers=None):
        if not url:
            raise ValueError('PyHole url cannot be empty')

        if params is None: params = {}
        if path is None: path = []
        if extra_headers is None: extra_headers = {}

        # To avoid namespace clashing with __gettattr__ attributes used for internal data starts with an _underscore
        self._extra_headers = extra_headers
        self._url = url
        self._params = params
        self._path = path
        self._user_agent = user_agent
        self._headers = { 'User-Agent' : self._user_agent }
        self._timeout = timeout
        self._force_slash = force_slash
        if self._force_slash:
            self._trailing_slash = '/'
        else:
            self._trailing_slash = ''

        if opener is None:
            self._opener = self.get_opener()
        else:
            self._opener = opener

    def _copy(self):
        '''Return a copy of itself for lazy url building'''
        return self.__class__(url=copy(self._url),
                        path=copy(self._path),
                        params=copy(self._params),
                        user_agent=copy(self._user_agent),
                        timeout=self._timeout,
                        opener=self._opener,
                        force_slash=self._force_slash,
                )
    def get_opener(self):
        return urllib2.build_opener(urllib2.HTTPCookieProcessor())

    def get_response_wrapper(self):
        '''Hook for processing response with custom function (e.g. yaml.load). Possibly you want to inherit and override this method'''
        return lambda x: x

    def get_http_headers(self):
        '''Return dics of HTTP headers'''
        headers = self._headers.copy()
        headers.update(self._extra_headers)
        return headers

    # Lazy URL building
    
    def __getattr__(self, name):
        copy = self._copy()
        copy._path.append(name)
        return copy

    def __call__(self, *args, **kwargs):
        copy = self._copy()
        copy._params.update(kwargs)
        for arg in args:
            if type(arg) is dict:
                copy._params.update(arg)
            else:
                copy._path.append(arg)
        
        return copy

    def __getitem__(self, item):
        copy = self._copy()
        copy._path.append(item)
        return copy
    
    # Creating URL
    def __makeurl__ (self):
        '''Creates full url from self'''
        url = copy(self._url)
        if self._path and self._url[-1] != '/':
            url += '/'
            
        url += '/'.join(map(lambda x: urllib2.quote(str(x), '~'), self._path))
        
        if not url[-1] == '/':
            url += self._trailing_slash
            
        if self._params:
            url += '?%s' % urllib.urlencode(self._params)
        #return self._url + ('/' if self._path and self._url[-1] != '/' else '') + '/'.join(map(lambda x: urllib2.quote(str(x), '~'), self._path)) + ('' if not self._path and self._url[-1] == '/' else self._trailing_slash) + ('?' + urllib.urlencode(self._params.items()) if self._params else '')
        return url
    # Making HTTP Post or Get
    def _get(self):
        '''Raw fetching GET request through urllib'''
        return self.__connect__(urllib2.Request(self.__makeurl__(), headers=self.get_http_headers()))


    def _post(self, data=None):
        '''Raw fetching POST request with data through urllib'''
        if data is None: data = {}
        return self.__connect__(urllib2.Request(self.__makeurl__(), data=urllib.urlencode(data), headers=self.get_http_headers()))
    
    def _put(self, data=None):
        '''Raw fetching PUT request with data through urllib'''
        if data is None: data = {}
        request = urllib2.Request(self.__makeurl__(), data=urllib.urlencode(data), headers=self.get_http_headers())
        request.get_method = lambda:'PUT'
        return self.__connect__(request)

    def _delete(self, data=None):
        '''Raw fetching DELETE request with data through urllib'''
        if data is None: data = {}
        request = urllib2.Request(self.__makeurl__(), data=urllib.urlencode(data), headers=self.get_http_headers())
        request.get_method = lambda:'DELETE'
        return self.__connect__(request)


    def _wrap_call(self, response, response_wrapper=None):
        '''Hook for wrapping response with possible conversion wrapper (e.g. yaml.load)'''
        return response_wrapper(response)    
    
    def get(self):
        '''Fetch with GET and process response with wrapper'''
        return self._wrap_call(self._get(), self.get_response_wrapper())


    def post(self, data=None):
        '''Fetch with POST and process response with wrapper'''
        if data is None: data = {}
        return self._wrap_call(self._post(data=data), self.get_response_wrapper())
    
    def put(self, data=None):
        '''Fetch with PUT and process response with wrapper'''
        if data is None: data = {}
        return self._wrap_call(self._put(data=data), self.get_response_wrapper())
    
    def delete(self, data=None):
        '''Fetch with DELETE and process response with wrapper'''
        if data is None: data = {}
        return self._wrap_call(self._delete(data=data), self.get_response_wrapper())
    
    # Connection layer
    def __connect__(self, request):
        '''Raw connecting and response fetching facility'''
        result = self._opener.open(request)#,  timeout=self._timeout)
        body = result.read()
        result.close()
        return body
        
    # Conversion to string
    def __str__(self):
        return self.__makeurl__().encode('ascii')

    def __unicode__(self):
        return self.__makeurl__()

    def __repr__(self):
        return self.__str__()
        
if __name__ == '__main__':
    a = PyHole('http://a')        
    print a.url
    print a._test
    print a.__test
