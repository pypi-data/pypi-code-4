
import stream
import types
import whiffenv
from rdjson import jsonParse

class NameComponent(stream.StreamComponent):
    def __init__(self, name, page, use_prefix=False):
        # page default is not parsed as json even if use_prefix is set...
        # name could be indexed by json sequence such as 'data[1,"hello"]'
        self.name = name
        self.page = page
        self.use_prefix = use_prefix
    def __repr__(self):
        return "NameComponent"+repr((self.name, self.file_path))
    def dump(self):
        tag = "get-env"
        if self.use_prefix:
            tag = "get-id"
        if self.page:
            pdump = self.page.dump()
            return "{{%s %s}}%s{{/%s}}" % (tag, repr(self.name), pdump, tag)
        else:
            return "{{%s %s/}}" % (tag, repr(self.name),)
    def bound_copy(self, in_stream, arguments, root_application, responding_path, path_remainder):
        page = self.page
        if not page:
            return self
        stream = page
        if isinstance(page, resolver.WsgiComponentFactory):
            page.file_path = self.file_path
            stream = page.makeWsgiComponent()
            stream.bind_root(root_application, responding_path, path_remainder, {})
            stream.file_path = self.file_path
        return NameComponent(self.name, stream, self.use_prefix)
    def whiff_call(self, env, start_response, update_environment=None, additional_args=None):
        if update_environment:
            env = update_environment(env)
        status = "200 OK"
        header_list = [ ("Content-Type", "text/plain") ] # XXXX ???
        (name, index_sequence) = parse_name(self.name)
        #pr "whiff call for name", repr(name)
        if self.use_prefix:
            prefix = env.get(whiffenv.FULL_CGI_PREFIX, "")
            #pr "extending with prefix", repr(prefix)
            name = prefix+name
        #pr "searching for name", repr(name)
        if env.has_key(name):
            theArg = env[name]
            #pr "ENV NAME FOUND", (name, theArg)
        else:
            #pr "NO ENV NAME FOUND", (name, env.keys())
            page = self.page
            if not page:
                raise ValueError, "environment entry %s not found and no default specified" % (
                    repr(name),)
            return page(env, start_response)
        for index in index_sequence:
            theArg = theArg[index]
        typeArg = type(theArg)
        if typeArg in whiffenv.JSON_TYPES:
            # format as json
            payload = jsonParse.format(theArg)
        else:
            # just make sure it's a string.
            payload = stream.mystr(theArg)
        start_response(status, header_list)
        return [payload]

def parse_name(name):
    if "[" in name:
        location = name.find("[")
        jsonIndices = name[location:]
        wrappedindices = jsonParse.stringAsJsonSequence(jsonIndices)
        indices = []
        for x in wrappedindices:
            if len(x)!=1:
                raise ValueError, "this index notation is not supported "+repr(x)
            indices.append(x[0])
        realname = name[:location]
        return (realname, indices)
    else:
        return (name, [])

# down here in case of circularity issues
import resolver
