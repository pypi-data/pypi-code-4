
whiffCategory = "tools"

whiffDoc = """
{{include "whiff_middleware/heading"}}
whiff_middleware/debugDump - dump WSGI environment as HTML
{{/include}}

The <code>whiff_middleware/debugDump</code>
middleware presents the WSGI environment in HTML
quoted form.

{{include "example"}}
{{using targetName}}debugDump{{/using}}
{{using page}}
<pre>
{{include "whiff_middleware/debugDump"/}}
</pre>
{{/using}}
{{/include}}

"""

# import must be absolute
from whiff.middleware import misc
from whiff import resolver
from whiff.rdjson import jsonParse
from whiff.middleware import quoteHtml

class dump(misc.utility):
    "dump out the environment as text/plain with html special characters quoted"
    def __init__(self,
                 parse_cgi = True,
                 content_type='text/plain'):
        self.content_type = content_type
        self.parse_cgi = parse_cgi
    def __call__(self, env, start_response):
        content_type = self.param_value(self.content_type, env)
        parse_cgi = self.param_json(self.parse_cgi, env)
        if parse_cgi:
            cgi = resolver.process_cgi(env, parse_cgi=True)
        json_env = jsonParse.format(env)
        quoted_json = resolver.quote(json_env)
        start_response("200 OK", [('Content-Type', content_type)])
        return [quoted_json]

__middleware__ = dump

if __name__=="__main__":
    env = {"test": "environment"}
    app = dump()
    print "test of debugDump gives", app(env, misc.ignore)

