
import stream
import whiffenv
from rdjson import jsonParse

class CgiComponent(stream.StreamComponent):
    # ???? default_stream is never used???
    def __init__(self, name, default_stream=None):
        self.name = name
        self.default_stream = default_stream
    def __repr__(self):
        return "CgiComponent"+repr((self.name, self.file_path))
    def dump(self):
        return "{{get-cgi %s/}}" % (repr(self.name),)
    def bound_copy(self, in_stream, arguments, root_application, responding_path, path_remainder):
        name = self.name
        default_stream = in_stream.get_cgi_default(name)
        return CgiComponent(name, default_stream)
    def whiff_call(self, env, start_response, update_environment=None, additional_args=None):
        if update_environment:
            env = update_environment(env)
        status = "200 OK"
        header_list = [ ("Content-Type", "text/plain") ] # XXXX ???
        name = self.name
        theValue = None
        # try to find the value in the cgi dictionary
        cgi_dict = env.get(whiffenv.CGI_DICTIONARY)
        if cgi_dict is None:
            raise ValueError, "cgi-dictionary has not been parsed by whiff"
        theList = cgi_dict.get(name)
        if theList is None:
            top_dict = env.get(whiffenv.TOP_CGI_DICTIONARY)
            full_prefix = env.get(whiffenv.FULL_CGI_PREFIX)
            keys = top_keys = None
            if cgi_dict is not None:
                keys = cgi_dict.keys()
            if top_dict is not None:
                top_keys = top_dict.keys()
            tpath = env.get(whiffenv.TEMPLATE_PATH)
            raise ValueError, "whiff cgi dictionary does not contain key: "+repr((
                name, self, keys, top_keys, full_prefix, tpath))
        if len(theList)!=1:
            raise ValueError, "ambiguous values for whiff parsed cgi name: "+repr((name, self, theList))
        theValue = theList[0]
        typeValue = type(theValue)
        # convert the value if it's a json type to a json format
        if typeValue in whiffenv.JSON_TYPES:
            theValue = jsonParse.format(theValue)
        #theValue = qq(theValue) # this is redundant
        # otherwise try to use the default
        start_response(status, header_list)
        return [theValue]

#def qq(v):
#    "by default all cgi values have special html marks quoted for security"
#    # use middleware to unquote if desired.
#    v = v.replace("&", "&amp;")
#    v = v.replace("<", "&lt;")
#    v = v.replace(">", "&gt;")
#    return v

