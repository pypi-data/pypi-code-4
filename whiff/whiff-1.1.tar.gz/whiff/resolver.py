"""
This module contains classes and methods used for
associating WSGI applications and middlewares to
paths in directories.
"""

# XXXX need to distinguish between imports that fail and sub-imports that fail

# XXXX probably should use urlparse.urljoin for some resolution steps instead of
#      adhoc methods.  Look for manipulations of path components...

import mimetypes
import sys
import imp
import types
import os
import os.path
import glob
import cgi
import whiffenv
import time

# traverse into directories only if this sentinel is defined
DIRECTORY_SENTINEL = "__wsgi_directory__"

# use this as the default wsgi callable application in a module
DEFAULT_WSGI_INTERPRETATION_NAME = "__wsgi__"

# use this as the default application generator (middleware) in a module
DEFAULT_WSGI_MIDDLEWARE = "__middleware__"

# use this module mark to decide whether to reload modules
WHIFF_MTIME = "__whiff_mtime__"

class ModuleRootResolutionException(ValueError):
    "There was an error trying to resolve a wsgi application by path"
    
class WhiffTemplateImportProblem(ValueError):
    "A module automatically imported by WHIFF tried to import a non-existant module"

class NoDefaultForDirectoryException(ModuleRootResolutionException):
    "The directory has no 'directory-listing' function defined"

def default_not_found_app(env, start_response):
    start_response('404 Not Found', [('Content-Type', 'text/html'),])
    yield "<html><head><title>404 - File Not Found</title></head>\n"
    yield "<body>\n"
    yield "<h3>404 - File not found</h3>\n"
    yield "<b>Whiff resolver could not resolve the http path</b><br>\n"
    yield "SCRIPT_NAME="+repr(env.get("SCRIPT_NAME"))+"<br>\n"
    yield "PATH_INFO="+repr(env.get("PATH_INFO"))+"<br>\n"
    yield "</body></html>\n"

class WsgiComponent:
    """
    Marker superclass for authorized module components which can be automatically
    called by a moduleRootApplication when they are located in a module.
    Anything that is not an instance of this class is considered a possible security
    risk and will not be used as a WSGI app automatically.

    Most client apps will not directly subclass this class, but will wrap their
    applications using WsgiApplicationWrapper to create a WsgiComponent.
    """
    # mark indicating whether the component can see other parameters in outer scopes
    Lexical = False
    
    whiff_root_application = None
    whiff_responding_path = None
    whiff_path_remainder = None
    whiff_outer_arguments = None
    whiff_bound_environment = None
    whiff_lexical_arguments = None
    no_filter = False # set to true to disable filter
    
    #def __init__(self):
    #    pass
    def duplicate(self, **args):
        "if the component will be used as a factory (static module variable) then this should return a fresh object"
        raise ModuleRootResolutionException, "default duplicate is not implemented for this class: "+self.__class__.__name__
    def bind_root(self, root_application, responding_path, path_remainder, outer_arguments):
        #pr "binding root", self, root_application, responding_path, path_remainder
        oldpath = self.whiff_responding_path
        if oldpath is not None: # and oldpath!=responding_path:
            #raise ValueError, "cannot rebind different responding_path "+repr((oldpath,responding_path))
            # refuse rebinding...
            #pr "binding refused!"
            return self.paths_ok(self.whiff_responding_path, self.whiff_path_remainder)
        self.whiff_root_application = root_application
        self.whiff_responding_path = responding_path
        self.whiff_path_remainder = path_remainder
        self.whiff_outer_arguments = outer_arguments
        return self.paths_ok(responding_path, path_remainder)
    def bind_environment(self, env, lexical_arguments=None):
        if lexical_arguments:
            my_lex = self.whiff_lexical_arguments
            if my_lex is None:
                my_lex = self.whiff_lexical_arguments = {}
            #pr "for", id(self)
            #pr "updating lexical args", my_lex.keys()
            #pr "with", lexical_arguments.keys
            # overlay: not update
            for (name,val) in lexical_arguments.items():
                if not my_lex.has_key(name):
                    my_lex[name] = val
        # override default environment scope (always)
        if env is not None and self.whiff_bound_environment is None:
            #pr "~~ OVERRIDING ENV FOR", self, ("template path", env.get(whiffenv.TEMPLATE_PATH))
            self.whiff_bound_environment = env # required for env_scope test case
            #pr "~~ AFTER OVERRIDING ENV FOR", self, env.get("variable")
            pass
        else:
            #pr "NOT OVERRIDING ENV"
            pass
    def paths_ok(self, responding_path, path_remainder):
        "for subclasses: check that the path is ok"
        return True # default: yes, no problem
    def update_environment(self, env):  # is this needed?
        "hook to allow early environment modifications (like cgi parameter pre-parsing)"
        return env # default: no change
    def whiff_call(self, env, start_response, update_environment=None, additional_args=None):
        """internal call operation --
             self.update_environment should be called before this.
             update_environment should be called by this method
             at the very last minute (so it doesn't get overridden).
        """
        # no default.
        raise ValueError, "virtual method must be defined at subclass"

    def __call__(self, env, start_response, update_environment=None, additional_args=None):
        "external call operation"
        try:
            # if the environment has been pre-bound use the bound environment instead of the passed environment
            #pr "__call__", self
            oenv = self.whiff_bound_environment
            if oenv:
                #pr "call using bound_environment"
                env = oenv # required for env_scope testcase
                pass
            #pr "in __call__ variable = ", env.get("variable")
            env = modifiedEnvironment(env)
            whiffenv.check_environment(env)
            env = self.update_environment(env)
            #pr "WsgiComponent calling whiff_call", id(self), self
            result = self.whiff_call(env, start_response, update_environment, additional_args=additional_args)
        finally:
            pass
        return result
        
def parse_cgi_get(env, quoted=True):
    env[whiffenv.CGI_DICTIONARY] = env.get(whiffenv.CGI_DICTIONARY,{})
    get_parameters = env.get("QUERY_STRING")
    #p "parsing get parameters", get_parameters
    if get_parameters:
        parse_url_encoded_parameters(env, get_parameters, quoted)
    #p "dict is now", env[whiffenv.CGI_DICTIONARY] 

def parse_cgi_post(env, quoted=True):
    "parse url-encoded post parameters: SHOULD ONLY BE CALLED ONCE"
    env[whiffenv.CGI_DICTIONARY] = env.get(whiffenv.CGI_DICTIONARY,{})
    content_length_str = env.get("CONTENT_LENGTH")
    if content_length_str:
        content_length = int(content_length_str)
        inpt = env.get("wsgi.input")
        if inpt:
            post_parameters = inpt.read(content_length)
            parse_url_encoded_parameters(env, post_parameters, quoted)

def parse_url_encoded_parameters(env, query_string, quoted=True):
    query_dict = cgi.parse_qs(query_string)
    cgi_dict = env.get(whiffenv.CGI_DICTIONARY, {})
    #p "parsed cgi parameters are", query_dict
    for (name, lst) in query_dict.items():
        oldlist = cgi_dict.get(name, [])
        for value in lst:
            if quoted:
                value = quote(value)
            #pr "now checking cgi", (name, value)
            if not value in oldlist:
                #pr "appending cgi", (name, value)
                oldlist.append(value)
        cgi_dict[name] = oldlist
    env[whiffenv.CGI_DICTIONARY] = cgi_dict
    #p "dict is now",  env[whiffenv.CGI_DICTIONARY]

def find_or_make_cgi_dictionary(env):
    cgi_dict = env.get(whiffenv.CGI_DICTIONARY, {})
    env[whiffenv.CGI_DICTIONARY] = cgi_dict

def override_cgi_require(env, name, value):
    value = quote(value) # cgi entries are always quoted by default in WHIFF
    cgi_dict = env.get(whiffenv.CGI_DICTIONARY, {})
    cgi_dict[name] = [value]
    env[whiffenv.CGI_DICTIONARY] = cgi_dict

def local_cgi_name(global_name, env):
    "trim cgi-prefix, if present, from global_name"
    prefix = env.get(whiffenv.FULL_CGI_PREFIX, None)
    if prefix is None:
        return global_name
    if global_name.startswith(prefix):
        return global_name[len(prefix):]
    raise ValueError, "global variable name does not match cgi_prefix "+repr((global_name, prefix))

