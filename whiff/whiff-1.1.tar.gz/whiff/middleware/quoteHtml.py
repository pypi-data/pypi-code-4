
whiffCategory = "formatting"

whiffDoc = """
{{include "whiff_middleware/heading"}}
whiff_middleware/quoteHtml - quote HTML special characters
{{/include}}

The <code>whiff_middleware/quoteHtml</code>
middleware replaces special characters in
an html page stream to
make the HTML markup visible when displayed
as HTML.

{{include "example"}}
{{using targetName}}quoteHtml{{/using}}
{{using page}}

<b><code>quoteHtml</code> example</b>
<pre>
{{include "whiff_middleware/quoteHtml"}}
<html>
<head> <title> example html document </html> </head>
<body>
<h1>Hello world</h1>
This is a very simple <em>HTML document</em>.
</body>
</html>
</pre>
{{/include}}


{{/using}}
{{/include}}
"""

# import must be absolute
from whiff.middleware import misc
from whiff.resolver import quote

#quotePairs = [("&lt;", "<"), ("&amp;", "&"), ("&gt;", ">")]

class quoteHtml(misc.utility):
    def __init__(self, page):
        self.page = page
    def __call__(self, env, start_response):
        # allow the page to start the response
        page = self.param_value(self.page, env, start_response)
        return [ quote(page) ]

__middleware__ = quoteHtml

if __name__=="__main__":
    q = quoteHtml("<h1>hi there!");
    t = q({}, misc.ignore)
    print "test of quote gives", list(t)
