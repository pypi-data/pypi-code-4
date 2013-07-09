\
import whiffenv
import types
import resolver
import sys
import page

StreamError = ValueError

class StreamComponent:
    "virtual superclass for things which may occur in a stream"
    parent_path = None
    file_path = None
    def bound_copy(self, in_stream, arguments, root_application, responding_path, path_remainder):
        "make a copy of self with arguments bound to the object (if needed)"
        raise ValueError, "virtual method must be implemented in subclass"
    def __call__(self, env, start_response):
        raise ValueError, "virtual method must be implemented in subclass"

def bind_arguments(arguments, outer_arguments, root_application, responding_path, path_remainder, file_path):
    #pr "stream.bind_argument"
    #pr "   arguments", arguments
    #pr "   outer_arguments", outer_arguments
    #pr "   root_application", root_application
    #pr "   responding_path", responding_path
    #pr "   path_remainder", path_remainder
    boundArguments = {}
    for (k,v) in arguments.items():
        #pr "        now binding", (k,v)
        boundV = v
        boundK = mystr(k)
        if isinstance(v, resolver.WsgiComponentFactory):
            #boundV = v.makeWsgiComponent(**outer_arguments)
            boundV = deferBindings(v, outer_arguments, file_path)
            boundV.bind_root(root_application, responding_path, path_remainder, outer_arguments)
        #pr "        bound as", (boundK, boundV)
        boundArguments[boundK] = boundV
    return boundArguments

def ignore_start_response(*arguments):
    "start_response which does nothing (for generating stream content outside of web context)"

# this import is low to avoid circular import issues.
#import resolver

