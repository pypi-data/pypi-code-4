#coding:utf-8
import re
class Route(object):
    def __init__(self):
        self.map = []

    def match(self, url):
        for r, f in self.map:
            m = r.match(url)
            if m:
                return f, m.groups()
        return None, None

    def __call__(self, path):
        if not path.endswith('$'):
            path += '$'
        re_path = re.compile(path)
        def _(func):
            self.map.append((re_path, func))
            return func
        return _

route = Route()