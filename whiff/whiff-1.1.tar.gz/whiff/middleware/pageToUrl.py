whiffCategory = "ajax"

whiffDoc = """
{{include "whiff_middleware/heading"}}
whiff_middleware/pageToUrl - encode a page as a URL
{{/include}}

The <code>whiff_middleware/pageToUrl</code>
middleware 
creates a URL encoding of a page.
This is the inverse operation of urlToPage.

{{include "example"}}
{{using targetName}}pageToUrl{{/using}}
{{using page}}

{{include "whiff_middleware/pageToUrl"}}
  <h1> Hi there! </h1>
{{/include}}

{{/using}}
{{/include}}
"""

from whiff.middleware import misc
from whiff.rdjson import jsonParse
import urllib

class pageToUrl(misc.utility):
    def __init__(self,
                 page,
                 urlBase="whiff_middleware/urlToPage"):
        self.page = page
        self.urlBase = urlBase
    def __call__(self, env, start_response):
        urlBase = self.param_value(self.urlBase, env)
        sr = StartResponseCatcher()
        content = self.param_value(self.page, env, sr.start_response)
        cgiDict = sr.cgiParameters(content)
        queryString = urllib.urlencode(cgiDict)
        result = "%s?%s" % (urlBase, queryString)
        return self.deliver_page(result, env, start_response)

class StartResponseCatcher:
    def __init__(self):
        # install defaults
        self.status = "200 OK"
        self.headers = [('Content-type', 'text/html')]
    def start_response(self, status, headers):
        self.status = status
        self.headers = headers
    def cgiParameters(self, content):
        D = {}
        D["status"] = self.status
        D["headers"] = jsonParse.format(self.headers)
        D["content"] = content
        return D

__middleware__ = pageToUrl

# === testing

def test():
    app = pageToUrl("<h1>hello world</h1>")
    print "test result", list( app({}, misc.ignore) )

if __name__=="__main__":
    test()
