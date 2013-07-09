"""
	Middleware to "unquote" an html page stream, replacing &amp; with & and so forth...
"""

whiffCategory = "formatting"

whiffDoc = """
{{include "whiff_middleware/heading"}}
whiff_middleware/unquoteEntities - unquote entities in HTML markup
{{/include}}

The <code>whiff_middleware/unquoteEntities</code>
middleware reverses "quoting" of HTML markup for entities
so that unicode entities (for example) will show up
as unicode glyphs when presented as html
in the page argument.

{{include "example"}}
{{using targetName}}unquoteEntities{{/using}}
{{using page}}

{{include "whiff_middleware/unquoteEntities"}}
&lt;h1&gt;Hello world&lt;/h1&gt;
This is a very simple &lt;em&gt;HTML fragment&lt;/em&gt;
-- with some unicode entities: <b>&amp;#952;&amp;#949;&amp;#8056;&amp;#962;:</b>.
{{/include}}

{{/using}}
{{/include}}

"""
from whiff.resolver import entitiesOk
from whiff.middleware import misc

class unquoteHtml(misc.utility):
    def __init__(self, page):
        self.page = page
    def __call__(self, env, start_response):
        page = self.page
        result = self.param_value(self.page, env, start_response)
        result = entitiesOk(result)
        return [result]

__middleware__ = unquoteHtml

if __name__=="__main__":
    t = unquoteHtml("xz&amp;yz&lt;")
    r = t({}, misc.ignore)
    print "test of unquote gives", list(r)
