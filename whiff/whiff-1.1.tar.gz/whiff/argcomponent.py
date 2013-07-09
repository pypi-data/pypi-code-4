
import stream
import whiffenv
from rdjson import jsonParse

class Invocation(stream.StreamComponent):
    "superclass for shared behaviors for arg-like components"
    tag_name = None
    argtag = "using"
    def __init__(self, argId, envDict, argumentsDict, cgi_sets, id_sets, root_application=None,
                 responding_path=None, path_remainder=None):
        self.argId = argId
        self.envDict = envDict
        self.argumentsDict = argumentsDict
        self.cgi_sets = cgi_sets
        self.id_sets = id_sets
        self.bound_cgi_sets = None
        self.bound_id_sets = None
        self.boundArguments = None
        self.allboundArguments = None
        self.root_application = root_application
        self.responding_path = responding_path
        self.path_remainder = path_remainder
        #pr "initialized invocation", self
    def get_arguments_dictionary(self):
        return self.argumentsDict.copy()
    def __repr__(self):
        return self.__class__.__name__ + repr((id(self), self.argId, self.file_path))
    def bound_copy(self, in_stream, bound_arguments, root_application, responding_path, path_remainder):
        ## XXX??? at the moment arguments may be bound many times when not all are needed: is this a performance issue?
        #pr "binding Invocation", repr(self)
        #pr "   binding", self.argumentsDict
        #pr "   Using", bound_arguments
        #pr "   responding path", responding_path
        file_path = self.file_path
        myBoundArgs = stream.bind_arguments(self.argumentsDict, bound_arguments,
                                            root_application, responding_path, path_remainder, file_path)
        myBoundCgiSets = stream.bind_arguments(self.cgi_sets, bound_arguments,
                                               root_application, responding_path, path_remainder, file_path)
        myBoundIdSets = stream.bind_arguments(self.id_sets, bound_arguments,
                                              root_application, responding_path, path_remainder, file_path)
        result = self.__class__(self.argId, self.envDict, self.argumentsDict, self.cgi_sets, self.id_sets,
                                root_application, responding_path, path_remainder)
        result.file_path = file_path
        result.boundArguments = myBoundArgs
        result.bound_cgi_sets = myBoundCgiSets
        result.bound_id_sets = myBoundIdSets
        #p "   Bound as", myBoundArgs
        allargs = bound_arguments.copy()
        allargs.update(myBoundArgs)
        result.allboundArguments = allargs
        return result
    def dump(self):
        E = self.envDict.items()
        E.sort()
        #pr "E BEFORE LISTIFFY", E
        E = [ (k, listiffy(v)) for (k,v) in E ]
        #pr "E AFTER LISTIFFY", E
        argtag = self.argtag
        L = ["{{%s "%self.tag_name, self.dumpId(), " ", repr(E), "}}"]
        A = self.argumentsDict.items()
        A.sort()
        L += [ u" {{%s %s}}%s{{/%s}} "%(argtag, name, listiffy(page), argtag) for (name,page) in A ]
        C = self.cgi_sets.items()
        C.sort()
        L += [ u" {{set-cgi %s}}%s{{/set-cgi}}" % (name, page) for (name, page) in C ]
        L.append("{{/%s}}"%self.tag_name)
        return "".join(L)
    def dumpId(self):
        return self.argId
    def get_arg(self, e, a=None):
        raise ValueError, "virtual method must be defined in subclass"
    def update_environment(self, env):
        # add environment overrides
        full_env = env.copy()
        full_env.update(self.envDict)
        full_env = resolver.process_cgi(full_env)
        # install set-cgi pages if specified (overriding any existing values)
        if self.cgi_sets:
            bound_cgi_sets = self.bound_cgi_sets
            if bound_cgi_sets is None:
                raise ValueError, "cannot update cgi environment for unbound invocation "+repr(self)
            for (name, stream) in bound_cgi_sets.items():
                #pr "argcomponent", self
                #pr "updating environment", stream
                stream_env = stream.update_environment(env)
                stream_iter = stream(stream_env, self.my_start_response)
                stream_list = list(stream_iter)
                stream_content = "".join(stream_list)
                resolver.override_cgi_require(full_env, name, stream_content)
        # install id_sets
        if self.id_sets:
            bound_id_sets = self.bound_id_sets
            if not bound_id_sets:
                raise ValueError, "cannot update environment for unbound invocation "+repr(self)
            bindings = {}
            prefix = full_env.get(whiffenv.FULL_CGI_PREFIX, "")
            for (name, stream) in bound_id_sets.items():
                stream_env = stream.update_environment(full_env)
                stream_iter = stream(stream_env, self.my_start_response)
                stream_str = "".join(list(stream_iter))
                # interpret the string as json
                (flag, stream_json, endLocation) = jsonParse.parseValue(stream_str)
                if not flag:
                    raise ValueError, "cannot parse set-id value for %s as json %s: %s" % (
                        repr(name), repr(stream_str[:100]), repr(stream_json))
                idname = prefix+name
                # XXXX need to emulate item assignment to mirror get-env: <set-env a[1]>13</set-env>
                bindings[idname] = stream_json
            full_env.update(bindings)
        #pr "arg updated environment at argId, url", (self.argId, full_env["whiff.template_url"])
        #pr "arg updated environment at id", repr(full_env.get(id))
        return full_env
    def my_start_response(self, *args):
        # ignore start_responses from cgi overrides.
        pass # ???
    def whiff_call(self, env, start_response, update_environment=None, additional_args=None):
        #pr "invocation whiff_call", self
        #pr "additional args", additional_args.keys()
        # get arg and possibly modify the environment
        if update_environment:
            env = update_environment(env)
        (theArg, env) = self.get_arg(env, additional_args)
        #pr "GOT THEARG", theArg
        isApp = False
        if isinstance(theArg, resolver.WsgiComponentFactory):
            args = self.boundArguments
            #pr "making component", theArg, args
            theComponent = theArg.makeWsgiComponent(args)
            isApp =True
        if isinstance(theArg, resolver.WsgiComponent):
            args = self.boundArguments
            #pr "duplicating", theArg, args
            theComponent = theArg.duplicate(**args)
            isApp = True
        if isApp:
            # bind the component arg the environment and additional arguments
            #pr "invocation binding", theComponent
            #pr "additional_args", additional_args.keys()
            theComponent.bind_environment(env, additional_args)
            # no bound arguments! ???
            #bound_arguments = {}
            bound_arguments = self.boundArguments
            #pr "arg whiff_call", self
            #pr "   binding", theComponent
            #pr "   root_application", self.root_application
            #pr "   responding_path", self.responding_path
            theComponent.bind_root(self.root_application, self.responding_path, self.path_remainder, bound_arguments)
            #env = theComponent.update_environment(env)
            # do overrides on environment XXXX (?) LATER!!
            #full_env = self.update_environment(env)
            full_env = env
            #pr "CALLING COMPONENT", theComponent
            #return theComponent.whiff_call(full_env, start_response)
            return theComponent(full_env, start_response, self.update_environment, additional_args=additional_args)
        else:
            # default for all other objects: convert to string
            status = "200 OK"
            header_list = [ ("Content-Type", "text/plain") ] # XXXX ???
            payload = str(theArg)
            start_response(status, header_list)
            #p "RETURNING PAYLOAD", repr(payload)
            return [payload]
        

