#coding: utf-8
from wae.config import config
from wae.httprequest import HttpRequest
from wae.httpresponse import HttpResponse
import wae.connect
from session import Session
from wsgiref.util import FileWrapper
import Cheetah.Template
import types, logging
import os, sys, traceback
import template
from wae.utils import exposed, delegate


class BaseApp(object):
    "应用程序基类"
    def __init__(self, env, request, response, session):
        assert isinstance(request, HttpRequest)
        assert isinstance(response, HttpResponse)
        if session!=None:
            assert isinstance(session, Session)

        self.env = env
        self.request = request
        self.response = response
        self.session = session

        self.errmsg = "Runtime Error"


    def initialize(self):
        """运行之前"""
        pass

    def finalize(self):
        """运行结束"""
        pass

    def abort(self):
        """运行发生异常而终止"""
        pass


    def get_templates(self, name, dirmap):
        "按继承次序关系返回模板"
        lst = []
        for c in type.mro(type(self)):
            if c in dirmap:
                lst.append("%s/%s" % (dirmap[c],name))
        return lst

    def render_template(self, tmpl, dirmap={}):
        """渲染模板"""
        tmpls = self.get_templates(tmpl, dirmap)
        for t in tmpls:
            fn = "%s.tmpl" % t
            if os.path.exists(fn) and not os.path.isdir(fn):
                fh = open(fn)
                text = fh.read()
                fh.close()
                text = "#encoding utf-8\n%s" % text

                try:
                    tclass = Cheetah.Template.Template.compile(source=text, baseclass=template.template)
                    return tclass(self, searchList=[{"resp":self.response}])

                except:
                    from middleware import logging_exc
                    logging_exc(self.env, message="template=%s" % fn)
                    self.response.set_status(500)
                    return "<h1>Render Error</h1>"

        logging.error("PATH_INFO: %s\n" % self.env.get("PATH_INFO",""))
        logging.error("QUERY_STRING: %s\n" % self.env.get("QUERY_STRING",""))
        logging.error("cannot load any of template: %s" % ", ".join(tmpls))
        return "No template"


    @classmethod
    def load_class(cls, entry, filename, classname):
        """加载下级类"""
        text = cls.meta.loadrc("%s.py" % filename)
        text += "\n"

        ae = {}
        exec text in ae

        o = ae[classname]
        o.meta = cls.meta
        o.pathinfo = "%s/%s" % (cls.pathinfo, entry)
        if cls.prefix=="":
            o.prefix = entry
        else:
            o.prefix = "%s/%s" % (cls.prefix, entry)
        return o

