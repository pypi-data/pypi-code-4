
whiffCategory = "ajax"


whiffDoc = """
{{include "whiff_middleware/heading"}}
whiff_middleware/resetHTML -- set document element content to page expansion
{{/include}}

The <code>whiff_middleware/resetHTML</code>
middleware is useful for implementing AJAX-type functionality.
It generates a javascript code fragment
to load the result of a request from the server set the HTML of a
document element to the content.
Any form parameters on the current page are sent to the request
as CGI form parameters, and the middleware allows other CGI form
parameters to be added to the request as well.
<p>
For example

{{include "whiffhtml"}}

<div id="GreetingDiv"> (greeting not yet loaded) </div>

<script>
var username = "Administrator";


{${include "whiff_middleware/resetHTML" 
     id: "GreetingDiv",
     Url:"Greeting"
}$}
     message: "Hello world",
     user: username
{${/include}$}

</script>
{{/include}}
generates javascript which requests the content for <code>./Greeting</code> in the current
context, assigning the CGI parameter <code>message</code> the value
<code>Hello world</code> and the CGI parameter "user" the current content of the javascript
variable <code>username</code>.  When the content for the request is received it will be
loaded as the content of the document element <code>GreetingDiv</code>.

"""

from whiff.middleware import misc
from whiff.middleware import runJavascript
from whiff import whiffenv

class resetHTML(misc.utility):
    def __init__(self, page="", Url="", id="", asynchronous=False):
        self.page = page
        self.Url = Url
        self.asynchronous = asynchronous
        self.id = id        
    def __call__(self, env, start_response):
        id = self.param_value(self.id, env).strip()
        if not id:
            assert "id" in env, "could not determine document element identity for resetHTML "+repr(page)
            id = env["id"].strip()
            assert id, "id for resetHTML must be non-empty"
        runJSApplication = runJavascript.__middleware__(page=self.page, Url=self.Url, asynchronous=self.asynchronous, contentCallback="setHtmlCallback")
        runJSprogram = self.param_value(runJSApplication, env)
        D = {}
        D["ID"] = id
        D["RUNJAVASCRIPT"] = runJSprogram
        result = TEMPLATE % D
        start_response("200 OK", [('Content-Type', 'application/javascript')])
        return [result]
        
TEMPLATE = """
(function () {
    function setHtmlCallback (htmlstring) {
        var element = document.getElementById("%(ID)s");
        element.innerHTML = htmlstring;
    }
    %(RUNJAVASCRIPT)s
}) () // call anon function
"""

__middleware__ = resetHTML        
