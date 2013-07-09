"""
Format an "<a href...>" anchor
"""

whiffCategory = "formatting"

whiffDoc = """
{{include "whiff_middleware/heading"}}
whiff_middleware/anchor - format an anchor
{{/include}}

The <code>whiff_middleware/anchor</code> is
a tool which is sometimes useful for
creating a large and complex <code>&lt;a href...&gt;</code> links.

{{include "example"}}
{{using targetName}}anchor{{/using}}
{{using page}}

{{include "whiff_middleware/anchor"}}
   {{using url}}http://whiff.sourceforge.net{{/using}}
   {{using id}}homePage{{/using}}
   {{using body}}The whiff home page{{/using}}
   {{using cgi_params}} {"name": "george castanza", "age": 33} {{/using}}
{{/include}}

{{/using}}
{{/include}}

"""

# imports must be absolute
from whiff.middleware import misc
from whiff.middleware import link

class anchor(misc.utility):
    # XXXX this should be generalized to allow other anchor options?
    def __init__(self, url, body, cgi_params=None, **attributes):
        self.url = url
        self.cgi_params = cgi_params
        self.body = body
        self.attributes = attributes
    def __call__(self, env, start_response):
        linkapp = link.__middleware__(self.url, self.cgi_params)
        linktext = self.param_value(linkapp, env)
        body = self.param_value(self.body, env)
        id = None
        attributes = {}
        for (k,v) in self.attributes.items():
            attributes[k] = self.param_value(v, env)
        iatts = attributes.items()
        iatts.sort()
        #result = '<a href="%s">%s</a>' % (thelink, body)
        headers = self.derive_headers('text/plain')
        start_response("200 OK", headers)
        yield '<a href="'
        yield linktext
        yield '"'
        for (k,v) in iatts:
            yield ' %s="' % k
            yield v
            yield '"'
        yield '>'
        yield body
        yield '</a>'

__middleware__ = anchor

def test():
    env = {}
    app = anchor("application.cgi",  {"variable1": "value1", "variable2": "value2"}, "the body of the anchor", "anchor_id")
    results = app(env, misc.ignore)
    print "test of anchor got ", list(results)

if __name__=="__main__":
    test()
