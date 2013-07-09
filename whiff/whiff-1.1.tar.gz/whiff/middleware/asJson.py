"""
Middleware to format a page value as a json value (properly quoted)
"""

whiffCategory = "formatting"

whiffDoc = """
{{include "whiff_middleware/heading"}}
whiff_middleware/asJson - format page as Json string
{{/include}}

The <code>whiff_middleware/asJson</code>
middleware translates a page value into a
JSON formatted string suitable for inclusion
in other JSON data structures.

{{include "example"}}
{{using targetName}}asJson{{/using}}
{{using page}}

{{include "whiff_middleware/asJson"}}

this sub-page has "quotes"
and new lines and also includes
{{include "whiff_middleware/absPath"}}other/directives{{/include}}.

{{/include}}

{{/using}}
{{/include}}

"""

from whiff.middleware import misc
from whiff.rdjson import jsonParse

class asJson(misc.utility):
    def __init__(self, page):
        self.page = page
    def __call__(self, env, start_response):
        page = self.param_value(self.page, env)
        start_response("200 OK", [('Content-Type', 'application/javascript')])
        yield( jsonParse.format(page) )

__middleware__ = asJson

def test():
    testpage = """ page including quote " and slashes //\\ """
    app = asJson(testpage)
    print "test value is", list(app({}, misc.ignore))

if __name__=="__main__":
    test()
    
