"""
Format an "<a href...>" anchor
"""

whiffCategory = "formatting"

whiffDoc = """
{{include "whiff_middleware/heading"}}
whiff_middleware/image - format an img reference
{{/include}}

The <code>whiff_middleware/image</code> creates
an <code>img</code> link in a similar manner to
the way the <code>anchor</code> middleware creates
anchor links.

{{include "example"}}
{{using targetName}}image{{/using}}
{{using page}}

Bar code:<br>

{{include "whiff_middleware/image"}}
    {{using url}}http://chart.apis.google.com/chart{{/using}}
    {{using params}}
        { 
		"cht": "qr", 
		"chs": "150x150",
		"choe": "UTF-8", 
		"chl": "Boogie\nWoogie\nBugle\nBoy?" 
	}
    {{/using}}
{{/include}}

{{/using}}
{{/include}}

"""

# imports must be absolute
from whiff.middleware import misc
from whiff.middleware import link

class image(misc.utility):
    # XXXX this should be generalized to allow other img options?
    def __init__(self, url, params, id=None):
        self.url = url
        self.params = params
        self.id = id
    def __call__(self, env, start_response):
        linkapp = link.__middleware__(self.url, self.params)
        thelink = self.param_value(linkapp, env)
        id = None
        if self.id:
            id = self.param_value(self.id, env)
        #result = '<a href="%s">%s</a>' % (thelink, body)
        headers = self.derive_headers('text/plain')
        start_response("200 OK", headers)
        yield '<img src="'
        yield thelink
        yield '"'
        if id:
            yield ' id="'
            yield id
            yield '"'
        yield '>'

__middleware__ = image

def test():
    env = {}
    app = image("application.cgi",  {"variable1": "value1", "variable2": "value2"}, "image_id")
    results = app(env, misc.ignore)
    print "test of image got ", list(results)

if __name__=="__main__":
    test()