def process_cgi(env,
                parse_cgi=None, # parse any cgi parameters (default: check environment)
                parse_get=None, # parse cgi GET parameters (default: check environment)
                parse_post=None, # parse cgi POST parameters (default: check environment)
                cgi_prefix=None # cull by prefix (default: check environment)
                ):
    "standard cgi parameter processing for WHIFF components, return new environment with adjustments"
    #pr "PROCESSING CGI WITH ARGUMENT PREFIX", cgi_prefix
    envcopy = env.copy()
    if envcopy.has_key(whiffenv.CGI_DICTIONARY):
        envcopy[whiffenv.CGI_DICTIONARY] = envcopy[whiffenv.CGI_DICTIONARY].copy()
    # parse cgi parameters if not done already
    cgi_parsed_here = False
    if parse_cgi is None:
        parse_cgi = envcopy.get(whiffenv.PARSE_CGI, False)
    if parse_get is None:
        parse_get = envcopy.get(whiffenv.PARSE_CGI_GET, False)
    if parse_post is None:
        parse_post = envcopy.get(whiffenv.PARSE_CGI_POST, False)
    if not envcopy.has_key(whiffenv.CGI_DICTIONARY):
        #pr "parse cgi flags", (parse_cgi, parse_get, parse_post)
        # if parse_cgi is set then install the cgi resource (parse get, post, or multipart)
        if parse_cgi:
            import gateway
            # resource path for cgi dictionary
            resourcePath = ["cgi", None]
            # get the dictionary and quote it
            unquoted = gateway.getResource(env, resourcePath)
            quoted = {}
            for name in unquoted:
                quoted[name] = [ quote(x) for x in unquoted[name]]
            envcopy[whiffenv.CGI_DICTIONARY] = quoted #gateway.getResource(env, resourcePath)
        else:
            if parse_get:
                # parse only the get parameters
                parse_cgi_get(envcopy)
                cgi_parsed_here = True
            if parse_post:
                # parse only the post parameters using standard cgi encoding (not multipart)
                parse_cgi_post(envcopy)
                cgi_parsed_here = True
        #pr "dict is now", envcopy.get(whiffenv.CGI_DICTIONARY)
        # XXX ? remove the marks?
    else:
        # someone else has already parsed the cgi parameters... don't do it again (???)
        pass
    #pr "after cgi-parse check dict is", envcopy.get(whiffenv.CGI_DICTIONARY)
    # store the cgi_dictionary as the top cgi dictionary unless already set 
    if envcopy.get(whiffenv.TOP_CGI_DICTIONARY) is None:
        envcopy[whiffenv.TOP_CGI_DICTIONARY] =  envcopy.get(whiffenv.CGI_DICTIONARY)
    # if a cgi-prefix is specified then cull the cgi-parameters (removing the prefix) and update the full prefix.
    if cgi_prefix is None:
        cgi_prefix = envcopy.get(whiffenv.CGI_PREFIX, "")
    full_prefix = envcopy.get(whiffenv.FULL_CGI_PREFIX, "")
    if cgi_prefix or (full_prefix and cgi_parsed_here):
        #pr "PROCESSING CGI PREFIX", cgi_prefix
        # update or create the full prefix entry
        full_prefix = envcopy.get(whiffenv.FULL_CGI_PREFIX, "")
        new_full_prefix = full_prefix+cgi_prefix
        envcopy[whiffenv.FULL_CGI_PREFIX] = new_full_prefix
        # if the cgi dictionary was parsed here then cull using the full prefix
        if cgi_parsed_here:
            cgi_prefix = new_full_prefix
        #pr "AT", envcopy["SCRIPT_NAME"], "SET CGI_PREFIX", envcopy[whiffenv.FULL_CGI_PREFIX]
        cgi_dict = envcopy.get(whiffenv.CGI_DICTIONARY)
        # set prefix to empty...
        if envcopy.has_key(whiffenv.CGI_PREFIX):
            #pr "NOW DELETING CGI_PREFIX", envcopy[whiffenv.CGI_PREFIX]
            #del envcopy[whiffenv.CGI_PREFIX]
            envcopy[whiffenv.CGI_PREFIX] = ""
        if cgi_dict is not None:
            prefixlen = len(cgi_prefix)
            # keep only cgi parameters which match the prefix, with the prefix removed from the name
            new_cgi_dict = {}
            for (k,v) in cgi_dict.items():
                if len(k)>prefixlen and k.startswith(cgi_prefix):
                    newk = k[prefixlen:]
                    new_cgi_dict[newk] = v
            envcopy[whiffenv.CGI_DICTIONARY] = new_cgi_dict
            #pr "old cgi dict", cgi_dict
            #pr "new cgi dict", new_cgi_dict
        else:
            # XXXX is this really an error?
            #raise ValueError, "cgi prefix may only be specified after cgi parameters have been parsed: "+repr(cgi_prefix) # ???
            pass
    return envcopy

#def add_cgi_require(env, name, value):
#    cgi_dict = env.get(whiffenv.CGI_DICTIONARY, {})
#    oldlist = cgi_dict.get(name, [])
#    if not value in oldlist:
#        oldlist.append(value)
#    cgi_dict[name] = oldlist
#    env[whiffenv.CGI_DICTIONARY] = cgi_dict

class WsgiComponentFactory:
    """
    Marker virtual superclass for registered objects which know how to make a WsgiComponent
    """
    # mark indicating whether the component can see other parameters in outer scopes
    Lexical = False

    whiff_root_application = None
    whiff_responding_path = None
    whiff_path_remainder = None
    whiff_outer_arguments = None
    whiff_bound_environment = None
    whiff_lexical_arguments = None
    file_path = None

    def makeWsgiComponent(self, **args):
        "abstract method that must be defined in subclasses"
        raise ValueError, "method not defined at virtual superclass"
    def clone(self):
        "abstract method to duplicate self for later binding"
        raise ValueError, "method not defined at virtual superclass"
    def bind_environment(self, env, lexical_arguments):
        "bind self to an environment dictionary"
        if lexical_arguments:
            if self.whiff_lexical_arguments is None:
                self.whiff_lexical_arguments = {}
            self.whiff_lexical_arguments.update(lexical_arguments)
        # override default environment scope (always)
        if env is not None: #self.whiff_bound_environment is None:
            #pr "OVERRIDING ENV FOR", self, env["SCRIPT_NAME"], env.get("variable")
            self.whiff_bound_environment = env
            #pr "AFTER OVERRIDING ENV FOR", self, env["SCRIPT_NAME"], env.get("variable")
            pass
        else:
            #pr "NOT OVERRIDING ENV"
            pass
    def preBind(self, root_application, responding_path, path_remainder=None, outer_arguments=None):
        "Partially bind self.  To avoid concurrency issues this must return a new object"
        #pr "prebinding", self
        #pr "   root app", root_application
        #pr "   responding_path", responding_path
        #pr "   path_remainder", path_remainder
        #pr "   outer_arguments", outer_arguments
        if self.whiff_root_application is not None:
            #raise ValueError, "ALREADY BOUND"
            #pr "DUPLICATE PREBIND REFUSED"
            #pr "   PREVIOUS RESPONDING PATH", self.whiff_responding_path
            return self
        if path_remainder is None:
            path_remainder = []
        if outer_arguments is None:
            outer_arguments = {}
        result = self.clone()
        result.whiff_root_application = root_application
        result.whiff_responding_path = responding_path
        result.whiff_path_remainder = path_remainder
        result.whiff_outer_arguments = outer_arguments
        return result
    def bound(self):
        "test whether self is bound"
        return self.whiff_root_application!=None
    def makeBoundWsgiComponent(self, **args):
        "generate application by binding arguments"
        #pr "making bound instance", self
        #pr "   root application", self.whiff_responding_path
        #pr "   path_remainder", self.whiff_path_remainder
        #pr "   outer_arguments", self.whiff_outer_arguments
        result = self.makeWsgiComponent(**args)
        #pr "   got result", result
        test = result.bind_root(self.whiff_root_application, self.whiff_responding_path, self.whiff_path_remainder, self.whiff_outer_arguments)
        #pr "   bound result", result
        if not test:
            raise ValueError, "cannot bind made wsgi component: binding refused"
        return result
    def __call__(self, **args):
        "auto bind if possible"
        if self.whiff_root_application is not None:
            return self.makeBoundWsgiComponent(**args)
        else:
            return self.makeWsgiComponent(**args)


def clean_component_name(n):
    "a module component cannot have a dot in it: make dots into underscores..."
    return n.replace('.', '_')

def wrapApplication(app):
    if app is not None:
        if not isinstance(app, WsgiComponent):
            app = WsgiApplicationWrapper(app)
        else:
            app = app.duplicate()
            pass
    return app

def wrapMiddleware(middleware):
    if middleware is not None and not isinstance(middleware, WsgiComponentFactory):
        middleware = WsgiClassWrapper(middleware)
    return middleware

