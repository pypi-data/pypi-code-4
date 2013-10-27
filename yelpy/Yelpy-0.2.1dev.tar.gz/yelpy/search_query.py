import urllib

from yelpy_objects import YelpyList

class SearchQuery(dict):

    SERVER_URL = "http://api.yelp.com/v2/search?"

    def __init__(self, **kwargs):
        super(SearchQuery, self).__init__()
        for key, val in kwargs.iteritems():
            self[key] = val

    def normalize(self, value):
        if isinstance(value, list):
            return YelpyList(value)
        return value

    def to_url(self):
        params = dict((key, self.normalize(value)) for key, value in self.iteritems() if value != None)
        return "{0}{1}".format(self.SERVER_URL, urllib.urlencode(params))
