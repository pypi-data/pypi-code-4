whiffCategory = "formatting"

whiffDoc = """
{{include "whiff_middleware/heading"}}
whiff_middleware/oneLine - collapse white space
{{/include}}
The <code>oneLine</code> middleware 
return content of page on one line
with whitespace collapsed to single blank.
This is useful, when appropriate, for reducing
URL lengths and the lengths of other data transfers.
"""

# import must be absolute
from whiff.middleware import misc

class oneLine(misc.utility):
    def __init__(self, page):
        self.page = page
        
    def __call__(self, env, start_response):
        # allow the page to start the response
        page = self.param_value(self.page, env, start_response)
        page = " ".join(page.split())
        return [ page ]

__middleware__ = oneLine

if __name__=="__main__":
    q = oneLine("<h1>\n\nhi there!   buddy\n    uh huh");
    t = q({}, misc.ignore)
    print "test of oneLine gives", list(t)