def modifiedEnvironment(env, additional_entries=None, root=None):
    "make a copy of environment, adding additional parameters if not present"
    # don't do anything if the entry point is known already (the environment has already been modified (?))
    ep = whiffenv.ENTRY_POINT
    # record the root ALWAYS if provided # if not known and provided
    newenv = env.copy()
    oldRoot = newenv.get(whiffenv.ROOT)
    if root is not None and oldRoot is not None:
        root.setParent(oldRoot)
    if root is not None:# and newenv.get(whiffenv.ROOT) is None:
        #pr "setting root", root
        newenv[whiffenv.ROOT] = root
        if root:
            # allocate a monitor for resources
            newenv[whiffenv.RESOURCES] = root.resourceMonitor()
    # finally make additions, if specified
    if additional_entries:
        for (k,v) in additional_entries.items():
            newenv[k] = v
    if env.get(ep, None) is not None:
        #pr "not modifying", env[ep]
        return newenv
    pi = env.get("PATH_INFO", "")
    sn = env.get("SCRIPT_NAME", "")
    path = sn+pi
    path = os.path.normpath(path)
    # just in case we are running on windows replace backslashes with forwards
    path = path.replace("\\", "/")
    # no two initial slashes please
    while path.startswith("//"):
        path = path[1:]
    #pr "modified", (pi, sn, path)
    newenv[ep] = path
    ## XXXXX THESE SETTINGS TO SCRIPT_NAME MAY NOT BE RIGHT, THEY SHOULD BE OVERRIDDEN BEFORE APP CALL (?)
    # ALSO record as script name
    #pr "RESOLVER RESETTING SCRIPT NAME", (env.get("SCRIPT_NAME"), path)
    newenv["SCRIPT_NAME"] = path
    # provisional null path_info until resolution
    newenv["PATH_INFO"] = ""
    newenv[whiffenv.TIME_STAMP] = time.time()
    return newenv

