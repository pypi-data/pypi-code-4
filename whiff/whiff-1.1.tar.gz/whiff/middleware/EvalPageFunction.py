
"""
create a javascript function value which "calls back" to expand a template at the server.
"""

whiffCategory = "ajax"

whiffDoc = """
{{include "whiff_middleware/heading"}}
whiff_middleware/EvalPageFunction -- generate a server call back
{{/include}}

create a javascript function value which "calls back"
to expand a template at the server.
"""


from whiff.rdjson import jsonParse

# these imports must be absolute
from whiff.middleware import misc
from whiff.middleware import expandPostedTemplate
from whiff import resolver
from whiff import whiffenv

class evalPageFunction(misc.javaScriptGenerator):
    def __init__(self, page,
                 expanderUrl="whiff_middleware/expandPostedTemplate",
                 expandRelativeTo=None,
                 asynchronous=False,
                 prefix=None,
                 cgi_pairs=None,
                 doCall=False,
                 inline=False,
                 contentCallback=""):
        self.doCall = doCall
        # the page to expand
        self.page = page
        # the location of the "expander" to do the expansion
        self.url = expanderUrl
        # the cgi prefix to use for extracting relevant parameters
        self.prefix = prefix
        # should the response be delivered asynchonously?
        self.asynchronous = asynchronous
        self.cgi_pairs = cgi_pairs
        self.expandRelativeTo = expandRelativeTo
        self.inline = inline
        self.contentCallback = contentCallback
    def __call__(self, env, start_response):
        env = env.copy()
        # force components to report javascript (except on failure)
        env[whiffenv.CONTENT_TYPE] = "application/javascript"
        #pr
        #pr "evalPageFunction __call__"
        #pr "   page = ", repr(self.page)
        # evaluate the URL
        url = self.param_value(self.url, env)
        url = url.strip()
        contentCallback = self.param_value(self.contentCallback, env).strip()
        if not contentCallback:
            contentCallback = "null" # no user supplied callback is default
        # DO NOT EVALUATE THE PAGE CONTENT! (NOW -- eval on return trip)
        pageContent = self.param_text(self.page)
        if self.prefix:
            prefix = self.param_value(self.prefix, env)
        else:
            prefix = env.get(whiffenv.FULL_CGI_PREFIX, "")
        prefix = prefix.strip()
        # PARSE CGI_PAIRS AS UNINTERPRETED TO ALLOW JAVASCRIPT VARIABLES TO PASS THROUGH
        #cgi_pairs = self.param_json(self.cgi_pairs, env)
        cgi_pairs = self.param_value(self.cgi_pairs, env)
        relativeUrl = "null"
        # adjust the environment relative to relative url if provided
        if self.expandRelativeTo is not None:
            rUrl = self.param_value(self.expandRelativeTo,env)
            #pr "eval page setting relative url", repr(rUrl)
            relativeUrl = jsonParse.formatString(rUrl)
            env = expandPostedTemplate.relativeEnvironment(env, rUrl)
        elif env.has_key(whiffenv.TEMPLATE_PATH):
            ##pr "EvalPageFunction using whiff entry point as relative url", env[whiffenv.ENTRY_POINT]
            #rUrl = env[whiffenv.ENTRY_POINT]
            #pr "EvalPageFunction using template path as relative url", env[whiffenv.TEMPLATE_PATH]
            rUrl = "/"+"/".join(env[whiffenv.TEMPLATE_PATH])
            while rUrl.startswith("//"):
                rUrl = rUrl[1:]
            #pr "eval page function relative url", rUrl
            relativeUrl = jsonParse.formatString(rUrl)
        # package page Content as javascript list format
        linebreak = "\n"
        if self.inline:
            linebreak = ""
        jsArray = misc.jsListFromString(pageContent, linebreak=linebreak)
        # make the url an absolute url
        absoluteUrl = misc.getAbsoluteUrl(url, env)
        #pr "translated absolute url", (url, absoluteUrl)
        D = {}
        D["ARRAY"] = jsArray
        D["URL"] = jsonParse.formatString(absoluteUrl)
        D["RELATIVE_URL"] = relativeUrl
        D["PREFIX"] = jsonParse.formatString(prefix)
        D["CONTENTCALLBACK"] = contentCallback
        asynchronous = False
        if self.asynchronous:
            asynchronous = self.param_json(self.asynchronous, env)
        D["ASYNCHRONOUS"] = jsonParse.format(asynchronous)
        if cgi_pairs:
            D["CGI_PAIRS"] = cgi_pairs # jsonParse.format(cgi_pairs)
        else:
            D["CGI_PAIRS"] = "[]"
        if self.inline:
            # inline call suitable for embedding directly in html tag
            javaScriptText = CALL_TEMPLATE % D
            javaScriptText = resolver.quote(javaScriptText)
        else:
            javaScriptText = JAVASCRIPTTEMPLATE % D
            if self.doCall:
                javaScriptText = "( %s ) ();" % javaScriptText
        #pr
        #pr "evalPage sending javascript"
        #pr javaScriptText.strip()
        #pr "end of evalPage javascript"
        #pr 
        headers = self.derive_headers('application/javascript')
        start_response('200 OK', headers)
        return [javaScriptText]

# split/join whitespace to get one line
CALL_TEMPLATE = """jswhiff_exec_template(%(URL)s, %(ARRAY)s, %(PREFIX)s, %(ASYNCHRONOUS)s, %(RELATIVE_URL)s, %(CGI_PAIRS)s, %(CONTENTCALLBACK)s)"""

JAVASCRIPTTEMPLATE = """
function () {
 var templateArray = %(ARRAY)s;
 var url = %(URL)s;
 var prefix = %(PREFIX)s;
 var asynchronous = %(ASYNCHRONOUS)s;
 var relativeUrl = %(RELATIVE_URL)s;
 var cgi_pairs = %(CGI_PAIRS)s;
 var contentCallback = %(CONTENTCALLBACK)s;
 jswhiff_exec_template(url, templateArray, prefix, asynchronous, relativeUrl, cgi_pairs, contentCallback);
}
"""

__middleware__ = evalPageFunction

if __name__=='__main__':
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
    testApp = evalPageFunction("alert('alert from trivial page');", inline=True)
    print """test output<br>

    <script src="whiff_middleware/whiff.js"></script>

    <h1>Expand a simple template at the server and exec file contents</h1>

    After click you should get an alert saying "alert from trivial page".
    Because it uses absolute paths this page may not work
    if not launched from ../runtest.py.
    <hr>
    """
    #for x in testApp(env, misc.ignore):
    #    print x
    fnSeq = testApp(env, misc.ignore)
    fnList = list(fnSeq)
    fntext = "".join(fnList)
    print '<a href="#nowhere" onclick="%s; return false;">CLICK HERE</a>' % fntext


