
whiffCategory = "ajax"

whiffDoc = """
{{include "whiff_middleware/heading"}}
whiff_middleware/loadList generate javascript to load a list
{{/include}}

The <code>whiff_middleware/absPath</code>
middleware returns a javascript function value.
The action of the function is to load the target element
with a list display and also assign all events to the elements
as needed.

{{include "python"}}
getter(prefix, matchValue="", index=None, style=default style)(env, sr)
{{/include}}
returns dictionary
{{include "python"}}
   { "format": htmlformat containing identifier,
     "value": value to deliver to target
     "action": other javascript action to execute on selection (function value, optional)
     "index": the index for the element
     "id": the id for the element
     }
{{/include}}
    or raises <code>IndexError</code> on index too large
one of matchValue or index must be provided.
{{include "python"}}
envelope(name)(env, sr)
{{/include}}
returns an HTML page formatting the a list of dictionaries with previous and next into HTML
the list of dictionaries will be stored at "name" in the environment as
{{include "python"}}
  [dictionaries, previous, next]
{{/include}}
where previous and next are set null whenever they are not needed.
"""

# this import must be absolute
from whiff import whiffenv
from whiff import stream
from whiff.rdjson import jsonParse
from whiff.middleware import misc
from whiff.middleware import setInnerHtml
from whiff.middleware import EvalPageFunction

class exampleGetter(misc.utility):
    "trivialish example getter: format the index inside a span"
    def __init__(self, prefix,
                 matchValue="",
                 index=None,
                 style="jswhiff_suggestionItem",
                 data=None,
                 ):
        self.data = data # not used in this case
        self.index = index
        self.matchValue = matchValue
        self.prefix = prefix
        self.style = style
    def __call__(self, env, start_response):
        index = self.param_json(self.index, env)
        prefix = self.param_value(self.prefix, env)
        matchValue = self.param_value(self.matchValue, env)
        style = self.param_value(self.style, env)
        # resolve the match versus the index
        finalIndex = None
        if matchValue:
            try:
                finalIndex = int(matchValue)
            except ValueError:
                pass
        if finalIndex is None:
            finalIndex = index
        if finalIndex is None:
            raise ValueError, "cannot determine index"
        identifier = "%s_%s"%(prefix, finalIndex)
        format = '<span id="%s" class="%s"> %s </span>' % (identifier, style, index)
        value = str(index)
        action = None
        D = {}
        D["format"] = format
        D["value"] = value
        D["action"] = action
        D["index"] = finalIndex
        D["id"] = identifier
        start_response("200 OK", [('Content-Type', 'application/javascript')])
        yield jsonParse.format(D)

class defaultEnvelope(misc.utility):
    "simple envelope which just formats elements separated by BR tags"
    def __init__(self, dataName="_loadListData"):
        self.dataName = dataName
    def __call__(self, env, start_response):
        dataName = self.param_value(self.dataName, env)
        name = whiffenv.getName(env, dataName)
        data = env[name]
        [dictionaries, previous, next, close] = data
        outList = []
        if previous:
            outList.append(previous["format"])
        for d in dictionaries:
            outList.append(d["format"])
        if next:
            outList.append(next["format"])
        start_response("200 OK", [('Content-Type', 'text/html')])
        inside = False
        yield close["format"]
        yield "<br>\n"
        yield "<center>\n"
        for x in outList:
            if inside:
                yield "<br>\n"
            yield x
            inside = True
        yield "</center>\n"