class moduleRootApplication(WsgiComponent):
    "Make a module into a WSGI app which serves its content (subject to security restrictions)"
    
    def __init__(self,
                 # the server relative URL prefix for the directory
                 root_path="",
                 # the module/directory to serve
                 root_module=None,
                 # the application to handle "not found" urls
                 on_not_found=default_not_found_app,
                 # middleware to use to wrap all applications (overridden via "no-filter")
                 filter_middleware=None,
                 # middleware to handle uncaught exceptions
                 exception_middleware=None,
                 # additional environment entries to insert for each request
                 environment=None,
                 # resource gateway object
                 resourceGateway=None,
                 # auto reload outdated locations if set
                 auto_reload=True,
                 ):
        self.resourceGateway = resourceGateway
        if root_module is None:
            raise ValueError, "root_module must be specified"
        # note: root path may be relocated under the parent path on bind_root, if it's a relative path
        self.root_path = root_path # clean_component_name(root_path)
        #self.root_path_list = root_path.split("/") #self.reduce_path_list(root_path)
        self.root_path_list = None
        self.root_module = root_module
        self.on_not_found = wrapApplication(on_not_found)
        self.filter_middleware = wrapMiddleware(filter_middleware)
        self.exception_middleware = wrapMiddleware(exception_middleware)
        self.environment = environment
        #pr "initialized", self, "with gateway", self.resourceGateway
        self.auto_reload = auto_reload

    def resourceMonitor(self):
        "create a resource monitor for a request"
        import gateway
        rg = self.getGateway()
        monitor = gateway.ResourceMonitor(rg, self.root_path)
        return monitor
        
    def getGateway(self):
        #pr
        #pr "getting gateway", self
        parentGateway = None
        rg = self.resourceGateway
        #pr "cached gateway", repr(rg)
        if rg is None:
            import gateway
            parent = self.whiff_root_application
            if parent:
                parentGateway = parent.getGateway()
                #pr "got parent gateway", parentGateway
            #pr "making new gateway"
            rg = self.resourceGateway = self.newResourceGateway(parentGateway)
        #pr "returning gateway", (self, rg, parentGateway)
        return rg

    def newResourceGateway(self, parentGateway):
        import gateway
        if parentGateway is not None:
            return gateway.ResourceGateway(parentGateway)
        # otherwise allocate standard request-temporary in memory finders for top level gateway
        from whiff.resources import localStorage
        from whiff.resources import FreshName
        from whiff.resources import cgiResource
        result = gateway.ResourceGateway(parentGateway, self.root_path)
        namefinder = FreshName.FreshNameFinder()
        result.registerFinder(prefix="freshName", finder=namefinder)    
        cgifinder = cgiResource.CgiFinder()
        result.registerFinder(prefix="cgi", finder=cgifinder)    
        localfinder = localStorage.Local()
        result.registerFinder(prefix="local", finder=localfinder)
        counterfinder = localStorage.Counters()
        result.registerFinder(prefix="counter", finder=counterfinder)
        return result

    def registerResourceFinder(self, prefix, finder):
        rg = self.getGateway()
        rg.registerFinder(prefix, finder)

    def registerStaticResource(self, prefix, resourceValue):
        from whiff.resources.static import staticResource
        finder = staticResource(resourceValue)
        self.registerResourceFinder(prefix, finder)

    def bind_root(self, root_application, responding_path, path_remainder, outer_arguments):
        "adjust relative root_path to sit below the root_application path"
        # XXXX possibly should clear exception_middleware if it is overridden by the root_application (?)
        #pr "root bind_root", (self, root_application, responding_path, path_remainder, outer_arguments)
        WsgiComponent.bind_root(self, root_application, responding_path, path_remainder, outer_arguments)
        # makes sure my gateway is bound to the root gateway
        myGateway = self.getGateway()
        rootGateway = root_application.getGateway()
        myGateway.bind_root(rootGateway)
        old_root_path_list = self.root_path_list
        root_path = self.root_path
        #new_root_path_list = root_application.reduce_path_list(root_path)
        new_root_path_list = responding_path
        if old_root_path_list is not None and old_root_path_list!=new_root_path_list:
            raise ValueError, "cannot rebind bound application root "+repr((old_root_path_list, new_root_path_list))
        self.root_path_list = new_root_path_list
        self.root_path = "/"+"/".join(new_root_path_list)
        #pr "application root bound to parent at", new_root_path_list, "for root module", self.root_module

    def get_root_path_list(self):
        "get a list of components for the http path for this directory"
        if self.root_path_list:
            return self.root_path_list
        #clean_root_path = clean_component_name(self.root_path)
        r = self.root_path.split("/") #self.reduce_path_list(self.root_path)
        r1 = []
        for x in r:
            if not x or x==".":
                pass
            elif x=="..":
                if not r1:
                    raise ValueError, "root_path backs up past top "+repr((self.root_path, r))
                del r1[-1]
            elif x:
                r1.append(x)
        self.root_path_list = r1
        return r1
        
    def __repr__(self):
        #return "moduleRootApplication(%s, %s, %s, %s)" % (self.root_path, self.root_module, self.on_not_found, self.filter_middleware)
        return "Root(%s, %s)" % (id(self), self.root_path)

    def duplicate(self, **args):
        "create a copy of self for possible rebinding"
        return moduleRootApplication(self.root_path, self.root_module, self.on_not_found, self.filter_middleware, self.exception_middleware,
                                     self.environment, self.resourceGateway)

    def __call__(self, env, start_response, update_environment=None, additional_args=None):
        "call possibly protected by exception middleware"
        #pr "__call__", self
        env = modifiedEnvironment(env, self.environment, self)
        ucallable = self.unprotected_call
        exception_middleware = self.exception_middleware
        error_wrapper = env.get(whiffenv.ERROR_WRAPPER)
        envcopy = env
        if exception_middleware and not error_wrapper:
            envcopy = env.copy()
            envcopy[whiffenv.ERROR_WRAPPER] = exception_middleware
            ucallable = exception_middleware(page=ucallable)
        return ucallable(envcopy, start_response)
        
    def unprotected_call(self, env, start_response):
        "find the module component to respond to this http request and call it as a wsgi app"
        #pr "unprotected_call", self
        on_not_found = self.on_not_found
        if on_not_found is not None:
            # execute not_found app if resolution fails.
            try:
                app = self.resolve_env(env)
            except ModuleRootResolutionException:
                # XXXX what about logging errors?
                return on_not_found(env, start_response)
        else:
            # no special handling for pages not found
            app = self.resolve_env(env)
        # wrap the app with the filter if present (only for top level entry point, not for subsections)
        #pr "   apply filter to", app
        app = self.apply_filter(app)
        #pr "unprotected call calling app", app
        result = app(env, start_response)
        return result

    def setParent(self, parent):
        if (parent is not self) and (parent is not None) and (self.whiff_root_application is None):
            oldParent = self.whiff_root_application
            #assert oldParent is None or oldParent==parent, "cannot reset parent"
            self.whiff_root_application = parent

    def apply_filter(self, app):
        "apply local filter and any parent filter to the application"
        #pr ; #pr ; #pr "apply_filter", self
        #pr "    to", app
        #parent = self.whiff_root_application
        # parent will automatically wrap with filter
        #if parent:
        #    # allow the parent to override any no_filter directive
        #    # parent middleware executes first!
        #    #pr "    applying parent filter", parent
        #    app = parent.apply_filter(app) # CAUSES DOUBLE WRAPPING FOR PARENT
        filter_middleware = self.filter_middleware
        no_filter = getattr(app, "no_filter", False) or filter_middleware is None
        if no_filter:
            #pr "   no filter to apply", (getattr(app, "no_filter", False), filter_middleware)
            result =  app
        # otherwise apply filter_middleware
        else:
            if not filter_middleware.bound():
                filter_middleware = self.filter_middleware = filter_middleware.preBind(self, self.get_root_path_list())
            #pr "   applying", filter_middleware
            result = filter_middleware(page=app)
            # the filtered app should not accept any other filters
            result.no_filter = True
        #pr "apply_filter", self
        #pr "    returns", result
        #pr
        return result
    
    def resolve_env(self, env, init_args=None):
        "find the module component corresponding to this path: return wsgi app"
        the_path = env.get('PATH_INFO')
        #pr "resolving path info", repr(the_path)
        if the_path is None:
            raise ModuleRootResolutionException, "'PATH_INFO' not available in environment "+repr(env.keys())
        #pr "resolve_env resolving path info", the_path
        the_script = env.get('SCRIPT_NAME')
        if the_script is None:
            raise ModuleRootResolutionException, "'SCRIPT_NAME' not available in environment"
        if the_script:
            if not the_path:
                the_path = the_script
            else:
                sc = the_script
                if not sc.endswith("/"):
                    sc += "/"
                the_path = sc+the_path
        #pr "calling resolve for", repr(the_path)
        (app, responding_path, path_remainder) = self.resolve(the_path, init_args, env=env)
        # environment is always fresh, modification in place is okay (?)
        #pr "resolve gave", (app, responding_path, path_remainder)
        env[whiffenv.RESPONDING_PATH] = responding_path
        env[whiffenv.PATH_REMAINDER] = path_remainder
        # xxxx environment additions to support repoze.who -- need to know the top level page entry path information
        # APP_PATH_INFO and APP_PATH are not overridden by subordinate apps
        app_path_info = "/".join(path_remainder)
        if app_path_info and not app_path_info.startswith("/"):
            app_path_info = "/"+app_path_info
        if app_path_info:
            env["PATH_INFO"] = app_path_info #[1:] -- path info should start with slash
        script_name = "/".join(responding_path)
        if not script_name.startswith("/"):
            script_name = "/"+script_name
        #pr "RESOLVE_ENV RESETTING SCRIPT NAME", (env.get("SCRIPT_NAME"), script_name)
        env["SCRIPT_NAME"] = script_name
        #pr "ASSIGNED SCRIPT_NAME AND PATH_INFO", (env["SCRIPT_NAME"] , env["PATH_INFO"] )
        if env.get(whiffenv.APP_PATH_INFO) is None:
            env[whiffenv.APP_PATH_INFO] = app_path_info
            #pr "app_path_info", app_path_info
        if env.get(whiffenv.APP_PATH) is None:
            app_path = "/".join(responding_path)
            #if env.get("SCRIPT_NAME"):
            #    app_path = env["SCRIPT_NAME"] + "/" + app_path
            if app_path and not app_path.startswith("/"):
                app_path = "/"+app_path
            env[whiffenv.APP_PATH] = app_path
            #pr "app_path", app_path
        # xxxx end of repoze.who additions
        #pr "resolved app", app
        #pr "paths", (responding_path, path_remainder)
        return app

    def resolve(self, path, init_args=None, env=None):
        "find the bound application associated with the path"
        #pr self, "resolving", path
        #if init_args is None:
        #    init_args = {}
        old_init_args = init_args
        init_args = {}
        if old_init_args:
            # convert arg names to ascii
            for (a,b) in old_init_args.items():
                stringArgName = str(a)
                init_args[ stringArgName ] = b
        (application_factory_callable, responding_path, path_remainder) = self.resolve_application_factory_callable(path, env)
        #pr "resolve creating application using", application_factory_callable, init_args
        application = application_factory_callable(**init_args)
        # no (outer) bound arguments ???
        bound_arguments = {}
        #pr "calling bind_root", application
        #pr "   root", self
        #pr "   responding path", responding_path
        #pr "   path_remainder", path_remainder
        #pr "   bound_arguments", bound_arguments
        test = application.bind_root(self, responding_path, path_remainder, bound_arguments)
        if test is False:
            raise ModuleRootResolutionException("path binding refused by handler "+repr((path, application)))
        return (application, responding_path, path_remainder)

    def resolve_application_factory_callable(self, path, env=None, backtrack=True):
        "find an application factory callable associated with the path"
        #pr "resolving path", path
        path_list = self.reduce_path_list(path)
        #pr "resolve application path list", path_list, "for", repr(path)
        try:
            remainder = self.path_list_remainder(path_list)
        except ModuleRootResolutionException:
            # the path does not match the expected prefix.
            # XXXXX if the implementation is buggy this might cause an infinite loop
            root = self.whiff_root_application
            if root is None and env is not None:
                root = env.get(whiffenv.ROOT)
            while root is not None and root.whiff_root_application is not None  and root!=root.whiff_root_application:
                # go all the way to the top
                root = root.whiff_root_application 
            #pr "root application is", repr(root)
            if root is not None and root!=self and backtrack:
                # give the highest root a chance to resolve the path (hopefully it won't delegate back to self again...)
                #abspath = "/"+('/'.join(path_list))
                abspath = path
                #if not abspath.startswith("/"):
                #    abspath = self.root_path+"/"+path
                #pr self, "delegating resolution to root on", (root, path, abspath)
                result = root.resolve_application_factory_callable(abspath, env, backtrack=False)
                return result
            #wr("path list does not match required prefix "+repr((path,self.get_root_path_list()))+"\n")
            raise ModuleRootResolutionException, "path list does not match required prefix "+repr((path,path_list,self.get_root_path_list(), self.root_path))
        #pr "remainder is", remainder
        current_location = self.root_module
        index = 0
        for r in remainder:
            #pr "getting component", r, "from", current_location
            (new_location, success) = self.get_component(current_location, r)
            if not success:
                #pr "no such component found"
                break
            #pr "component found", (r, new_location)
            if self.auto_reload:
                new_location = self.update_location(new_location)
                pass
            current_location = new_location
            index += 1
        responding_path = self.get_root_path_list() + remainder[:index]
        path_remainder = remainder[index:]
        #pr "location found with responding path", responding_path, "remainder", path_remainder
        #pr "location is", current_location
        application_factory_callable = self.get_application_factory_callable(current_location, responding_path, path_remainder)
        if application_factory_callable is None:
            raise ModuleRootResolutionException("unable to resolve path "+repr((path, path_list)))
        #pr "resolved callable", (path, application_factory_callable, responding_path, path_remainder)
        return (application_factory_callable, responding_path, path_remainder)

    def update_location(self, location):
        "reload if needed"
        try:
            if type(location) is types.ModuleType:
                do_reload = False
                fn = location.__file__
                if fn.endswith(".pyc"):
                    fn = fn[:-1]
                if os.path.exists(fn):
                    fn_mtime = int( os.path.getmtime(fn) )
                    md_mtime = getattr(location, WHIFF_MTIME, None)
                    if md_mtime is not None:
                        if md_mtime<fn_mtime:
                            #pr "file changed: reloading module", (fn, location)
                            do_reload = True
                            md_mtime = fn_mtime
                    else:
                        md_mtime = fn_mtime
                    if not do_reload and hasattr(location, "__path__"):
                        path0 = location.__path__[0]
                        if os.path.exists(path0):
                            dir_mtime = int( os.path.getmtime(path0) )
                            if md_mtime<dir_mtime:
                                #pr "dir change: reloading package root", (location, dir_mtime)
                                do_reload = True
                                md_mtime = dir_mtime
                    #pr "setting load time", location, md_mtime
                    setattr(location, WHIFF_MTIME, md_mtime)
                if do_reload:
                    #pr "reloading", location
                    location = reload(location)
        except:
            #pr "exception in update_location", sys.exc_type, sys.exc_value
            raise
        return location
    
    def resolve_middleware(self, path, env=None):
        "find the middleware associated with the path"
        #pr "resolve middleware", path
        (application_factory_callable, responding_path, path_remainder) = self.resolve_application_factory_callable(path,env)
        #pr "got callable", application_factory_callable
        #pr "got responding path", responding_path
        #pr "got path_remainder", path_remainder
        if path_remainder:
            raise ModuleRootResolutionException, "path not completely resolved "+repr((responding_path, path_remainder))
        if isinstance(application_factory_callable, WsgiComponentFactory):
            #pr "prebinding middleware", application_factory_callable, self, responding_path
            application_factory_callable = application_factory_callable.preBind(self, responding_path)
        else:
            raise ValueError, "path does not resolve to middleware "+repr(path) #?? SHOULD THIS BE AN ERROR?
        return application_factory_callable
        
    def get_component(self, currentlocation, name):
        "find the subcomponent with the given name associated with the current location"
        #pr   "get_component: looking in", currentlocation, "for", name
        name = clean_component_name(name)
        if not getattr(currentlocation, DIRECTORY_SENTINEL, False):
            # permission to use this object as a wsgi_directory is not provided...
            #pr   "   no DIRECTORY_SENTINEL", DIRECTORY_SENTINEL
            return (currentlocation, False)
        if hasattr(currentlocation, name):
            #pr   "   found attribute", repr(name)
            component = getattr(currentlocation, name)
            return (component, True)
        if type(currentlocation) is types.ModuleType and name!="whiff_middleware":
            #pr ' attempt to force a "dotted" import', (name, currentlocation)
            try:
                my_import(name, currentlocation)
            except ImportError:
                #pr "got import error"
                pass
            if hasattr(currentlocation, name):
                ##pr "   found dotted import", repr(name)
                component = getattr(currentlocation, name)
                return (component, True)
        # finally if the name is "whiff_middleware" return the standard middleware
        if name=="whiff_middleware":
            import whiff.middleware # import here to avoid circularity
            #pr  "fake import of middleware module", (currentlocation, whiff.middleware)
            return (whiff.middleware, True)
        #pr "   get_component defaulting to failure"
        #pr "   get_component defaulting to failure"
        return (currentlocation, False)

    def get_application_factory_callable(self, current_location, responding_path, path_remainder):
        "find the class to use to create an application for the current location"
        # XXXX binding logic may need modification here (it seems inconsistent)
        #pr "getting factory callable", current_location
        loc_type = type(current_location)
        #pr "responding", responding_path
        #pr "path_remainder", path_remainder
        if loc_type is types.ModuleType:
            has_wsgi = hasattr(current_location, DEFAULT_WSGI_INTERPRETATION_NAME)
            has_middleware = hasattr(current_location, DEFAULT_WSGI_MIDDLEWARE)
            if has_wsgi and has_middleware:
                #pr "ambiguous", current_location
                #pr "   dir=", dir(current_location)
                #pr "   wsgi=", current_location.__wsgi__
                #pr "   middleware=", current_location.__middleware__
                #for x in dir(current_location):
                    #pr (x, getattr(current_location, x))
                raise ModuleRootResolutionException, "ambiguous module entries: could be middleware or application: "+repr((current_location,
                                                                                        DEFAULT_WSGI_INTERPRETATION_NAME, DEFAULT_WSGI_MIDDLEWARE))
            if has_wsgi:
                #pr "get_application_factory_callable returns default wsgi interpretation"
                newlocation = getattr(current_location, DEFAULT_WSGI_INTERPRETATION_NAME)
                newlocation = wrapApplication(newlocation)
                return newlocation.duplicate
            elif has_middleware:
                #pr  "get_application_factory_callable returns default wsgi middleware"
                newlocation = getattr(current_location, DEFAULT_WSGI_MIDDLEWARE)
                result = wrapMiddleware(newlocation)
                #pr "prebinding", (result, self, responding_path, path_remainder)
                result = result.preBind(self, responding_path, path_remainder)
                return result
            else:
                #return None # no application factory: let caller report the error
                raise NoDefaultForDirectoryException, "module does not have a registered wsgi interpretation "+repr((current_location, dir(current_location), responding_path, path_remainder))
        elif loc_type is types.ClassType:
            if issubclass(current_location, WsgiComponent):
                # found class!
                return current_location
            else:
                raise ModuleRootResolutionException, "class not permitted because it is not subclass "+repr(
                    (current_location, WsgiComponent))
        elif isinstance(current_location, WsgiComponentFactory):
            # found factory!
            #pr "prebinding", (current_location, self, responding_path, path_remainder)
            current_location = current_location.preBind(self, responding_path, path_remainder)
            return current_location
        elif isinstance(current_location, WsgiComponent):
            # found instance!
            #pr "returning instance duplicate method", current_location
            return current_location.duplicate
        else:
            raise ModuleRootResolutionException, "don't know how to get application factory for objects of this type "+repr(
                (current_location, loc_type))

    def path_list_remainder(self, path_list):
        "return the remainder of the path as a list after removing the prefix for self"
        rpl = self.get_root_path_list()
        #rpl = map(clean_component_name, rpl)
        lenrpl = len(rpl)
        if path_list[:lenrpl]!=rpl:
            #pr ("path list does not match required prefix "+repr((rpl, path_list))+"\n")
            raise ModuleRootResolutionException, "path list does not match required prefix "+repr((rpl, path_list))
        remainder = path_list[lenrpl:]
        return remainder

    def absolute_path(self, path, base_path_list=None, clean=True):
        absolute_path_list = self.reduce_path_list(path, base_path_list)
        result = "/"+"/".join(absolute_path_list)
        # nuke duplicate slashes
        while result.startswith("//"):
            result = result[1:]
        return result

    def reduce_path_list(self, path, base_path_list=None, clean=False):
        "find the absolute path corresponding to input path relative to self.root_path, returned as list of components"
        # XXXX should check where this logic may be inlined and replace...
        #pr "reduce_path_list", (path, base_path_list)
        result = []
        if base_path_list is None:
            if not path.startswith("/"):
                path = self.root_path+"/"+path
        else:
            if not path.startswith("/"):
                result = base_path_list[:-1]
        #pr "starting at", result
        L = path.split("/")
        for x in L:
            if x=="..":
                if not result:
                    raise ModuleRootResolutionException, "cannot reduce path above root "+repr(L)
                del result[-1]
            elif x and x!=".":
                if clean:
                    x = clean_component_name(x)
                result.append(x)
        return result
        
