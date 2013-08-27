import urllib2
import urllib

__all__ = ('Request')


class Request(object):
    def __init__(self, url, query_data, body, headers={}):
        self.url = url
        self.query_data = query_data
        self.body = body
        self.headers = headers

    def get_full_url(self):
        if not self.query_data:
            return self.url
        return self.url + '?' + urllib.urlencode(self.query_data)

    def get(self):
        request = urllib2.Request(url=self.get_full_url(), headers=self.headers)
        response = urllib2.urlopen(request)
        return response.read()
    
    def post(self):
        if len(self.body.keys()) == 1:
            data = self.body[self.body.keys()[0]]
        else:
            data = urllib.urlencode(self.body)

        request = urllib2.Request(self.get_full_url(), data, self.headers)
        response = urllib2.urlopen(request)
        return response.read()
    
    def put(self):
        pass
    
    def delete(self):
        pass