class ArgComponent(Invocation):
    tag_name = "use"
    def get_arg(self, env, additional_args=None):
        #p4 "ArgComponent sees args", self.boundArguments, additional_args.keys()
        #p4 "looking for", repr(self.argId)
        args = self.allboundArguments
        if args is None:
            raise ValueError, "attempt to evaluate unbound argument "+repr(self)
        name = self.argId
        try:
            theArg = args[name]
        except KeyError:
            if additional_args is None:
                additional_args = {}
            try:
                theArg = additional_args[name]
            except KeyError:
                raise KeyError, "did not find name [%s] in arg selection %s for %s" % (str(name), (args.keys(), additional_args.keys()), repr(self))
        return (theArg, env)

# cosmetic fix for string testing consistency
def listiffy(x):
    import types
    tx = type(x)
    if tx in (types.ListType, types.TupleType):
        return [listiffy(e) for e in x]
    elif tx is types.DictType:
        result = {}
        for (a,b) in x.items():
            result[a] = listiffy(b)
        return result
    else:
        return x
    
# import at bottom to avoid circularity issues
import resolver

class SectionBinding(resolver.WsgiComponentFactory):
    # allow outer arguments to be visible
    Lexical = True
    def __init__(self, sectionName, filename):
        self.sectionName = sectionName
        self.filename = filename
    def __repr__(self):
        return "SectionBinding"+ repr((id(self), self.sectionName, self.filename))
    def clone(self):
        #pr "cloning", self
        result = SectionBinding(self.sectionName, self.filename)
        result.whiff_bound_environment = self.whiff_bound_environment
        return result
    def makeWsgiComponent(self, **args):
        #pr "** making component for using binding", (self.sectionName, self, args.keys())
        result = SectionResolver(self.sectionName, args, self.filename)
        #pr "** made", result
        return result

class SectionResolver(resolver.WsgiComponent):
    # allow outer arguments to be visible
    Lexical = True

    allocation_limit = None # set to none for non-test
    allocated = 0
    
    def __init__(self, sectionName, args, filename):
        assert args.has_key(sectionName), "name must be available as an argument "+repr((sectionName, args.keys()))
        self.sectionName = sectionName
        self.args = args
        self.filename = filename
        if self.allocation_limit:
            count = self.allocated
            count+=1
            assert count<self.allocation_limit, "allocated past testing limit"
            SectionResolver.allocated = count
    def __repr__(self):
        return "SectionResolver"+repr((id(self), self.sectionName, self.filename))
    
    def whiff_call(self, env, start_response, update_environment=None, additional_args=None):
        try:
            args = self.args
            sectionName = self.sectionName
            #pr "!!! calling using", (sectionName, self.filename)
            #pr "!!! at template path", env[whiffenv.TEMPLATE_PATH]
            #pr "!!! args are", args.keys()
            #pr "!!! additional args are", additional_args.keys()
            using = args[sectionName]
            #pr "!!! got using", using
            # remove using from arguments to prevent infinite recursion
            #   XXXX this is a bit of a hack... I'm not sure why it's needed.
            myargs = args.copy()
            del myargs[sectionName]
            if additional_args and additional_args.has_key(sectionName):
                additional_args = additional_args.copy()
                del additional_args[sectionName]
            component = using.duplicate(**myargs)
            #pr "!!! using duplicated", component, args.keys()
            result = component(env, start_response, update_environment, additional_args= additional_args)
        finally:
            pass
        return result