# the following was taken and slightly modified from
# ./Python-2.5.2/Demo/imputil/knee.py
# I'm not sure if this name uniqueness hack is really needed...
EMULATED_MODULE_LOAD_COUNTER = [0]

def import_module(partname, parent):
    "try to import module from parent"
    # XXX -- this sometimes reports an import error from a sub-module which is misinterpreted as a missing parent!
    count = EMULATED_MODULE_LOAD_COUNTER[0]
    EMULATED_MODULE_LOAD_COUNTER[0] = count+1
    #pr "trying import", (partname, parent, parent.__path__)
    try:
        fp, pathname, stuff = imp.find_module(partname,
                                              parent and parent.__path__)
    except ImportError:
        #pr "ImportError"
        return None
    #pr "found", (fp, pathname, stuff)
    try:
        loadname = partname+"_"+str(count) # make sure the partname is unique... ?
        try:
            m = imp.load_module(partname, fp, pathname, stuff) # XXXX is first arg right?
        except ImportError:
            return my_import(partname, parent)
        except:
            #pr "exception from load_module", sys.exc_type, sys.exc_value
            raise
    finally:
        if fp: fp.close()
    if parent:
        #pr "in", parent, "setting", partname, "to", m
        setattr(parent, partname, m)
    return m

def my_import(partname, parent):
    parentname = parent.__name__
    name = '%s.%s' % (parentname, partname)
    try:
        __import__(name)
    except ImportError:
        parent = __import__(parentname)
        reload(parent)
        try:
            __import__(name)
        except ImportError:
            info = sys.exc_info()
            (ty, ex, tb) = info
            sex = str(ex)
            test = sex.find(partname)
            if test>0:
                 raise ImportError("could not locate %s in parent %s" % (partname, parent))
            else:
                 raise WhiffTemplateImportProblem("when locating %s in %s recieved import error %s" % (partname, parent, sex))
    return sys.modules[name]

