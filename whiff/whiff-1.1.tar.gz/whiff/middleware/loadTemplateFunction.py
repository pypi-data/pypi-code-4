
whiffCategory = "ajax"

whiffDoc = """
{{include "whiff_middleware/heading"}}
whiff_middleware/loadTemplateFunction
{{/include}}

The <code>whiff_middleware/loadTemplateFunction</code>
middleware 
makes a javascript function which loads an HTML page
and a JAVASCRIPT page from the server and sets the HTML
content as the inner HTML of element with id ELEMENT_ID,
and subsequently executes the javascript (for example
to define callbacks for newly created elements).
"""

# these imports must be absolute

# XXXX as an optimization, if no additional arguments are provided, could uses EvalPageFunction
from whiff.middleware import CallPageFunction
from whiff.middleware import misc

# XXXX this method generates two http requests, when one might be sufficient?

NULL_FUNCTION = "function() {}"

# this template is emulated -- not used directly (for reference)
SET_INNER_HTML_FUNCTION_TEMPLATE = """
    {{include "whiff_middleware/CallPageFunction"}}
// Generate HTML and javascript at server to execute here
// first load template to the element innerHTML
        {{include "whiff_middleware/setInnerHtml"}}
            {{using elementName}}%(ELEMENT_ID)s{{/using}}
            {{using page}}%(HTML_PAGE)s{{/using}}
        {{/include}}
        ;
// then execute the javascript
        %(JAVASCRIPT_PAGE)s
        ;
    {{/include}}
"""

# "call-back" template to expand html template and execute javascript
INNER_HTML_ACTION_TEMPLATE = """
// Generate HTML and javascript at server to execute here
// first load template to the element innerHTML
        {{include "whiff_middleware/setInnerHtml"}}
            {{using elementName}}%(ELEMENT_ID)s{{/using}}
            {{using page}}%(HTML_PAGE)s{{/using}}
        {{/include}}
        ; // end of code to load HTML
// then execute the javascript
        %(JAVASCRIPT_PAGE)s
"""

class loadTemplateFunction(misc.javaScriptGenerator):
    def __init__(self, page, elementId, javascriptPage=None,
                 expanderUrl="whiff_middleware/expandPostedTemplate",
                 expandRelativeTo=None,
                 asynchronous=False,
                 prefix=None,
                 doCall=False,
                 **page_arguments):
        self.doCall = doCall
        self.page = page
        self.elementId = elementId
        self.javascriptPage = javascriptPage
        self.expanderUrl = expanderUrl
        self.expandRelativeTo = expandRelativeTo
        self.asynchronous = asynchronous
        self.prefix = prefix
        self.page_arguments = page_arguments
    def __call__(self, env, start_response):
        D = {}
        D["SET_INNER_HTML_FUNCTION"] = NULL_FUNCTION
        D["EXEC_JAVASCRIPT_FUNCTION"] = NULL_FUNCTION
        page = self.page
        elementId = self.elementId
        javascriptPage = self.javascriptPage
        expanderUrl = self.expanderUrl
        expandRelativeTo = self.expandRelativeTo
        asynchronous = self.asynchronous
        prefix = self.prefix
        # expand the non-templates
        eId = self.param_value(elementId, env)
        if eId: eId = eId.strip()
        expUrl = self.param_value(expanderUrl, env)
        if expUrl: expUrl = expUrl.strip()
        expRelative = self.param_value(expandRelativeTo, env)
        if expRelative: expRelative = expRelative.strip()
        prefix = self.param_value(prefix, env)
        # DON'T expand the template
        pageText = self.param_text(page)
        javascriptText = self.param_text(javascriptPage)
        # set substitutions in call back payload
        D = {}
        if pageText is None:
            raise ValueError, "page text cannot be None"
        if eId is None:
            raise ValueError, "element id cannot be None"
        D["ELEMENT_ID"] = eId
        D["HTML_PAGE"] = pageText
        D["JAVASCRIPT_PAGE"] = "// no javascript"
        if javascriptText is not None:
            D["JAVASCRIPT_PAGE"] = javascriptText
        javaScriptText = INNER_HTML_ACTION_TEMPLATE % D
        pageFunctionMaker = CallPageFunction.__middleware__(
            javaScriptText, expanderUrl, expandRelativeTo, asynchronous, prefix,
            doCall=self.doCall, **self.page_arguments)
        return pageFunctionMaker(env, start_response)

__middleware__ = loadTemplateFunction

if __name__=="__main__":
    testapp = loadTemplateFunction("THE NEW VALUE", "myElementId",
                                   "alert('YOU CLICKED')")
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
    sresult = testapp(env, misc.ignore)
    lresult = list(sresult)
    result = "".join(lresult)
    print """test output <br>
    <script src="whiff_middleware/whiff.js"></script>

    <h1>Load from server test</h1>
    
    Below is a simple table
    <center>
    <table border>
    <tr>
    <td id="myElementId">THIS IS THE OLD VALUE</td>
    <td> <input type="BUTTON" name="BUTTON" value="BUTTON" onclick="buttonClick()"> </td>
    </tr>
    </table>
    </center>
    When you click the button the value should change to THE NEW VALUE
    and you should get an alert saying "YOU CLICKED".  Behind the scenes
    is a (trivial) round trip back to the server to expand the template.
    <script>
    """
    print "var buttonClick=", result, ";"
    print "</script>"

