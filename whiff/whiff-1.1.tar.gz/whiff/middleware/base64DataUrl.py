whiffDoc = """
{{include "whiff_middleware/heading"}}
whiff_middleware/base64DataUrl -- generate a data link for content encoded using base64 encoding
{{/include}}

The <code>whiff_middleware/base64DataUrl</code>
encodes that data content as a data URL using base64 encoding.
This is useful for embedding image data into HTML document without
the use of links outside the document.

{{include "example"}}
{{using targetName}}base64DataUrl{{/using}}
{{using page}}

<img src="{{include "whiff_middleware/base64DataUrl" whiff.strip: true}}
    {{include "whiff_middleware/png/bnfImage"}}
    apple ::= (oranges | "peaches")* animals
    {{/include}}
{{/include}}">


{{/using}}
{{/include}}
"""

whiffCategory = "Formatting"

# import must be absolute
from whiff.middleware import misc
#import misc
from whiff.resolver import quote
import base64
from whiff import stream

class base64DataUrl(misc.utility):
    def __init__(self, page):
        self.page = page
    def __call__(self, env, start_response):
        # allow the page to start the response
        page = self.param_binary(self.page, env)
        page = stream.mystr(page)
        b64data = base64.b64encode(page)
        content_type = self.component_content_type()
        assert content_type is not None, "no content type for payload"
        url = "data:%s;base64,%s" % (content_type, b64data)
        return self.deliver_page(url, env, start_response)

__middleware__ = base64DataUrl

def test():
    env = {}
    from png.bnfImage import bnfImage
    bnfapp = bnfImage('apple ::= (oranges | "peaches")* animals')
    app = base64DataUrl(bnfapp)
    sresult = app(env, misc.ignore)
    result = "".join(list(sresult))
    print "test got", repr(result)
    print "<br>"
    print '<img src="%s">' % result

if __name__=="__main__":
    test()

