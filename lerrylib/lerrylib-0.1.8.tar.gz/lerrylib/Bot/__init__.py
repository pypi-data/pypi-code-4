#coding:utf-8
from lerrylib.extract import extract, extract_all
try:
    from bot import bot
except:
    from _bot import bot
from route import route
from urlparse import urlparse, parse_qs

class Page(object):

    def __init__(self, req):
        p = urlparse(req.url)
        req.arguments = parse_qs(p.query, 1)
        self.req = req
        self.html = req.content

    def get_argument(self, name, default=None):
        result = self.req.arguments.get(name, None)
        if result is None:
            return default
        return result[0].encode('utf-8', 'ignore')

    def extract(self, begin, end):
        return extract(begin, end, self.html)

    def extract_all(self, begin, end):
        return extract_all(begin, end, self.html)