class FileContentApplication(WsgiComponent):
    "application to deliver the content of the file using the mime type"
    def __init__(self, file_path, mime_type):
        assert file_path is not None, "no path?"
        self.file_path = file_path
        self.mime_type = mime_type
        self.__doc__ = "static file"
    def duplicate(self, **args):
        result = FileContentApplication(self.file_path, self.mime_type)
        result.__doc__ = self.__doc__
        return result
    def whiff_call(self, env, start_response, update_environment=None, additional_args=None):
        if update_environment:
            env = update_environment(env)
        try:
            f = open(self.file_path, "rb")
        except IOError:
            raise ModuleRootResolutionException("could not read file "+repr(self.file_path))
        content = f.read()
        content_length = str(len(content))
        headers = [
            ('Content-Type', self.mime_type),
            ("Cache-Control", "max-age=20000000, public"),
            ("Expires", "Thu, 1 Apr 2023 20:00:00 GMT"),
            ('CONTENT_LENGTH', content_length)
            ]
        start_response('200 OK', headers)
        return [content]

class BasicDirectoryListingTable(WsgiComponent):
    "non-featurized directory listing, for testing and simple use"
    def __init__(self, dir_path):
        self.__doc__ = "basic listing for %s" % repr(dir_path)
        self.dir_path = dir_path
    def duplicate(self, **args):
        result = BasicDirectoryListingTable(self.dir_path)
        result.__doc__ = self.__doc__
        return result
    def check_env(self, env):
        "stub for subclasses: could make sure that env points to this directory, if required, for example"
        return None
    def whiff_call(self, env, start_response, update_environment=None, additional_args=None):
        if update_environment:
            env = update_environment(env)
        self.check_env(env)
        root_app = self.whiff_root_application
        #p "for", self, "root_app", root_app
        dir_path = self.dir_path
        http_dir_path = env["SCRIPT_NAME"]+env["PATH_INFO"]
        try:
            st = os.stat(dir_path)
        except OSError:
            raise ModuleRootResolutionException("could not stat directory")
        if not os.path.isdir(dir_path):
            raise ModuleRootResolutionException("cannot list non-directory")
        filenames = os.listdir(dir_path)
        L = [ "<h1>Directory listing for %s</h1>" % repr(dir_path) ]
        L.append(" <em> http: %s </em><br> " % repr(http_dir_path) )
        L.append("<table border>")
        L.append("<tr> <th> file </th> <th> size </th> <th> type </th> <th> handler documentation </th> </tr>")
        if filenames:
            for filename in filenames:
                #file_path = os.path.join(dir_path, filename)
                file_path = pathjoin(dir_path, filename)                
                absolute_path = http_dir_path+"/"+filename
                link = '<a href="%s">%s</a>' % (filename, filename)
                st = os.stat(file_path)
                size = st[6]
                (mime_type, encoding) = mimetypes.guess_type(filename)
                if encoding and mime_type:
                    mime_type = "%s/%s" % (mime_type, encoding)
                doc = "n/a"
                if not root_app:
                    doc = "no resolver"
                if root_app and http_dir_path:
                    http_path = "%s/%s" % (http_dir_path, filename)
                    #p "attempting to resolve", http_path
                    try:
                        (resolution, rp, pr) = root_app.resolve(http_path, env=env)
                    except NoDefaultForDirectoryException:
                        doc = "directory with no 'listing' function defined"
                        link = filename # disable link
                    except ModuleRootResolutionException:
                        doc = "not reachable (no handler found)"
                        link = filename # disable link
                    else:
                        if hasattr(resolution, "__doc__") and resolution.__doc__:
                            doc = "documented resolver: "+str(resolution.__doc__)
                        else:
                            tr = type(resolution)
                            if tr is types.ClassType:
                                doc = "class "+repr(resolution.__name__)
                            elif tr is types.InstanceType:
                                doc = "instance of class "+repr(resolution.__class__.__name__)
                            else:
                                doc = "undocumented resolver: "+repr(type(resolution).__name__)
                L.append('<tr>')
                L.append('<td valign="top">%s</td>' % link)
                L.append('<td valign="top">%s</td>' % size)
                L.append('<td valign="top">%s</td>' % mime_type)
                L.append('<td>%s</td>' % doc)
                L.append('</tr>')
        else:
            L.append('<tr> <th colspan="4"> No files. </th> </tr>')
        L.append("</table>")
        text = "\n".join(L)
        content_length = str(len(text))
        mime_type = "text/html"
        start_response('200 OK', [('Content-Type', mime_type), ('CONTENT_LENGTH', content_length)])
        return [text]

def wrapped_application(thing):
    "duplicate, instantiate or wrap thing as a WsgiComponent."
    if isinstance(thing, WsgiComponent):
        return thing.duplicate()
    if isinstance(thing, WsgiComponentFactory):
        return thing.makeWsgiComponent()
    return publish_wsgi_callable(thing)

class ContentOfDirectoryByMime(WsgiComponent):
    "deliver files in directory using the mime type associated with the file extension"
    default_mime_type = "application/octet-stream"
    def __init__(self, dir_path, index_application):
        self.dir_path = dir_path
        self.index_application = index_application
        self.__doc__ = "content of directory by Mime types for "+repr(dir_path)
    def __repr__(self):
        return self.__class__.__name__+repr((self.dir_path, self.whiff_responding_path, self.whiff_path_remainder))
    def duplicate(self, **args):
        # import here to avoid circularity issues
        #from whiff.middleware import redirect
        result = self.__class__(self.dir_path, self.index_application)
        result.__doc__ = self.__doc__
        return result
    def whiff_call(self, env, start_response, update_environment=None, additional_args=None):
        if update_environment:
            env = update_environment(env)
        remainder = self.whiff_path_remainder
        #pr "dirByMime called with responding path", self.whiff_responding_path, "remainder", remainder
        if not remainder:
            # directory index request: must redirect to "/" if the request doesn't end in "/" (otherwise relative urls break)
            #pr "directory index", self, "remainder", remainder
            request = env.get("SCRIPT_NAME", "") + env.get("PATH_INFO", "")
            if not request.endswith("/"):
                #url = reconstruct_url(env, False)+"/"
                url = request_uri(env, False)+"/"
                #pr "redirecting to", repr(url)
                from whiff.middleware.redirect import redirect
                page = wrapped_application(redirect(url))
                page.bind_root(self.whiff_root_application, self.whiff_responding_path, self.whiff_path_remainder, self.whiff_outer_arguments)
                return page(env, start_response)
            # otherwise bind and send the index_app if specified
            index_app = self.index_application
            if index_app is not None:
                page = wrapped_application(index_app)
                page.bind_root(self.whiff_root_application, self.whiff_responding_path, self.whiff_path_remainder, self.whiff_outer_arguments)
                return page(env, start_response)
            # otherwise send the default directory content
            return self.directory_content(env, start_response)
        lenRemainder = len(remainder)
        if lenRemainder>1:
            raise ModuleRootResolutionException("sub-directory is not viewable "+repr(remainder))
        if lenRemainder<1:
            return self.directory_content(env, start_response)
        else:
            #raise ValueError, "disabled"
            path = env["SCRIPT_NAME"] + env["PATH_INFO"]
            path = os.path.normpath(path)
            filename = os.path.split(path)[-1]
            #filename = remainder[-1]
            return self.file_content(filename, env, start_response)
    def directory_content(self, env, start_response):
        raise ModuleRootResolutionException("directory content view not permitted")
    def file_content(self, filename, env, start_response):
        test = self.special_file_content(filename, env, start_response)
        if test is not None:
            return test
        test = self.mime_file_content(filename, env, start_response)
        if test is not None:
            return test
        return self.unknown_mime_file_content(file, env, start_response)
    def mime_file_content(self, filename, env, start_response):
        dmt = self.default_mime_type
        (mime_type, encoding) = mimetypes.guess_type(filename)
        if dmt and (not mime_type or encoding):
            mime_type = dmt
            encoding = False
        if not mime_type:
            return None # handled by other method
        if encoding:
            raise ModuleRootResolutionException("encoded content") # XXXX fix this someday
        #file_path = os.path.join(self.dir_path, filename)
        file_path = pathjoin(self.dir_path, filename)
        fc = FileContentApplication(file_path, mime_type)
        return fc(env, start_response)
    def special_file_content(self, filename, env, start_response):
        return None # this is stub for subclass extension
    def unknown_mime_file_content(self, filename, env, start_response):
        raise ModuleRootResolutionException("unknown mime type")

class MimeDirectoryWithListing(ContentOfDirectoryByMime):
    "deliver files using the mime type associated with the file extension.  Deliver directory for root"
    def paths_ok(self, responding_path, path_remainder):
        # refuse to serve any path that has more than one remainder
        if path_remainder and len(path_remainder)>1:
            #pr "MIME DIRECTORY DOESN'T LIKE PATH REMAINDERS", path_remainder
            return False
        return True
    def directory_content(self, env, start_response):
        dir_path = self.dir_path
        app = BasicDirectoryListingTable(dir_path)
        bound_arguments = {}
        app.bind_root(self.whiff_root_application, self.whiff_responding_path, self.whiff_path_remainder, bound_arguments)
        return app(env, start_response)

