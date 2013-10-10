# -*- coding: utf-8 -*-
from django.utils import simplejson
from fcdjangoutils.jsonview import *

# View decorators to automate some common view tasks:

def cookie_view(fn):
    """Views that uses request.GET['cookie']. Views can set elements
in the cookie object, and they will be updated on the client.
    """
    def withcookie(request, *arg, **kw):
        cookie_str = "{}"
        if 'cookie' in request.GET:
            cookie_str = request.GET['cookie']
        cookie = simplejson.loads(cookie_str)
        res = fn(request, cookie=cookie, *arg, **kw)
        if res is None:
            res = {}
        new_cookie_str = simplejson.dumps(cookie, sort_keys=True, default=jsonify_models)
        if new_cookie_str != cookie_str:
            res['cookie'] = new_cookie_str
        return res
    return withcookie
