# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------------
# pyojo                                           Copyright (c) 2011 nabla.net
# ----------------------------------------------------------------------------
""" All the members of this module are available in the pyojo package. 

"""

import inspect
import traceback
import ConfigParser

import pyojo.data as data
from .func import *



class Config(object):
    """ Global configuration parameters
    
        Parameters:
        
        - **route**: List of available routes
        - **config**: Multipurpose configuration dictionary
        - **cmd**: TODO: Dictionary of commands.
        - **task**: TODO: Pending tasks.
        - **title**: Application web page title.
        - **cwd**: Main python module current working directory.
        - **url**: Dynamic modules path
        - **path**: Package pyojo root path.
        - **www**: Standard web server files path.
        - **config_ini**: Configuration file config.ini
        - **ini**: Configuration parameters.
        - **step**: Debug counter.
        
    """
    route = []
    config = data.DefaultDict()
    cmd = {}
    task = {}
    title = "pyojo Application"
    cwd = os.path.abspath(os.getcwd())
    url = os.path.join(cwd, "srv")
    path = os.path.dirname(__file__)
    www = os.path.join(path, "server", "www")
    config_ini = os.path.join(path, "config.ini")
    ini = ConfigParser.RawConfigParser()
    ini.read(config_ini)
    step = 0

    
    def __new__(cls):
        raise Error("Yo don't need a Config instance.")
    
    @staticmethod    
    def log():
        """ Config the framework.
        """
        #sys.path.append(os.path.join(self.path, '..'))
        #self.config['webapp2_extras.sessions'] = {'secret_key': str(id(self))}
        log.info("Initializing %s", Config.__class__)
        log.info("Current working directory %s", Config.cwd)
        log.info("Reading parameters from %s", Config.config_ini)
        log.info("Static server files at %s", Config.www)
        log.info("Dynamic server files at %s", Config.url)
        

    @staticmethod
    def get_tasks(taskid, method="GET"):
        """ Return pending operations for task when called with a http verb.
        """
        if not Config.task.has_key(taskid): 
            return []
        if not Config.task[taskid].has_key(method): 
            return []
        return Config.task[taskid][method]

     
    @staticmethod   
    def get_route_map():
        """ Get route map
        """
        routes = []
        for routeobj in Config.route:
            routes.append({"route": routeobj.route,
                           "method": routeobj.method,
                           "accept": routeobj.accept,
                           "cls": routeobj.cls,
                           "call": repr(routeobj.call),
                           "args": routeobj.args,
                           "name": routeobj.name})
        return routes
    
    


#----------------------------------------------------------------------------
#--- Decorators

class route(Decorator):
    """ Decorator to register a route.
    
        Routes are appended to the pyojo.Config.routes list. This route objects
        have the following attributes, besides the parameters:
        
        * .name: the original name of the function or class.
        
        * .cls: the type name, "function" or the superclass.
        
        * .args: list of expected arguments.
        
        * .regex: route url as compiled regular expression.
        
        :param url: the URL to match
        :param method: applicable HTTP VERB, default is any. 
        :param accept: acceptable content type
        
    """
    
    def __init__(self, url="/", 
                       method="GET,POST,PUT,DELETE", 
                       accept="*/*"):
        """ Set route attributes.
        """
        self.route = url
        self.method = method
        self.accept = accept
        self.regex = re.compile(template_to_regex(url))
        Config.route.append(self)
        
        self.call = None
        self.name = None
        self.args = None
        self.type = None
        self.cls = None
        
    def __call__(self, call):
        """ Set call parameters.
        """
        self.call = call
        self.name = call.__name__
        self.cls = type(call).__name__
        
        #args, varargs, keywords, defaults = inspect.getargspec(call)
        if inspect.ismethod(call): #FIX
            self.type = "method"
            self.args = inspect.getargspec(call)[0]
        elif inspect.isfunction(call):
            self.type = "function"
            self.args = inspect.getargspec(call)[0]
        elif inspect.isclass(call):
            self.type = "class"
            self.cls = inspect.getmro(call)[1]
            if inspect.isfunction(call.__init__):
                self.args = inspect.getargspec(call.__init__)[0]
            else: 
                self.args = []
        else:
            self.type = "unknown"

        if len(self.args) == 0: 
            args = "()"
        else: 
            args = "(%s)" % repr(self.args)[1:-1]
        log.info("Config.route['%s']%s %s as %s %s %s", self.name, 
                 args, self.type, self.route, self.method, self.accept)    
        return call

    def __repr__(self):
        return "<Route %s %s>" % (self.route, self.call)




class command(Decorator):
    """ Decorator to register a command.
        
        Simply it can be called with Config.cmd[name]()
        
        :param: name
        :paramtype: string
        
    """
    def __init__(self, name):
        self.name = name
        
    def __call__(self, func):
        log.info("Config.cmd['%s'] %s", self.name, func)    
        
        def call_func(*args, **kwargs):
            return func(*args, **kwargs)
        
        call_func.__name__ = "cmd_" + self.name
        Config.cmd[self.name] = call_func
        return call_func










