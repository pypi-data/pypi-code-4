#!/usr/bin/env python
# -*- coding: utf-8 -*-
# created: zhangpeng <zhangpeng@ivtime.com>

from code import interact

class Url(object):
    def __init__(self):
        self.handlers = []

    def __call__(self, url, **kwds):
        def _(cls):
            self.handlers.append((url, cls, kwds))
            return cls
        return _
url = Url()
except_url = Url()
