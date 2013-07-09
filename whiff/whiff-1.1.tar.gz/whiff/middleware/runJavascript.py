
whiffCategory = "ajax"

whiffDoc = """
{{include "whiff_middleware/heading"}}
whiff_middleware/runJavascript -- get a javascript page from the server and run it
{{/include}}

The <code>whiff_middleware/runJavascript</code>
middleware is useful for implementing AJAX-type functionality.
It generates a javascript code fragment
to load the result of a request from the server and attempt to execute the content
of the response as javascript in the context of the current page.
Any form parameters on the current page are sent to the request
as CGI form parameters, and the middleware allows other CGI form
parameters to be added to the request as well.
<p>
For example

{{include "whiffhtml"}}
<script>
var username = "Administrator";


{${include "whiff_middleware/runJavascript"  Url:"Greeting"}$}
     message: "Hello world",
     user: username
{${/include}$}

</script>
{{/include}}
generates javascript which requests the content for <code>./Greeting</code> in the current
context, assigning the CGI parameter <code>message</code> the value
<code>Hello world</code> and the CGI parameter "user" the current content of the javascript
variable <code>username</code>.  When the content for the request is received it will be
evaluated as Javascript in the browser.

"""

from whiff.middleware import misc
from whiff.middleware import Eval
from whiff import whiffenv

class runJavascript(misc.utility):
    def __init__(self, page="", Url="", asynchronous=False, contentCallback="null"):
        self.page = page
        self.Url = Url
        self.asynchronous = asynchronous
        self.contentCallback = contentCallback
    def __call__(self, env, start_response):
        Url = self.param_value(self.Url, env).strip()
        page = self.param_value(self.page, env).strip()
        contentCallback = self.param_value(self.contentCallback, env).strip()
        asynchronous = self.param_json(self.asynchronous, env)
        if not Url:
            assert "Url" in env, "could not determine request URL for runJavascript "+repr(page)
            Url = env["Url"].strip()
            assert Url, "Url for runJavascript must be non-empty"
        D = {}
        D["Url"] = Url
        D["page"] = page
        D["contentCallback"] = contentCallback
        if asynchronous:
            D["async"] = "true"
        else:
            D["async"] = "false"
        template = EVALCONTENTTEMPLATE % D
        relativeUrl = env[whiffenv.TEMPLATE_URL] #whiffenv.absPath(env, "dummy.txt")
        #pr "template="
        #pr template
        #pr "relativeUrl", relativeUrl
        application = Eval.__middleware__(
            page = template,
            relativeUrl = relativeUrl, # XXXXXX???
            )
        return self.deliver_page(application, env, start_response)

# page template to interpret
EVALCONTENTTEMPLATE = """
(
function () { // load and run javascript from %(Url)s
    var descriptorMapping = { %(page)s };
    var cgi = [];
    for (var descriptorName in descriptorMapping) {
        var descriptorValue = descriptorMapping[descriptorName];
        cgi.push( [descriptorName, descriptorValue] );
    }
    var action = 
    {{include "whiff_middleware/EvalPageFunction"}}
        {{using page}} {{include "%(Url)s"/}} {{/using}}
        {{using cgi_pairs}} cgi {{/using}}
        {{using asynchronous}} %(async)s {{/using}}
        {{using contentCallback}} %(contentCallback)s {{/using}}
    {{/include}};
    action();
}
) (); // evaluate anonymous function to load and run javascript from %(Url)s
"""

__middleware__ = runJavascript