class StreamApp(resolver.WsgiComponent):
    "wrapper for a sequence of applications used to construct a page, with other information"

    # allow outer arguments of containing streams to be visible
    Lexical = True
    
    def __init__(self, overrides, arguments, cgi_defaults, component_list, default_arguments, #id_overrides,
                 default_content_type="text/html", default_status='200 OK'):
        #ast type(cgi_defaults) is types.DictionaryType, "cgi_defaults must be a dict"
        #pr "stream", id(self), component_list
        #pr "with cgi_defaults", cgi_defaults
        #pr "at init overrides are", overrides
        #self.id_overrides = id_overrides
        #self.bound_id_overrides = None
        self.overrides = overrides
        #pr "in stream", id(self), "initial args", arguments.keys()
        self.arguments = arguments
        self.default_arguments = default_arguments
        self.cgi_defaults = None
        self.unbound_cgi_defaults = cgi_defaults
        self.components = None
        self.root_application = self.responding_path = self.path_remainder = None
        self.unbound_components = component_list
        self.content_type = None
        self.response_headers = {}
        self.statuses = {}
        self.default_content_type = default_content_type
        self.default_status = default_status
        self.status = None
        self.additional_headers = None
        self.file_path = None
        self.parent_path = None
        # if environment overrides specifies no filter then disable filters for this page
        self.no_filter = not overrides.get(whiffenv.DO_FILTER, True)
        self.bound_to_root = False
        self.text = None
        self.bound_arguments = None
        #pr "stream", self, "initted"
        #pr "with components", self.unbound_components
        #assert len(component_list)>0, "components cannot be empty: "+repr(self)
    def get_content(self, env):
        contentSequence = list( self(env, ignore_start_response) )
        result = "".join(contentSequence)
        return result
    def __repr__(self):
        bound = "not bound"
        ncomponents = None
        if self.components is not None:
            ncomponents = len(self.components)
        if self.file_path:
            return "Stream( %s : %s : %s )" % (id(self), self.file_path, ncomponents)
        else:
            return "Stream( %s :: %s : %s : %s )" % (id(self), repr(self.text), ncomponents, self.parent_path)
        #if self.root_application:
        #    bound = repr(self.root_application)
        #return "StreamApp[%s]"%bound + repr((id(self), self.file_path))
    def updateArguments(self, dictionary):
        "add additional argument definitions"
        #pr "in stream", id(self), "update args", dictionary.keys()
        self.arguments.update(dictionary)
        if self.bound_to_root:
            # rebind components also
            self.bind_root(self.root_application, self.responding_path, self.path_remainder, self.outer_arguments, force=True)
    def bind_root(self, root_application, responding_path, path_remainder, outer_arguments=None, force=False):
        #pr "binding root for stream", id(self), repr(self)
        #pr "   file path is", self.file_path
        #pr "   text is", repr(self.text)
        #pr "   root_application", root_application
        #pr "   responding_path", responding_path
        #pr "   path_remainder", path_remainder
        #pr "   outer_arguments", outer_arguments
        if self.bound_to_root and not force:
            #pr "STREAM PREVENTING REBIND ATTEMPT for", id(self)
            if self.unbound_cgi_defaults:
                assert self.cgi_defaults is not None, "cgi defaults not bound "+repr(self.unbound_cgi_defaults)
            #pr "   old root", self.bound_to_root, self.root_application
            #pr "   old responding_path", self.responding_path
            return True
        if outer_arguments is None:
            outer_arguments = {}
        self.root_application = root_application
        self.responding_path = responding_path
        self.path_remainder = path_remainder
        self.outer_arguments = outer_arguments
        file_path = self.file_path
        my_bound_arguments = bind_arguments(self.arguments, outer_arguments,
                                            root_application, responding_path, path_remainder, file_path)
        #pr "in stream", self
        #pr "args", self.arguments.keys()
        #pr "outer args", outer_arguments.keys()
        bound_arguments = outer_arguments.copy()
        #pr "adding my_bound_args", my_bound_arguments.keys()
        bound_arguments.update(my_bound_arguments)
        #pr "FOR STREAM", self
        #pr "BOUND ARGUMENTS", bound_arguments.keys()
        self.bound_arguments = bound_arguments
        # bind the overrides
        #self.bound_id_overrides = bind_arguments(self.id_overrides, bound_arguments,
        #root_application, responding_path, path_remainder, file_path)
        #pr "CALLING CGI DEFAULTS FOR STREAM", self
        #pr "WITH UNBOUND", self.unbound_cgi_defaults
        cgi_defaults = {}
        for (name, cgiPage) in self.unbound_cgi_defaults.items():
            if isinstance(cgiPage, page.Page):
                cgiStream = cgiPage.makeWsgiComponent() # no arguments allowed!
                cgiStream.bind_root(root_application, responding_path, path_remainder, outer_arguments)
                cgi_defaults[name] = cgiStream
            else:
                cgi_defaults[name] = cgiPage # should be a string...
        self.cgi_defaults = cgi_defaults
        # components should be bound last because they may use the other bindings
        #self.components = [ c.bound_copy(self, bound_arguments, root_application, responding_path, path_remainder)
        #                    for c in self.unbound_components]
        components = []
        path = self.file_path
        if not path:
            path = self.parent_path
        for uc in self.unbound_components:
            #pr "  now binding", uc
            bc = uc.bound_copy(self, bound_arguments, root_application, responding_path, path_remainder)
            bc.parent_path = path
            #pr "  bound", uc
            #pr "  as", bc
            components.append(bc)
        self.components = components
        #pr "stream", self, "bound to root"
        #pr "with components", self.components
        self.bound_to_root = True
        return True # binding accepted
    def get_cgi_default(self, name):
        return self.cgi_defaults.get(name)
    def duplicate(self, **args):
        "make a fresh copy for new binding"
        allArgs = args.copy()
        allArgs.update(self.arguments)
        result = self.__class__(self.overrides, allArgs, self.unbound_cgi_defaults,
                                self.unbound_components, self.default_arguments, #self.id_overrides,
                                self.default_content_type, self.default_status)
        result.file_path = self.file_path
        result.text = self.text
        # if these are set they override any rebind attempt (???)
        result.root_application = self.root_application
        result.responding_path = self.responding_path
        result.path_remainder = self.path_remainder
        result.components = self.components
        result.content_type = self.content_type
        result.bound_to_root = self.bound_to_root
        result.bound_arguments = self.bound_arguments
        result.cgi_defaults = self.cgi_defaults
        result.whiff_bound_environment = self.whiff_bound_environment
        #result.bound_id_overrides = self.bound_id_overrides
        #pr "stream duplicate generated", result
        #pr "duplicate of", self
        #pr "with components", result.components
        return result
    def my_start_response(self, status, response_headers):
        #pr repr(self.text)
        #pr "my_start_response", (status, response_headers)
        if self.status is None:
            self.statuses[status] = status
        for pair in response_headers:
            self.response_headers[pair] = 1
    def forgetContentTypes(self):
        "remove content-types from recorded response headers (for cgi-defaults)"
        for pair in self.response_headers.keys():
            if pair[0].upper()=="CONTENT-TYPE":
                del self.response_headers[pair]
    def update_environment(self, env):
        #pr "update_environment", self, env.get(whiffenv.CGI_DICTIONARY)
        if self.components is None:
            raise ValueError, "stream cannot be serialized before binding (call to bind_root): "+repr(self)
        envcopy = env.copy()
        # add the source path, if available
        fp = self.file_path
        #assert fp is not None, "no path"
        if fp:
            if type(fp) not in  types.StringTypes:
                raise ValueError, "path should be string: "+repr(fp)
            envcopy[whiffenv.SOURCE_PATH] = fp
        # record the responding path in environment to help components do name resolution.
        envcopy[whiffenv.TEMPLATE_PATH] = self.responding_path
        pathurl = "/"
        if self.responding_path:
            pathurl = "/"+"/".join(self.responding_path)
        envcopy[whiffenv.TEMPLATE_URL] = pathurl
        # add environment overrides
        #pr "env overrides", self.overrides
        # double check rpc mark
        if self.overrides.get(whiffenv.RPC_TAINTED, True)!=True:
            raise ValueError, "Security: whiff page may not unset environment taint mark "+repr(whiffenv.RPC_TAINTED)
        envcopy.update(self.overrides)
        #pr "DUMPING WHIFF PARAMETERS"
        #for x in envcopy.keys():
            #if x.startswith("whiff"):
                #pr x, envcopy[x]
        additional_headers = []
        # remember additional headers from environment
        if envcopy.has_key(whiffenv.HEADERS):
            additional_headers = envcopy[whiffenv.HEADERS]
            del envcopy[whiffenv.HEADERS] # don't send additional headers to sub-components
        self.additional_headers = additional_headers
        # get cgi parameters if required and adjust environment for cgi prefix
        #pr "PROCESSING_CGI FOR", id(self), self, self.cgi_defaults
        if self.unbound_cgi_defaults:
            if self.cgi_defaults is None:
                raise ValueError, "unbound cgi defaults "+repr(self.unbound_cgi_defaults)
        envcopy = resolver.process_cgi(envcopy)
        # add cgi-defaults where no value is provided, but only if cgi parameters have been parsed.
        # cgi-defaults must follow the naming convention after the prefix is removed (if any).
        if self.cgi_defaults:
            #pr "cgi-defaults for", self
            #pr "adding defaults", self.cgi_defaults.keys()
            #pr "to dictionary", envcopy.get(whiffenv.CGI_DICTIONARY)
            cgi_dict = envcopy.get(whiffenv.CGI_DICTIONARY)
            if cgi_dict is None:
                raise ValueError, "cannot provide cgi defaults unless cgi parameters have been parsed"
            for (name, thing) in self.cgi_defaults.items():
                if not cgi_dict.has_key(name):
                    # cgi_default value can be a stream or a simple string...
                    if isinstance(thing, StreamApp):
                        stream = thing
                        stream_env = stream.update_environment(env)
                        stream_iter = stream(stream_env, self.my_start_response)
                        stream_list = list(stream_iter)
                        cgi_content = "".join(stream_list)
                    else:
                        # XXXX probably should only allow strings...
                        cgi_content = mystr(thing)
                    #pr "now defaulting cgi", name, cgi_content
                    resolver.override_cgi_require(envcopy, name, cgi_content)
            # ignore content-types from cgi-defaults
            self.forgetContentTypes()
        # add id_overrides based on the prefix
        #prefix = envcopy.get(whiffenv.FULL_CGI_PREFIX, "")
        #envchanges = {}
        #for (name, page) in self.bound_id_overrides.items():
        #    page_env = page.update_environment(envcopy)
        #    page_iter = page(page_env, self.my_start_response)
        #    page_str = "".join(list(page_iter))
        #    # interpret the string as json!
        #    page_json = jsonParse.parseValue(page_str)
        #    idname = prefix+name
        #envchanges[idname] = page_json
        #envcopy.update(envchanges)
        return envcopy
    def whiff_call(self, env, start_response, update_environment=None, additional_args=None):
        if update_environment:
            env = update_environment(env)
        if additional_args is None:
            additional_args = {}
        # evaluate the components
        #envcopy = self.update_environment(env)
        #pr 
        #pr "whiff_call for", repr(self)
        #pr "   cgi_dict is", env.get(whiffenv.CGI_DICTIONARY)
        #pr "   text is", repr(self.text)
        #pr "   root_application", self.root_application
        #pr "   responding_path", self.responding_path
        #pr "   path_remainder", self.path_remainder
        #pr "   components", self.components
        if self.additional_headers is None:
            raise ValueError, "cannot execute whiff_call before update_environment"
        if self.root_application is None:
            raise ValueError, "cannot execute whiff_call before bind_root"
        # use the bound environment for this stream if available NOT HERE!
        #if self.whiff_bound_environment:
        #    #pr self, "using bound environment"
        #    #pr "BEFORE script name", env.get("SCRIPT_NAME"), "content type", env.get(whiffenv.CONTENT_TYPE)
        #    env = self.whiff_bound_environment
        #    #pr "AFTER script name", env.get("SCRIPT_NAME"), "content type", env.get(whiffenv.CONTENT_TYPE)
        envcopy = env.copy()
        sr = self.my_start_response
        # strip the components of all white head and tail if requested
        doStrip = envcopy.get(whiffenv.STRIP)
        #pr "doStrip is", repr(doStrip)
        components = self.components
        if doStrip:
            components = components[:]
            while components and textcomponent.whiteComponent(components[0]):
                #pr "deleting head"
                del components[0]
            while components and textcomponent.whiteComponent(components[-1]):
                #pr "deleting tail"
                del components[-1]
            if components:
                components[0] = textcomponent.lstrip(components[0])
                components[-1] = textcomponent.rstrip(components[-1])
        # this forces materialization of components
        # (no laziness here) in order to force calls to start_response
        #p  "COMPONENTS:", self
        #component_calls = [
        #    list(component(envcopy, sr)) for component in self.components]
        component_calls = []
        # prebind all arguments so they evaluate in this stream's scope (not any other scope)
        #pr 
        #pr "@@ binding arguments for", self
        #pr "@@    CHECKING ARGUMENTS", self.bound_arguments.keys(), "AT", envcopy['whiff.template_path']
        default_arguments = self.default_arguments
        if self.bound_arguments:
            all_args = {}
            lexical_args = {}
            if self.whiff_lexical_arguments:
                lexical_args = self.whiff_lexical_arguments
                all_args.update(lexical_args)
            for (name, arg) in self.bound_arguments.items():
                #if ((isinstance(arg, resolver.WsgiComponent) or isinstance(arg, resolver.WsgiComponentFactory))
                #    and default_arguments.has_key(name)):
                if ((isinstance(arg, resolver.WsgiComponent) or isinstance(arg, resolver.WsgiComponentFactory))):
                    #pr "@@    ", self, "BINDING ENVIRONMENT for default argument"
                    #pr "@@    ", name, arg
                    #pr "@@    with template path=", repr(envcopy[whiffenv.TEMPLATE_PATH])
                    if default_arguments.has_key(name):
                        #pr "binding default argument with outer scope", name, lexical_args.keys()
                        arg.bind_environment(envcopy, lexical_args)
                    else:
                        # don't bind environment for non-default argument
                        arg.bind_environment(None, all_args)
                else:
                    #pr "SKIPPED BINDING ENV", arg, arg.__class__
                    pass
        #pr "done binding arguments", self
        #pr
        # and similarly for bound_id_overrides
        #if self.bound_id_overrides:
        #    for (name, arg) in self.bound_id_overrides.items():
        #        if isinstance(arg, resolver.WsgiComponent):
        #            arg.bind_environment(envcopy)
        #pr "CALLING COMPONENTS FOR", self
        #pr "  with cgi_dict", envcopy.get(whiffenv.CGI_DICTIONARY)
        additional_args = additional_args.copy()
        #pr "in stream", self
        #pr "with additional args", additional_args.keys()
        if self.whiff_lexical_arguments:
            #pr "adding lexical args", self.whiff_lexical_arguments.keys()
            additional_args.update(self.whiff_lexical_arguments) 
        # overlay
        for (a,b) in self.bound_arguments.items():
            if not additional_args.has_key(a):
                additional_args[a] = b
        for component in components:
            #pr "...in stream", self, " cgi ", envcopy.get(whiffenv.CGI_DICTIONARY)
            #pr "...now calling component", (component, sr)
            try:
                called_component = list(component.whiff_call(envcopy, sr, additional_args=additional_args))
            except:
                (tp, vl, tb) = sys.exc_info()
                vl = str(vl)
                vl = repr(vl)
                vl = vl.replace("\\n", " ")
                vl = vl.replace("\\t", " ")
                vl = vl.replace('"', "")
                vl = vl.replace("'", "")
                vl = vl.replace("\\", "")
                vl2 = vl
                if self.file_path:
                    vl2 = "%s :: %s" % (self.file_path, vl)
                raise tp, vl2, tb
            for chunk in called_component:
                assert type(chunk) in types.StringTypes, "component should produce sequence of strings "+repr((component, chunk))
            component_calls.append(called_component)
        #p  "COMPONENT CALLS:"
        #for c in component_calls:
        #    #p  c
        # now do start_response
        header_list = []
        content_type = None
        # collect headers from components, but strip out and check content types
        content_types = {}
        for (name, value) in self.response_headers:
            if name.upper().strip()=="CONTENT-TYPE":
                ct = value.lower()
                content_types[ct] = ct
            else:
                header_list.append( (name, value) )
        # content type from environment takes precedence
        #pr "looking in env for content type", env.keys()
        if envcopy.has_key(whiffenv.CONTENT_TYPE):
            content_type = envcopy[whiffenv.CONTENT_TYPE]
            #pr self, "chose content type from env", content_type
        elif content_types:
            # use content type claimed by components, if unambiguous
            # hacky: if there are 2 content types and one of them is text/plain: ignore text/plain
            if len(content_types)>=2:
                if "text/plain" in content_types:
                    del content_types["text/plain"]
            if len(content_types)>1:
                #pr "for", self, "with text"
                #pr self.text
                raise ValueError, "ambiguous content types "+repr((content_types.keys(), self))
            content_type = content_types.keys()[0]
            #pr self, "chose content type from components", content_type
        # if no known content type do default
        if content_type is None:
            content_type = self.default_content_type
            #pr self, "chose content type from default", content_type
        # no unicode in ct!
        content_type = mystr(content_type)
        # add a content type
        #pr self, 'ADDING CONTENT TYPE', repr(content_type)
        header_list.append( ('Content-Type', content_type) )
        # Now add any additional headers specified in the WSGI environment
        for (k,v) in self.additional_headers:
            k = mystr(k)
            v = mystr(v)
            header_list.append( (k,v) ) # validate list of pairs...
        # pick the highest status from the default and those returned by components (?)
        statuses = self.statuses.keys()
        statuses.append(self.default_status)
        statuses.sort()
        status = statuses[-1]
        #status = self.default_status
        if envcopy.has_key(whiffenv.STATUS):
            status = envcopy[whiffenv.STATUS]
        #pr "evalling stream", self, "with num components", len(component_calls)
        #pr  "stream starting", status, header_list
        # status must be a string!
        status = mystr(status)
        start_response(status, header_list)
        return self.response_generator(component_calls)
    def response_generator(self, component_calls):
        # now send the components
        for component_sequence in component_calls:
            for chunk in component_sequence:
                yield mystr(chunk) # auto-convert unicode