class task(Decorator):
    """ Decorator to register a function as a task. The function must accept a 
        Dispatch instance as parameter. A Dispatch subclass can have associated 
        tasks, that will be called before or after the main response.  
        
        Config.task[name]={}
        Config.task[name]["GET"]=[]
        
        
        :param task: task name
        :param method: task method
        :param first: insert this function first
        
    """
    def __init__(self, name, method="GET", first=False):
        """ Create a task accesible by name.
        
        """

        self.task = name
        self.method = method
        self.first = first
        
        if not name in Config.task:
            Config.task[name] = {}
        if not method in Config.task[name]:
            Config.task[name][method] = []
        
    def __call__(self, func):
        if self.first:
            Config.task[self.task][self.method].insert(0, func)
        else:
            Config.task[self.task][self.method].append(func)
        return func





'''
@route(r'/pyojo/cmd/{command:(.*)}', accept="*/xml")
class Command(Reply):
    """ A command is a python function who returns a response.
    """
    content = "text/plain"
    def GET(self):
        cmd = self.command.split("/")[0]
        print "COMMAND %s %s" % (cmd, Config.cmd)
        
        if Config.cmd.has_key(cmd):
            call = Config.cmd[cmd]
            log.debug("Executing command %s", call)
            return call(self.request)
        return "CMD %s" % self.command

'''
    
#----------------------------------------------------------------------------
#--- Reply


class ContentType(object): 
    """ Base class for all content handlers.
    """
    handle = None
    
    @classmethod
    def handles(cls, response):
        """ True if this class can handle the response type.
        """
        if cls.handle is None: 
            return False
        return isinstance(response, cls.handle)

    def rtype(self):
        """ Type of the response.
        """
        return type(self.response).__name__

    def see(self, request):
        request.status = 200
        return [self.__class__.__name__]

    def __init__(self, response):
        """ Assing response attribute.
        """
        self.response = response
                
    def __call__(self, request):
        """ Get the final response.
        """
        request.status = 404
        return []



class Reply(object):
    """ Base class for all custom responses.
    
        Decorate with pyojo.route
    """
    _i = 0
    content = "*/*"
    
         
    def __init__(self, request):
        self.request = request
        self.body = []
        self.__iter__ = self.readline

    def write(self, item): #FIX
        try:
            self.body.append(item)
        except:
            self.body = [self.body]
            self.body.append(item)

    def readline(self): #FIX
        
        if isinstance(self.body, basestring):
            print "<- STRING"
            yield [self.body]
        else:    
            for item in self.body:
                print "<- %s" % type(item)
                yield item
        
    def read(self):
        try:
            return "%s" % "".join(self.body)
        except:
            return "%s" % self.body
        
    __iter__ = readline
    __str__ = read
            
    def reply(self):
        """ Call to the method for the HTTP verb.
        """
        call = getattr(self, self.request.method)
        try:
            call()
        except:
            pass

    def send(self, iterable):
        """ Return the Response object to the Request.
        """
        if isinstance(iterable, basestring):
            self.body = [iterable]
        else:
            self.body = iterable
        return self
                   
    def GET(self):
        """ Method called if request method is GET
        """ 
        raise ResponseNotImplemented(self, "GET")
    
    def POST(self): 
        """ Method called if request method is POST
        """ 
        raise ResponseNotImplemented(self, "POST")
    
    def PUT(self): 
        """ Method called if request method is PUT
        """ 
        raise ResponseNotImplemented(self, "PUT")
    
    def DELETE(self): 
        """ Method called if request method is DELETE
        """ 
        raise ResponseNotImplemented(self, "DELETE")
 
    def set_content(self):
        """ Override to set Content-Type and other headers.
        """
        pass
 




class ScriptXML(data.XML):
    """A pyojo XML response for asynchronous requests.
    """
    def __init__(self):
        """ Create a new pyojo command script.
        """
        self.calls = []
        super(ScriptXML, self).__init__(tag="response")
                
    def call(self, module, call=None):
        """ Request a pyojo AMD module and call a defined function.
        
            This commands are executed all at the same time.
        """
        prop = {"script": module}
        if call is not None: 
            prop["call"] = call
        self.new_node("pyojo", prop, parent=self.root)
        self.calls.append(module)
        
    def script(self, code):
        """ TODO.
        """
        self.new_node("script", text=code, parent=self.root)

    def code(self, code):
        """ Force the browser to eval this code string.
        """
        self.new_node("javascript", text=code, parent=self.root)
        
    def content(self, target, text):
        """ Replaces the content of a DOM node.
        """
        prop = {"target": target}
        self.new_node("content", prop=prop, text=text, parent=self.root)

    def append(self, target, text):
        """ Appends the content to a DOM node.
        """
        prop = {"target": target}
        self.new_node("append", prop=prop, text=text, parent=self.root)
        


class Traceback(object):
    """ Stores information about an exception.
    """
    def __init__(self, exc_info, request):
                
        self.info = {"method": request.method,
                     "url": request.url,
                     "accept": request.accept,
                     "handler": request.handler_info,
                     "async": request.async}
        
        self.exc_type, self.exc_value, exc_traceback = exc_info 

        trace = "\n"
        for line in traceback.format_tb(exc_traceback):
            trace +="%s\n" % line # re.escape(line.replace(self.path, "pyojo"))
        
        self.trace = trace

    def __str__(self):
        return "%s: %s" % (self.exc_type.__name__, self.exc_value)
    