"""
Wsgi app to redirect to a new location
"""

whiffCategory = "logic"

whiffDoc = """
{{include "whiff_middleware/heading"}}
whiff_middleware/redirect - redirect the client to another URL
{{/include}}

The <code>whiff_middleware/redirect</code>
middleware sends a response which redirects
the client to another URL location.

"""
# import must be absolute
from whiff.middleware import misc
from whiff import whiffenv

class redirect(misc.utility):
    def __init__(self, location, status="302 Moved Temporarily", page=None, relative=False):
        self.location = location
        self.status = status
        self.page = page
        self.relative = relative
    def __call__(self, env, start_response):
        from whiff import resolver # avoid circularity problem
        relative = self.param_json(self.relative, env)
        # no double slashes at start of location
        location = self.param_value(self.location, env) #str(self.location)
        while location.startswith("//"):
            location = location[1:]
        status = self.param_value(self.status, env) #str(self.status)
        page = self.param_value(self.page, env)
        if relative:
            assert False, "relative implementation is not finished, sorry"
        if page is None:
            page = "relocated to %s<br>\n" % repr(location)
        headers = self.derive_headers('text/html')
        headers.append( ('Location', location) )
        #pr "REDIRECTION", repr(status), headers
        #pr "\n".join( map(repr, sorted(env.items() )))
        start_response(status, headers)
        #start_response('200 OK', [('Content-type', 'text/html')]) # for debug
        return [page]
        #yield "\n<br> SERVER_NAME "+repr(env.get("SERVER_NAME"))
        #yield "\n<br> SERVER_PORT "+repr(env.get("SERVER_PORT"))
        #yield "\n<br> SCRIPT_NAME "+repr(env.get("SCRIPT_NAME"))
        #yield "\n<br> PATH_INFO "+repr(env.get("PATH_INFO"))

__middleware__ = redirect

def test():
    r = redirect("http://www.yahoo.com")
    print "redirect test yields", list(r({}, misc.ignore))

if __name__=="__main__":
    test()
