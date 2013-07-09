
whiffCategory = "ajax"

whiffDoc = """
{{include "whiff_middleware/heading"}}
whiff_middleware/PopUpJS - load content and pop-up HTML section
{{/include}}

The <code>whiff_middleware/PopUpJS</code>
middleware 
returns javascript to popup targetId with content loaded from page,
providing both show (popup) and hide functions.
"""

# this import must be absolute
from whiff import whiffenv
from whiff import stream
from whiff.rdjson import jsonParse
from whiff.middleware import misc
from whiff.middleware import setInnerHtml
from whiff.middleware import EvalPageFunction

class PopUpJS(misc.utility):
    def __init__(self,
                 positionId, # id of element to popup near
                 popupId,  # initial popup content should say something like "loading..."
                 page,
                 expandPage=False,
                 javascript="", # javascript to execute after pop up show
                 hideJavascript="", # javascript to execute after pop up hide
                 hideFunction = "",
                 showFunction = "",
                 asynchronous = True,
                 ):
        # xxxx if async and javascript then javascript may execute BEFORE popup is loaded!
        self.showFunction = showFunction
        self.hideFunction = hideFunction
        self.popupId = popupId
        self.positionId = positionId
        self.page = page
        self.asynchronous = asynchronous
        self.javascript = javascript
        self.hideJavascript = hideJavascript
        self.expandPage = expandPage
    def __call__(self, env, start_response):
        expandPage = self.param_json(self.expandPage, env)
        if expandPage:
            pageText = self.param_value(self.page, env)
        else:
            pageText = self.param_text(self.page)
        showFunction = self.param_value(self.showFunction, env).strip()
        hideFunction = self.param_value(self.hideFunction, env).strip()
        showFunction = self.param_value(self.showFunction, env).strip()
        javascript = self.param_value(self.javascript, env)
        hideJavascript = self.param_value(self.hideJavascript, env)
        popupId = self.param_value(self.popupId, env).strip()
        positionId = self.param_value(self.positionId, env).strip()
        asynchronous = self.param_json(self.asynchronous, env)
        setHtmlText = """
        {{include "whiff_middleware/setInnerHtml"}}
            {{using page}}%s{{/using}}
            {{using elementName}}%s{{/using}}
        {{/include}}
        """ % (pageText, popupId)
        loadApp = EvalPageFunction.evalPageFunction(setHtmlText, asynchronous=asynchronous)
        loadFn = self.param_value(loadApp, env)
        showFn = """
        (function (x,y) {
            var popupId = "%s";
            var popupElement = document.getElementById(popupId);
            if ( (x==null) || (y==null) ) {
                var positionId = "%s";
                var positionElement = document.getElementById(positionId);
                jswhiff_PositionElementAt(popupElement, positionElement);
            } else {
                popupElement.style.left = x+"px";
                popupElement.style.top = y+"px";
            }
            //al("making visible "+popupElement);
            popupElement.style.visibility = "visible";
            var setHtml = (%s);
            setHtml();
            %s
        })
        """ % (popupId, positionId, loadFn, javascript)
        hideFn = """
        (function () {
            var popupElement = document.getElementById("%s");
            popupElement.style.visibility = "hidden";
            %s
        })
        """ % (popupId, hideJavascript)
        start_response("200 OK", [('Content-Type', 'application/javascript')])
        if showFunction:
            # NOTE: intentionally install the function at global scope!
            #yield "var "
            yield showFunction
            yield " = "
            yield showFn
            yield ";\n"
        else:
            # if showFn name is not provided simply execute the show operation
            yield "( //show pop up operation"
            yield showFn
            yield ") () ; // execute the show operation"
        if hideFunction:
            # NOTE: intentionally install the function at global scope!
            #yield "var "
            yield hideFunction
            yield " = "
            yield hideFn
            yield ";\n"
            
__middleware__ = PopUpJS

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
    p = PopUpJS("POSITION", "POPUP", "HELLO FROM THE PAGE", hideFunction="HIDEFUNCTION", showFunction="SHOWFUNCTION")
    g = p(env, misc.ignore)
    print "test result"
    print "".join(list(g))

if __name__=="__main__":
    test()
