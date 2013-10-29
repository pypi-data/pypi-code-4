#!/usr/bin/env python
# -*- coding: utf-8 -*-
# created: zhangpeng <zhangpeng@ivtime.com>

import os
from tornado.web import (RequestHandler, StaticFileHandler as _StaticFileHandler,
                         ErrorHandler as _ErrorHandler, HTTPError
                        )
from tornado.wsgi import HTTPRequest
from torweb.wrappers import cached_property
from torweb.sessions import SessionStore
from torweb.datastructure import MultiDict, ImmutableMultiDict
from code import interact

__all__ = ['BaseHandler', 'StaticFileHandler', 'ErrorHandler', 'XMLRPCHandler', 'JSONRPCHandler', 'WSGIRequest']


class BaseHandler(RequestHandler):
    def prepare(self):
        '''
        before request
        '''
        pass
        #print 'before request'
    @property
    def args(self):
        names = self.request.arguments.keys()
        arguments = {}
        for name in names:
            arguments[name] = self.get_argument(name)
        return arguments
    @property
    def query_args(self):
        cls = ImmutableMultiDict
        result = []
        keys = []
        querys = self.request.query
        querys = querys.split('&')
        for query_str in querys:
            if not query_str:continue
            if '=' in query_str:
                key, value = query_str.split('=')
            else:
                key = query_str; value = u''
            result.append((key, value.decode('utf-8', 'ignore')))
        return cls(result)
    def on_finish(self):
        '''
        after request
        '''
        pass
        #print 'finish'
    @cached_property
    def session(self):
        '''根据session_sid值来获取session对象，或者初始化一个session对象'''
        session_store = self.application.session_store
        sid = self.cookies.get('session_id')
        if sid is None:
            return session_store.new()
        else:
            return session_store.get(sid.value)

    def save_session(self):
        '''返回response之前，向客户端写入cookie
        保存session_sid到cookie
        '''
        try:
            self.set_cookie('session_id', self.session.sid, expires_days=3650)
        except AttributeError:
            pass
        if self.session.should_save:
            self.application.session_store.save(self.session)
    def write_jsonp(self, obj):
        key = self.get_argument("callback", u"jsonpcallback")
        try:
            from simplejson import dumps
        except:
            from json import dumps
        s = dumps(obj)
        self.set_header("Content-Type", "application/json")
        self.write(key+u'(' + s + u')')

class StaticFileHandler(_StaticFileHandler):
    static_handler = True

class ErrorHandler(_ErrorHandler): 
    """Generates an error response with status_code for all requests.""" 
    def __init__(self, application, request, status_code): 
        RequestHandler.__init__(self, application, request)
        self.set_status(status_code) 
    def initialize(self, app=None, request=None, status_code=404):
        self.app = app; self.status_code = status_code
    def prepare(self): 
        raise HTTPError(self._status_code)
#    def get_error_html(self, status_code, **kwargs): 
#        from ivtime import base_path
#        return open(os.path.join(base_path,'static', 'error','404.html')).read() 

def private(func):
    # Decorator to make a method, well, private.
    class PrivateMethod(object):
        def __init__(self):
            self.private = True
        __call__ = func
    return PrivateMethod()

class XMLRPCHandler(BaseHandler):
    def get(self):
        pass
    def post(self):
        import xmlrpclib
        try:
            params, method_name = xmlrpclib.loads(self.request.body)
        except:
            # Bad request formatting, bad.
            raise Exception('Deal with how you want.')
        if method_name in dir(RequestHandler):
            # Pre-existing, not an implemented attribute
            raise AttributeError('%s is not implemented.' % method_name)
        try:
            method = getattr(self, method_name)
        except:
            # Attribute doesn't exist
            raise AttributeError('%s is not a valid method.' % method_name)
        if not callable(method):
            # Not callable, so not a method
            raise Exception('Attribute %s is not a method.' % method_name)
        if method_name.startswith('_') or \
                ('private' in dir(method) and method.private is True):
            # No, no. That's private.
            raise Exception('Private function %s called.' % method_name)
        response = method(*params)
        response_xml = xmlrpclib.dumps((response,), methodresponse=True)
        self.set_header("Content-Type", "text/xml")
        self.write(response_xml)


class JSONRPCHandler(BaseHandler):
    def get(self, *args, **kwargs):
        return self.post()
    def post(self, *args, **kwargs):
        """
            JSON-RPC 2.0
            Request Object:
                {u'jsonrpc': u'2.0', u'params': [1, 2], u'id': u'3ebm619c', u'method': u'add'}
            Response Object:
                {"jsonrpc": "2.0", "result": 3, "id": "3ebm619c"}
        """
        import jsonrpclib
        try:
            json_request = jsonrpclib.loads(self.request.body)
            params = json_request.get("params", [])
            method_name = json_request.get("method", "")
        except:
            # Bad request formatting, bad.
            raise Exception('Deal with how you want.')
        if method_name in dir(RequestHandler):
            # Pre-existing, not an implemented attribute
            raise AttributeError('%s is not implemented.' % method_name)
        try:
            method = getattr(self, method_name)
        except:
            # Attribute doesn't exist
            raise AttributeError('%s is not a valid method.' % method_name)
        if not callable(method):
            # Not callable, so not a method
            raise Exception('Attribute %s is not a method.' % method_name)
        if method_name.startswith('_') or \
                ('private' in dir(method) and method.private is True):
            # No, no. That's private.
            raise Exception('Private function %s called.' % method_name)
        response = method(*params)
        response_json = jsonrpclib.dumps(response, methodresponse=True, rpcid=json_request["id"])
        self.set_header("Content-Type", "text/json")
        self.write(response_json)


class WSGIRequest(HTTPRequest):
    def __init__(self, env):
        #super(HTTPRequest, self).__init__(env)
        HTTPRequest.__init__(env)
        self.environ = env