def mystr(x):
    if type(x) is types.UnicodeType:
        return x.encode('utf-8')
    return str(x)

def myunicode(x):
    if type(x) is types.UnicodeType:
        return x
    return unicode(str(x), "utf-8", "ignore")

def deferBindings(thePage, arguments, file_path=None):
    if isinstance(thePage, DeferStreamBindings):
        return thePage.defer(arguments)
    else:
        thePage = resolver.wrapMiddleware(thePage)
        #if not isinstance(thePage, page.DeferPageBindings):
        #thePage = page.DeferPageBindings(page)
        return DeferStreamBindings(thePage, file_path, arguments)

class DeferStreamBindings(resolver.WsgiComponent):
    root_application = None
    
    def __init__(self, page, file_path, arguments=None):
        assert not isinstance(page, DeferStreamBindings), "cannot double defer"
        if arguments is None:
            arguments = {}
        self.file_path = file_path
        self.arguments = arguments
        page.file_path = file_path
        self.page = page
        self.bound_environment = None
        self.lexical_arguments = {}
        # copy the text attribute if present
        if hasattr(page, "text"):
            self.text = page.text
        else:
            #pr "NO TEXT FOUND FOR", page
            pass
        #pr "DEFERRED BINDINGS initialized", self
        #pr "   with arguments", arguments
        
    def __call__(self, env, start_response, update_environment=None, additional_args=None):
        theStream = self.duplicate()
        if isinstance(theStream, DeferStreamBindings):
            raise ValueError, "bad duplicate "+repr(theStream)
        return theStream(env, start_response, update_environment, additional_args)
    
    def __repr__(self):
        return "DeferStreamBindings" + repr((id(self), self.file_path, self.page, self.arguments))
    
    def bind_root(self, root_application, responding_path, path_remainder, outer_arguments=None):
        self.root_application = root_application
        self.responding_path = responding_path
        self.path_remainder = path_remainder
        self.outer_arguments = outer_arguments
        #pr "BOUND", self, "with outer args", outer_arguments
        
    def bind_environment(self, env, lexical_arguments=None):
        if lexical_arguments:
            self.lexical_arguments.update(lexical_arguments)
        if env is not None and self.bound_environment is None:
            #pr "$$ deferred BINDING ENVIRONMENT", self
            #pr "$$ deferred AT SCRIPT_NAME", env["SCRIPT_NAME"]
            self.bound_environment = env
            pass
        else:
            #pr "$$ NOT BINDING ENVIRONMENT", self
            pass
        
    def combine_args(self, args):
        allargs = {}
        # XXX is this the right order of binding in case of name collision?
        allargs.update(args)
        allargs.update(self.arguments)
        #whiffenv.myupdate(allargs, self.arguments)
        return allargs
    
    def defer(self, args):
        allargs = self.combine_args(args)
        return DeferStreamBindings(self.page, self.file_path, allargs)
    
    def duplicate(self, **args):
        #pr "++ DUPLICATE", self, args.keys()
        #pr "++ self.arguments", self.arguments.keys()
        allargs = args
        thePage = self.page
        #pr "++ PAGE IS", thePage
        #pr "++ basic args", args.keys()
        if thePage.Lexical:
            # also include outer arguments
            allargs = self.combine_args(args)
            #pr "  allargs = ", allargs.keys()
        #pr "getting wsgi component with allargs", allargs.keys()
        theStream = thePage.makeWsgiComponent(**allargs)
        #theStream = self.page.makeWsgiComponent(**args)
        #pr "  got stream", theStream
        if self.root_application is not None:
            theStream.bind_root(self.root_application, self.responding_path, self.path_remainder, self.outer_arguments)
        theStream.file_path = self.file_path
        #pr "  bound stream", theStream
        if self.bound_environment or self.lexical_arguments:
            #pr "++", self, "deferred DUPLICATE BINDING ENVIRONMENT", theStream
            #pr "++    AT", repr(self.bound_environment["whiff.template_url"])
            theStream.bind_environment(self.bound_environment, self.lexical_arguments)
            pass
        else:
            #pr "++ NO ENV BOUND FOR", self, dir(self)
            pass
        return theStream

def asMiddleware(stream, env):
    def middleware(**args):
        d = deferBindings(stream, {})
        if env.has_key(whiffenv.ROOT):
            root_application = env[whiffenv.ROOT]
            responding_path = env[whiffenv.TEMPLATE_PATH]
            path_remainder = ""
            d.bind_root(root_application, responding_path, path_remainder)
        return d.duplicate(**args)
    return middleware

import page # put low to avoid circularity issues
import textcomponent
import argcomponent
from rdjson import jsonParse
