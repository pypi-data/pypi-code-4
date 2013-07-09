whiffDoc = """
{{include "whiff_middleware/heading"}}
whiff_middleware/CallPageFunction -- calls a page expanded at the server
{{/include}}

The <code>whiff_middleware/CallPageFunction</code>
middleware expands a page at the server and returns a generated
javascript function to the browser, and evaluates the generated
function.
This middleware is sometimes useful for implementing AJAX functionality.
"""

whiffCategory = "ajax"

# import must be absolute
from whiff.middleware import misc
from whiff.middleware import EvalPageFunction

class CallPageFunction(misc.javaScriptGenerator):
    def __init__(self,
                 page, # page to expand (not evaluated, text passed to client for callback)
                 expanderUrl="whiff_middleware/expandPostedTemplate",
                 expandRelativeTo=None,
                 asynchronous=False,
                 prefix=None,
                 doCall=False,
                 cgi_pairs=None,
                 **page_arguments # arguments to pass to client after expansion
                 ):
        self.doCall = doCall
        # the page to expand
        self.page = page
        # the location of the "expander" to do the expansion
        self.url = expanderUrl
        # the cgi prefix to use for extracting relevant parameters
        self.prefix = prefix
        # should the response be delivered asynchonously?
        self.asynchronous = asynchronous
        self.expandRelativeTo = expandRelativeTo
        self.page_arguments = page_arguments
        self.cgi_pairs = cgi_pairs
    def __call__(self, env, start_response):
        page_text = self.param_text(self.page)
        argsitems = self.page_arguments.items()
        argsitems.sort()
        argsList = []
        for (name, value) in argsitems:
            arg_text = self.param_value(value, env)
            arg_using = "{{using %s}}%s{{/using}}" % (name, arg_text)
            argsList.append(arg_using)
        argSections = "\n".join(argsList)
        D = {}
        D["PAGE"] = page_text
        D["ARGUMENT_SECTIONS"] = argSections
        callbackPage = callbackPageTemplate % D
        # XXX DO WE NEED THE OTHER PARAMETERS TO EVALPAGEFUNCTION???
        jspage = EvalPageFunction.__middleware__(callbackPage,
                    self.url, self.expandRelativeTo, self.asynchronous, self.prefix,
                    self.cgi_pairs, self.doCall)
        return jspage(env, start_response)

callbackPageTemplate = """
{{include "whiff_middleware/callPageWithStrings"}}
{{using page}}%(PAGE)s{{/using}}
%(ARGUMENT_SECTIONS)s
{{/include}}
"""

__middleware__ = CallPageFunction

def test():
    env = {
        "wsgi.url_scheme" : "http",
        "PATH_INFO" : "/whatever",
        "QUERY_STRING" : "TESTVAR=1",
        "REMOTE_ADDR" : "127.0.0.1",
        "REMOTE_HOST" : "localhost",
        "REQUEST_METHOD" : "GET",
        "SCRIPT_NAME" : "",
        "SERVER_NAME" : "localhost",
        "SERVER_PORT" : "8888",
        "SERVER_PROTOCOL" : "HTTP/1.1",
        "SERVER_SOFTWARE" : "WSGIServer/0.1 Python/2.5",
        }
    app = CallPageFunction("TEST PAGE ARG1={{use ARG1}}", ARG1="TEXT OF ARG1")
    sresult = app(env, misc.ignore)
    result = "".join(list(sresult))
    print "test returns"
    print result
    print "end of test"

if __name__=="__main__":
    test()
