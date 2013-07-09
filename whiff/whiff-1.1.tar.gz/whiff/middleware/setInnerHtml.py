"""
middleware returning javascript fragment which sets the innerHTML of a named element
to the contents of a page.
"""

whiffCategory = "ajax"

whiffDoc = """
{{include "whiff_middleware/heading"}}
whiff_middleware/setInnerHTML - set inner html for element to page
{{/include}}

The <code>whiff_middleware/setInnerHTML</code>
middleware generates javascript code to set
the innerHtml of the HTML DOM element with
name <code>elementName</code> to the contents
of <code>page</code>.

"""
from whiff import stream
from whiff.rdjson import jsonParse
from whiff import whiffenv

# this import must be absolute
from whiff.middleware import misc

class setInnerHtml(misc.javaScriptGenerator):
    def __init__(self, page, elementName=None):
        self.elementName = elementName
        self.page = page
    def __call__(self, env, start_response):
        # get name as a string
        name = self.param_value(self.elementName, env)
        if name:
            name = name.strip()
        if not name:
            # look in environment for default name
            name = whiffenv.getName(env)
        if not name:
            # default to use the current {{id/}}
            name = env.get(whiffenv.FULL_CGI_PREFIX)
        if name:
            name = name.strip()
        if not name:
            raise ValueError, "for setInnerHtml no elementName specified and no cgi prefix set"
        #pr "setInnerHtml.__call__"
        # evaluate the page
        pageContent = self.param_value(self.page, env)
        #pr "page content", repr(pageContent)
        pageContentArray = misc.jsListFromString(pageContent)
        nameString = jsonParse.formatString(name)
        nameString = nameString.strip()
        D = {}
        D["ARRAY"] = pageContentArray
        D["NAME"] = nameString
        javaScriptText = JAVASCRIPTTEMPLATE % D
        headers = self.derive_headers('application/javascript')
        start_response('200 OK', headers)        
        return [javaScriptText]

JAVASCRIPTTEMPLATE = """
var whiff_last_set_inner_html_action = function() {
    var payload = %(ARRAY)s;
    var text = payload.join("");
    var targetId = %(NAME)s;
    var target = document.getElementById(targetId);
    target.innerHTML = text;
};
// execute the action
whiff_last_set_inner_html_action();
"""

__middleware__ = setInnerHtml

if __name__=="__main__":
    testApp = setInnerHtml(elementName="testId", page="fake test page content \nwith two lines")
    print """test output<br>
    <h1>test of generated javascript</h1>
    <pre id="testId">test area, text should be replaced with test page</pre>
    """
    for x in testApp({}, misc.ignore):
        print x


