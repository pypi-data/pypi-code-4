# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------------
# pyojo                                           Copyright (c) 2013 nabla.net
# ----------------------------------------------------------------------------
""" This is the main pyojo module. 

    The goal is to define a page with modular building blocks witch will be 
    asynchronously loaded from the server, who will send the javascript code 
    to create them at the browser. If a block depends on the previous existence
    of another block (its parent, for example), the pyojo script will try to 
    retrieve all dependencies before executing the code.
    
    Request is the entry point, create a instance passing environ and then use
    the get_response() to get the content. The get_headers() method and the 
    status attribute are then passed to the WSGI start_response function.
    
    The response must be iterable, and there is a collection of ContentType
    subclasses that can be returned to the WSGI applicattion depending on the
    type of the response, they return the iterable when called.
    
    There is one special ContentType subclass called Reply, witch handles the
    Response subclass responses, to do your own custom responses.
                
"""

__author__ = "Txema Vicente Segura"
__version__ = "0.0.2 prealpha"
__copyright__ = "Copyright (C) 2013 nabla.net"


import time
import rfc822
import traceback

import pyojo.data as data
import pyojo.content as content
from .func import *
from .base import *



class Request(object):
    """ Answers a request with an appropriate response.
    
        The WSGI application creates one instance and then asks 
        a response calling the get_response method.
        
    """
    
      
    def __init__(self, environ=None):
        """ Create an instance to find the response for a request.
        
            :param environ: 
               request description, as described in 
               http://www.python.org/dev/peps/pep-0333/
            
            :type environ: dict
            
            Attributes:
            
             - **environ**:  Request description.
             - **url**: HTTP path.
             - **method**: HTTP verb.
             - **query**: Request parameters
             - **accept**: Expected content type.
             - **async**: True if AJAX.
             - **cookies**: Cookies.
             - **response_header**: Response Headers.
              
             
        """
        self.environ = environ
        self.response = None
        self._status = 102 #Processing
        self.handler_info = "None"
        self.error_info = ""
        self.response_header = data.LimitedDict(data.HEADERS_RESPONSE)
        self.response_header["Server"] = "pyojo %s" % __version__
        self.response_header["Date"] = rfc822.formatdate(time.time())
        
        if environ is None:
            self.config = None
            self.environ = {}
            self.url = "/"
            self.method = None
            self.query = ()
            self.accept = '*/*'
            self.async = False
            self.cookies = ""
        else:
            self.init(environ)            

    
    def __call__(self, environ, start_response):
        """ Act like a WSGI application.
        
            :param start_response:
                If passed, then .
               
        """
        response = self.get_response()
        start_response(self.status, self.get_response_headers())
        return response
        
    
    def init(self, environ):
        """ Initialize attributes analyzing environ.
            
            :param environ: request description dictionary.
        """
        self.environ = environ
        self.url = environ['PATH_INFO']
        self.method = environ['REQUEST_METHOD']
        self.query = parse_qs(environ['QUERY_STRING'])
        self.accept = environ.get('HTTP_ACCEPT','*/*')
        if not "/dojo/" in self.url:
            log.debug("Request %s %s %s", self.url, 
                                          self.method, 
                                          self.accept.split(";")[0])
            
        requested_with = environ.get('HTTP_X_REQUESTED_WITH')
        self.async = 'XMLHttpRequest' == requested_with
        
        self.cookies = environ.get('HTTP_COOKIE', '')
        
        self.route_type = {"function": self.route_function,
                           "class": self.route_class}
        #http_request_headers(environ)
        #if str(time.time())[8] in self.url:
        #    self.url, ext = os.path.splitext(self.url)
        #    self.url = self.url.rsplit("/",1)[0]+ext
        #    log.info("URL=%s" % self.url)

            
        try:
            self.config = Config
        except NameError:
            class Temp(object):
                "Mock Config"
                www = None
                url = None
                route = []
                debug = True
            self.config = Temp

    
            
    def __deduce(self):
        """ Find the answer.
        
            Checks routes and static files, looking for the correct answer.
            
            :returns: something or None
        """
        #Don't waste time.
        if content.CachedText.instances.has_key(self.url):
            return content.CachedText(self.url)
        
        if "/static/" in self.url: 
            sequence = (self.static, self.route, self.module)
        else:
            sequence = (self.module, self.route, self.static)
        
        for method in sequence:
            response = method()
            if response is not None:
                return response
        return None 
    
    
    def get_response(self):
        """ Get the response.
        
            :returns: the response
            :rtype: iterable
        """
        handler = None
        response = self.__deduce()
                
        if True:#Config.debug
            if self.async:
                handler_info = "XHR-" + self.handler_info
            else:
                handler_info = self.handler_info
                
            self.response_header["X-Handler"] = handler_info
            self.response_header["X-Type"] = str(type(response))[1:-1]
                
        if isinstance(response, ContentType):
            self._log_content(response)
            handler = response
            #return response(self)
        else:
            rtype = type(response).__name__
            for cls in subclasses(ContentType):
                if cls.handles(response):
                    handler = cls(response)
                    self._log_content(handler, rtype)
                    break#return handler(self)

        
        if handler is not None:
            if self.param("code") is not None:
                print "SEE %s" % type(handler)
                return handler.see(self)
            else:    
                return handler(self)
        
        log.warning("Response type %s unknown", type(response)) #.__name__
        if self.status == 102:
            self.status = 501 #Not implemented
        
        return response


    def get_response_headers(self):
        """ Get headers as a list of tuples.
        """
        if self.response_header["Content-Type"] is None:
            log.warn("Content-Type header is not set for %s", self.url)
        response_headers = []
        for key, value in self.response_header.iteritems():
            response_headers.append((key, str(value)))
        return response_headers



 
 
    @property
    def status(self):
        """ Get the current status code.
        
            :returns: status code and description
            :rtype: string
        """
        status = "%s %s" % (self._status, data.HTTP_STATUS[self._status])
        return status
    
    
    @status.setter
    def status(self, code):
        """ Set the current status code.
        """
        assert code in data.HTTP_STATUS.keys(), "HTTP Status unknown"
        self._status = code
        if code != 200: 
            log.debug("HTTP Status %s for %s", code, self.url)
     
     
    def content_type(self, mime):
        """ Sets the content type, and charset if applicable.
        """
        if ("text" in mime) and (not "charset" in mime):
            mime += "; charset=utf-8"    
        self.response_header["Content-Type"] = mime


    def static(self, url=None):
        """ Look for a static file.
        
            :returns: FileSystem or CachedText instance, or None.
        """
        if url is None: 
            url = self.url
        
        if self.config.www is None: 
            log.error("Static files folder not configured")
            return None
        
        path = url.replace("/", os.path.sep)
        if path.startswith(os.path.sep): 
            path = path[1:]
        filename = os.path.normpath(os.path.join(self.config.www, path))
        
        if not os.path.isfile(filename):
            return None
        
        ext = os.path.splitext(path)[1][1:]
        if not data.MIMETYPE.has_key(ext):
            log.error("Unknown mimetype for '%s'", ext)
            return None
        
        if ext in ["js", "css", "html"]:
            return content.CachedText(url, filename)
        
        return content.FileSystem(filename)


    def module(self, url=None):
        """ Look for a python module.
        
            :returns: result of calling the HTTP verb, or None.
        """
        
        if self.config.url is None: 
            return None
        if url is None:
            url = self.url
        mod_name = "_".join(url.lstrip("/").rsplit(".", 1))
        path_mod = os.path.abspath(os.path.join(Config.url, mod_name+".py"))
        if not os.path.exists(path_mod):
            return None
        
        self.handler_info = "module %s" % (mod_name)
        try:
            module = import_url(Config.url, url)
        except ModuleNotFoundError, ex:
            log.warning("Module %s: %s", mod_name, ex)
            return None
        except Exception, ex:
            log.error("Exception loading %s: %s", mod_name, ex)
            return self.error(sys.exc_info())
        if module is None:
            return None
        
        ext = os.path.splitext(url)[1]
        if len(ext)>0:
            self.content_type(data.MIMETYPE[ext[1:]])
        function = self.method
        if self.param("method") is not None:
            function = self.param("method")
        self.handler_info = "module %s.%s" % (mod_name, function)
        
        if hasattr(module, function):
            call = getattr(module, function)
            try:
                response = call(self)
            except Exception, ex:
                log.error("Exception calling %s.%s: %s", mod_name, function, ex)
                return self.error(sys.exc_info())
            self.status = 200
            return response


    def route_function(self, routeobj, params=None):
        """ Call the route function.
        
            Check expected arguments and call the handler function.
        """
        if params is None:
            params = {}
        kwargs = params
        if "request" in routeobj.args: 
            kwargs["request"] = self
        if "environ" in routeobj.args: 
            kwargs["environ"] = self.environ

        self.handler_info = "function %s(%s)" % (routeobj.name, 
                                             repr(kwargs)[1:-1])
        log.debug("Route '%s' is '%s': %s %s (%s) type '%s' for '%s'",
                    self.url, routeobj.route, routeobj.type, routeobj.name,
                    kwargs, routeobj.accept, self.accept)
        try:
            response = routeobj.call(**kwargs)
        except Exception:
            return self.error(sys.exc_info())
        return response


    def route_class(self, routeobj, params=None):
        """ Call the route class.
        
            If is a Response subclass, create a new instance. Then the route 
            parameters are set as instance attributes, and the requested method 
            is called.
            
            TODO: params, other classes
        """
        if params is None:
            params = {}
            
        if issubclass(routeobj.call, Reply):
            self.handler_info = "class %s(%s).%s %s" % (routeobj.name, 
                                                        id(self), 
                                                        self.method,
                                                        params)
            obj = routeobj.call(self)
            self.content_type(obj.content)
            for attr, value in params.iteritems():
                setattr(obj, attr, value)
            try:
                method = getattr(obj, self.method)
                response = method()
            except Exception:
                #response = [self.reply_exception(method)]#501
                return self.error(sys.exc_info())
            return response


    def route(self):
        """ Look for a appropiate route.
        
            Checks the route map and if one route accepts the URL and the request
            method, and it fits in the expected Content-Type, calls the route and
            returns the returned value.
        
            :returns: route call result 
            :rtype: something or None
        """
        for route in self.config.route:
            match = route.regex.match(self.url)
            if match:
                if not self.method in route.method: continue
                if not accepts(route.accept, self.accept): 
                    continue
                self.status = 200
                return self.route_type[route.type](route, match.groupdict())
        return None


    def error(self, exc_info):
        """ Handles exceptions.
        
            :returns: Traceback
        """
        exc_type, exc_value, exc_traceback = exc_info
        
        status = "Request %s%s %s accepts %s" % ("XHR-" if self.async else "", 
                                                 self.method, 
                                                 self.url,
                                                 self.accept)
        status += "\nHandler %s" % self.handler_info
         
        error = "%s: %s" % (exc_type.__name__, exc_value)
        trace = "\n"
        for line in traceback.format_tb(exc_traceback):
            trace +="%s\n" % line # re.escape(line.replace(self.path, "pyojo"))
        
        print status + trace + error
        self.error_info = status + trace + error
        
        self.status = 500
        return Traceback(exc_info, self)


    def param(self, param):
        """ Get a query parameter value.
        
            :param param: parameter name
            :type param: string
            :returns: value
            :rtype: string
        """
        value = self.query.get(param, None)
        if type(value)==type([]):
            if len(value)==1:
                return value[0]
        return value


    def _log_content(self, response, rtype=None):
        """ Log content type.
        """
        if "/dojo/" in self.url: 
            return
        if "/favicon" in self.url: 
            return
        
        if rtype is None:
            rtype = response.rtype()
        else:
            rtype = "*" + rtype
        log.debug("Content %s(%s) %s %s",
                  response.__class__.__name__, 
                  rtype,
                  self.response_header["Content-Type"], 
                  self.status)



#---------------------------------------------------------------------------
