#coding: utf-8
import mimetypes
from UserDict import IterableUserDict
import Cheetah.Template
import logging, os, copy, Cookie

class HttpResponse(IterableUserDict):
    "HTTP响应"

    def __init__(self):
        IterableUserDict.__init__(self)
        self.status = 200
        self.headers = {}
        self.cookies = {}

    def set_status(self, status):
        self.status = status

    def set_header(self, name, value):
        self.headers[name.lower()] = value

    def set_cookie(self, key, value):
        self.cookies[key] = value
        cc = Cookie.SimpleCookie()
        cc[key] = value
        self.set_header("set-cookie", cc.output().split(":")[-1].strip())
        logging.info("set-cookie: %s" % cc.output().split(":")[-1].strip())


    def set_data(self, key, val):
        self.data[key] = val

    def file(self, filename, sio):
        "返回文件结果"
        ctype, enc = mimetypes.guess_type(path)
        if ctype==None or enc!=None:
            ctype = "application/octet-stream"

        self.set_header("content-type", ctype)
        # import urllib
        # self.add_header("Content-Disposition", "attachment;%s;charset=utf-8" % urllib.urlencode({"filename":filename}))
        self.set_header("content-disposition", "attachment;filename=%s;charset=utf-8" % filename)
        self.set_header("content-length", sio.len)
        return sio

