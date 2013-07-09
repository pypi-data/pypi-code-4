
whiffCategory = 'formatting'

whiffDoc = """
{{include "whiff_middleware/heading"}}
whiff_middleware/urlEncode - apply standard URL parameter encoding to page text
{{/include}}

The <code>whiff_middleware/urlEncode</code>
middleware
creates a URL parameter encoding of a page.

{{include "example"}}
{{using targetName}}urlEncode{{/using}}
{{using page}}

{{include "whiff_middleware/urlEncode"}}
  <h1> Hi there? </h1>
  {{/include}}

  {{/using}}
  {{/include}}
  """
from whiff.middleware import misc
import urllib

class urlEncode(misc.utility):
    def __init__(self,
                 page,
                 ):
        self.page = page
    def __call__(self, env, start_response):
        page = self.param_value(self.page, env)
        upage = urllib.quote(page)
        return self.deliver_page(upage, env, start_response)

__middleware__ = urlEncode

def test():
    page = "<h1> this that </h1>"
    app = pageToUrl(page)
    print "".join(list(app({}, misc.ignore))) # verbose

if __name__=="__main__":
    test()

                     
