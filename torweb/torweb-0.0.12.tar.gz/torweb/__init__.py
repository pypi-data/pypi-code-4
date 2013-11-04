#!/usr/bin/env python
# -*- coding: utf-8 -*-
# created: zhangpeng <zhangpeng@ivtime.com>

import os
import re
import tornado.options
from tornado.web import (Application, RequestHandler, StaticFileHandler as _StaticFileHandler,
                         RedirectHandler, HTTPError)
import tornado.wsgi
from tornado.wsgi import WSGIApplication as _WSGIApplication
from torweb.urls import url
from torweb.config import Yaml_Config
#from torweb.handlers import StaticFileHandler, ErrorHandler, WSGIRequest
from torweb.handlers import StaticFileHandler, ErrorHandler
from code import interact
from os.path import abspath, dirname, join
base_path = abspath(dirname(__file__))
import sys
sys.path.insert(0, abspath(join(base_path, 'utils')))
sys.path.insert(0, abspath(join(base_path, 'lib')))

def get_modules(prefix, parent):
    if not os.path.isfile(os.path.join(parent, '__init__.py')):
        return
    for pathname in os.listdir(parent):
        child = os.path.join(parent, pathname)
        if pathname.startswith('.'):
            continue
        elif pathname == '__init__.py':
            yield '.'.join(prefix), pathname.split('.')[0]
        elif os.path.isdir(child):
            for i in get_modules(prefix+[pathname], child):
                yield i, pathname.split('.')[0]
        elif os.path.isfile(child) and pathname.endswith('.py'):
            yield '.'.join(prefix+[pathname[:-3]]), pathname.split('.')[0]


class WebApplication(Application):
    def __call__(self, request): 
        if request.path.endswith("/"):
            if request.method in ("GET", "HEAD"):
                uri = request.path.rstrip("/")
                if uri:  # don't try to redirect '/' to ''
                    if request.query:
                        uri += "?" + request.query
                    hdr = RedirectHandler(self, request, url=uri)
                    hdr._execute(transforms, *args, **kwargs)
                    return hdr
            else:
                raise HTTPError(404)
        super(WebApplication, self).__call__(request)
        #print """Called by HTTPServer to execute the request."""
        #print "##################################################"
        ##interact(local=locals())
        #transforms = [t(request) for t in self.transforms]
        #handler = None
        #args = []
        #kwargs = {}
        ## removeslash
        #
        #if request.path.endswith("/"):
        #    if request.method in ("GET", "HEAD"):
        #        uri = request.path.rstrip("/")
        #        if uri:  # don't try to redirect '/' to ''
        #            if request.query:
        #                uri += "?" + request.query
        #            hdr = RedirectHandler(self, request, url=uri)
        #            hdr._execute(transforms, *args, **kwargs)
        #            return hdr
        #    else:
        #        raise HTTPError(404)
        #
        ## addslash
        ##li = [_compile for _compile in self._static_urls if re.compile(_compile).match(request.path)]
        ##if len(li) == 0 and not request.path.endswith("/"):
        ##    if request.method in ("GET", "HEAD"):
        ##        uri = request.path + "/"
        ##        if request.query:
        ##            uri += "?" + request.query
        ##        hdr = RedirectHandler(self, request, url=uri)
        ##        hdr._execute(transforms, *args, **kwargs)
        ##        return hdr
        ##    raise HTTPError(404)
        #handlers = self._get_host_handlers(request)
        #if not handlers:
        #    handler = RedirectHandler(
        #        self, request, url="http://" + self.default_host + "/")
        #else:
        #    for spec in handlers:
        #        match = spec.regex.match(request.path)
        #        static_flag = spec.kwargs.has_key('path') \
        #                and hasattr(spec.handler_class, 'static_handler') \
        #                and spec.handler_class.static_handler == True
        #        if match:
        #            handler = spec.handler_class(self, request, **spec.kwargs)
        #            if spec.regex.groups:
        #                # None-safe wrapper around url_unescape to handle
        #                # unmatched optional groups correctly
        #                def unquote(s):
        #                    if s is None:
        #                        return s
        #                    from tornado import escape
        #                    return escape.url_unescape(s, encoding=None)
        #                # Pass matched groups to the handler.  Since
        #                # match.groups() includes both named and unnamed groups,
        #                # we want to use either groups or groupdict but not both.
        #                # Note that args are passed as bytes so the handler can
        #                # decide what encoding to use.

        #                if spec.regex.groupindex:
        #                    kwargs = dict(
        #                        (str(k), unquote(v))
        #                        for (k, v) in match.groupdict().iteritems())
        #                else:
        #                    args = [unquote(s) for s in match.groups()]
        #            break
        #    if not handler:
        #        handler = ErrorHandler(self, request, status_code=404)

        ## In debug mode, re-compile templates and reload static files on every
        ## request so you don't need to restart to see changes
        #if self.settings.get("debug"):
        #    with RequestHandler._template_loader_lock:
        #        for loader in RequestHandler._template_loaders.values():
        #            loader.reset()
        #    _StaticFileHandler.reset()

        #handler._execute(transforms, *args, **kwargs)
        #return handler

