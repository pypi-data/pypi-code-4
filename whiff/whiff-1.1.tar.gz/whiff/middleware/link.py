"""
Format a link encoding specified cgi parameters (expanded).
"""

whiffCategory = "formatting"

whiffDoc = """
{{include "whiff_middleware/heading"}}
whiff_middleware/link - encode a URL link
{{/include}}

The <code>whiff_middleware/link</code>
middleware is sometimes useful for constructing
complex URLs with many CGI parameters.

{{include "example"}}
{{using targetName}}link{{/using}}
{{using page}}

{{include "whiff_middleware/link"}}
    {{using url}}some/url{{/using}}
    {{using params}}
        { "name": "sally", "age": 12, "grade": 6 }
    {{/using}}
{{/include}}

{{/using}}
{{/include}}

"""

import urllib

# imports must be absolute
from whiff.middleware import misc

class link(misc.utility):
    def __init__(self, url, params):
        self.url = url
        self.params = params
    def __call__(self, env, start_response):
        # it might be useful to generalize this to support "additional parameters"?
        url = self.param_value(self.url, env)
        params = self.param_json(self.params, env)
        uparams = urllib.urlencode(params)
        result = "%s?%s" % (url, uparams)
        headers = self.derive_headers('text/plain')
        start_response("200 OK", headers)
        return [result]

__middleware__ = link

def test():
    env = {}
    app = link("application.cgi", {"variable1": "value1", "variable2": "value2"})
    results = app(env, misc.ignore)
    print "test of link got", list(results)

if __name__=="__main__":
    test()