class LazyPageFromFile(WsgiComponentFactory):
    "create a page by parsing file, only when requested (lazy)"
    def __init__(self, filepath=None, text=None):
        if filepath is None and text is None:
            raise ValueError, "one of filepath or text must be provided"
        self.text = text
        self.filepath = filepath
        self.page = None
        self.loadtime = 0
    def clone(self):
        result =  LazyPageFromFile(self.filepath, self.text)
        result.page = self.page
        result.loadtime = self.loadtime
        return result
    def __repr__(self):
        t = self.filepath
        if t is None:
            t = self.text[:10]
        return "LazyPageFromFile"+ repr((t,))
    def makeWsgiComponent(self, **args):
        import parseTemplate
        #pr repr(self)
        #pr "lazy page making component args=", args, "root=", self.whiff_root_application
        #pr "filename = ", self.filepath
        page = self.page
        filepath = self.filepath
        inString = self.text
        if page and filepath and inString is None:
            # check whether the file has been modified
            loadtime = self.loadtime
            mtime = os.path.getmtime(filepath)
            if loadtime<mtime:
                # expire the cached page
                #pr "CACHED PAGE TEMPLATE EXPIRED", mtime, loadtime
                page = self.page = None
        if page is None:
            # parse the page
            if inString is None:
                f = open(filepath)
                inString = f.read()
                self.loadtime = time.time()
                #pr "PAGE LOADED FROM FILE", (filepath, self.loadtime)
                f.close()
            if filepath is None:
                filepath = "[literal string: "+repr(inString[:20])+"...]"
            (test, result, cursor) = parseTemplate.parse_page(inString, file_path=filepath)
            if test:
                page = result
            else:
                parsedPart = inString[:cursor]
                parsedLines = parsedPart.split("\n")
                lineNo = len(parsedLines)
                chunk1 = inString[max(cursor-80,0):cursor]
                chunk2 = inString[cursor:cursor+80]
                raise ValueError, ("For template file "+repr(self.filepath)+
                                   " near line "+str(lineNo)+
                                   " page parse reports error: "+repr((cursor, result, chunk1, chunk2)))
            self.page = page
        result = page.makeWsgiComponent(**args)
        result.__doc__ = self.__doc__
        return result

def template(text, filepath=None):
    "conveniece abbreviation"
    return LazyPageFromFile(filepath, text)

def callUrl(url, env, start_response, relative_url=None):
    "import an application (with no middleware parameters) defined using relative URL"
    #pr "calling url", url
    import urlcomponent
    env = env.copy()
    if relative_url is None:
        relative_url = env[whiffenv.RESPONDING_PATH]
    root = env[whiffenv.ROOT]
    absurl = urlcomponent.resolveUrl(url, relative_url)
    env["PATH_INFO"] = ""
    #pr "CALLURL RESETTING SCRIPT NAME", (env.get("SCRIPT_NAME"), absurl)
    env["SCRIPT_NAME"] = absurl
    try:
        application = root.resolve_env(env)
    except ModuleRootResolutionException:
        raise ValueError, "cannot call url %s -- module not found wrt %s" % (
            repr(url), repr(relative_url))
    return application(env, start_response)

def middlewareFromUrl(url):
    "import a simple middleware defined in URL as a python component"
    if '"' in url:
        raise ValueError, "url may not contain quote "+repr(url)
    templateText = '{{require page/}}{{include "%s"}} {{use page/}}{{/include}}' % url
    return template(templateText)

def publish_class(wsgi_class):
    "make a class 'visible' for automatic detection"
    return WsgiClassWrapper(wsgi_class)

def publish_wsgi_callable(wsgi_callable):
    "make a callable 'visible' for automatic detection"
    return wrapApplication(wsgi_callable)

class WsgiClassWrapper(WsgiComponentFactory):
    "marker wrapper which marks an application class as published and suitable for automatic detection as a WSGI component factory"
    def __init__(self, wsgi_class):
        self.wsgi_class = wsgi_class
    def clone(self):
        return WsgiClassWrapper(self.wsgi_class)
    def __repr__(self):
        return "CWrap( %s )" % repr(self.wsgi_class)
    def makeWsgiComponent(self, **args):
        #pr "now calling", self.wsgi_class
        #pr "with", args.keys()
        # hold off on making the instance... may need to bind the arguments
        #wsgi_instance = self.wsgi_class(**args)
        wsgi_instance = None
        #p "WsgiClassWrapper.makeWsgiComponent got instance", wsgi_instance
        result = WsgiApplicationWrapper(wsgi_instance, self.wsgi_class, args)
        #p "WsgiClassWrapper.makeWsgiComponent returning", wsgi_instance
        # middleware should not accept filters (?)
        if self.whiff_root_application:
            #pr "binding root for wsgiclasswrapper component"
            test = result.bind_root(self.whiff_root_application, self.whiff_responding_path, self.whiff_path_remainder, self.whiff_outer_arguments)
        result.no_filter = True
        return result

class WsgiApplicationWrapper(WsgiComponent):
    "marker wrapper which marks wsgi-callable as published and suitable for automatic detection as a WSGI component"
    def __init__(self, wsgi_callable, wsgi_factory=None, wsgi_factory_args=None, bind_root_operation=None):
        #from whiff.middleware.repoze import who
        #if bind_root_operation is None and isinstance(wsgi_callable, WsgiComponent):
        #    bind_root_operation = wsgi_callable.bind_root
        self.wsgi_callable = wsgi_callable
        self.wsgi_factory = wsgi_factory
        if wsgi_factory and wsgi_factory_args is None:
            wsgi_factory_args = {}
        self.wsgi_factory_args = wsgi_factory_args
        self.bind_root_operation = bind_root_operation
        self.root_application = None
        self.responding_path = None
        self.path_remainder = None
        self.outer_arguments = None        
        assert wsgi_callable is None or wsgi_factory is None, "cannot define both callable and factory"
        assert wsgi_callable is not None or wsgi_factory is not None, "must define one of callable or factory"
    def __repr__(self):
        #return "WsgiApplicationWrapper(%s, %s, %s)" % (self.wsgi_callable, self.wsgi_factory, self.wsgi_factory_args)
        return "WsgiApplicationWrapper( %s, %s, %s )" % (id(self), self.wsgi_callable, self.wsgi_factory )
    def bind_root(self, root_application, responding_path, path_remainder, outer_arguments):
        #pr "binding root", self
        WsgiComponent.bind_root(self, root_application, responding_path, path_remainder, outer_arguments)
        self.root_application = root_application
        self.responding_path = responding_path
        self.path_remainder = path_remainder
        self.outer_arguments = outer_arguments
        br = self.bind_root_operation
        if br is not None:
            #p "delegating to", br
            return br(root_application, responding_path, path_remainder, outer_arguments)
        #p"done binding root", self
        return True
    def duplicate(self, **args):
        "create a copy of self for rebinding"
        #pr "duplicating", self
        wcallable = self.wsgi_callable
        factory = self.wsgi_factory
        old_args = self.wsgi_factory_args
        new_args = old_args
        if old_args:
            new_args = old_args.copy()
            for key in old_args.keys():
                if args.has_key(key):
                    new_args[key] = args[key]
        result = WsgiApplicationWrapper(wcallable, factory, new_args, self.bind_root_operation)
        if self.whiff_lexical_arguments:
            #pr "wrapper duplicating lexical arguments", self.whiff_lexical_arguments.keys()
            result.whiff_lexical_arguments = self.whiff_lexical_arguments.copy()
        return result
    def whiff_call(self, env, start_response, update_environment=None, additional_args=None):
        "generate page for application."
        #pr "wrapper whiff_call", self
        #pr "lexical args", self.whiff_lexical_arguments
        if update_environment:
            env = update_environment(env)
        else:
            env = env.copy()
        #if self.responding_path is not None:
            # adjust path information in environment
            #pr "adjusting responding path", env[whiffenv.RESPONDING_PATH], self.responding_path
            #env[whiffenv.RESPONDING_PATH] = self.responding_path
            #env[whiffenv.PATH_REMAINDER] = self.path_remainder
            #pass
        #pr "WsgiApplicationWrapper calling wsgi_callable", self
        wcallable= self.wsgi_callable
        generatedHere = False
        if wcallable is None:
            generatedHere = True
            factory = self.wsgi_factory
            args = self.wsgi_factory_args
            root_application = self.root_application
            responding_path = self.responding_path
            path_remainder = self.path_remainder
            outer_arguments = self.outer_arguments
            bound_args = args
            #pr "binding arguments for args"
            if root_application:
                try:
                    bound_args = {}
                    # bind the args
                    #pr "wrapping arg variable=", env.get("variable")
                    for (k,v) in args.items():
                        #pr "binding", v
                        #v = wrapped_application(v)
                        if not isinstance(v, WsgiComponent):
                            #pr "WRAPPING", v
                            #v = wrapped_application(v)
                            pass
                        if hasattr(v, "bind_environment"):
                            #pr "binding environment", v
                            #pr v.bind_environment
                            #pr "additional_args", additional_args
                            v.bind_environment(None, additional_args)
                        bound_args[k] = v
                except:
                    #pr "ERROR IN ARGUMENT BINDING"
                    #pr sys.exc_info()
                    raise
            else:
                #pr "can't bind environment for args"
                pass
            try:
                wcallable = factory(**bound_args)
            except:
                #pr "exception from factory", factory
                #pr "with bound arguments", bound_args
                raise
            # now bind the callable
            if root_application is not None and isinstance(wcallable, WsgiComponent):
                wcallable.bind_root(root_application, responding_path, path_remainder, outer_arguments)
        try:
            #pr "wsgi wrapper calling wcallable", (wcallable, start_response)
            #return wcallable(env, start_response)
            # returned normalized WSGI call
            return normalize(wcallable, env, start_response)
        except:
            #pr "exception calling", wcallable
            raise

