#coding: utf-8
import Cheetah.Template
import datetime
from utils import N
import format

class template(Cheetah.Template.Template):
    "扩展函数/属性的模板"

    def __init__(self, app, *args, **kwargs):
        from app import BaseApp
        assert isinstance(app, BaseApp)

        Cheetah.Template.Template.__init__(self, *args, **kwargs)

        self._app = app
        self._response = app.response
        self._request = app.request

        # URL & ABSOLUTE URL
        pi = app.env.get('PATH_INFO', '')
        if not pi.startswith("/"): pi="/%s" % pi
        self.url = pi
        if pi!="/":
            self.aurl = "http://%s%s" % (app.env.get("HOST"), pi)
        else:
            self.aurl = "http://%s" % app.env.get("HOST")
        self.querystring = app.env.get("QUERY_STRING","")

        self.today = datetime.date.today()


    def _get_app(self): return self._app
    app = property(_get_app)

    def _get_response(self): return self._response
    response = property(_get_response)

    def _get_request(self): return self._request
    resquest = property(_get_request)


    def N(self, *args, **kwargs):
        return N(*args, **kwargs)

    def format_date(self, d, fmt='y-m-d'):
        return format.format_date(d, fmt=fmt)

    def format_number(self, val, decimal=2, comma=True, cur="", verbose=None):
        #if cur!="":
        #    if not isinstance(cur, Currency):
        #        cur = Currency.get_instance(self.ctx, cur)
        #        if cur==None: cur=""
        return format.format_number(val, decimal=decimal, comma=comma, cur=cur, verbose=verbose)

