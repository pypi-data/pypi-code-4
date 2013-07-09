"""
	Middleware to "unquote" an html page stream, replacing &amp; with & and so forth...
"""

whiffCategory = "formatting"

whiffDoc = """
{{include "whiff_middleware/heading"}}
whiff_middleware/unquoteHtml - unquote HTML markup
{{/include}}

The <code>whiff_middleware/unquoteHtml</code>
middleware reverses "quoting" of HTML markup
in the page argument.

{{include "example"}}
{{using targetName}}unquoteHtml{{/using}}
{{using page}}

{{include "whiff_middleware/unquoteHtml"}}
&lt;h1&gt;Hello world&lt;/h1&gt;
This is a very simple &lt;em&gt;HTML fragment&lt;/em&gt;.
{{/include}}

{{/using}}
{{/include}}

"""
from whiff.resolver import unquote
from whiff.middleware import misc

class unquoteHtml(misc.utility):
    def __init__(self, page):
        self.page = page
    def __call__(self, env, start_response):
        page = self.page
        result = self.param_value(self.page, env, start_response)
        result = unquote(result)
        return [result]

__middleware__ = unquoteHtml

if __name__=="__main__":
    t = unquoteHtml("xz&amp;yz&lt;")
    r = t({}, misc.ignore)
    print "test of unquote gives", list(r)