def publish_templates(from_path, in_globals, extension=".whiff", mime_extensions=False, directory_middleware="index"):
    "publish as whiff configuration templates any file in directory from_path ending in extension in in_globals."
    from whiff.middleware import redirect
    len_ext = len(extension)
    filenames = os.listdir(from_path)
    nameToInfo = {}
    nameToUrl = {}
    urlToPage = {}
    for filename in filenames:
        splitfn = filename.split(".")
        filepath = pathjoin(from_path, filename)
        if os.path.isdir(filepath):
            nameToInfo[filename] = "sub-directory"
            nameToUrl[filename] = filename
        elif filename.endswith(extension):
            #filepath = os.path.join(from_path, filename)
            page = LazyPageFromFile(filepath)
            component_name = filename[:-len_ext]
            variable_name = clean_component_name(component_name)
            #pr "for", in_globals.get("__name__")
            #pr "....setting", variable_name, "whiff template to", page
            in_globals[variable_name] = page
            nameToInfo[filename] = "whiff configuration template"
            nameToUrl[filename] = component_name
            urlToPage[component_name] = page
        elif len(splitfn)==2 and splitfn[1] in ("py", "pyc"):
            nameToInfo[filename] = "python code file"
            nameToUrl[filename] = splitfn[0]
        elif mime_extensions:
            # try to guess mime type
            (mime_type, encoding) = mimetypes.guess_type(filename)
            if encoding and mime_type:
                mime_type = "%s/%s" % (mime_type, encoding)
            elif mime_type is None:
                mime_type = "text/plain" # default
            variable_name = clean_component_name(filename)
            page = FileContentApplication(filepath, mime_type)
            #pr "recognized mime type", variable_name, "set to", page
            in_globals[variable_name] = page
            nameToInfo[filename] = "static file of type "+mime_type
            nameToUrl[filename] = filename
            urlToPage[filename] = page
    if directory_middleware and in_globals.get(DEFAULT_WSGI_INTERPRETATION_NAME) is None:
        directory_page = None
        if directory_middleware==True:
            #pr "for", in_globals.get("__file__"), "using table"
            directory_middleware = directoryTable
        if type(directory_middleware) in types.StringTypes:
            if urlToPage.has_key(directory_middleware):
                #pr "for", in_globals.get("__file__"), "using index page", directory_middleware
                directory_middleware = urlToPage[directory_middleware]
            else:
                directory_middleware = None # no index page found
        if directory_page is None and directory_middleware is not None:
            #pr "for", in_globals.get("__file__"), "using provided middleware", directory_middleware
            wrapped_directory_middleware = wrapMiddleware(directory_middleware)
            directory_page = wrapped_directory_middleware.makeWsgiComponent(
                nameToInfo=nameToInfo, nameToUrl=nameToUrl)
        if directory_page is not None:
            
            directory_url = "__whiff_directory_listing__"
            redirect_directory = listingRedirect(directory_url)
            #pr "for", in_globals.get("__file__"), "setting", directory_url, directory_page
            in_globals[directory_url] = directory_page
            in_globals[DEFAULT_WSGI_INTERPRETATION_NAME] = redirect_directory

class listingRedirect:
    def __init__(self, directory_url):
        self.directory_url = directory_url
    def __call__(self, env, start_response):
        from whiff.middleware import redirect
        ep = env[whiffenv.ENTRY_POINT]
        #pr "redirect responding_path "+repr(env.get(whiffenv.RESPONDING_PATH))+"<br>\n"
        #pr "path_remainder "+repr(env.get(whiffenv.PATH_REMAINDER))+"<br>\n"
        #pr "env", "\n".join(map(repr, env.items()))
        responding_path = env.get(whiffenv.RESPONDING_PATH)
        path_remainder = env.get(whiffenv.PATH_REMAINDER)
        if path_remainder:
            raise ModuleRootResolutionException("cannot find whiff interpretation for path "+\
                                                repr((responding_path, path_remainder)))
        directory_url = self.directory_url
        if ep.find(directory_url)>0:
            raise ModuleRootResolutionException("looping attempting to find interpretation for path" +\
                                                repr((responding_path, path_remainder, ep))+
                                                " this usually means a include points to a non-existant location")
        redirect_to = ep+"/"+self.directory_url
        while redirect_to.startswith("//"):
            redirect_to = redirect_to[1:]
        #pr "redirecting to", redirect_to
        app = redirect.redirect(redirect_to)
        return app(env, start_response)

class directoryTable:
    def __init__(self, nameToInfo, nameToUrl):
        self.nameToInfo = nameToInfo
        self.nameToUrl = nameToUrl
    def __call__(self, env, start_response):
        start_response('200 OK',  [('Content-Type','text/html')])
        return self.responseGenerator(env)
    def responseGenerator(self, env):
        n2i = self.nameToInfo
        n2u = self.nameToUrl
        names = n2i.keys()
        names.sort()
        yield "default whiff directory listing<br>\n"
        yield "responding_path "+repr(env.get(whiffenv.RESPONDING_PATH))+"<br>\n"
        yield "path_remainder "+repr(env.get(whiffenv.PATH_REMAINDER))+"<br>\n"
        yield '<table border>\n'
        for name in names:
            yield '<tr>'
            yield '<td>'
            u = n2u.get(name)
            if u:
                yield '<a href="%s">%s</a>' % (u,name)
            yield '</td>'
            yield '<td>'
            i = n2i.get(name)
            if i:
                yield i
            yield '</td>'
            yield '</tr>\n'
        yield '</table>\n'

def pathjoin(*paths):
    "avoid regression test errors on different platforms by always using forward slashes to join path components..."
    return "/".join(paths)

quotePairs = [("&amp;", "&"),  ("&lt;", "<"), ("&gt;", ">"), ("&quot;", '"')]

def quote(result, quotePairs=quotePairs):
    "quote string for embedding in html"
    #pr "quoting", repr(result)
    result = stream.myunicode(result)
    for (quoted, unquoted) in quotePairs:
        result = result.replace(unquoted, quoted)
    #pr "quoted result", repr(result)
    #result = stream.mystr(result)
    return result

def entitiesOk(result):
    "unquote just the entities"
    return result.replace("&amp;", "&")

unquotePairs = [("lt;", "<"), ("quot;", '"'), ("gt;", ">"),  ("amp;", "&")]

def unquote(result, unquotePairs=unquotePairs):
    "convert quoted html text into unquoted html text"
    # this is not an efficient algorithm for very large strings with lots of quoted values.
    sresult = result.split("&")
    lresult = [sresult[0]]
    for fragment in sresult[1:]:
        #pr "processing", fragment
        replaced = ""
        kept = fragment
        fixed = "&"
        for (quoted, unquoted) in unquotePairs:
            lq = len(quoted)
            prefix = fragment[:lq].lower()
            if prefix==quoted:
                fixed = unquoted
                kept = fragment[lq:]
                #pr "matched", (fixed, kept)
                break
        #pr "appending", (fixed,kept)
        if fixed:
            lresult.append(fixed)
        if kept:
            lresult.append(kept)
    result = "".join(lresult)
    #pr "unquote Html returning", [result]
    return result

# put at bottom to prevent module circularity problems
#import parseTemplate
#from whiff.middleware.redirect import redirect
from wsgiref.util import request_uri
#import whiff.middleware
import stream
from normalizeWsgiApplication import normalize
