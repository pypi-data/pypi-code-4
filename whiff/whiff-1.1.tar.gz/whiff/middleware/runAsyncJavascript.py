whiffCategory = "ajax"

whiffDoc = """
{{include "whiff_middleware/heading"}}
whiff_middleware/runAsyncJavascript -- get a javascript page from the server and run it without pausing the browser
{{/include}}


The <code>whiff_middleware/runJavascript</code>
middleware is useful for implementing AJAX-type functionality.
It generates a javascript code fragment
to load the result of a request from the server and attempt to execute the content
of the response as javascript in the context of the current page without causing
the browser to wait for the result.  This is a variant of
<code>whiff_middleware/runJavascript</code>, which see.
{{include "whiffhtml"}}

{${include "whiff_middleware/runAsyncJavascript"  Url:"Greeting"}$}
     message: "Hello world",
     user: username
{${/include}$}

{{/include}}
"""

import runJavascript

def runAsyncJavascript(page="", Url=""):
    return runJavascript.__middleware__(page=page, Url=Url, asynchronous=True)

__middleware__ = runAsyncJavascript
