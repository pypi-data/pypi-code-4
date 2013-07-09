
whiffCategory = "ajax"

whiffDoc = """
{{include "whiff_middleware/heading"}}
whiff_middleware/loadMonth - load month javascript
{{/include}}

The <code>whiff_middleware/listGetter</code>
middleware returns a javascript function value.
The action of the function is to load the target element
with a month display and also assign all events to the elements
as needed.  This middleware is deprecated, please use <code>jquery</code> instead.
"""

# XXX this needs to be generalized to support other month formats, localization, etc.

# this import must be absolute
from whiff.middleware import misc
from whiff.middleware import monthHtml
from whiff.middleware import wMonth
from whiff.middleware import setInnerHtml
from whiff.middleware import EvalPageFunction

class loadMonth(misc.javaScriptGenerator):
    def __init__(self,
                 target,
                 source,
                 positioner="",
                 prefix="",
                 year=None,
                 month=None,
                 day=None,
                 ymd="", # current form value if any
                 sourceAction="onfocus",
                 style="jswhiff_suggestionItem",
                 ):
        self.prefix = prefix
        self.target = target
        self.positioner = positioner
        self.source = source
        self.sourceAction = sourceAction
        self.year = year
        self.month = month
        self.day = day
        self.ymd = ymd
        self.style = style
    def __call__(self, env, start_response):
        source = self.param_value(self.source, env)
        positioner = self.param_value(self.positioner, env).strip()
        #pr "got positioner", positioner
        if not positioner:
            positioner = source
        sourceAction = self.param_value(self.sourceAction, env)
        prefix = self.param_value(self.prefix, env)
        year = self.param_json(self.year, env)
        month = self.param_json(self.month, env)
        day = self.param_json(self.day, env)
        target = self.param_value(self.target, env)
        ymd = self.param_value(self.ymd, env).strip()
        #pr "loadMonth called with", (prefix, year, month, day, target)
        doFocus = False
        if ymd:
            # if ymd is present, do an immediate focus
            doFocus = True
            # try to parse mdy as yyyy-mm-dd
            symd = ymd.split("-")
            symr = filter(None, symd)
            try:
                iymd = [int(x,10) for x in symd]
            except ValueError:
                #pr "ymd is garbage", symd
                pass # ignore garbage
            else:
                #pr "interpreting ymd values", iymd
                if len(iymd)>0:
                    y = iymd[0]
                    if y>0:
                        while y<1000:
                            y *= 10
                        #pr "setting year", y
                        year = y
                        month = 1
                        day = 1
                if len(iymd)>1:
                    m = iymd[1]
                    if m>0 and m<13:
                        #pr "setting month", m
                        month = m
                if len(iymd)>2:
                    d = iymd[2]
                    if d>0 and d<32:
                        #pr "setting day", d
                        day = d 
        #pr "loadMonth adjusted with", (prefix, year, month, day, target)
        (month, day, year) = monthHtml.fixMDY(month, day, year)
        style = self.param_value(self.style, env)
        # get set innerhtml action to set target content
        monthTextApp = monthHtml.MonthHtml(prefix, year, month, day, style)
        setMonthJavascriptApp = setInnerHtml.setInnerHtml(monthTextApp, target)
        setMonthJavascript = self.param_value(setMonthJavascriptApp, env)
        # get eval functions to bring up next and previous month
        getNextFn = self.LoadOtherMonthfn(env, target, source, positioner, prefix, year, month+1, sourceAction, style, False)
        getPrevFn = self.LoadOtherMonthfn(env, target, source, positioner, prefix, year, month-1, sourceAction, style, False)
        reloadFn = self.LoadOtherMonthfn(env, target, source, positioner, prefix, year, month, sourceAction, style, True, True)
        # create a wMonth month encapsulation
        wm = wMonth.Month(prefix, year, month, day)
        # ids for previous and next links
        lprev = "%s_previous" % prefix
        lnext = "%s_next" % prefix
        ldisable = "%s_disable" % prefix
        start_response("200 OK", [('Content-Type', 'application/javascript')])
        # encapsulate everything in an anonymous function
        yield "(function () { //anonymous function begins \n"
        # first set the innerhtml
        yield setMonthJavascript
        # declare the next and prev actions
        yield "goNext = "
        yield getNextFn
        yield ";\n"
        yield "goPrev = "
        yield getPrevFn
        yield ";\n"
        yield "reload ="
        yield reloadFn
        # declare the bindings
        yield "var Bindings = [\n"
        # month element bindings
        yield wm.jsBindings(lprev, lnext, lprev, lnext)
        # bindings for next and prev elements
        id1 = wm.firstId()
        idn = wm.lastId()
        # lprev binding
        yield "\n"
        yield ', {"id": "%s", "v": "%s", "u": "%s", "d": "%s", "r":"%s", "l": "%s", "action": %s}\n' % (lprev, "(previous)", idn, id1, lnext, idn, "goPrev")
        # lnext binding
        yield ', {"id": "%s", "v": "%s", "u": "%s", "d": "%s", "r":"%s", "l": "%s", "action": %s}\n' % (lnext, "(next)", idn, id1, lprev, id1, "goNext")
        # disble binding
        yield ', {"id": "%s", "v": "%s", "u": "%s", "d": "%s", "r":"%s", "l": "%s", "disable":true, "action": %s}\n' % (ldisable, "(disable)", idn, id1, lprev, id1, "null")
        # end of bindings
        yield "   ];\n"
        # get the source element
        yield 'var sourceElement = document.getElementById("%s");\n' % source.strip()
        bindAction = "    jswhiff_bindSuggestions('%s', '%s', '%s',  null, Bindings, true, null, reload)\n" % (
            source.strip(), target.strip(), positioner.strip(),)        # set the action for the sourceElement
        if doFocus:
            # bind immediately
            yield bindAction
        else:
            # set action for source element
            yield "sourceElement.%s = function () {\n" % sourceAction.strip()
            yield bindAction
            yield "    };\n"
        # finally close and call the anonymous functions
        yield "}) (); // call the anonymous function\n"

    def LoadOtherMonthfn(self, env, target, source, positioner, prefix, year, month, sourceAction, style, useValue, asynchronous=False):
        gen = LoadOtherMonthFunctionPageGen(target, source, positioner, prefix, year, month, sourceAction, style, useValue, "sourceValue")
        page = "\n".join(list(gen))
        cgi_pairs = None
        if useValue:
            cgi_pairs = '[["sourceValue", sourceValue]]'
        loadApp = EvalPageFunction.evalPageFunction(page, cgi_pairs=cgi_pairs, asynchronous=asynchronous)
        loadFunction = self.param_value(loadApp, env)
        def genfn():
            yield "function () {\n"
            yield '   var sourceElement = document.getElementById("%s");\n' % source
            yield '   var sourceValue = sourceElement.value;\n'
            #yield '   alert("got source value "+sourceValue);\n'
            yield "   var loadFunction="
            yield loadFunction
            yield ";\n"
            yield "   loadFunction();\n"
            # make sure the target stays visible
            yield '   var targetElement = document.getElementById("%s");\n' % target
            yield '   targetElement.style.visibility = "visible";\n'
            # set focus to source
            yield '   sourceElement.focus();\n'
            yield '   sourceElement.onfocus();\n'
            yield "}\n"
        g = genfn()
        L = list(g)
        return "".join(L)

def LoadOtherMonthFunctionPageGen(target, source, positioner, prefix, year, month, sourceAction, style, useValue, ValueCgiName):
    yield '{{include "whiff_middleware/loadMonth"}}'
    yield '{{using source}}%s{{/using}}' % source
    yield '{{using target}}%s{{/using}}' % target
    yield '{{using positioner}}%s{{/using}}' % positioner
    if useValue:
        yield '{{using ymd}}{{get-cgi %s/}}{{/using}}' % ValueCgiName
    if prefix:
        yield '{{using prefix}}%s{{/using}}' % prefix
    if year:
        yield '{{using year}}%s{{/using}}' % year
    if month is not None:
        yield '{{using month}}%s{{/using}}' % month
    if sourceAction:
        yield '{{using sourceAction}}%s{{/using}}' % sourceAction
    if style:
        yield '{{using style}}%s{{/using}}' % style
    yield '{{/include}}'
        
__middleware__ = loadMonth

def test():
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
    L = loadMonth("TARGET", "SOURCE", "POSITIONER")
    G = L(env, misc.ignore)
    T = "".join(list(G))
    print "test generates:"
    print T
    
if __name__=="__main__":
    test()
