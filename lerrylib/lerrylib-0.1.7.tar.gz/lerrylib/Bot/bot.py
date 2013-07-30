#coding:utf-8
import _env
import gevent
import gevent.monkey
import requests
from gevent.queue import Empty, Queue
from urlparse import urlparse, parse_qs
from route import route
gevent.monkey.patch_all()

ua = 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.31 (KHTML, like Gecko) Chrome/26.0.1410.64 Safari/537.31'

class Bot(object):
    cookie = None
    headers = {}

    def __init__(self, route):
        self.queue = Queue()
        self.route = route

    def _fetch(self):
        queue = self.queue
        timeout = self.timeout
        route = self.route
        while True:
            try:
                url = queue.get(timeout=timeout+5)
            except Empty:
                return

            headers = self.headers

            if self.cookie:
                headers['Cookie'] = self.cookie
            headers['User-Agent'] = ua
            req = requests.get(url, timeout=timeout, headers=headers, proxies=self.proxies)
            p = urlparse(req.url)

            cls, args = route.match(p.path)
            if cls:
                o = cls(req)
                r = o.get(*args)
                if r:
                    for i in r:
                        if i:
                            queue.put(i)

    def run(self, num=10, timeout=60, proxies={}, cookie=None):
        self.proxies = proxies
        self.timeout = timeout
        self.cookie = cookie
        for i in xrange(num):
            g = gevent.spawn(self._fetch)
        g.join()

    def put(self, url):
        self.queue.put(url)


bot = Bot(route)