class loadList(misc.javaScriptGenerator):
    def __init__(self,
                 target, # target identity
                 source, # source identity
                 getter, # middleware to get an item dictionary (index=item number, id=identifier)
                 data=None, # additional data used by getter
                 positioner = "", # positioner element (optional)
                 matchPattern="", # pattern to match, if available
                 envelope=defaultEnvelope, # middleware to wrap the list (page, previousId=prefix+"_prev", nextId=prefix+"_next")
                 start=0, # starting index to display
                 size=None, # number to display (defaults to all)
                 firstIndex=None, # the initial index of the whole series (default to start)
                 focusAt = None, # focus index, default to start
                 prefix="",
                 dataName = "_loadListData",
                 sourceAction="onfocus",
                 style="jswhiff_suggestionItem",
                 reentryUrl="", # configuration entry point for callbacks (must be set to have previous/next)
                 previous="&#8743;",
                 next="&#8744;",
                 ):
        self.prefix = prefix
        self.data = data
        self.target = target
        self.positioner = positioner
        self.source = source
        self.getter = getter
        self.matchPattern = matchPattern
        self.envelope = envelope
        self.sourceAction = sourceAction
        self.start = start
        self.size = size
        self.focusAt = focusAt
        self.style = style
        self.firstIndex = firstIndex
        self.dataName = dataName
        self.next = next
        self.previous = previous
        self.reentryUrl = reentryUrl
        
    def LoadOtherPageGen(self, target, source, positioner, prefix, start, size, firstIndex, dataName,
                  sourceAction, style, reentryUrl, previous, next):
        "load page generator using reentryUrl: reentryUrl is responsible for finding getter and envelope, other parameters passed thru"
        if not reentryUrl:
            raise ValueError, "cannot implement previous/next functionality without reentryUrl"
        start = jsonParse.format(start)
        size = jsonParse.format(size)
        firstIndex = jsonParse.format(firstIndex)
        yield '{{include "%s"}}' % reentryUrl
        yield '{{using target}}%s{{/using}}' % target
        yield '{{using source}}%s{{/using}}' % source
        yield '{{using positioner}}%s{{/using}}' % positioner
        yield '{{using prefix}}%s{{/using}}' % prefix
        yield '{{using start}}%s{{/using}}' % start
        yield '{{using size}}%s{{/using}}' % size
        yield '{{using firstIndex}}%s{{/using}}' % firstIndex
        yield '{{using dataName}}%s{{/using}}' % dataName
        yield '{{using sourceAction}}%s{{/using}}' % sourceAction
        yield '{{using style}}%s{{/using}}' % style
        yield '{{using reentryUrl}}%s{{/using}}' % reentryUrl
        yield '{{using previous}}%s{{/using}}' % previous
        yield '{{using next}}%s{{/using}}' % next
        yield '{{/include}}'
        
    def LoadOther(self, env, target, source, positioner, prefix, start, size, firstIndex, dataName,
                  sourceAction, style, reentryUrl, previous, next, useValue, asynchronous):
        gen = self.LoadOtherPageGen(target, source, positioner, prefix, start, size, firstIndex, dataName,
                                    sourceAction, style, reentryUrl, previous, next)
        page = "\n".join(list(gen))
        cgi_pairs = None
        if useValue:
            cgi_pairs = '[["sourceValue", sourceValue]]'
        #elif start is not None:
        #    cgi_pairs = '[["sourceValue", "%s"]]' % start
        loadApp = EvalPageFunction.evalPageFunction(page, cgi_pairs=cgi_pairs, asynchronous=asynchronous)
        loadFunction = self.param_value(loadApp, env)
        return reloadTargetFunction(source, target, loadFunction)
            
    def otherBindings(self, prefix, name, display, style, action=None):
        identity = "%s__%s" % (prefix, name)
        D = {}
        format = '<span id="%s" class="%s"> %s </span>' % (identity, style, display)
        D["format"] = format
        D["value"] = None
        D["action"] = action
        D["index"] = None
        D["id"] = identity
        return (identity, D)

    def formatBinding(self, identifier, value, up, down, right, left, action, disable):
        disableOption = ""
        if disable:
            disableOption = ', "disable": true'
        if not action:
            action = "null"
        qvalue = jsonParse.format(value)
        f = '{"id": "%s", "v": %s, "u": "%s", "d": "%s", "r":"%s", "l": "%s", "action": %s %s}\n' % (
            identifier, qvalue, up, down, right, left, action, disableOption)
        return f

    def dictBinding(self, dict, up, down):
        identifier = dict.get("id")
        value = dict.get("value")
        action = dict.get("action")
        disable = dict.get("disable")
        return self.formatBinding(identifier, value, up, down, up, down, action, disable)
    
    def bindings(self, elementDicts, previousDict, nextDict, closeDict, focusAt):
        "generate the javascript bindings dictionaries for the elements"
        # map id's to bindings
        D = {}
        upId = downId = None
        sequence = list(elementDicts)
        sequence = sequence + [closeDict]
        if nextDict:
            sequence = sequence + [nextDict]
        if previousDict:
            sequence = sequence + [previousDict]
        i = 0
        for dictionary in sequence:
            identifier = upId = downId = dictionary.get("id")
            upId = sequence[i-1].get("id")
            if i+1<len(sequence):
                downId = sequence[i+1].get("id")
            else:
                downId = sequence[0].get("id")
            binding = self.dictBinding(dictionary, upId, downId)
            D[identifier] = binding
            i+=1
        inside = False
        # generate the focusAt binding if present first
        focusbinding = D.get(focusAt)
        if focusbinding:
            yield focusbinding
            inside = True
        # generate all others in order
        for dictionary in sequence:
            if inside:
                yield ","
            identifier = dictionary.get("id")
            if identifier!=focusAt:
                yield D[identifier]
            inside = True
        
    def __call__(self, env, start_response):
        # copy the environment for safety
        env = env.copy()
        next = self.param_value(self.next, env)
        previous = self.param_value(self.previous, env)
        source = self.param_value(self.source, env)
        positioner = self.param_value(self.positioner, env).strip()
        if not positioner:
            positioner = source
        dataName = self.param_value(self.dataName, env)
        name = whiffenv.getName(env, dataName)
        sourceAction = self.param_value(self.sourceAction, env)
        prefix = self.param_value(self.prefix, env)
        data = self.param_json(self.data, env)
        start = self.param_json(self.start, env)
        size = self.param_json(self.size, env)
        focusAt = self.param_json(self.focusAt, env)
        target = self.param_value(self.target, env)
        style = self.param_value(self.style, env)
        matchPattern = self.param_value(self.matchPattern, env).strip()
        getter = stream.asMiddleware(self.getter, env)
        envelope = stream.asMiddleware(self.envelope, env)
        firstIndex = self.param_json(self.firstIndex, env)
        reentryUrl = self.param_value(self.reentryUrl, env)
        #pr "loadList called with", (start, size, firstIndex)
        # if a cgi require "sourceValue" is provided it overrides matchPattern
        sourceValue = whiffenv.cgiGet(env, "sourceValue", strict=False)
        # by default do deferred focus
        doFocus = False
        #pr "found sourceValue", sourceValue
        if sourceValue:
            # cgi require means that focus should be immediate
            doFocus = True
            matchPattern = sourceValue
        # if matchPattern is provided it overrides start and focusAt
        if matchPattern:
            jfirstIndex = jsonParse.format(firstIndex)
            #pr "matching pattern", (prefix, matchPattern, jfirstIndex, style)
            getFirst = getter(prefix=prefix, matchValue=matchPattern, index=jfirstIndex, style=style, data=data)
            first = self.param_json(getFirst, env) 
            #pr "adjusting with getFirst", first
            start = first["index"]
            focusAt = first["index"]
        if focusAt is None:
            focusAt = start
        #if firstIndex is None:
        #    firstIndex = start
        #pr "loadList adjusted with", (start, size, firstIndex)
        # collect the info on elements for the list
        elements = []
        index = start
        end = None
        noMore = False
        if start is None:
            start = 0
        if size is not None:
            end = start+size
        while end is None or index<end:
            elementIdentifier = "%s_%s" % (prefix, index)
            try:
                #pr "getting index", (prefix, index, style)
                sindex = jsonParse.format(index)
                elementApp = getter(prefix=prefix, index=sindex, style=style, data=data)
                # may raise index error on past end
                elementDict = self.param_json(elementApp, env)
            except IndexError:
                noMore = True
                break
            elements.append(elementDict)
            index += 1
        # determine whether to include previous and next links
        previousId = previousDict = None
        if (firstIndex is None or firstIndex<start) and size is not None and reentryUrl:
            (previousId, previousDict) = self.otherBindings(prefix, "previous", previous, style, "goPrevious")
        nextId = nextDict = None
        if not noMore and size is not None and reentryUrl:
            (nextId, nextDict) = self.otherBindings(prefix, "next", next, style, "goNext")
        (closeId, closeDict) = self.otherBindings(prefix, "close", "&#215;", style, "null")
        closeDict["disable"] = True
        # place the dictionaries in the environment for use by the envelope
        env[name] = [elements, previousDict, nextDict, closeDict]
        # get the bindings sequence
        bindingsGen = self.bindings(elements, previousDict, nextDict, closeDict, focusAt)
        # get set innerhtml action to set target content by evaluating the envelope
        contentApp = envelope(dataName=dataName)
        setContentJavascriptApp = setInnerHtml.setInnerHtml(contentApp, target)
        setContentJavascript = self.param_value(setContentJavascriptApp, env)
        # get eval functions to bring up next and previous segments
        getNextFn = None
        if nextId is not None:
            getNextFn = self.LoadOther(env, target, source, positioner, prefix, start+size, size, firstIndex, dataName,
                                       sourceAction, style, reentryUrl, previous, next, False, False)
        getPrevFn = None
        if previousId is not None:
            previousStart = start-size
            if previousStart<firstIndex:
                previousStart = firstIndex
            getPrevFn = self.LoadOther(env, target, source, positioner, prefix, previousStart, size, firstIndex, dataName,
                                       sourceAction, style, reentryUrl, previous, next, False, False)
        # if an entry Url is provided, define a reload function
        reloadFn = None
        if reentryUrl:
            reloadFn = self.LoadOther(env, target, source, positioner, prefix, start, size, firstIndex, dataName,
                                       sourceAction, style, reentryUrl, previous, next, True, True)
        # ids for previous and next links
        start_response("200 OK", [('Content-Type', 'application/javascript')])
        # encapsulate everything in an anonymous function
        yield "(function () { //anonymous function begins \n"
        # first set the innerhtml
        yield setContentJavascript
        # declare the next and prev actions
        if getNextFn:
            yield "goNext = "
            yield getNextFn
            yield ";\n"
        if getPrevFn:
            yield "goPrevious = "
            yield getPrevFn
            yield ";\n"
        if reloadFn:
            yield "reload = "
            yield reloadFn
            yield ";\n"
            reloadAction = "reload"
        else:
            reloadAction = "null"
        # declare the bindings
        yield "var Bindings = [\n"
        # element bindings
        for b in bindingsGen:
            yield b
        # end of bindings
        yield "   ];\n"
        # get the source element
        yield 'var sourceElement = document.getElementById("%s");\n' % source.strip()
        bindAction = "    jswhiff_bindSuggestions('%s','%s', '%s', null, Bindings, true, null, %s);\n" % (
            source.strip(), target.strip(), positioner.strip(), reloadAction)
        if doFocus:
            # immediate focus: execute the bind now
            yield bindAction
        else:
            # deferred focus: set the action for the sourceElement
            yield "sourceElement.%s = function () {\n" % sourceAction.strip()
            yield bindAction
            yield "    };\n"
        # finally close and call the anonymous functions
        yield "}) (); // call the anonymous function\n"

def reloadTargetFunctionGen(source, target, loadFunction):
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

def reloadTargetFunction(source,target,loadFunction):
    g = reloadTargetFunctionGen(source, target, loadFunction)
    L = list(g)
    return "".join(L)

__middleware__ = loadList

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
    L = loadList("TARGET", "SOURCE",
                  getter=exampleGetter,
                  matchPattern="123",
                  envelope=defaultEnvelope,
                  start=99,
                  size=10,
                  firstIndex=-1000,
                  focusAt="124",
                  prefix="XXX",
                  reentryUrl="/TESTURL")
    G = L(env, misc.ignore)
    T = "".join(list(G))
    print "test generates:"
    print T
    
if __name__=="__main__":
    test()