class WSGIApplication(_WSGIApplication):
    def __call__(self, environ):
        handler = web.Application.__call__(self, tornado.wsgi.HTTPRequest(environ))
        assert handler._finished
        status = str(handler._status_code) + " " + \
            httplib.responses[handler._status_code]
        headers = handler._headers.items()
        if hasattr(handler, "_new_cookie"):
            for cookie in handler._new_cookie.values():
                headers.append(("Set-Cookie", cookie.OutputString(None)))
        start_response(status,
                       [(native_str(k), native_str(v)) for (k, v) in headers])
        return handler._write_buffer


class DebugApplication(Application):
    "Tornado Application supporting werkzeug interactive debugger."
 
    # This supports get_error_html in Handler above.
 
    def __init__(self, *args, **kwargs):
        print "init DebuggedApplication"
        from werkzeug.debug import DebuggedApplication
        self.debug_app = DebuggedApplication(self.debug_wsgi_app, evalex=True)
        self.debug_container = tornado.wsgi.WSGIContainer(self.debug_app)
        super(DebugApplication, self).__init__(*args, **kwargs)
 
    def __call__(self, request):
        if '__debugger__' in request.uri:
            # Do not call get_current_traceback here, as this is a follow-up
            # request from the debugger. DebugHandler loads the traceback.
            return self.debug_container(request)
        return super(DebugApplication, self).__call__(request)
 
    @classmethod
    def debug_wsgi_app(cls, environ, start_response):
        print "Fallback WSGI application, wrapped by werkzeug's debug middleware."
        status = '500 Internal Server Error'
        response_headers = [('Content-type', 'text/plain')]
        start_response(status, response_headers)
        return ['Failed to load debugger.\n']
 
    def get_current_traceback(self):
        "Get the current Python traceback, keeping stack frames in debug app."
        traceback = get_current_traceback()
        for frame in traceback.frames:
            self.debug_app.frames[frame.id] = frame
        self.debug_app.tracebacks[traceback.id] = traceback
        return traceback
 
    def get_traceback_renderer_keywords(self):
        "Keep consistent debug app configuration."
        # DebuggedApplication generates a secret for use in interactions.
        # Otherwise, an attacker could inject code into our application.
        # Debugger gives an empty response when secret is not provided.
        return dict(evalex=self.debug_app.evalex, secret=self.debug_app.secret)

def get_current_traceback():
    "Get the current traceback in debug mode, using werkzeug debug tools."
    # Lazy import statement, as debugger is only used in development.
    from werkzeug.debug.tbtools import get_current_traceback
    # Experiment with skip argument, to skip stack frames in traceback.
    traceback = get_current_traceback(skip=2, show_hidden_frames=False,
                                      ignore_system_exceptions=True)
    return traceback

 
def make_application(app, debug=False, wsgi=False):
    app_path = os.path.abspath(os.path.dirname(app.__file__))
    if hasattr(app, 'settings'):
        conf = app.settings
    else:
        conf = Yaml_Config(app_path, os.path.join(app_path, 'settings.yaml'))
    views_path = os.path.join(app_path, 'views')
    for module, name in get_modules([app.__name__, 'views'], views_path):
        if type(module) == tuple:
            module = module[0]
        __import__(module, {}, {}, name)
    from torweb.urls import url, except_url
    def _set_debug(kw):
        kw["debug"] = debug
        return kw
    url_handlers = url.handlers
    url_handlers = [(u, c, _set_debug(kw)) for u, c, kw in url_handlers]
    _static_urls = [url for url, cls, kw in url.handlers if kw.has_key("path") and hasattr(cls, 'static_handler') and cls.static_handler==True]
    #for u, cls, kw in url_handlers:
    #    if kw.has_key('path') and hasattr(cls, 'static_handler') and cls.static_handler == True: 
    #        static_handler = cls
    #        _static_urls.append(u)
    #if not static_handler:
    #    url_handlers.append((r"/static/(.*)", StaticFileHandler, {"path": os.path.join(app_path, 'static')}))
    #    _static_urls.append(r'/static/(.*)')
    #url_handlers.reverse()
    url_handlers.extend(except_url.handlers)
    #for u, cls, kw in url_handlers:
    #    print "%s \r\t\t\t\t--> %s(%s)" % (u, cls, kw)
    if debug:
        application = DebugApplication(url_handlers, **{'debug':debug})
    else:
        if wsgi == True:
            application = _WSGIApplication(url_handlers, **{'debug':debug})
        else:
            application = WebApplication(url_handlers, **{'debug':debug})
    application.url_handlers = url_handlers
    application._static_urls = _static_urls
    # 初始化session store
    application.session_store = conf.session_store
    return application

class InitializeApplication(object):
    def __init__(self, app):
        self.app = app
        self.app_path = os.path.abspath(os.path.dirname(app.__file__))
        self.conf = Yaml_Config(os.path.join(app_path, 'settings.yaml'))
        pass
    def make_application(self, debug, wsgi):
        return make_application(self.app, debug, wsgi)
