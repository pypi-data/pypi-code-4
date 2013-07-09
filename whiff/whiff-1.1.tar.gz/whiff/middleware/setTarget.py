
whiffCategory = "ajax"

whiffDoc = """
{{include "whiff_middleware/heading"}}
whiff_middleware/setTarget - set javascript properties for HTML DOM element
{{/include}}

The <code>whiff_middleware/setTarget</code>
middleware 
assigns the innerHtml and javascript
callbacks for an HTML DOM element.
"""

# these imports must be absolute
from whiff.middleware import misc
from whiff.middleware import loadTemplateFunction

# XXXX as an optimization, if no additional arguments are provided, could uses EvalPageFunction
from whiff.middleware import CallPageFunction
from whiff.middleware import EvalPageFunction
from whiff import whiffenv
from whiff import parseTemplate

CALLBACKLIST = """
onabort onblur onchange onclick ondblclick
onerror onfocus onkeydown onkeyup onmousedown
onmouseout onmouseover onmouseup onmove
onreset onresize onsubmit onload onunload
""".split()

CALLBACKDICT = {}
for x in CALLBACKLIST:
    CALLBACKDICT[x] = x

class setTarget(misc.javaScriptGenerator):
    def __init__(self, target, innerHtml=None, miscJavascript=None,
                 expanderUrl="whiff_middleware/expandPostedTemplate",
                 expandRelativeTo=None,
                 asynchronous=False,
                 prefix=None,
                 doCall=False,
                 **callbacks_and_arguments):
        self.doCall = doCall
        # separate callbacks from arguments
        callbacks = {}
        page_arguments = {}
        for (n,v) in callbacks_and_arguments.items():
            if n in CALLBACKDICT:
                callbacks[n] = v
            else:
                page_arguments[n] = v
        # make sure there is something to do
        if not innerHtml and not callbacks:
            raise ValueError, "no innerhtml or callbacks -- nothing to do!"
        self.target = target
        self.innerHtml = innerHtml
        self.miscJavascript = miscJavascript
        self.expanderUrl = expanderUrl
        self.expandRelativeTo = expandRelativeTo
        self.asynchronous = asynchronous
        self.prefix = prefix
        self.callbacks = callbacks
        self.page_arguments = page_arguments
    def jsGenerator(self, env):
        expanderUrl = self.expanderUrl
        expandRelativeTo = self.expandRelativeTo
        asynchronous = self.asynchronous
        prefix = self.prefix
        my_start_response = self.my_start_response
        if self.miscJavascript or self.callbacks:
            yield("// create an anonymous function and call it")
            yield("var lastSetTargetAction = function () {")
            yield("   // get the target")
            target = self.param_value(self.target, env)
            target = target.strip()
            yield('   var target = document.getElementById("%s");' % target)
            callbacks = self.callbacks.items()
            callbacks.sort()
            for (cbname, callback) in callbacks:
                callbackText = self.param_text(callback)
                #callbackText = parseTemplate.quoteText(callbackText)
                callbackJavascriptMaker = CallPageFunction.__middleware__(
                    callbackText, expanderUrl, expandRelativeTo,
                    asynchronous, prefix, **self.page_arguments)
                callbackJavascriptSeq = callbackJavascriptMaker(env, my_start_response)
                callbackJavascript = "".join(list(callbackJavascriptSeq))
                # need to quote callback javascript so it will pass through the first template evaluation
                callbackJavascript = parseTemplate.quoteText(callbackJavascript)
                #pr "setTarget callback for", repr(cbname)
                #pr "yeilding"
                #pr callbackJavascript
                #pr "end of yield"
                yield("   target.%s = %s ;" % (cbname, callbackJavascript))
            if self.miscJavascript:
                yield self.param_text(self.miscJavascript)
                yield ";"
            yield(" };")
            yield("// call the function now")
            yield("lastSetTargetAction();")
    def javascriptPage(self, env):
        L = list(self.jsGenerator(env))
        return "\n".join(L)
    def __call__(self, env, start_response):
        jscallbacks = self.javascriptPage(env)
        if self.innerHtml:
            # wrap using loadTemplateFunction
            elementId = self.target
            page = self.innerHtml
            # DON'T need to quote javascript so template will pass through first evaluation
            javascriptPage = jscallbacks
            app = loadTemplateFunction.__middleware__(
                page, elementId, javascriptPage,
                self.expanderUrl, self.expandRelativeTo,
                self.asynchronous, self.prefix, doCall=True)
            #return dump(app(env, start_response))
            page = self.param_value(app,env)
            # need to quote page so it survives the first round trip
            page = parseTemplate.quoteText(page)
        else:
            # otherwise just expand the the javascript template
            page = jscallbacks
        env = env.copy()
        env[whiffenv.CONTENT_TYPE] = "application/javascript"
        # if there are page arguments then use callpage, otherwise use the simpler expandpage implementation
        if self.page_arguments:
            #pr "page args", self.page_arguments
            app = CallPageFunction.__middleware__(
                page,
                self.expanderUrl, self.expandRelativeTo,
                self.asynchronous, self.prefix, doCall=self.doCall, **self.page_arguments)
        else:
            #pr "no page args", self.page_arguments
            app = EvalPageFunction.__middleware__(
                page,
                self.expanderUrl, self.expandRelativeTo,
                self.asynchronous, self.prefix, doCall=self.doCall)
        return dump(app(env, start_response))

def dump(data):
    ldata = list(data)
    sdata = "".join(ldata)
    #pr "SET TARGET SENDING"
    #pr sdata
    #pr "END OF SET TARGET SEND"
    return ldata

__middleware__ = setTarget

if __name__=="__main__":
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
    testapp1 = setTarget("exampleId", "NEW INNER HTML1", "alert('misc javascript1')",
               onclick= "alert('onclick via server callback1')") #, dummy1="dummy1")
    sresult1 = testapp1(env, misc.ignore)
    lresult1 = list(sresult1)
    result1 = "".join(lresult1)
    print "test output from setTarget.py<br>"
    print "<script>"
    print "var callback1=", result1, ";"
    testapp2 = setTarget("exampleId", None, "alert('only javascript2')",
               onclick= "alert('onclick2 via server callback')", dummy2="dummy2")
    sresult2 = testapp2(env, misc.ignore)
    lresult2 = list(sresult2)
    result2 = "".join(lresult2)
    print "var callback2=", result2, ";"
    print "</script>"
    print """
    <script src="whiff_middleware/whiff.js"></script>
    <h1>set callback test</h1>

    <table border>
    <tr>
    <td>click:</td>
    <td bgcolor="pink" id="exampleId" onclick="alert('old onclick')">
    ORIGINAL TEXT</td>
    </tr>
    </table>
    <hr>
    <input type="button" value="1: change text, get alert, change onclick"
           onclick="callback1()">
    <input type="button" value="2: same text, get alert, change onclick"
           onclick="callback2()">
    <hr><hr>
"""
