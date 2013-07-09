
"""
Attach strings as arguments to a page (mainly for use as client/server call back)
"""

whiffDoc = """
{{include "whiff_middleware/heading"}}
whiff_middleware/callPageWithStrings -- expand a page with string arguments
{{/include}}

The <code>whiff_middleware/CallPageFunction</code>
middleware expands a page using string arguments.
This middleware is sometimes useful for implementing AJAX functionality.
"""

whiffCategory = "ajax"

# import must be absolute
from whiff.middleware import misc
from whiff import resolver

class callPageWithStrings(misc.javaScriptGenerator):
    def __init__(self,
                 page,  # page to expand
                 **arguments # arguments not to expand
                 ):
        self.page = page
        self.arguments = arguments
    def __call__(self, env, start_response):
        #pr
        #pr "callPageWithStrings"
        #pr self.param_text(self.page)
        argsDict = {}
        for (name, value) in self.arguments.items():
            argtext = self.param_text(value)
            #pr "name", name
            #pr "set to text", repr(argtext)
            argsDict[name] = resolver.wrapApplication(textWrapper(argtext))
        #pr "now calling page..."
        #pr
        # bind the argsDict to the page/stream
        page = self.page.duplicate()
        #pr "setting args", argsDict
        page.updateArguments(argsDict)
        return page(env, start_response)

class textWrapper:
    def __init__(self, text):
        self.text = text
    def __call__(self, env, start_response):
        start_response("200 OK", [('Content-Type', 'text/plain')])
        return [self.text]

__middleware__ = callPageWithStrings

def test():
    from whiff import parseTemplate
    env = {
        "wsgi.url_scheme" : "http",
        "PATH_INFO" : "/whatever",
        "QUERY_STRING" : "",
        "REMOTE_ADDR" : "127.0.0.1",
        "REMOTE_HOST" : "localhost",
        "REQUEST_METHOD" : "GET",
        "SCRIPT_NAME" : "",
        "SERVER_NAME" : "localhost",
        "SERVER_PORT" : "8888",
        "SERVER_PROTOCOL" : "HTTP/1.1",
        "SERVER_SOFTWARE" : "WSGIServer/0.1 Python/2.5",
        }
    root = "dummy value not None"
    rpath = []
    pathr = []
    outer_args = {}
    (test, page, cursor) = parseTemplate.parse_page("page with ARG= [{{use ARG/}}]", file_path="(test)")
    if not test:
        c1 = templateText[ max(0, cursor-20): cursor ]
        c2 = templateText[ cursor : cursor+20 ]
        raise ValueError, "template parse for payload reports error "+repr((result, cursor, c1, c2))
    stream = page.makeWsgiComponent()
    stream.bind_root(root, rpath, pathr, outer_args)
    app = callPageWithStrings(stream, ARG="VALUE FOR ARG")
    sresult = app(env, misc.ignore)
    result = "".join(list(sresult))
    print "test result::", result

if __name__=="__main__":
    test()
