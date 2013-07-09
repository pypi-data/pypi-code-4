
import resolver
import stream
import whiffenv

PageError = ValueError

class Page(resolver.WsgiComponentFactory):
    # allow outer variables to be visible
    Lexical = True
    def __init__(self, file_path):
        #assert file_path is not None, "no file path for page"
        self.text = None
        self.overrides = {}
        #self.id_overrides = {}
        self.parameters = {}
        self.cgi_defaults = {}
        self.component_list = []
        self.file_path = file_path
        #pr "CREATED PAGE", self
        #pr "PATH", self.file_path
    def get_components(self):
        return self.component_list[:]
    def sanity_check(self):
        #assert len(self.component_list)>0, "complete page has no components: "+repr((self.file_path, self.text))
        pass
    def clone(self):
        result = Page(self.file_path)
        result.text = self.text
        result.overrides = self.overrides
        #result.id_overrides = self.id_overrides
        result.parameters = self.parameters
        result.cgi_defaults = self.cgi_defaults
        result.component_list = self.component_list
        result.sanity_check()
        return result
    def __repr__(self):
        return self.dump()
        #return "Page"+ repr((id(self), self.file_path))
    def info(self):
        if self.file_path:
            return "Page"+ repr((id(self), self.file_path))
        elif self.text:
            return "Page"+ repr((id(self), self.text[:80]+"..."))
        else:
            return "Page"+ repr((id(self),))
    def dump(self):
        R = self.overrides.items()
        R.sort()
        L = [ repr(R) ]
        #L += [ "{{require %s/}}" % (repr(name),) for name in self.parameters.keys() ]
        #idpairs = self.id_overrides.items()
        #idpairs.sort()
        #for (k,v) in idpairs:
        #    L.append("{{set-id %s}}%s{{/set-id}}" % (k, v.dump()))
        parameterpairs = self.parameters.items()
        parameterpairs.sort()
        for (k,v) in parameterpairs:
            if v is None:
                L.append( "{{require %s/}}"% repr(k) )
            else:
                L.append( "{{require %s}} %s {{/require}}" % (repr(k), v.dump()))
        C = self.cgi_defaults.items()
        C.sort()
        for (name, page) in C:
            L.append( "{{cgi-default %s}}%s{{/cgi-default}}" % (name, page))
        L += [ c.dump() for c in self.component_list ]
        return "".join(L)
    def add_cgi_default(self, name, subpage):
        self.cgi_defaults[name] = subpage
    def add_require(self, name, defaultValue=None):
        self.parameters[name] = defaultValue
    #def add_environment(self, name, value):
    #    D = {name:value}
    #    return self.add_environment_dict(D)
    def add_environment_dict(self, dict):
        if dict.get(whiffenv.RPC_TAINTED, True) != True:
            raise ValueError, "Security: whiff directive cannot unset environment taint mark "+repr(whiffenv.RPC_TAINTED)
        whiffenv.check_environment(dict)
        self.overrides.update(dict)
    #def add_id_override(self, name, page):
    #    self.id_overrids[name] = page
    def add_component(self, component):
        self.component_list.append(component)
    def makeWsgiComponent(self, **arguments):
        file_path = self.file_path
        arguments = arguments.copy()
        params = self.parameters
        default_arguments = {}
        for pname in params.keys():
            pvalue = params[pname]
            if not arguments.has_key(pname):
                if pvalue is not None:
                    # use default argument
                    #p "default", pname, pvalue
                    bind_path(pvalue, file_path)
                    arguments[pname] = pvalue
                    default_arguments[pname] = 1
                else:
                    raise PageError, "for page "+self.info()+" missing argument "+repr((pname,arguments.keys()))
        for c in self.component_list:
            c.file_path = file_path
        for d in self.cgi_defaults.values():
            bind_path(d, file_path)
        # extra arguments ok for now?
        try:
            the_app = stream.StreamApp(self.overrides, arguments, self.cgi_defaults, self.component_list,
                                       default_arguments) #self.id_overrides)
        except AssertionError:
            raise AssertionError, "could not create stream from page "+repr((self, self.file_path))
        the_app.text = self.text
        the_app.file_path = self.file_path
        #pr "page", id(self), "generated", the_app
        return the_app

def bind_path(element, file_path):
    if isinstance(element, resolver.WsgiComponentFactory):
        element.file_path = file_path
    return element

class DeferPageBindings(resolver.WsgiComponentFactory):
    def __init__(self, page):
        self.page = page
    def __repr__(self):
        return "DeferPageBindings(%s : %s)" % (id(self), repr(self.page))
    __str__=__repr__
    def clone(self):
        return DeferPageBindings(self.page)
    def dump(self):
        return self.page.dump()
    def makeWsgiComponent(self, **arguments):
        "return the page to be bound later"
        p = self.page
        file_path = None
        if hasattr(p, "file_path"):
            file_path = p.file_path
        result = stream.deferBindings(p, arguments, file_path)
        be = self.whiff_bound_environment
        if be is not None: 
            result.bind_environment(be)
        return result
                
